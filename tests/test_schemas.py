"""Tests for JSON schema validation of I2I protocol schemas."""

import json
from pathlib import Path

import jsonschema
import pytest

SCHEMAS_DIR = Path(__file__).parent.parent / "schemas"


def _load_schema(name):
    return json.loads((SCHEMAS_DIR / name).read_text())


class TestCommitMessageSchema:
    schema = None

    @pytest.fixture(autouse=True)
    def _load(self):
        self.schema = _load_schema("commit-message.schema.json")

    def test_commit_message_schema_valid(self):
        """Well-formed commit message should pass validation."""
        msg = {
            "type": "PROPOSAL",
            "scope": "runtime/scheduler",
            "summary": "add exponential backoff to retry logic",
            "body": "Implementing exponential backoff with jitter.",
        }
        # Should not raise
        jsonschema.validate(msg, self.schema)

    def test_commit_message_schema_invalid_type(self):
        """Invalid type 'FOOBAR' should fail validation."""
        msg = {
            "type": "FOOBAR",
            "scope": "test",
            "summary": "bad type",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(msg, self.schema)

    def test_commit_message_schema_missing_required(self):
        """Missing 'scope' should fail validation."""
        msg = {
            "type": "REVIEW",
            "summary": "missing scope field",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(msg, self.schema)
