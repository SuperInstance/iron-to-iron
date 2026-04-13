"""
I2I v2 Protocol - Comprehensive Test Suite

Tests for all 20 message types, message bus, validation, serialization,
and error handling.
"""

import asyncio
import json
import time
import unittest
from datetime import datetime, timezone, timedelta

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from i2i_v2 import (
    # Version and constants
    PROTOCOL_VERSION,
    MESSAGE_TYPE_NAMES,
    __version__,
    # Message types
    MessageCategory,
    MessageTypeDefinition,
    FieldSchema,
    ALL_MESSAGE_TYPES,
    MESSAGE_TYPE_HEARTBEAT,
    MESSAGE_TYPE_TASK_CLAIM,
    MESSAGE_TYPE_TASK_COMPLETE,
    MESSAGE_TYPE_TRUST_UPDATE,
    MESSAGE_TYPE_SIGNAL_BROADCAST,
    MESSAGE_TYPE_FLEET_DISCOVERY,
    MESSAGE_TYPE_MERIT_AWARD,
    MESSAGE_TYPE_BOTTLE_CAST,
    MESSAGE_TYPE_NAMESPACE_QUERY,
    MESSAGE_TYPE_OPCODE_REQUEST,
    MESSAGE_TYPE_INSTRUCTION_STREAM,
    MESSAGE_TYPE_CONFIDENCE_REPORT,
    MESSAGE_TYPE_VIEWPOINT_EXCHANGE,
    MESSAGE_TYPE_COORDINATE_PROPOSE,
    MESSAGE_TYPE_COORDINATE_ACCEPT,
    MESSAGE_TYPE_COORDINATE_REJECT,
    MESSAGE_TYPE_STATUS_REPORT,
    MESSAGE_TYPE_ERROR_REPORT,
    MESSAGE_TYPE_SHUTDOWN,
    MESSAGE_TYPE_PING,
    # Lookup functions
    get_message_type,
    get_message_type_by_code,
    list_message_types,
    list_message_types_by_category,
    # Message
    Message,
    MessageHeader,
    create_pong,
    create_error_reply,
    # Bus
    MessageBus,
    DeliveryGuarantee,
    BusMetrics,
    # Exceptions
    I2IError,
    InvalidMessageTypeError,
    MessageValidationError,
    SerializationError,
    MessageBusError,
    DuplicateHandlerError,
    NoHandlerError,
    VersionMismatchError,
    MessageExpiredError,
)


# ========================================================================
# 1. Protocol Version and Constants
# ========================================================================

class TestProtocolVersion(unittest.TestCase):
    """Test protocol version and constant definitions."""

    def test_version_is_v2(self):
        self.assertEqual(PROTOCOL_VERSION, "2.0.0")
        self.assertEqual(__version__, "2.0.0")

    def test_twenty_message_types_defined(self):
        self.assertEqual(len(MESSAGE_TYPE_NAMES), 20)

    def test_all_message_type_names_are_unique(self):
        self.assertEqual(len(set(MESSAGE_TYPE_NAMES)), 20)

    def test_all_types_registered_in_all_message_types(self):
        for name in MESSAGE_TYPE_NAMES:
            self.assertIn(name, ALL_MESSAGE_TYPES)


# ========================================================================
# 2. Message Type Definitions (all 20)
# ========================================================================

class TestMessageTypes(unittest.TestCase):
    """Test all 20 message type definitions."""

    def test_01_heartbeat_definition(self):
        mt = MESSAGE_TYPE_HEARTBEAT
        self.assertEqual(mt.name, "HEARTBEAT")
        self.assertEqual(mt.code, "HBT")
        self.assertEqual(mt.category, MessageCategory.HEARTBEAT)
        self.assertTrue(mt.fields[0].name == "agent_id")
        self.assertEqual(mt.ttl_seconds, 30)

    def test_02_task_claim_definition(self):
        mt = MESSAGE_TYPE_TASK_CLAIM
        self.assertEqual(mt.name, "TASK_CLAIM")
        self.assertEqual(mt.code, "TCL")
        self.assertTrue(mt.expects_reply)
        self.assertIn("TASK_COMPLETE", mt.reply_types)

    def test_03_task_complete_definition(self):
        mt = MESSAGE_TYPE_TASK_COMPLETE
        self.assertEqual(mt.name, "TASK_COMPLETE")
        self.assertEqual(mt.code, "TCM")
        self.assertEqual(mt.category, MessageCategory.TASK)
        self.assertIn("success", mt.fields[2].enum_values)

    def test_04_trust_update_definition(self):
        mt = MESSAGE_TYPE_TRUST_UPDATE
        self.assertEqual(mt.name, "TRUST_UPDATE")
        self.assertEqual(mt.code, "TRU")
        self.assertEqual(mt.category, MessageCategory.TRUST)

    def test_05_signal_broadcast_definition(self):
        mt = MESSAGE_TYPE_SIGNAL_BROADCAST
        self.assertEqual(mt.name, "SIGNAL_BROADCAST")
        self.assertEqual(mt.code, "SIG")
        self.assertIn("lighthouse", mt.fields[2].enum_values)

    def test_06_fleet_discovery_definition(self):
        mt = MESSAGE_TYPE_FLEET_DISCOVERY
        self.assertEqual(mt.name, "FLEET_DISCOVERY")
        self.assertEqual(mt.code, "DSC")
        self.assertTrue(mt.expects_reply)

    def test_07_merit_award_definition(self):
        mt = MESSAGE_TYPE_MERIT_AWARD
        self.assertEqual(mt.name, "MERIT_AWARD")
        self.assertEqual(mt.code, "MRT")
        self.assertEqual(mt.category, MessageCategory.TRUST)

    def test_08_bottle_cast_definition(self):
        mt = MESSAGE_TYPE_BOTTLE_CAST
        self.assertEqual(mt.name, "BOTTLE_CAST")
        self.assertEqual(mt.code, "BTL")
        self.assertEqual(mt.category, MessageCategory.KNOWLEDGE)

    def test_09_namespace_query_definition(self):
        mt = MESSAGE_TYPE_NAMESPACE_QUERY
        self.assertEqual(mt.name, "NAMESPACE_QUERY")
        self.assertEqual(mt.code, "NSQ")
        self.assertTrue(mt.expects_reply)

    def test_10_opcode_request_definition(self):
        mt = MESSAGE_TYPE_OPCODE_REQUEST
        self.assertEqual(mt.name, "OPCODE_REQUEST")
        self.assertEqual(mt.code, "OPR")
        self.assertIn("INSTRUCTION_STREAM", mt.reply_types)

    def test_11_instruction_stream_definition(self):
        mt = MESSAGE_TYPE_INSTRUCTION_STREAM
        self.assertEqual(mt.name, "INSTRUCTION_STREAM")
        self.assertEqual(mt.code, "INS")

    def test_12_confidence_report_definition(self):
        mt = MESSAGE_TYPE_CONFIDENCE_REPORT
        self.assertEqual(mt.name, "CONFIDENCE_REPORT")
        self.assertEqual(mt.code, "CFR")
        self.assertEqual(mt.category, MessageCategory.COORDINATION)

    def test_13_viewpoint_exchange_definition(self):
        mt = MESSAGE_TYPE_VIEWPOINT_EXCHANGE
        self.assertEqual(mt.name, "VIEWPOINT_EXCHANGE")
        self.assertEqual(mt.code, "VPE")
        self.assertIn("for", mt.fields[3].enum_values)

    def test_14_coordinate_propose_definition(self):
        mt = MESSAGE_TYPE_COORDINATE_PROPOSE
        self.assertEqual(mt.name, "COORDINATE_PROPOSE")
        self.assertEqual(mt.code, "COP")
        self.assertIn("COORDINATE_ACCEPT", mt.reply_types)
        self.assertIn("COORDINATE_REJECT", mt.reply_types)

    def test_15_coordinate_accept_definition(self):
        mt = MESSAGE_TYPE_COORDINATE_ACCEPT
        self.assertEqual(mt.name, "COORDINATE_ACCEPT")
        self.assertEqual(mt.code, "COA")

    def test_16_coordinate_reject_definition(self):
        mt = MESSAGE_TYPE_COORDINATE_REJECT
        self.assertEqual(mt.name, "COORDINATE_REJECT")
        self.assertEqual(mt.code, "COR")

    def test_17_status_report_definition(self):
        mt = MESSAGE_TYPE_STATUS_REPORT
        self.assertEqual(mt.name, "STATUS_REPORT")
        self.assertEqual(mt.code, "STR")
        self.assertEqual(mt.category, MessageCategory.STATUS)

    def test_18_error_report_definition(self):
        mt = MESSAGE_TYPE_ERROR_REPORT
        self.assertEqual(mt.name, "ERROR_REPORT")
        self.assertEqual(mt.code, "ERR")
        self.assertEqual(mt.category, MessageCategory.ERROR)

    def test_19_shutdown_definition(self):
        mt = MESSAGE_TYPE_SHUTDOWN
        self.assertEqual(mt.name, "SHUTDOWN")
        self.assertEqual(mt.code, "SDN")
        self.assertEqual(mt.category, MessageCategory.LIFECYCLE)

    def test_20_ping_definition(self):
        mt = MESSAGE_TYPE_PING
        self.assertEqual(mt.name, "PING")
        self.assertEqual(mt.code, "PNG")
        self.assertEqual(mt.category, MessageCategory.HEARTBEAT)
        self.assertTrue(mt.expects_reply)
        self.assertEqual(mt.ttl_seconds, 30)


# ========================================================================
# 3. Lookup Functions
# ========================================================================

class TestLookups(unittest.TestCase):
    """Test message type lookup functions."""

    def test_get_by_name(self):
        mt = get_message_type("HEARTBEAT")
        self.assertEqual(mt.code, "HBT")

    def test_get_by_code(self):
        mt = get_message_type_by_code("HBT")
        self.assertEqual(mt.name, "HEARTBEAT")

    def test_get_unknown_raises(self):
        with self.assertRaises(InvalidMessageTypeError):
            get_message_type("NOT_A_TYPE")

    def test_get_unknown_code_raises(self):
        with self.assertRaises(InvalidMessageTypeError):
            get_message_type_by_code("XXX")

    def test_list_types_returns_20(self):
        types = list_message_types()
        self.assertEqual(len(types), 20)

    def test_list_by_category(self):
        cats = list_message_types_by_category()
        self.assertIn("heartbeat", cats)
        self.assertIn("task", cats)
        self.assertIn("trust", cats)
        # HEARTBEAT and PING both in heartbeat category
        self.assertEqual(len(cats["heartbeat"]), 2)


# ========================================================================
# 4. Field Schema Validation
# ========================================================================

class TestFieldSchemaValidation(unittest.TestCase):
    """Test FieldSchema.validate_value()."""

    def test_required_field_missing(self):
        field = FieldSchema("agent_id", "string", required=True)
        errors = field.validate_value(None)
        self.assertEqual(len(errors), 1)
        self.assertIn("required", errors[0].lower())

    def test_optional_field_missing_ok(self):
        field = FieldSchema("metadata", "object", required=False)
        errors = field.validate_value(None)
        self.assertEqual(len(errors), 0)

    def test_wrong_type(self):
        field = FieldSchema("count", "integer", required=True)
        errors = field.validate_value("not an int")
        self.assertTrue(len(errors) > 0)

    def test_correct_integer(self):
        field = FieldSchema("count", "integer", required=True)
        errors = field.validate_value(42)
        self.assertEqual(len(errors), 0)

    def test_enum_valid(self):
        field = FieldSchema("status", "enum", required=True,
                            enum_values=["active", "idle"])
        errors = field.validate_value("active")
        self.assertEqual(len(errors), 0)

    def test_enum_invalid(self):
        field = FieldSchema("status", "enum", required=True,
                            enum_values=["active", "idle"])
        errors = field.validate_value("unknown")
        self.assertTrue(len(errors) > 0)

    def test_float_range_min(self):
        field = FieldSchema("score", "float", required=True, min_value=0.0)
        errors = field.validate_value(-0.1)
        self.assertTrue(len(errors) > 0)

    def test_float_range_max(self):
        field = FieldSchema("score", "float", required=True, max_value=1.0)
        errors = field.validate_value(1.5)
        self.assertTrue(len(errors) > 0)

    def test_string_max_length(self):
        field = FieldSchema("name", "string", required=True, max_length=5)
        errors = field.validate_value("way too long")
        self.assertTrue(len(errors) > 0)

    def test_array_item_type(self):
        field = FieldSchema("ids", "array", required=False, item_type="string")
        errors = field.validate_value(["a", "b", 123])
        self.assertTrue(len(errors) > 0)

    def test_array_item_type_all_valid(self):
        field = FieldSchema("ids", "array", required=False, item_type="string")
        errors = field.validate_value(["a", "b", "c"])
        self.assertEqual(len(errors), 0)


# ========================================================================
# 5. Payload Validation
# ========================================================================

class TestPayloadValidation(unittest.TestCase):
    """Test MessageTypeDefinition.validate_payload()."""

    def test_valid_heartbeat_payload(self):
        mt = MESSAGE_TYPE_HEARTBEAT
        errors = mt.validate_payload({
            "agent_id": "agent-001",
            "status": "active",
            "timestamp": "2026-04-11T00:00:00Z",
        })
        self.assertEqual(len(errors), 0)

    def test_missing_required_field(self):
        mt = MESSAGE_TYPE_HEARTBEAT
        errors = mt.validate_payload({
            "agent_id": "agent-001",
            # Missing "status" and "timestamp"
        })
        self.assertTrue(len(errors) > 0)

    def test_unexpected_field_detected(self):
        mt = MESSAGE_TYPE_HEARTBEAT
        errors = mt.validate_payload({
            "agent_id": "agent-001",
            "status": "active",
            "timestamp": "2026-04-11T00:00:00Z",
            "bogus_field": "should not be here",
        })
        self.assertTrue(any("unexpected" in e.lower() for e in errors))

    def test_valid_task_claim(self):
        errors = MESSAGE_TYPE_TASK_CLAIM.validate_payload({
            "task_id": "task-123",
            "agent_id": "agent-001",
            "task_type": "code_review",
        })
        self.assertEqual(len(errors), 0)

    def test_valid_error_report(self):
        errors = MESSAGE_TYPE_ERROR_REPORT.validate_payload({
            "agent_id": "agent-001",
            "error_code": "OOM",
            "severity": "critical",
            "description": "Out of memory",
        })
        self.assertEqual(len(errors), 0)


# ========================================================================
# 6. Message Creation and Validation
# ========================================================================

class TestMessageCreation(unittest.TestCase):
    """Test Message.create() with all 20 types."""

    def _create_msg(self, type_name, payload):
        return Message.create(type_name, payload, source_agent="test-agent")

    def test_create_heartbeat(self):
        msg = self._create_msg("HEARTBEAT", {
            "agent_id": "agent-001",
            "status": "active",
            "timestamp": "2026-04-11T00:00:00Z",
        })
        self.assertEqual(msg.type_name, "HEARTBEAT")
        self.assertEqual(msg.type_code, "HBT")
        self.assertTrue(msg.is_valid())

    def test_create_task_claim(self):
        msg = self._create_msg("TASK_CLAIM", {
            "task_id": "t-1",
            "agent_id": "a-1",
            "task_type": "testing",
            "priority": "high",
        })
        self.assertEqual(msg.type_name, "TASK_CLAIM")
        self.assertTrue(msg.is_valid())

    def test_create_task_complete(self):
        msg = self._create_msg("TASK_COMPLETE", {
            "task_id": "t-1",
            "agent_id": "a-1",
            "result": "success",
            "summary": "All tests pass",
        })
        self.assertEqual(msg.type_name, "TASK_COMPLETE")
        self.assertTrue(msg.is_valid())

    def test_create_trust_update(self):
        msg = self._create_msg("TRUST_UPDATE", {
            "from_agent": "a-1",
            "to_agent": "a-2",
            "trust_delta": 0.3,
            "reason": "Great review",
        })
        self.assertEqual(msg.type_name, "TRUST_UPDATE")
        self.assertTrue(msg.is_valid())

    def test_create_signal_broadcast(self):
        msg = self._create_msg("SIGNAL_BROADCAST", {
            "agent_id": "oracle1",
            "agent_name": "Oracle1",
            "role": "lighthouse",
            "capabilities": ["vocab", "disputes"],
        })
        self.assertEqual(msg.type_name, "SIGNAL_BROADCAST")
        self.assertTrue(msg.is_valid())

    def test_create_fleet_discovery(self):
        msg = self._create_msg("FLEET_DISCOVERY", {
            "agent_id": "scout-1",
            "query_type": "announce",
        })
        self.assertEqual(msg.type_name, "FLEET_DISCOVERY")
        self.assertTrue(msg.is_valid())

    def test_create_merit_award(self):
        msg = self._create_msg("MERIT_AWARD", {
            "from_agent": "a-1",
            "to_agent": "a-2",
            "merit_type": "code_excellence",
            "points": 50,
            "citation": "Excellent implementation",
        })
        self.assertEqual(msg.type_name, "MERIT_AWARD")
        self.assertTrue(msg.is_valid())

    def test_create_bottle_cast(self):
        msg = self._create_msg("BOTTLE_CAST", {
            "from_agent": "a-1",
            "bottle_type": "lesson_learned",
            "content": "Always validate before merge",
        })
        self.assertEqual(msg.type_name, "BOTTLE_CAST")
        self.assertTrue(msg.is_valid())

    def test_create_namespace_query(self):
        msg = self._create_msg("NAMESPACE_QUERY", {
            "from_agent": "a-1",
            "target_agent": "a-2",
            "query_type": "vocab_list",
        })
        self.assertEqual(msg.type_name, "NAMESPACE_QUERY")
        self.assertTrue(msg.is_valid())

    def test_create_opcode_request(self):
        msg = self._create_msg("OPCODE_REQUEST", {
            "request_id": "req-1",
            "from_agent": "a-1",
            "target_agent": "a-2",
            "opcode": "EVAL",
        })
        self.assertEqual(msg.type_name, "OPCODE_REQUEST")
        self.assertTrue(msg.is_valid())

    def test_create_instruction_stream(self):
        msg = self._create_msg("INSTRUCTION_STREAM", {
            "stream_id": "s-1",
            "agent_id": "a-1",
            "sequence_num": 1,
            "instruction": "eval(x + 1)",
            "status": "in_progress",
        })
        self.assertEqual(msg.type_name, "INSTRUCTION_STREAM")
        self.assertTrue(msg.is_valid())

    def test_create_confidence_report(self):
        msg = self._create_msg("CONFIDENCE_REPORT", {
            "agent_id": "a-1",
            "topic": "backoff strategy",
            "confidence": 0.85,
            "rationale": "Benchmarks show improvement",
        })
        self.assertEqual(msg.type_name, "CONFIDENCE_REPORT")
        self.assertTrue(msg.is_valid())

    def test_create_viewpoint_exchange(self):
        msg = self._create_msg("VIEWPOINT_EXCHANGE", {
            "from_agent": "a-1",
            "topic": "retry strategy",
            "viewpoint": "Linear backoff is better for low concurrency",
            "stance": "for",
        })
        self.assertEqual(msg.type_name, "VIEWPOINT_EXCHANGE")
        self.assertTrue(msg.is_valid())

    def test_create_coordinate_propose(self):
        msg = self._create_msg("COORDINATE_PROPOSE", {
            "from_agent": "a-1",
            "to_agent": "a-2",
            "coordination_type": "joint_review",
            "proposal": "Let's review the PR together",
        })
        self.assertEqual(msg.type_name, "COORDINATE_PROPOSE")
        self.assertTrue(msg.is_valid())

    def test_create_coordinate_accept(self):
        msg = self._create_msg("COORDINATE_ACCEPT", {
            "from_agent": "a-2",
            "proposal_id": "prop-1",
        })
        self.assertEqual(msg.type_name, "COORDINATE_ACCEPT")
        self.assertTrue(msg.is_valid())

    def test_create_coordinate_reject(self):
        msg = self._create_msg("COORDINATE_REJECT", {
            "from_agent": "a-2",
            "proposal_id": "prop-1",
            "reason": "Too busy right now",
        })
        self.assertEqual(msg.type_name, "COORDINATE_REJECT")
        self.assertTrue(msg.is_valid())

    def test_create_status_report(self):
        msg = self._create_msg("STATUS_REPORT", {
            "agent_id": "a-1",
            "status": "busy",
            "current_task": "Reviewing PRs",
            "capacity": 40,
        })
        self.assertEqual(msg.type_name, "STATUS_REPORT")
        self.assertTrue(msg.is_valid())

    def test_create_error_report(self):
        msg = self._create_msg("ERROR_REPORT", {
            "agent_id": "a-1",
            "error_code": "OOM",
            "severity": "high",
            "description": "Memory limit exceeded",
        })
        self.assertEqual(msg.type_name, "ERROR_REPORT")
        self.assertTrue(msg.is_valid())

    def test_create_shutdown(self):
        msg = self._create_msg("SHUTDOWN", {
            "agent_id": "a-1",
            "reason": "maintenance",
            "message": "Back in 5 minutes",
        })
        self.assertEqual(msg.type_name, "SHUTDOWN")
        self.assertTrue(msg.is_valid())

    def test_create_ping(self):
        msg = self._create_msg("PING", {
            "from_agent": "a-1",
            "timestamp": "2026-04-11T00:00:00Z",
        })
        self.assertEqual(msg.type_name, "PING")
        self.assertTrue(msg.is_valid())

    def test_create_invalid_type_raises(self):
        with self.assertRaises(InvalidMessageTypeError):
            self._create_msg("BOGUS", {"field": "value"})

    def test_create_invalid_payload_fails_validation(self):
        msg = self._create_msg("HEARTBEAT", {
            "agent_id": "a-1",
            # missing required "status" and "timestamp"
        })
        self.assertFalse(msg.is_valid())


# ========================================================================
# 7. Message Serialization (JSON)
# ========================================================================

class TestMessageSerialization(unittest.TestCase):
    """Test JSON serialization and deserialization."""

    def test_to_json_roundtrip(self):
        original = Message.create("PING", {
            "from_agent": "a-1",
            "timestamp": "2026-04-11T00:00:00Z",
            "nonce": "nonce-123",
        }, source_agent="a-1")

        json_str = original.to_json()
        restored = Message.from_json(json_str)

        self.assertEqual(restored.header.message_type, "PING")
        self.assertEqual(restored.header.message_code, "PNG")
        self.assertEqual(restored.payload["nonce"], "nonce-123")
        self.assertEqual(restored.header.source_agent, "a-1")

    def test_to_dict_roundtrip(self):
        original = Message.create("STATUS_REPORT", {
            "agent_id": "a-1",
            "status": "online",
            "capacity": 80,
        }, source_agent="a-1")

        data = original.to_dict()
        restored = Message.from_dict(data)

        self.assertEqual(restored.type_name, "STATUS_REPORT")
        self.assertEqual(restored.payload["capacity"], 80)

    def test_pretty_json(self):
        msg = Message.create("HEARTBEAT", {
            "agent_id": "a-1",
            "status": "active",
            "timestamp": "2026-04-11T00:00:00Z",
        })
        pretty = msg.to_json(pretty=True)
        self.assertIn("\n", pretty)
        # Parseable
        parsed = json.loads(pretty)
        self.assertEqual(parsed["header"]["message_type"], "HEARTBEAT")

    def test_from_json_invalid_raises(self):
        with self.assertRaises(SerializationError):
            Message.from_json("not valid json {{{")

    def test_from_json_empty_object(self):
        msg = Message.from_json("{}")
        self.assertEqual(msg.header.protocol_version, PROTOCOL_VERSION)

    def test_serialization_preserves_correlation_id(self):
        msg = Message.create("TASK_CLAIM", {
            "task_id": "t-1",
            "agent_id": "a-1",
            "task_type": "code_review",
        }, source_agent="a-1", correlation_id="corr-123")

        json_str = msg.to_json()
        restored = Message.from_json(json_str)
        self.assertEqual(restored.header.correlation_id, "corr-123")


# ========================================================================
# 8. Commit Message Format
# ========================================================================

class TestCommitMessageFormat(unittest.TestCase):
    """Test I2I commit message generation."""

    def test_heartbeat_commit_format(self):
        msg = Message.create("HEARTBEAT", {
            "agent_id": "oracle1",
            "status": "active",
            "timestamp": "2026-04-11T00:00:00Z",
        }, source_agent="oracle1")

        commit = msg.to_commit_message()
        self.assertIn("[I2I:HEARTBEAT:HBT]", commit)
        self.assertIn("oracle1", commit)

    def test_task_claim_commit_format(self):
        msg = Message.create("TASK_CLAIM", {
            "task_id": "T-016",
            "agent_id": "superz",
            "task_type": "implementation",
            "priority": "high",
            "summary": "Implement I2I v2 protocol",
        }, source_agent="superz")

        commit = msg.to_commit_message()
        self.assertIn("[I2I:TASK_CLAIM:TCL]", commit)
        self.assertIn("Implement I2I v2 protocol", commit)
        self.assertIn("Co-Authored-By: superz", commit)

    def test_error_report_commit_format(self):
        msg = Message.create("ERROR_REPORT", {
            "agent_id": "a-1",
            "error_code": "OOM",
            "severity": "critical",
            "description": "Out of memory during processing",
        }, source_agent="a-1")

        commit = msg.to_commit_message()
        self.assertIn("[I2I:ERROR_REPORT:ERR]", commit)
        self.assertIn("Co-Authored-By: a-1", commit)


# ========================================================================
# 9. Message Signing
# ========================================================================

class TestMessageSigning(unittest.TestCase):
    """Test message signing and verification."""

    def test_sign_produces_hash(self):
        msg = Message.create("PING", {
            "from_agent": "a-1",
            "timestamp": "2026-04-11T00:00:00Z",
        })
        sig = msg.sign()
        self.assertEqual(len(sig), 64)  # SHA-256 hex digest
        # Verify produces same hash (signature excluded from hash computation)
        self.assertEqual(msg.compute_hash(), sig)
        self.assertTrue(msg.verify_signature())

    def test_verify_tampered_message(self):
        msg = Message.create("PING", {
            "from_agent": "a-1",
            "timestamp": "2026-04-11T00:00:00Z",
        })
        msg.sign()
        # Tamper with payload
        msg.payload["from_agent"] = "attacker"
        self.assertFalse(msg.verify_signature())

    def test_unsigned_message_fails_verify(self):
        msg = Message.create("PING", {
            "from_agent": "a-1",
            "timestamp": "2026-04-11T00:00:00Z",
        })
        self.assertFalse(msg.verify_signature())


# ========================================================================
# 10. Message TTL and Expiration
# ========================================================================

class TestMessageTTL(unittest.TestCase):
    """Test message TTL checking and expiration."""

    def test_fresh_message_not_expired(self):
        msg = Message.create("PING", {
            "from_agent": "a-1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self.assertTrue(msg.check_ttl())
        self.assertFalse(msg.is_expired)

    def test_expired_message_raises(self):
        msg = Message.create("PING", {
            "from_agent": "a-1",
            "timestamp": "2026-04-11T00:00:00Z",
        })
        # Force old header timestamp to trigger expiration
        msg.header.timestamp = "2020-01-01T00:00:00Z"
        with self.assertRaises(MessageExpiredError):
            msg.check_ttl()

    def test_is_expired_property(self):
        msg = Message.create("PING", {
            "from_agent": "a-1",
            "timestamp": "2026-04-11T00:00:00Z",
        })
        # Force old header timestamp to trigger expiration
        msg.header.timestamp = "2020-01-01T00:00:00Z"
        self.assertTrue(msg.is_expired)


# ========================================================================
# 11. Helper Functions
# ========================================================================

class TestHelperFunctions(unittest.TestCase):
    """Test create_pong and create_error_reply helpers."""

    def test_create_pong(self):
        ping = Message.create("PING", {
            "from_agent": "a-1",
            "timestamp": "2026-04-11T00:00:00Z",
            "nonce": "nonce-abc",
        }, source_agent="a-1", target_agent="a-2")

        pong = create_pong(ping)
        self.assertEqual(pong.type_name, "PING")
        self.assertEqual(pong.header.target_agent, "a-1")
        self.assertEqual(pong.header.reply_to, ping.header.message_id)
        self.assertEqual(pong.payload["nonce"], "nonce-abc")

    def test_create_error_reply(self):
        msg = Message.create("OPCODE_REQUEST", {
            "request_id": "req-1",
            "from_agent": "a-1",
            "target_agent": "a-2",
            "opcode": "INVALID",
        }, source_agent="a-1", target_agent="a-2")

        error = create_error_reply(msg, "UNKNOWN_OPCODE", "high",
                                    "Opcode not recognized")
        self.assertEqual(error.type_name, "ERROR_REPORT")
        self.assertEqual(error.header.reply_to, msg.header.message_id)
        self.assertEqual(error.payload["error_code"], "UNKNOWN_OPCODE")

    def test_create_error_reply_with_task_id(self):
        msg = Message.create("TASK_CLAIM", {
            "task_id": "T-999",
            "agent_id": "a-1",
            "task_type": "implementation",
        }, source_agent="a-1", target_agent="a-2")

        error = create_error_reply(msg, "TASK_FAILED", "critical",
                                    "Build failed", recoverable=False)
        self.assertEqual(error.payload["related_task_id"], "T-999")
        self.assertEqual(error.payload["recoverable"], False)


# ========================================================================
# 12. Message Bus - Handler Registration
# ========================================================================

class TestMessageBusRegistration(unittest.TestCase):
    """Test handler registration and management."""

    def setUp(self):
        self.bus = MessageBus(bus_id="test-bus")

    def test_register_handler(self):
        handler = lambda m: None
        self.bus.register_handler("PING", handler, agent_id="a-1")
        self.assertEqual(self.bus.get_handler_count("PING"), 1)

    def test_register_multiple_handlers(self):
        self.bus.register_handler("PING", lambda m: None, agent_id="a-1")
        self.bus.register_handler("PING", lambda m: None, agent_id="a-2")
        self.assertEqual(self.bus.get_handler_count("PING"), 2)

    def test_duplicate_handler_raises(self):
        handler = lambda m: None
        self.bus.register_handler("PING", handler, agent_id="a-1")
        with self.assertRaises(DuplicateHandlerError):
            self.bus.register_handler("PING", handler, agent_id="a-1")

    def test_unregister_handler(self):
        self.bus.register_handler("PING", lambda m: None, agent_id="a-1")
        self.bus.register_handler("PING", lambda m: None, agent_id="a-2")
        self.bus.unregister_handler("PING", agent_id="a-1")
        self.assertEqual(self.bus.get_handler_count("PING"), 1)

    def test_register_unknown_type_raises(self):
        with self.assertRaises(InvalidMessageTypeError):
            self.bus.register_handler("BOGUS", lambda m: None)

    def test_get_registered_types(self):
        self.bus.register_handler("PING", lambda m: None, agent_id="a-1")
        self.bus.register_handler("HEARTBEAT", lambda m: None, agent_id="a-2")
        types = self.bus.get_registered_types()
        self.assertIn("PING", types)
        self.assertIn("HEARTBEAT", types)


# ========================================================================
# 13. Message Bus - Synchronous Dispatch
# ========================================================================

class TestMessageBusSyncDispatch(unittest.TestCase):
    """Test synchronous message dispatch."""

    def setUp(self):
        self.bus = MessageBus(bus_id="sync-test")
        self.received = []

    def _make_handler(self, reply_type=None):
        def handler(msg):
            self.received.append(msg)
            if reply_type:
                return Message.create(reply_type, {
                    "from_agent": "responder",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }, source_agent="responder")
            return None
        return handler

    def test_send_to_handler(self):
        self.bus.register_handler("PING", self._make_handler(), agent_id="a-1")
        ping = Message.create("PING", {
            "from_agent": "sender",
            "timestamp": "2026-04-11T00:00:00Z",
        })
        self.bus.send(ping)
        self.assertEqual(len(self.received), 1)
        self.assertEqual(self.received[0].type_name, "PING")

    def test_send_no_handler_raises(self):
        ping = Message.create("PING", {
            "from_agent": "sender",
            "timestamp": "2026-04-11T00:00:00Z",
        })
        with self.assertRaises(NoHandlerError):
            self.bus.send(ping)

    def test_send_and_wait_returns_reply(self):
        self.bus.register_handler("PING", self._make_handler("PING"), agent_id="a-1")
        ping = Message.create("PING", {
            "from_agent": "sender",
            "timestamp": "2026-04-11T00:00:00Z",
        })
        reply = self.bus.send_and_wait(ping)
        self.assertEqual(reply.type_name, "PING")
        self.assertEqual(reply.header.source_agent, "responder")

    def test_send_with_filter(self):
        called = []
        def handler(msg):
            called.append(msg)

        self.bus.register_handler("HEARTBEAT", handler, agent_id="a-1",
                                   filter_fn=lambda m: m.payload.get("status") == "active")

        active = Message.create("HEARTBEAT", {
            "agent_id": "a-1", "status": "active",
            "timestamp": "2026-04-11T00:00:00Z",
        })
        sleeping = Message.create("HEARTBEAT", {
            "agent_id": "a-2", "status": "sleeping",
            "timestamp": "2026-04-11T00:00:00Z",
        })

        self.bus.send(active)
        self.bus.send(sleeping)
        self.assertEqual(len(called), 1)

    def test_metrics_updated(self):
        self.bus.register_handler("PING", self._make_handler(), agent_id="a-1")
        ping = Message.create("PING", {
            "from_agent": "sender",
            "timestamp": "2026-04-11T00:00:00Z",
        })
        self.bus.send(ping)
        self.assertGreater(self.bus.metrics.messages_sent, 0)
        self.assertGreater(self.bus.metrics.messages_received, 0)

    def test_no_reply_send_and_wait_raises(self):
        self.bus.register_handler("PING", self._make_handler(), agent_id="a-1")
        ping = Message.create("PING", {
            "from_agent": "sender",
            "timestamp": "2026-04-11T00:00:00Z",
        })
        with self.assertRaises(MessageBusError):
            self.bus.send_and_wait(ping)


# ========================================================================
# 14. Message Bus - Async Dispatch
# ========================================================================

class TestMessageBusAsyncDispatch(unittest.IsolatedAsyncioTestCase):
    """Test asynchronous message dispatch."""

    async def test_async_send(self):
        bus = MessageBus(bus_id="async-test")
        received = []

        async def handler(msg):
            received.append(msg)
            return None

        bus.register_handler("PING", handler, agent_id="a-1")

        ping = Message.create("PING", {
            "from_agent": "sender",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        await bus.send_async(ping)
        self.assertEqual(len(received), 1)

    async def test_async_send_and_wait(self):
        bus = MessageBus(bus_id="async-wait-test")

        async def handler(msg):
            return Message.create("PING", {
                "from_agent": "responder",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }, source_agent="responder")

        bus.register_handler("PING", handler, agent_id="a-1")

        ping = Message.create("PING", {
            "from_agent": "sender",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        reply = await bus.send_and_wait_async(ping, timeout=5.0)
        self.assertEqual(reply.header.source_agent, "responder")

    async def test_async_send_no_handler_raises(self):
        bus = MessageBus(bus_id="async-nohandler")
        ping = Message.create("PING", {
            "from_agent": "sender",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        with self.assertRaises(NoHandlerError):
            await bus.send_async(ping)


# ========================================================================
# 15. Message Bus - Pub/Sub
# ========================================================================

class TestMessageBusPubSub(unittest.TestCase):
    """Test publish/subscribe patterns."""

    def setUp(self):
        self.bus = MessageBus(bus_id="pubsub-test")

    def test_subscribe_and_publish(self):
        self.bus.subscribe("a-1", "SIGNAL_BROADCAST")
        self.bus.subscribe("a-2", "SIGNAL_BROADCAST")

        msg = Message.create("SIGNAL_BROADCAST", {
            "agent_id": "broadcaster",
            "agent_name": "Broadcaster",
            "role": "lighthouse",
            "capabilities": ["review", "test"],
        })

        count = self.bus.publish(msg)
        self.assertEqual(count, 2)

    def test_get_subscribers(self):
        self.bus.subscribe("a-1", "PING")
        self.bus.subscribe("a-2", "PING")
        subs = self.bus.get_subscribers("PING")
        self.assertEqual(subs, {"a-1", "a-2"})

    def test_unsubscribe(self):
        self.bus.subscribe("a-1", "PING")
        self.bus.unsubscribe("a-1", "PING")
        subs = self.bus.get_subscribers("PING")
        self.assertEqual(len(subs), 0)


# ========================================================================
# 16. Message Bus - History
# ========================================================================

class TestMessageBusHistory(unittest.TestCase):
    """Test message history tracking."""

    def setUp(self):
        self.bus = MessageBus(bus_id="history-test")
        self.bus.register_handler("PING", lambda m: None, agent_id="a-1")

    def test_history_records_messages(self):
        for i in range(5):
            msg = Message.create("PING", {
                "from_agent": f"sender-{i}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            self.bus.send(msg)

        history = self.bus.get_history()
        self.assertEqual(len(history), 5)

    def test_history_filtered_by_type(self):
        self.bus.register_handler("HEARTBEAT", lambda m: None, agent_id="a-1")

        ping = Message.create("PING", {
            "from_agent": "a-1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        hb = Message.create("HEARTBEAT", {
            "agent_id": "a-1", "status": "active",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        self.bus.send(ping)
        self.bus.send(hb)

        ping_history = self.bus.get_history(type_name="PING")
        self.assertEqual(len(ping_history), 1)
        self.assertEqual(ping_history[0].type_name, "PING")

    def test_history_limit(self):
        for i in range(20):
            msg = Message.create("PING", {
                "from_agent": f"a-{i}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            self.bus.send(msg)

        limited = self.bus.get_history(limit=5)
        self.assertEqual(len(limited), 5)


# ========================================================================
# 17. Message Bus - Priority Ordering
# ========================================================================

class TestMessageBusPriority(unittest.TestCase):
    """Test handler priority ordering."""

    def test_higher_priority_handler_called_first(self):
        bus = MessageBus(bus_id="priority-test")
        call_order = []

        def low_handler(msg):
            call_order.append("low")

        def high_handler(msg):
            call_order.append("high")

        bus.register_handler("PING", low_handler, agent_id="a-1", priority=0)
        bus.register_handler("PING", high_handler, agent_id="a-2", priority=100)

        ping = Message.create("PING", {
            "from_agent": "sender",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        bus.send(ping)

        self.assertEqual(call_order, ["high", "low"])


# ========================================================================
# 18. Message Bus - Delivery Guarantees and Metrics
# ========================================================================

class TestMessageBusGuarantees(unittest.TestCase):
    """Test delivery guarantee settings and metrics."""

    def test_default_guarantee(self):
        bus = MessageBus()
        self.assertEqual(bus.guarantee, DeliveryGuarantee.AT_MOST_ONCE)

    def test_custom_guarantee(self):
        bus = MessageBus(guarantee=DeliveryGuarantee.EXACTLY_ONCE)
        self.assertEqual(bus.guarantee, DeliveryGuarantee.EXACTLY_ONCE)

    def test_metrics_reset(self):
        bus = MessageBus(bus_id="metrics-test")
        bus.register_handler("PING", lambda m: None, agent_id="a-1")
        msg = Message.create("PING", {
            "from_agent": "a-1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        bus.send(msg)
        self.assertGreater(bus.metrics.messages_sent, 0)
        bus.reset_metrics()
        self.assertEqual(bus.metrics.messages_sent, 0)

    def test_dropped_message_counted(self):
        bus = MessageBus(bus_id="drop-test")
        msg = Message.create("PING", {
            "from_agent": "a-1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        try:
            bus.send(msg)
        except NoHandlerError:
            pass
        self.assertEqual(bus.metrics.messages_dropped, 1)


# ========================================================================
# 19. Bus Repr
# ========================================================================

class TestBusRepr(unittest.TestCase):
    def test_repr(self):
        bus = MessageBus(bus_id="repr-test")
        bus.register_handler("PING", lambda m: None, agent_id="a-1")
        r = repr(bus)
        self.assertIn("repr-test", r)
        self.assertIn("handlers=1", r)


# ========================================================================
# 20. Version Mismatch
# ========================================================================

class TestVersionMismatch(unittest.TestCase):
    def test_version_mismatch_raises(self):
        msg = Message.create("PING", {
            "from_agent": "a-1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        msg.header.protocol_version = "1.0.0"
        with self.assertRaises(VersionMismatchError):
            msg.validate()

    def test_correct_version_validates(self):
        msg = Message.create("PING", {
            "from_agent": "a-1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        errors = msg.validate()
        self.assertEqual(len(errors), 0)


# ========================================================================
# 21. End-to-End Protocol Flow
# ========================================================================

class TestEndToEndProtocolFlow(unittest.TestCase):
    """Test realistic multi-step protocol flows."""

    def test_handshake_flow(self):
        """Simulate a complete handshake: SIGNAL_BROADCAST -> DISCOVERY."""
        bus = MessageBus(bus_id="e2e-handshake")

        discovered_agents = []

        def discovery_handler(msg):
            if msg.header.message_type == "FLEET_DISCOVERY":
                return Message.create("SIGNAL_BROADCAST", {
                    "agent_id": "oracle1",
                    "agent_name": "Oracle1",
                    "role": "lighthouse",
                    "capabilities": ["vocab", "disputes"],
                }, source_agent="oracle1")
            return None

        bus.register_handler("FLEET_DISCOVERY", discovery_handler, agent_id="oracle1")

        discovery = Message.create("FLEET_DISCOVERY", {
            "agent_id": "new-agent",
            "query_type": "seek",
        }, source_agent="new-agent")

        replies = bus.send(discovery)
        self.assertEqual(len(replies), 1)
        self.assertEqual(replies[0].type_name, "SIGNAL_BROADCAST")
        self.assertEqual(replies[0].payload["role"], "lighthouse")

    def test_coordination_flow(self):
        """Simulate propose -> accept flow."""
        bus = MessageBus(bus_id="e2e-coord")

        def coordinate_handler(msg):
            if msg.header.message_type == "COORDINATE_PROPOSE":
                return Message.create("COORDINATE_ACCEPT", {
                    "from_agent": "a-2",
                    "proposal_id": msg.payload.get("task_id", ""),
                }, source_agent="a-2")
            return None

        bus.register_handler("COORDINATE_PROPOSE", coordinate_handler, agent_id="a-2")

        proposal = Message.create("COORDINATE_PROPOSE", {
            "from_agent": "a-1",
            "to_agent": "a-2",
            "coordination_type": "joint_review",
            "proposal": "Review the v2 protocol PR",
            "task_id": "task-review-1",
        }, source_agent="a-1")

        reply = bus.send_and_wait(proposal)
        self.assertEqual(reply.type_name, "COORDINATE_ACCEPT")

    def test_ping_pong_flow(self):
        """Simulate PING/PONG flow."""
        bus = MessageBus(bus_id="e2e-pingpong")

        def ping_handler(msg):
            return create_pong(msg)

        bus.register_handler("PING", ping_handler, agent_id="responder")

        ping = Message.create("PING", {
            "from_agent": "sender",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "nonce": "test-nonce",
        }, source_agent="sender", target_agent="responder")

        pong = bus.send_and_wait(ping)
        self.assertEqual(pong.payload["nonce"], "test-nonce")
        self.assertEqual(pong.header.target_agent, "sender")

    def test_error_handling_flow(self):
        """Simulate request -> error flow."""
        bus = MessageBus(bus_id="e2e-error")

        def opcode_handler(msg):
            return create_error_reply(
                msg,
                error_code="UNKNOWN_OPCODE",
                severity="medium",
                description=f"Opcode {msg.payload.get('opcode')} not supported",
            )

        bus.register_handler("OPCODE_REQUEST", opcode_handler, agent_id="target")

        request = Message.create("OPCODE_REQUEST", {
            "request_id": "req-1",
            "from_agent": "source",
            "target_agent": "target",
            "opcode": "NONEXISTENT",
        }, source_agent="source", target_agent="target")

        error = bus.send_and_wait(request)
        self.assertEqual(error.type_name, "ERROR_REPORT")
        self.assertIn("NONEXISTENT", error.payload["description"])

    def test_full_task_lifecycle(self):
        """Simulate full task lifecycle: claim -> complete -> trust update."""
        bus = MessageBus(bus_id="e2e-task")

        def task_handler(msg):
            if msg.header.message_type == "TASK_CLAIM":
                return Message.create("TASK_COMPLETE", {
                    "task_id": msg.payload["task_id"],
                    "agent_id": "worker-1",
                    "result": "success",
                    "summary": "Task completed successfully",
                }, source_agent="worker-1")
            return None

        bus.register_handler("TASK_CLAIM", task_handler, agent_id="worker-1")

        claim = Message.create("TASK_CLAIM", {
            "task_id": "T-016",
            "agent_id": "worker-1",
            "task_type": "implementation",
            "priority": "high",
            "summary": "Implement I2I v2",
        }, source_agent="worker-1")

        complete = bus.send_and_wait(claim)
        self.assertEqual(complete.type_name, "TASK_COMPLETE")
        self.assertEqual(complete.payload["result"], "success")

        # Trust update for good work
        trust = Message.create("TRUST_UPDATE", {
            "from_agent": "fleet",
            "to_agent": "worker-1",
            "trust_delta": 0.2,
            "reason": "Completed T-016 successfully",
            "interaction_type": "task_completion",
        }, source_agent="fleet")
        self.assertTrue(trust.is_valid())


if __name__ == "__main__":
    unittest.main(verbosity=2)
