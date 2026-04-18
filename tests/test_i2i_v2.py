"""Comprehensive tests for I2I v2 protocol — all 20 message types.

Tests cover:
  - Factory constructors for each message type
  - v1 and v2 serialization formats
  - JSON serialization / deserialization
  - Commit message parsing (v1 and v2)
  - Backward compatibility with v1 message types
  - Message registry and type queries
  - Validation utilities
"""

import json
import re
import pytest

from i2i_messages import (
    # Enums
    MessageType,
    MessageLayer,
    MESSAGE_CODES,
    _CODE_TO_TYPE,
    MESSAGE_LAYERS,
    # Base
    I2IMessage,
    # Factory constructors
    health_check,
    heartbeat,
    agent_onboarding,
    agent_offboarding,
    task_claim,
    task_complete,
    task_blocked,
    coordination_request,
    coordination_response,
    code_review_request,
    code_review_response,
    merge_request,
    conflict_detected,
    make_test_results,
    knowledge_share,
    spec_update,
    fence_posted,
    fence_released,
    bottle_dropped,
    bottle_collected,
    # Registry
    create_message,
    # Parsing
    parse_commit_message,
    is_valid_i2i_message,
    _extract_body,
    _V1_TYPE_MAP,
    # Queries
    get_all_types,
    get_types_by_layer,
)


# ==========================================================================
# 1. Registry & Enum tests
# ==========================================================================

class TestMessageRegistry:
    def test_20_types(self):
        assert len(MessageType) == 20

    def test_all_have_codes(self):
        for mt in MessageType:
            assert mt in MESSAGE_CODES, f"{mt} missing code"

    def test_all_codes_unique(self):
        codes = list(MESSAGE_CODES.values())
        assert len(codes) == len(set(codes))

    def test_all_have_layers(self):
        for mt in MessageType:
            assert mt in MESSAGE_LAYERS, f"{mt} missing layer"

    def test_code_reverse_lookup(self):
        for mt, code in MESSAGE_CODES.items():
            assert _CODE_TO_TYPE[code] == mt

    def test_get_all_types(self):
        all_types = get_all_types()
        assert len(all_types) == 20

    def test_get_types_by_layer_fleet(self):
        fleet = get_types_by_layer(MessageLayer.FLEET)
        assert MessageType.HEALTH_CHECK in fleet
        assert MessageType.HEARTBEAT in fleet
        assert MessageType.AGENT_ONBOARDING in fleet
        assert MessageType.AGENT_OFFBOARDING in fleet
        assert len(fleet) == 4

    def test_get_types_by_layer_task(self):
        task = get_types_by_layer(MessageLayer.TASK)
        assert len(task) == 5

    def test_get_types_by_layer_code(self):
        code = get_types_by_layer(MessageLayer.CODE)
        assert len(code) == 5

    def test_get_types_by_layer_knowledge(self):
        knowledge = get_types_by_layer(MessageLayer.KNOWLEDGE)
        assert len(knowledge) == 2

    def test_get_types_by_layer_fence(self):
        fence = get_types_by_layer(MessageLayer.FENCE)
        assert len(fence) == 2

    def test_get_types_by_layer_bottle(self):
        bottle = get_types_by_layer(MessageLayer.BOTTLE)
        assert len(bottle) == 2

    def test_layers_total(self):
        total = sum(
            len(get_types_by_layer(l)) for l in MessageLayer
        )
        assert total == 20


# ==========================================================================
# 2. Base I2IMessage tests
# ==========================================================================

class TestBaseMessage:
    def test_default_fields(self):
        msg = I2IMessage(msg_type=MessageType.HEALTH_CHECK, scope="fleet", summary="ping")
        assert msg.msg_type == MessageType.HEALTH_CHECK
        assert msg.scope == "fleet"
        assert msg.summary == "ping"
        assert msg.body == ""
        assert msg.sender == ""
        assert msg.recipient == ""
        assert msg.version == 2
        assert msg.code == "HCK"
        assert msg.layer == MessageLayer.FLEET
        assert len(msg.msg_id) == 12

    def test_v2_format(self):
        msg = I2IMessage(msg_type=MessageType.HEALTH_CHECK, scope="fleet", summary="ping")
        s = msg.to_v2_format()
        assert s == "[I2I:HEALTH_CHECK:HCK] fleet — ping"

    def test_v2_format_with_body(self):
        msg = I2IMessage(
            msg_type=MessageType.HEALTH_CHECK, scope="fleet", summary="pong",
            body="All systems operational"
        )
        s = msg.to_v2_format()
        assert "[I2I:HEALTH_CHECK:HCK]" in s
        assert "fleet — pong" in s
        assert "All systems operational" in s

    def test_v1_format(self):
        msg = I2IMessage(msg_type=MessageType.HEALTH_CHECK, scope="fleet", summary="ping")
        s = msg.to_v1_format()
        assert s == "[I2I:HEALTH_CHECK] fleet — ping"
        assert ":HCK" not in s  # no code in v1

    def test_json_roundtrip(self):
        msg = I2IMessage(
            msg_type=MessageType.HEARTBEAT,
            scope="fleet",
            summary="alive",
            sender="agent-a",
            metadata={"capacity": 80},
        )
        json_str = msg.to_json()
        restored = I2IMessage.from_json(json_str)
        assert restored.msg_type == MessageType.HEARTBEAT
        assert restored.sender == "agent-a"
        assert restored.summary == "alive"
        assert restored.metadata["capacity"] == 80

    def test_dict_conversion(self):
        msg = I2IMessage(msg_type=MessageType.TASK_CLAIM, scope="task/42", summary="claimed")
        d = msg.to_dict()
        assert d["msg_type"] == "TASK_CLAIM"
        assert d["code"] == "TCL"
        assert d["layer"] == "task"
        assert "msg_id" in d

    def test_str(self):
        msg = I2IMessage(msg_type=MessageType.HEARTBEAT, scope="fleet", summary="ok")
        assert str(msg).startswith("[I2I:")


# ==========================================================================
# 3. Per-type factory constructor tests
# ==========================================================================

class TestHealthCheck:
    def test_ping(self):
        msg = health_check(sender="agent-a")
        assert msg.msg_type == MessageType.HEALTH_CHECK
        assert msg.code == "HCK"
        assert msg.summary == "ping"

    def test_pong(self):
        msg = health_check(sender="agent-b", summary="pong")
        assert msg.summary == "pong"

    def test_custom_scope(self):
        msg = health_check(sender="a", scope="node-3")
        assert msg.scope == "node-3"


class TestHeartbeat:
    def test_default(self):
        msg = heartbeat(sender="agent-a")
        assert msg.msg_type == MessageType.HEARTBEAT
        assert msg.code == "HBT"
        assert "agent-a" in msg.summary

    def test_with_metadata(self):
        msg = heartbeat(sender="a", metadata={"cpu": 45, "memory": "2GB"})
        assert msg.metadata["cpu"] == 45

    def test_with_body(self):
        msg = heartbeat(sender="a", body="Working on T-016")
        assert msg.body == "Working on T-016"


class TestAgentOnboarding:
    def test_default(self):
        msg = agent_onboarding(sender="new-agent")
        assert msg.msg_type == MessageType.AGENT_ONBOARDING
        assert msg.code == "AOB"
        assert "new-agent" in msg.summary
        assert msg.layer == MessageLayer.FLEET

    def test_with_capabilities(self):
        msg = agent_onboarding(
            sender="scout-1",
            body="FLUX runtime, 150 vocabularies",
            metadata={"role": "scout", "realm": "SuperInstance"},
        )
        assert msg.metadata["role"] == "scout"


class TestAgentOffboarding:
    def test_default(self):
        msg = agent_offboarding(sender="old-agent")
        assert msg.msg_type == MessageType.AGENT_OFFBOARDING
        assert msg.code == "AOF"
        assert "old-agent" in msg.summary

    def test_with_reason(self):
        msg = agent_offboarding(sender="x", body="Decommissioned")
        assert msg.body == "Decommissioned"


class TestTaskClaim:
    def test_default(self):
        msg = task_claim(sender="worker", task_id="T-016")
        assert msg.msg_type == MessageType.TASK_CLAIM
        assert msg.code == "TCL"
        assert msg.scope == "task/T-016"
        assert msg.metadata["task_id"] == "T-016"

    def test_custom(self):
        msg = task_claim(sender="w", task_id="X", scope="custom", summary="custom summary")
        assert msg.scope == "custom"
        assert msg.summary == "custom summary"


class TestTaskComplete:
    def test_default(self):
        msg = task_complete(sender="worker", task_id="T-016")
        assert msg.msg_type == MessageType.TASK_COMPLETE
        assert msg.code == "TCM"
        assert "completed" in msg.summary
        assert msg.metadata["task_id"] == "T-016"

    def test_with_results(self):
        msg = task_complete(sender="w", task_id="T-001", body="All 20 types implemented")
        assert "20 types" in msg.body


class TestTaskBlocked:
    def test_default(self):
        msg = task_blocked(sender="w", task_id="T-010")
        assert msg.msg_type == MessageType.TASK_BLOCKED
        assert msg.code == "TBL"
        assert "blocked" in msg.summary
        assert msg.metadata["task_id"] == "T-010"

    def test_with_blocker(self):
        msg = task_blocked(sender="w", task_id="T-010", blocker="Missing API token")
        assert msg.metadata["blocker"] == "Missing API token"


class TestCoordinationRequest:
    def test_default(self):
        msg = coordination_request(sender="a")
        assert msg.msg_type == MessageType.COORDINATION_REQUEST
        assert msg.code == "CRQ"
        assert "requests help" in msg.summary

    def test_with_topic(self):
        msg = coordination_request(sender="a", topic="merge conflict")
        assert "merge conflict" in msg.summary

    def test_with_recipient(self):
        msg = coordination_request(sender="a", recipient="agent-b", topic="help")
        assert msg.recipient == "agent-b"


class TestCoordinationResponse:
    def test_accept(self):
        msg = coordination_response(sender="b", accepted=True)
        assert msg.msg_type == MessageType.COORDINATION_RESPONSE
        assert msg.code == "CRS"
        assert "accepts" in msg.summary
        assert msg.metadata["accepted"] is True

    def test_decline(self):
        msg = coordination_response(sender="b", accepted=False)
        assert "declines" in msg.summary
        assert msg.metadata["accepted"] is False


class TestCodeReviewRequest:
    def test_default(self):
        msg = code_review_request(sender="reviewer")
        assert msg.msg_type == MessageType.CODE_REVIEW_REQUEST
        assert msg.code == "RRQ"
        assert "requests code review" in msg.summary

    def test_with_target(self):
        msg = code_review_request(sender="r", target_agent="author")
        assert msg.recipient == "author"


class TestCodeReviewResponse:
    def test_default(self):
        msg = code_review_response(sender="reviewer")
        assert msg.msg_type == MessageType.CODE_REVIEW_RESPONSE
        assert msg.code == "RRS"
        assert "provides code review feedback" in msg.summary

    def test_with_body(self):
        body = "**Strengths**\n- Clean code\n\n**Suggested Improvements**\n- Add tests"
        msg = code_review_response(sender="r", body=body)
        assert "Clean code" in msg.body


class TestMergeRequest:
    def test_default(self):
        msg = merge_request(sender="author")
        assert msg.msg_type == MessageType.MERGE_REQUEST
        assert msg.code == "MRQ"
        assert "requests merge" in msg.summary

    def test_with_branch(self):
        msg = merge_request(sender="a", branch="feature/i2i-v2")
        assert "feature/i2i-v2" in msg.summary
        assert msg.metadata["branch"] == "feature/i2i-v2"


class TestConflictDetected:
    def test_default(self):
        msg = conflict_detected(sender="merger", files=["src/main.py", "src/utils.py"])
        assert msg.msg_type == MessageType.CONFLICT_DETECTED
        assert msg.code == "CFD"
        assert "2 file(s)" in msg.summary
        assert len(msg.metadata["conflict_files"]) == 2

    def test_no_files(self):
        msg = conflict_detected(sender="m", files=[])
        assert "0 file(s)" in msg.summary


class TestTestResults:
    def test_all_passed(self):
        msg = make_test_results(sender="ci", passed=61, failed=0, total=61)
        assert msg.msg_type == MessageType.TEST_RESULTS
        assert msg.code == "TRS"
        assert msg.summary == "61/61 passed, 0 failed"
        assert msg.metadata["passed"] == 61

    def test_with_failures(self):
        msg = make_test_results(sender="ci", passed=49, failed=12, total=61)
        assert "49/61 passed, 12 failed" == msg.summary

    def test_custom_scope(self):
        msg = make_test_results(sender="ci", passed=10, failed=0, total=10, scope="integration")
        assert msg.scope == "integration"


class TestKnowledgeShare:
    def test_default(self):
        msg = knowledge_share(sender="sage")
        assert msg.msg_type == MessageType.KNOWLEDGE_SHARE
        assert msg.code == "KSH"
        assert "shared knowledge" in msg.summary

    def test_with_topic(self):
        msg = knowledge_share(sender="sage", topic="LRU cache patterns")
        assert "LRU cache patterns" in msg.summary


class TestSpecUpdate:
    def test_default(self):
        msg = spec_update(sender="architect")
        assert msg.msg_type == MessageType.SPEC_UPDATE
        assert msg.code == "SUP"
        assert "spec updated" in msg.summary

    def test_with_version(self):
        msg = spec_update(sender="a", spec_name="I2I", version="2.0")
        assert "I2I" in msg.summary
        assert "2.0" in msg.summary
        assert msg.metadata["spec_name"] == "I2I"
        assert msg.metadata["version"] == "2.0"


class TestFencePosted:
    def test_default(self):
        msg = fence_posted(sender="worker")
        assert msg.msg_type == MessageType.FENCE_POSTED
        assert msg.code == "FPT"
        assert "fence posted" in msg.summary

    def test_with_resource(self):
        msg = fence_posted(sender="w", resource="src/protocol.py", fence_id="f-001")
        assert "src/protocol.py" in msg.summary
        assert msg.metadata["fence_id"] == "f-001"
        assert msg.metadata["resource"] == "src/protocol.py"


class TestFenceReleased:
    def test_default(self):
        msg = fence_released(sender="worker")
        assert msg.msg_type == MessageType.FENCE_RELEASED
        assert msg.code == "FRL"
        assert "fence released" in msg.summary

    def test_with_id(self):
        msg = fence_released(sender="w", fence_id="f-001")
        assert "f-001" in msg.summary


class TestBottleDropped:
    def test_default(self):
        msg = bottle_dropped(sender="sage")
        assert msg.msg_type == MessageType.BOTTLE_DROPPED
        assert msg.code == "BTD"
        assert "bottle dropped" in msg.summary

    def test_with_id(self):
        msg = bottle_dropped(sender="sage", bottle_id="b-42")
        assert "b-42" in msg.summary
        assert msg.metadata["bottle_id"] == "b-42"


class TestBottleCollected:
    def test_default(self):
        msg = bottle_collected(sender="finder")
        assert msg.msg_type == MessageType.BOTTLE_COLLECTED
        assert msg.code == "BTC"
        assert "bottle collected" in msg.summary

    def test_with_id(self):
        msg = bottle_collected(sender="f", bottle_id="b-42")
        assert "b-42" in msg.summary


# ==========================================================================
# 4. create_message generic factory tests
# ==========================================================================

class TestCreateMessage:
    def test_by_enum(self):
        msg = create_message(MessageType.HEALTH_CHECK, sender="a")
        assert msg.msg_type == MessageType.HEALTH_CHECK

    def test_by_string(self):
        msg = create_message("HEARTBEAT", sender="a")
        assert msg.msg_type == MessageType.HEARTBEAT

    def test_all_types_creatable(self):
        for mt in MessageType:
            if mt == MessageType.TASK_CLAIM:
                msg = create_message(mt, sender="test", task_id="T-000")
            elif mt == MessageType.TASK_COMPLETE:
                msg = create_message(mt, sender="test", task_id="T-000")
            elif mt == MessageType.TASK_BLOCKED:
                msg = create_message(mt, sender="test", task_id="T-000")
            else:
                msg = create_message(mt, sender="test")
            assert msg.msg_type == mt

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError):
            create_message("NOT_A_TYPE")

    def test_kwargs_pass_through(self):
        msg = create_message(
            "HEARTBEAT", sender="w",
            body="details", metadata={"key": "val"}
        )
        assert msg.body == "details"
        assert msg.metadata["key"] == "val"


# ==========================================================================
# 5. Serialization format tests
# ==========================================================================

class TestV2Format:
    def test_all_types_produce_v2(self):
        for mt in MessageType:
            msg = I2IMessage(msg_type=mt, scope="test", summary="test")
            fmt = msg.to_v2_format()
            code = MESSAGE_CODES[mt]
            assert f"[I2I:{mt.value}:{code}] test — test" == fmt

    def test_em_dash_in_format(self):
        msg = I2IMessage(msg_type=MessageType.HEARTBEAT, scope="fleet", summary="alive")
        assert " — " in msg.to_v2_format()


class TestV1Format:
    def test_no_code(self):
        msg = I2IMessage(msg_type=MessageType.HEARTBEAT, scope="fleet", summary="ok")
        assert ":HBT" not in msg.to_v1_format()

    def test_has_brackets(self):
        for mt in MessageType:
            msg = I2IMessage(msg_type=mt, scope="s", summary="x")
            assert msg.to_v1_format().startswith("[I2I:")


class TestBodyExtraction:
    def test_no_body(self):
        assert _extract_body("[I2I:TEST] s — x") == ""

    def test_with_body(self):
        raw = "[I2I:TEST] s — x\n\nBody text here\nMore body"
        assert _extract_body(raw) == "Body text here\nMore body"

    def test_multiline_body(self):
        raw = "[I2I:TEST] s — x\n\nLine 1\nLine 2\n\nLine 4"
        body = _extract_body(raw)
        assert body.startswith("Line 1")
        assert body.endswith("Line 4")


# ==========================================================================
# 6. Parsing tests
# ==========================================================================

class TestParseV2:
    def test_basic(self):
        msg = parse_commit_message("[I2I:HEALTH_CHECK:HCK] fleet — ping")
        assert msg.msg_type == MessageType.HEALTH_CHECK
        assert msg.scope == "fleet"
        assert msg.summary == "ping"
        assert msg.body == ""

    def test_with_body(self):
        raw = "[I2I:HEARTBEAT:HBT] fleet — agent-a alive\n\nCPU: 45%\nMemory: 2GB"
        msg = parse_commit_message(raw)
        assert msg.msg_type == MessageType.HEARTBEAT
        assert "CPU: 45%" in msg.body

    def test_all_v2_types(self):
        for mt in MessageType:
            code = MESSAGE_CODES[mt]
            raw = f"[I2I:{mt.value}:{code}] scope — summary"
            msg = parse_commit_message(raw)
            assert msg.msg_type == mt

    def test_preserves_whitespace(self):
        raw = "[I2I:TASK_CLAIM:TCL] task/T-016 — worker claims T-016"
        msg = parse_commit_message(raw)
        assert msg.scope == "task/T-016"


class TestParseV1:
    def test_basic_v1(self):
        msg = parse_commit_message("[I2I:PROPOSAL] src/memory.py — implement LRU cache")
        assert msg.scope == "src/memory.py"
        assert msg.summary == "implement LRU cache"

    def test_v1_mapped_types(self):
        for v1_name, v2_type in _V1_TYPE_MAP.items():
            raw = f"[I2I:{v1_name}] topic — summary"
            msg = parse_commit_message(raw)
            assert msg.msg_type == v2_type, f"{v1_name} should map to {v2_type}"

    def test_v1_with_body(self):
        raw = "[I2I:REVIEW] agent — feedback\n\n**Strengths**\n- Good code"
        msg = parse_commit_message(raw)
        assert "Strengths" in msg.body


class TestIsValidMessage:
    def test_valid_v2(self):
        assert is_valid_i2i_message("[I2I:HEARTBEAT:HBT] fleet — alive")

    def test_valid_v1(self):
        assert is_valid_i2i_message("[I2I:PROPOSAL] src/x.py — add feature")

    def test_invalid(self):
        assert not is_valid_i2i_message("Not an I2I message")
        assert not is_valid_i2i_message("")
        assert not is_valid_i2i_message("[I2I] nope")


# ==========================================================================
# 7. Round-trip tests (serialize → parse → verify)
# ==========================================================================

class TestRoundTrip:
    def test_v2_roundtrip(self):
        original = heartbeat(sender="agent-a", metadata={"cpu": 30})
        v2_str = original.to_v2_format()
        parsed = parse_commit_message(v2_str)
        assert parsed.msg_type == original.msg_type
        assert parsed.scope == original.scope
        assert parsed.summary == original.summary

    def test_v2_with_body_roundtrip(self):
        original = task_complete(sender="w", task_id="T-001", body="All tests pass")
        v2_str = original.to_v2_format()
        parsed = parse_commit_message(v2_str)
        assert parsed.body == "All tests pass"

    def test_json_roundtrip_preserves_all(self):
        original = make_test_results(
            sender="ci", passed=100, failed=3, total=103,
            metadata={"branch": "main", "duration": "45s"},
        )
        json_str = original.to_json()
        restored = I2IMessage.from_json(json_str)
        assert restored.msg_type == original.msg_type
        assert restored.metadata["passed"] == 100
        assert restored.metadata["branch"] == "main"
        assert restored.metadata["duration"] == "45s"

    def test_all_types_v2_roundtrip(self):
        for mt in MessageType:
            original = I2IMessage(msg_type=mt, scope="test", summary="test roundtrip")
            v2_str = original.to_v2_format()
            parsed = parse_commit_message(v2_str)
            assert parsed.msg_type == mt


# ==========================================================================
# 8. Backward compatibility with v1
# ==========================================================================

class TestV1BackwardCompat:
    def test_v1_proposal_parses(self):
        raw = "[I2I:PROPOSAL] src/memory.py — implement LRU cache"
        msg = parse_commit_message(raw)
        assert msg is not None
        assert msg.scope == "src/memory.py"

    def test_v1_still_generatable(self):
        msg = I2IMessage(msg_type=MessageType.HEALTH_CHECK, scope="fleet", summary="ping")
        v1 = msg.to_v1_format()
        assert v1.startswith("[I2I:HEALTH_CHECK]")
        # Can be parsed back
        parsed = parse_commit_message(v1)
        assert parsed.msg_type == MessageType.HEALTH_CHECK

    def test_v1_types_count(self):
        v1_types = ["PROPOSAL", "REVIEW", "COMMENT", "VOCAB", "DISPUTE", "RESOLVE",
                     "WIKI", "DOJO", "GROWTH", "SIGNAL", "TOMBSTONE", "ACCEPT", "REJECT"]
        assert len(v1_types) == 13
        for v1_type in v1_types:
            assert v1_type in _V1_TYPE_MAP, f"v1 type {v1_type} not mapped"

    def test_v1_format_no_body(self):
        msg = I2IMessage(msg_type=MessageType.HEARTBEAT, scope="fleet", summary="ok")
        v1 = msg.to_v1_format()
        # Should be single line
        assert "\n" not in v1

    def test_v2_message_has_version_field(self):
        msg = I2IMessage(msg_type=MessageType.HEALTH_CHECK, scope="x", summary="y")
        assert msg.version == 2


# ==========================================================================
# 9. Integration-style tests
# ==========================================================================

class TestIntegration:
    def test_fleet_health_scenario(self):
        """Simulate a full fleet health check exchange."""
        ping = health_check(sender="monitor", scope="node-3", summary="ping")
        pong = health_check(sender="node-3", scope="monitor", summary="pong")

        assert ping.to_v2_format() == "[I2I:HEALTH_CHECK:HCK] node-3 — ping"
        assert pong.to_v2_format() == "[I2I:HEALTH_CHECK:HCK] monitor — pong"

        parsed_ping = parse_commit_message(ping.to_v2_format())
        assert parsed_ping.msg_type == MessageType.HEALTH_CHECK

    def test_task_lifecycle(self):
        """Simulate claim → complete flow."""
        claim = task_claim(sender="worker", task_id="T-016")
        complete = task_complete(sender="worker", task_id="T-016", body="All 20 types done")

        assert claim.msg_type == MessageType.TASK_CLAIM
        assert complete.msg_type == MessageType.TASK_COMPLETE
        assert "T-016" in claim.scope
        assert "20 types" in complete.body

    def test_coordination_exchange(self):
        req = coordination_request(sender="a", recipient="b", topic="merge conflict")
        resp = coordination_response(sender="b", recipient="a", accepted=True,
                                     body="I can help with that")

        assert req.recipient == "b"
        assert resp.metadata["accepted"] is True
        assert "help" in resp.body

    def test_bottle_lifecycle(self):
        drop = bottle_dropped(sender="sage", bottle_id="b-001", body="Use LRU for caches")
        collect = bottle_collected(sender="learner", bottle_id="b-001")

        assert drop.metadata["bottle_id"] == "b-001"
        assert collect.metadata["bottle_id"] == "b-001"
        assert drop.msg_type == MessageType.BOTTLE_DROPPED
        assert collect.msg_type == MessageType.BOTTLE_COLLECTED

    def test_message_ids_unique(self):
        msg1 = I2IMessage(msg_type=MessageType.HEARTBEAT, scope="x", summary="y")
        msg2 = I2IMessage(msg_type=MessageType.HEARTBEAT, scope="x", summary="y")
        assert msg1.msg_id != msg2.msg_id

    def test_all_types_have_correct_layer(self):
        """Verify each type is assigned to the correct layer."""
        fleet_types = {MessageType.HEALTH_CHECK, MessageType.HEARTBEAT,
                       MessageType.AGENT_ONBOARDING, MessageType.AGENT_OFFBOARDING}
        task_types = {MessageType.TASK_CLAIM, MessageType.TASK_COMPLETE,
                      MessageType.TASK_BLOCKED, MessageType.COORDINATION_REQUEST,
                      MessageType.COORDINATION_RESPONSE}
        code_types = {MessageType.CODE_REVIEW_REQUEST, MessageType.CODE_REVIEW_RESPONSE,
                      MessageType.MERGE_REQUEST, MessageType.CONFLICT_DETECTED,
                      MessageType.TEST_RESULTS}
        knowledge_types = {MessageType.KNOWLEDGE_SHARE, MessageType.SPEC_UPDATE}
        fence_types = {MessageType.FENCE_POSTED, MessageType.FENCE_RELEASED}
        bottle_types = {MessageType.BOTTLE_DROPPED, MessageType.BOTTLE_COLLECTED}

        for mt in fleet_types:
            assert MESSAGE_LAYERS[mt] == MessageLayer.FLEET
        for mt in task_types:
            assert MESSAGE_LAYERS[mt] == MessageLayer.TASK
        for mt in code_types:
            assert MESSAGE_LAYERS[mt] == MessageLayer.CODE
        for mt in knowledge_types:
            assert MESSAGE_LAYERS[mt] == MessageLayer.KNOWLEDGE
        for mt in fence_types:
            assert MESSAGE_LAYERS[mt] == MessageLayer.FENCE
        for mt in bottle_types:
            assert MESSAGE_LAYERS[mt] == MessageLayer.BOTTLE
