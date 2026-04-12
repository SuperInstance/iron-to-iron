"""Tests for i2i-resolve.py — dispute lifecycle."""

import json
import uuid
from pathlib import Path

import pytest

from i2i_resolve import (
    init_dispute,
    add_counter_claim,
    analyze_dispute,
    resolve_dispute,
)


class TestDisputeLifecycle:
    def test_init_creates_dir(self, tmp_path):
        d = init_dispute(topic="t", claim="c", confidence="high", agent_name="a", repo_path=tmp_path)
        assert Path(d).is_dir()

    def test_init_metadata(self, tmp_path):
        d = init_dispute(topic="t", claim="c", confidence="high", agent_name="a", repo_path=tmp_path)
        m = json.loads((Path(d) / "metadata.json").read_text())
        assert m["status"] == "open"
        assert m["claims"][0]["position"] == "c"
        uuid.UUID(m["dispute_id"])  # should not raise

    def test_init_creates_claim_file(self, tmp_path):
        d = init_dispute(topic="t", claim="Original", confidence="high", agent_name="a", repo_path=tmp_path)
        files = list(Path(d).glob("claim-*.md"))
        assert len(files) >= 1
        assert "Original" in files[0].read_text()

    def test_add_counter(self, tmp_path):
        d = init_dispute(topic="t", claim="A", confidence="high", agent_name="a", repo_path=tmp_path)
        add_counter_claim(dispute_dir=Path(d), claim="B", confidence="medium", agent_name="b")
        m = json.loads((Path(d) / "metadata.json").read_text())
        assert m["status"] == "in_progress"
        assert len(m["claims"]) == 2

    def test_analyze(self, tmp_path):
        d = init_dispute(topic="t", claim="A", confidence="high", agent_name="a", repo_path=tmp_path)
        add_counter_claim(dispute_dir=Path(d), claim="B", confidence="medium", agent_name="b")
        r = analyze_dispute(Path(d))
        assert r["number_of_claims"] == 2

    def test_resolve(self, tmp_path):
        d = init_dispute(topic="t", claim="A", confidence="high", agent_name="a", repo_path=tmp_path)
        add_counter_claim(dispute_dir=Path(d), claim="B", confidence="medium", agent_name="b")
        rp = resolve_dispute(dispute_dir=Path(d), resolution="compromise", rationale="both valid", winner="a", dissenter="b", resolution_type="compromise")
        assert Path(rp).exists()
        m = json.loads((Path(d) / "metadata.json").read_text())
        assert m["status"] == "resolved"

    def test_full_lifecycle(self, tmp_path):
        d = init_dispute(topic="full", claim="A", confidence="high", agent_name="a", repo_path=tmp_path)
        add_counter_claim(dispute_dir=Path(d), claim="B", confidence="medium", agent_name="b")
        assert analyze_dispute(Path(d))["number_of_claims"] == 2
        resolve_dispute(dispute_dir=Path(d), resolution="arbitration", rationale="evidence", winner="a", dissenter="b", resolution_type="arbitration")
        m = json.loads((Path(d) / "metadata.json").read_text())
        assert m["status"] == "resolved"
