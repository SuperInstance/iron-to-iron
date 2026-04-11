"""Tests for i2i-review.py — review template, parsing, validation."""

import re
from pathlib import Path

import pytest

from i2i_review import (
    create_review_template,
    parse_review,
    validate_review,
)


class TestCreateReviewTemplate:
    def test_basic(self):
        r = create_review_template(target_agent="a", repository="r", branch="b", commit="c", reviewer="rv", scope="s")
        assert "[I2I:REVIEW]" in r and "a" in r

    def test_output_file(self, tmp_path):
        out = tmp_path / "review.md"
        r = create_review_template(target_agent="a", repository="r", branch="b", commit="c", reviewer="rv", scope="s", output_file=str(out))
        assert out.exists() and out.read_text() == r

    def test_date_format(self):
        r = create_review_template(target_agent="a", repository="r", branch="b", commit="c", reviewer="rv", scope="s")
        assert re.search(r"\d{4}-\d{2}-\d{2}", r)


class TestParseReview:
    def _write(self, tmp, content):
        f = tmp / "review.md"
        f.write_text(content)
        return f

    def test_valid(self, tmp_path):
        c = "---\nTarget Agent: a\nRepository: r\nReviewer: rv\n---\n## Executive Summary\nS\n"
        r = parse_review(self._write(tmp_path, c))
        assert r["target_agent"] == "a"

    def test_no_frontmatter(self, tmp_path):
        r = parse_review(self._write(tmp_path, "## Executive Summary\nS\n"))
        assert isinstance(r, dict)

    def test_empty(self, tmp_path):
        assert isinstance(parse_review(self._write(tmp_path, "")), dict)


class TestValidateReview:
    def _write(self, tmp, content):
        f = tmp / "review.md"
        f.write_text(content)
        return f

    def test_perfect(self, tmp_path):
        c = "---\nTarget Agent: a\n---\n[I2I:REVIEW]\n## Executive Summary\nS\n## Strengths\n- G\n## Suggested Improvements\n- T\n## Blind Spots\n- B\n## Synergy Opportunities\n- O\n## Conclusion\nD\n"
        assert validate_review(self._write(tmp_path, c)) == []

    def test_missing_i2i(self, tmp_path):
        c = "---\nTarget Agent: a\n---\n## Executive Summary\nS\n## Strengths\n- G\n## Suggested Improvements\n- T\n## Blind Spots\n- B\n## Synergy Opportunities\n- O\n## Conclusion\nD\n"
        assert any("I2I" in e for e in validate_review(self._write(tmp_path, c)))

    def test_multiple_missing(self, tmp_path):
        c = "---\nTarget Agent: a\n---\n[I2I:REVIEW]\n## Conclusion\nD\n"
        assert len(validate_review(self._write(tmp_path, c))) >= 4
