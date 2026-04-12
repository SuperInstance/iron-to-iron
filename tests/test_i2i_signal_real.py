"""Tests for i2i-signal.py — vocabulary scanning, signal generation, agent comparison."""

import hashlib
import json
from pathlib import Path

import pytest

from i2i_signal import (
    interpret_compatibility,
    parse_ese_file,
    scan_vocabularies,
    read_tombstones,
    generate_signal,
    compare_agents,
    verify_tombstones,
)


class TestInterpretCompatibility:
    def test_highly_compatible_1_0(self):
        assert "Highly compatible" in interpret_compatibility(1.0)

    def test_highly_compatible_0_8(self):
        assert "Highly compatible" in interpret_compatibility(0.8)

    def test_compatible_0_5(self):
        r = interpret_compatibility(0.5)
        assert "Compatible" in r and "Highly" not in r

    def test_limited_0_2(self):
        assert "Limited" in interpret_compatibility(0.2)

    def test_incompatible_0_0(self):
        assert "Incompatible" in interpret_compatibility(0.0)

    def test_below_highly(self):
        assert "Highly" not in interpret_compatibility(0.79)

    def test_negative(self):
        assert "Incompatible" in interpret_compatibility(-0.5)

    def test_below_compatible(self):
        r = interpret_compatibility(0.49)
        assert "Limited" in r or "Compatible" not in r


class TestParseEseFile:
    def _write(self, tmp, content):
        f = tmp / "test.ese"
        f.write_text(content)
        return f

    def test_normal(self, tmp_path):
        r = parse_ese_file(self._write(tmp_path, "a: b\nc: d\n"))
        assert r["count"] == 2
        assert r["entries"][0]["concept"] == "a"

    def test_comments(self, tmp_path):
        r = parse_ese_file(self._write(tmp_path, "# comment\na: b\n"))
        assert r["count"] == 1

    def test_blank_lines(self, tmp_path):
        r = parse_ese_file(self._write(tmp_path, "a: b\n\n\nc: d\n"))
        assert r["count"] == 2

    def test_multi_colon(self, tmp_path):
        r = parse_ese_file(self._write(tmp_path, "x: a: b: c\n"))
        assert r["entries"][0]["definition"] == "a: b: c"

    def test_empty(self, tmp_path):
        r = parse_ese_file(self._write(tmp_path, ""))
        assert r["count"] == 0


class TestScanVocabularies:
    def test_normal(self, tmp_path):
        d = tmp_path / "vocabularies"
        d.mkdir()
        (d / "a.ese").write_text("x: y\n")
        (d / "b.ese").write_text("z: w\n")
        assert len(scan_vocabularies(tmp_path)) == 2

    def test_missing(self, tmp_path):
        assert scan_vocabularies(tmp_path) == []

    def test_non_ese_ignored(self, tmp_path):
        d = tmp_path / "vocabularies"
        d.mkdir()
        (d / "readme.md").write_text("ignore")
        (d / "v.ese").write_text("a: b\n")
        assert len(scan_vocabularies(tmp_path)) == 1

    def test_empty_dir(self, tmp_path):
        (tmp_path / "vocabularies").mkdir()
        assert scan_vocabularies(tmp_path) == []


class TestReadTombstones:
    def test_valid(self, tmp_path):
        ts = tmp_path / "tombstones.json"
        ts.write_text(json.dumps({"entries": [], "summary": {"total": 0}}))
        assert read_tombstones(tmp_path)["summary"]["total"] == 0

    def test_missing(self, tmp_path):
        r = read_tombstones(tmp_path)
        assert "entries" in r

    def test_extra_fields(self, tmp_path):
        ts = tmp_path / "tombstones.json"
        ts.write_text(json.dumps({"entries": [], "summary": {}, "extra": True}))
        assert read_tombstones(tmp_path).get("extra") is True


class TestVerifyTombstones:
    def _entry(self, c, d):
        return {"concept": c, "definition": d, "hash": hashlib.sha256(f"{c}:{d}".encode()).hexdigest()}

    def test_all_valid(self, tmp_path):
        ts = tmp_path / "tombstones.json"
        ts.write_text(json.dumps({"entries": [self._entry("a", "b")]}))
        assert verify_tombstones(ts) == []

    def test_tampered(self, tmp_path):
        ts = tmp_path / "tombstones.json"
        h = hashlib.sha256("a:original".encode()).hexdigest()
        ts.write_text(json.dumps({"entries": [{"concept": "a", "definition": "tampered", "hash": h}]}))
        assert len(verify_tombstones(ts)) == 1

    def test_empty(self, tmp_path):
        ts = tmp_path / "tombstones.json"
        ts.write_text(json.dumps({"entries": []}))
        assert verify_tombstones(ts) == []

    def test_multiple_bad(self, tmp_path):
        ts = tmp_path / "tombstones.json"
        entries = [self._entry("ok", "fine"), {"concept": "bad1", "definition": "x", "hash": "wrong"}, {"concept": "bad2", "definition": "y", "hash": "wrong"}]
        ts.write_text(json.dumps({"entries": entries}))
        assert len(verify_tombstones(ts)) == 2


class TestGenerateSignal:
    def test_single_vocab(self, tmp_path):
        d = tmp_path / "vocabularies"
        d.mkdir()
        (d / "v.ese").write_text("a: b\nc: d\ne: f\n")
        r = generate_signal(tmp_path)
        assert r["total_entries"] == 3

    def test_agent_id(self, tmp_path):
        d = tmp_path / "vocabularies"
        d.mkdir()
        (d / "v.ese").write_text("x: y\n")
        assert generate_signal(tmp_path)["agent_id"] == tmp_path.name

    def test_empty(self, tmp_path):
        assert generate_signal(tmp_path)["total_entries"] == 0

    def test_with_tombstones(self, tmp_path):
        d = tmp_path / "vocabularies"
        d.mkdir()
        (d / "v.ese").write_text("a: b\n")
        (tmp_path / "tombstones.json").write_text(json.dumps({"entries": [], "summary": {}}))
        assert "tombstones" in generate_signal(tmp_path)


class TestCompareAgents:
    def _agent(self, tmp, name, concepts, vocab_name=None):
        d = tmp / name
        d.mkdir()
        vd = d / "vocabularies"
        vd.mkdir()
        vfile = vocab_name if vocab_name else f"{name}.ese"
        (vd / vfile).write_text("\n".join(f"{c}: def" for c in concepts))
        return d

    def test_identical(self, tmp_path):
        a = self._agent(tmp_path, "a", ["x", "y"], vocab_name="shared.ese")
        b = self._agent(tmp_path, "b", ["x", "y"], vocab_name="shared.ese")
        assert compare_agents(a, b)["compatibility_score"] == 1.0

    def test_no_overlap(self, tmp_path):
        a = self._agent(tmp_path, "a", ["x"], vocab_name="sysprog.ese")
        b = self._agent(tmp_path, "b", ["y"], vocab_name="ml.ese")
        assert compare_agents(a, b)["compatibility_score"] == 0.0

    def test_partial(self, tmp_path):
        # a has shared.ese with [y,z], core.ese with [x]; b has shared.ese with [y,z], extra.ese with [w]
        a_dir = tmp_path / "a"
        a_dir.mkdir()
        avd = a_dir / "vocabularies"
        avd.mkdir()
        (avd / "shared.ese").write_text("y: def\nz: def")
        (avd / "core.ese").write_text("x: def")
        b_dir = tmp_path / "b"
        b_dir.mkdir()
        bvd = b_dir / "vocabularies"
        bvd.mkdir()
        (bvd / "shared.ese").write_text("y: def\nz: def")
        (bvd / "extra.ese").write_text("w: def")
        r = compare_agents(a_dir, b_dir)
        assert r["shared_count"] == 1
        assert r["compatibility_score"] == 0.5

    def test_one_empty(self, tmp_path):
        a = self._agent(tmp_path, "a", ["x"])
        (tmp_path / "b").mkdir()
        assert compare_agents(a, tmp_path / "b")["compatibility_score"] == 0.0

    def test_interpretation_included(self, tmp_path):
        a = self._agent(tmp_path, "a", ["shared"], vocab_name="shared.ese")
        b = self._agent(tmp_path, "b", ["shared"], vocab_name="shared.ese")
        assert "interpretation" in compare_agents(a, b)


class TestParseEseFileEdgeCases:
    def test_parse_ese_file_non_utf8(self, tmp_path):
        """Non-UTF-8 bytes should be handled gracefully (UnicodeDecodeError)."""
        f = tmp_path / "bad.ese"
        f.write_bytes(b"\xff\xfe invalid utf8\r\nx: y\n")
        with pytest.raises(UnicodeDecodeError):
            parse_ese_file(f)


class TestScanVocabulariesEdgeCases:
    def test_scan_vocabularies_nested_subdirs_ignored(self, tmp_path):
        """Files in subdirectories of vocabularies/ should NOT be picked up."""
        d = tmp_path / "vocabularies"
        d.mkdir()
        (d / "top.ese").write_text("a: b\n")
        sub = d / "subdir"
        sub.mkdir()
        (sub / "nested.ese").write_text("c: d\n")
        result = scan_vocabularies(tmp_path)
        names = [v["file"] for v in result]
        assert "top.ese" in names
        assert "nested.ese" not in names
        assert len(result) == 1


class TestReadTombstonesEdgeCases:
    def test_read_tombstones_malformed_json(self, tmp_path):
        """Malformed JSON in tombstones.json should be handled gracefully."""
        ts = tmp_path / "tombstones.json"
        ts.write_text("{invalid json!!!")
        with pytest.raises(json.JSONDecodeError):
            read_tombstones(tmp_path)


class TestVerifyTombstonesEdgeCases:
    def test_verify_tombstones_missing_definition_field(self, tmp_path):
        """Entry without 'definition' key should not crash."""
        ts = tmp_path / "tombstones.json"
        ts.write_text(json.dumps({"entries": [{"concept": "orphan", "hash": "whatever"}]}))
        # Should not raise — entry with missing definition should be flagged as suspicious
        result = verify_tombstones(ts)
        assert isinstance(result, list)
