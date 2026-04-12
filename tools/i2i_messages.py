#!/usr/bin/env python3
"""
I2I Protocol v2 — Message Type System

Implements 20 message types for fleet agent communication.
Supports serialization to I2I commit format and JSON.
Backward compatible with v1 message format [I2I:TYPE] scope — summary.
v2 uses extended format: [I2I:TYPE:CODE] scope — summary

Message Types:
  Fleet Layer:
    HEALTH_CHECK       (HCK)  — ping/pong for agent availability
    HEARTBEAT          (HBT)  — periodic agent status
    AGENT_ONBOARDING   (AOB)  — new agent joining
    AGENT_OFFBOARDING  (AOF)  — agent leaving

  Task Layer:
    TASK_CLAIM         (TCL)  — agent claims a task
    TASK_COMPLETE      (TCM)  — agent reports completion
    TASK_BLOCKED       (TBL)  — agent reports blocker
    COORDINATION_REQUEST  (CRQ)  — ask for help
    COORDINATION_RESPONSE (CRS)  — response to help request

  Code Layer:
    CODE_REVIEW_REQUEST  (RRQ)  — request code review
    CODE_REVIEW_RESPONSE (RRS)  — code review feedback
    MERGE_REQUEST       (MRQ)  — request PR merge
    CONFLICT_DETECTED   (CFD)  — notify about merge conflict
    TEST_RESULTS        (TRS)  — test suite results

  Knowledge Layer:
    KNOWLEDGE_SHARE     (KSH)  — share discovered information
    SPEC_UPDATE         (SUP)  — ISA/spec change notification

  Fence Layer:
    FENCE_POSTED        (FPT)  — new fence (work claim) posted
    FENCE_RELEASED      (FRL)  — fence released

  Bottle Layer:
    BOTTLE_DROPPED      (BTD)  — new message-in-a-bottle
    BOTTLE_COLLECTED    (BTC)  — bottle read/acknowledged
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enums & Constants
# ---------------------------------------------------------------------------

class MessageLayer(str, Enum):
    FLEET = "fleet"
    TASK = "task"
    CODE = "code"
    KNOWLEDGE = "knowledge"
    FENCE = "fence"
    BOTTLE = "bottle"


class MessageType(str, Enum):
    """All 20 I2I v2 message types with short codes."""
    HEALTH_CHECK = "HEALTH_CHECK"
    HEARTBEAT = "HEARTBEAT"
    AGENT_ONBOARDING = "AGENT_ONBOARDING"
    AGENT_OFFBOARDING = "AGENT_OFFBOARDING"
    TASK_CLAIM = "TASK_CLAIM"
    TASK_COMPLETE = "TASK_COMPLETE"
    TASK_BLOCKED = "TASK_BLOCKED"
    COORDINATION_REQUEST = "COORDINATION_REQUEST"
    COORDINATION_RESPONSE = "COORDINATION_RESPONSE"
    CODE_REVIEW_REQUEST = "CODE_REVIEW_REQUEST"
    CODE_REVIEW_RESPONSE = "CODE_REVIEW_RESPONSE"
    MERGE_REQUEST = "MERGE_REQUEST"
    CONFLICT_DETECTED = "CONFLICT_DETECTED"
    TEST_RESULTS = "TEST_RESULTS"
    KNOWLEDGE_SHARE = "KNOWLEDGE_SHARE"
    SPEC_UPDATE = "SPEC_UPDATE"
    FENCE_POSTED = "FENCE_POSTED"
    FENCE_RELEASED = "FENCE_RELEASED"
    BOTTLE_DROPPED = "BOTTLE_DROPPED"
    BOTTLE_COLLECTED = "BOTTLE_COLLECTED"


# Short 3-letter codes for each type (used in v2 commit format)
MESSAGE_CODES: Dict[MessageType, str] = {
    MessageType.HEALTH_CHECK: "HCK",
    MessageType.HEARTBEAT: "HBT",
    MessageType.AGENT_ONBOARDING: "AOB",
    MessageType.AGENT_OFFBOARDING: "AOF",
    MessageType.TASK_CLAIM: "TCL",
    MessageType.TASK_COMPLETE: "TCM",
    MessageType.TASK_BLOCKED: "TBL",
    MessageType.COORDINATION_REQUEST: "CRQ",
    MessageType.COORDINATION_RESPONSE: "CRS",
    MessageType.CODE_REVIEW_REQUEST: "RRQ",
    MessageType.CODE_REVIEW_RESPONSE: "RRS",
    MessageType.MERGE_REQUEST: "MRQ",
    MessageType.CONFLICT_DETECTED: "CFD",
    MessageType.TEST_RESULTS: "TRS",
    MessageType.KNOWLEDGE_SHARE: "KSH",
    MessageType.SPEC_UPDATE: "SUP",
    MessageType.FENCE_POSTED: "FPT",
    MessageType.FENCE_RELEASED: "FRL",
    MessageType.BOTTLE_DROPPED: "BTD",
    MessageType.BOTTLE_COLLECTED: "BTC",
}

# Reverse lookup: code -> type
_CODE_TO_TYPE: Dict[str, MessageType] = {v: k for k, v in MESSAGE_CODES.items()}

# Layer mapping
MESSAGE_LAYERS: Dict[MessageType, MessageLayer] = {
    MessageType.HEALTH_CHECK: MessageLayer.FLEET,
    MessageType.HEARTBEAT: MessageLayer.FLEET,
    MessageType.AGENT_ONBOARDING: MessageLayer.FLEET,
    MessageType.AGENT_OFFBOARDING: MessageLayer.FLEET,
    MessageType.TASK_CLAIM: MessageLayer.TASK,
    MessageType.TASK_COMPLETE: MessageLayer.TASK,
    MessageType.TASK_BLOCKED: MessageLayer.TASK,
    MessageType.COORDINATION_REQUEST: MessageLayer.TASK,
    MessageType.COORDINATION_RESPONSE: MessageLayer.TASK,
    MessageType.CODE_REVIEW_REQUEST: MessageLayer.CODE,
    MessageType.CODE_REVIEW_RESPONSE: MessageLayer.CODE,
    MessageType.MERGE_REQUEST: MessageLayer.CODE,
    MessageType.CONFLICT_DETECTED: MessageLayer.CODE,
    MessageType.TEST_RESULTS: MessageLayer.CODE,
    MessageType.KNOWLEDGE_SHARE: MessageLayer.KNOWLEDGE,
    MessageType.SPEC_UPDATE: MessageLayer.KNOWLEDGE,
    MessageType.FENCE_POSTED: MessageLayer.FENCE,
    MessageType.FENCE_RELEASED: MessageLayer.FENCE,
    MessageType.BOTTLE_DROPPED: MessageLayer.BOTTLE,
    MessageType.BOTTLE_COLLECTED: MessageLayer.BOTTLE,
}

# Regex patterns for parsing
# Separator: em dash (U+2014) or hyphen, both with surrounding spaces
V1_PATTERN = re.compile(r"^\[I2I:(\w+)\]\s*(.+?)\s[—-]\s(.+)$", re.MULTILINE)
V2_PATTERN = re.compile(r"^\[I2I:(\w+):(\w+)\]\s*(.+?)\s[—-]\s(.+)$", re.MULTILINE)


# ---------------------------------------------------------------------------
# Base Message
# ---------------------------------------------------------------------------

@dataclass
class I2IMessage:
    """Base class for all I2I v2 messages."""
    msg_type: MessageType
    scope: str
    summary: str
    body: str = ""
    sender: str = ""
    recipient: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    msg_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    version: int = 2
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def code(self) -> str:
        return MESSAGE_CODES[self.msg_type]

    @property
    def layer(self) -> MessageLayer:
        return MESSAGE_LAYERS[self.msg_type]

    def to_v1_format(self) -> str:
        """Serialize to v1 commit format: [I2I:TYPE] scope — summary"""
        lines = [f"[I2I:{self.msg_type.value}] {self.scope} — {self.summary}"]
        if self.body:
            lines.append("")
            lines.append(self.body)
        return "\n".join(lines)

    def to_v2_format(self) -> str:
        """Serialize to v2 commit format: [I2I:TYPE:CODE] scope — summary"""
        lines = [f"[I2I:{self.msg_type.value}:{self.code}] {self.scope} — {self.summary}"]
        if self.body:
            lines.append("")
            lines.append(self.body)
        return "\n".join(lines)

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = asdict(self)
        d["msg_type"] = self.msg_type.value
        d["code"] = self.code
        d["layer"] = self.layer.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> I2IMessage:
        """Deserialize from dictionary."""
        data = dict(data)
        data["msg_type"] = MessageType(data.pop("msg_type"))
        data.pop("code", None)
        data.pop("layer", None)
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> I2IMessage:
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))

    def __str__(self) -> str:
        return self.to_v2_format()


# ---------------------------------------------------------------------------
# Concrete Message Constructors (typed convenience factories)
# ---------------------------------------------------------------------------

def health_check(
    sender: str = "",
    scope: str = "fleet",
    summary: str = "ping",
    body: str = "",
    **kwargs,
) -> I2IMessage:
    """Create a HEALTH_CHECK message. Use summary 'ping' or 'pong'."""
    return I2IMessage(
        msg_type=MessageType.HEALTH_CHECK,
        sender=sender,
        scope=scope,
        summary=summary,
        body=body,
        **kwargs,
    )


def heartbeat(
    sender: str,
    scope: str = "fleet",
    summary: str = "",
    body: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> I2IMessage:
    """Create a HEARTBEAT message with agent status."""
    if not summary:
        summary = f"{sender} alive"
    return I2IMessage(
        msg_type=MessageType.HEARTBEAT,
        sender=sender,
        scope=scope,
        summary=summary,
        body=body,
        metadata=metadata or {},
        **kwargs,
    )


def agent_onboarding(
    sender: str,
    scope: str = "fleet",
    summary: str = "",
    body: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> I2IMessage:
    """Create an AGENT_ONBOARDING message for new agent joining."""
    if not summary:
        summary = f"{sender} joining fleet"
    return I2IMessage(
        msg_type=MessageType.AGENT_ONBOARDING,
        sender=sender,
        scope=scope,
        summary=summary,
        body=body,
        metadata=metadata or {},
        **kwargs,
    )


def agent_offboarding(
    sender: str,
    scope: str = "fleet",
    summary: str = "",
    body: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> I2IMessage:
    """Create an AGENT_OFFBOARDING message for agent leaving."""
    if not summary:
        summary = f"{sender} leaving fleet"
    return I2IMessage(
        msg_type=MessageType.AGENT_OFFBOARDING,
        sender=sender,
        scope=scope,
        summary=summary,
        body=body,
        metadata=metadata or {},
        **kwargs,
    )


def task_claim(
    sender: str,
    task_id: str,
    scope: str = "",
    summary: str = "",
    body: str = "",
    **kwargs,
) -> I2IMessage:
    """Create a TASK_CLAIM message."""
    if not scope:
        scope = f"task/{task_id}"
    if not summary:
        summary = f"{sender} claims {task_id}"
    return I2IMessage(
        msg_type=MessageType.TASK_CLAIM,
        sender=sender,
        scope=scope,
        summary=summary,
        body=body,
        metadata={"task_id": task_id},
        **kwargs,
    )


def task_complete(
    sender: str,
    task_id: str,
    scope: str = "",
    summary: str = "",
    body: str = "",
    **kwargs,
) -> I2IMessage:
    """Create a TASK_COMPLETE message."""
    if not scope:
        scope = f"task/{task_id}"
    if not summary:
        summary = f"{sender} completed {task_id}"
    return I2IMessage(
        msg_type=MessageType.TASK_COMPLETE,
        sender=sender,
        scope=scope,
        summary=summary,
        body=body,
        metadata={"task_id": task_id},
        **kwargs,
    )


def task_blocked(
    sender: str,
    task_id: str,
    blocker: str = "",
    scope: str = "",
    summary: str = "",
    body: str = "",
    **kwargs,
) -> I2IMessage:
    """Create a TASK_BLOCKED message."""
    if not scope:
        scope = f"task/{task_id}"
    if not summary:
        summary = f"{sender} blocked on {task_id}"
    return I2IMessage(
        msg_type=MessageType.TASK_BLOCKED,
        sender=sender,
        scope=scope,
        summary=summary,
        body=body,
        metadata={"task_id": task_id, "blocker": blocker},
        **kwargs,
    )


def coordination_request(
    sender: str,
    recipient: str = "",
    topic: str = "",
    scope: str = "coordination",
    summary: str = "",
    body: str = "",
    **kwargs,
) -> I2IMessage:
    """Create a COORDINATION_REQUEST message."""
    if not summary:
        summary = f"{sender} requests help{(': ' + topic) if topic else ''}"
    return I2IMessage(
        msg_type=MessageType.COORDINATION_REQUEST,
        sender=sender,
        recipient=recipient,
        scope=scope,
        summary=summary,
        body=body,
        **kwargs,
    )


def coordination_response(
    sender: str,
    recipient: str = "",
    accepted: bool = True,
    scope: str = "coordination",
    summary: str = "",
    body: str = "",
    **kwargs,
) -> I2IMessage:
    """Create a COORDINATION_RESPONSE message."""
    if not summary:
        status = "accepts" if accepted else "declines"
        summary = f"{sender} {status} help request"
    return I2IMessage(
        msg_type=MessageType.COORDINATION_RESPONSE,
        sender=sender,
        recipient=recipient,
        scope=scope,
        summary=summary,
        body=body,
        metadata={"accepted": accepted},
        **kwargs,
    )


def code_review_request(
    sender: str,
    target_agent: str = "",
    scope: str = "review",
    summary: str = "",
    body: str = "",
    **kwargs,
) -> I2IMessage:
    """Create a CODE_REVIEW_REQUEST message."""
    if not summary:
        summary = f"{sender} requests code review"
    return I2IMessage(
        msg_type=MessageType.CODE_REVIEW_REQUEST,
        sender=sender,
        recipient=target_agent,
        scope=scope,
        summary=summary,
        body=body,
        **kwargs,
    )


def code_review_response(
    sender: str,
    target_agent: str = "",
    scope: str = "review",
    summary: str = "",
    body: str = "",
    **kwargs,
) -> I2IMessage:
    """Create a CODE_REVIEW_RESPONSE message."""
    if not summary:
        summary = f"{sender} provides code review feedback"
    return I2IMessage(
        msg_type=MessageType.CODE_REVIEW_RESPONSE,
        sender=sender,
        recipient=target_agent,
        scope=scope,
        summary=summary,
        body=body,
        **kwargs,
    )


def merge_request(
    sender: str,
    branch: str = "",
    scope: str = "merge",
    summary: str = "",
    body: str = "",
    **kwargs,
) -> I2IMessage:
    """Create a MERGE_REQUEST message."""
    if not summary:
        summary = f"{sender} requests merge{(': ' + branch) if branch else ''}"
    return I2IMessage(
        msg_type=MessageType.MERGE_REQUEST,
        sender=sender,
        scope=scope,
        summary=summary,
        body=body,
        metadata={"branch": branch},
        **kwargs,
    )


def conflict_detected(
    sender: str,
    files: Optional[List[str]] = None,
    scope: str = "merge",
    summary: str = "",
    body: str = "",
    **kwargs,
) -> I2IMessage:
    """Create a CONFLICT_DETECTED message."""
    if not summary:
        summary = f"merge conflict detected in {len(files or [])} file(s)"
    return I2IMessage(
        msg_type=MessageType.CONFLICT_DETECTED,
        sender=sender,
        scope=scope,
        summary=summary,
        body=body,
        metadata={"conflict_files": files or []},
        **kwargs,
    )


def make_test_results(
    sender: str,
    passed: int = 0,
    failed: int = 0,
    total: int = 0,
    scope: str = "tests",
    summary: str = "",
    body: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> I2IMessage:
    """Create a TEST_RESULTS message."""
    if not summary:
        summary = f"{passed}/{total} passed, {failed} failed"
    base_meta = {"passed": passed, "failed": failed, "total": total}
    if metadata:
        base_meta.update(metadata)
    return I2IMessage(
        msg_type=MessageType.TEST_RESULTS,
        sender=sender,
        scope=scope,
        summary=summary,
        body=body,
        metadata=base_meta,
        **kwargs,
    )


def knowledge_share(
    sender: str,
    topic: str = "",
    scope: str = "knowledge",
    summary: str = "",
    body: str = "",
    **kwargs,
) -> I2IMessage:
    """Create a KNOWLEDGE_SHARE message."""
    if not summary:
        summary = f"shared knowledge: {topic}" if topic else "shared knowledge"
    return I2IMessage(
        msg_type=MessageType.KNOWLEDGE_SHARE,
        sender=sender,
        scope=scope,
        summary=summary,
        body=body,
        **kwargs,
    )


def spec_update(
    sender: str,
    spec_name: str = "",
    version: str = "",
    scope: str = "spec",
    summary: str = "",
    body: str = "",
    **kwargs,
) -> I2IMessage:
    """Create a SPEC_UPDATE message."""
    if not summary:
        summary = f"spec updated: {spec_name}" + (f" -> {version}" if version else "")
    return I2IMessage(
        msg_type=MessageType.SPEC_UPDATE,
        sender=sender,
        scope=scope,
        summary=summary,
        body=body,
        metadata={"spec_name": spec_name, "version": version},
        **kwargs,
    )


def fence_posted(
    sender: str,
    fence_id: str = "",
    resource: str = "",
    scope: str = "fence",
    summary: str = "",
    body: str = "",
    **kwargs,
) -> I2IMessage:
    """Create a FENCE_POSTED message."""
    if not summary:
        summary = f"fence posted: {resource or fence_id}"
    return I2IMessage(
        msg_type=MessageType.FENCE_POSTED,
        sender=sender,
        scope=scope,
        summary=summary,
        body=body,
        metadata={"fence_id": fence_id, "resource": resource},
        **kwargs,
    )


def fence_released(
    sender: str,
    fence_id: str = "",
    resource: str = "",
    scope: str = "fence",
    summary: str = "",
    body: str = "",
    **kwargs,
) -> I2IMessage:
    """Create a FENCE_RELEASED message."""
    if not summary:
        summary = f"fence released: {resource or fence_id}"
    return I2IMessage(
        msg_type=MessageType.FENCE_RELEASED,
        sender=sender,
        scope=scope,
        summary=summary,
        body=body,
        metadata={"fence_id": fence_id, "resource": resource},
        **kwargs,
    )


def bottle_dropped(
    sender: str,
    bottle_id: str = "",
    scope: str = "bottle",
    summary: str = "",
    body: str = "",
    **kwargs,
) -> I2IMessage:
    """Create a BOTTLE_DROPPED message."""
    if not summary:
        summary = f"bottle dropped: {bottle_id or 'message-in-a-bottle'}"
    return I2IMessage(
        msg_type=MessageType.BOTTLE_DROPPED,
        sender=sender,
        scope=scope,
        summary=summary,
        body=body,
        metadata={"bottle_id": bottle_id},
        **kwargs,
    )


def bottle_collected(
    sender: str,
    bottle_id: str = "",
    scope: str = "bottle",
    summary: str = "",
    body: str = "",
    **kwargs,
) -> I2IMessage:
    """Create a BOTTLE_COLLECTED message."""
    if not summary:
        summary = f"bottle collected: {bottle_id or 'message-in-a-bottle'}"
    return I2IMessage(
        msg_type=MessageType.BOTTLE_COLLECTED,
        sender=sender,
        scope=scope,
        summary=summary,
        body=body,
        metadata={"bottle_id": bottle_id},
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Message Registry — allows generic create + parse
# ---------------------------------------------------------------------------

# Map each MessageType to its convenience constructor
_FACTORY = {
    MessageType.HEALTH_CHECK: health_check,
    MessageType.HEARTBEAT: heartbeat,
    MessageType.AGENT_ONBOARDING: agent_onboarding,
    MessageType.AGENT_OFFBOARDING: agent_offboarding,
    MessageType.TASK_CLAIM: task_claim,
    MessageType.TASK_COMPLETE: task_complete,
    MessageType.TASK_BLOCKED: task_blocked,
    MessageType.COORDINATION_REQUEST: coordination_request,
    MessageType.COORDINATION_RESPONSE: coordination_response,
    MessageType.CODE_REVIEW_REQUEST: code_review_request,
    MessageType.CODE_REVIEW_RESPONSE: code_review_response,
    MessageType.MERGE_REQUEST: merge_request,
    MessageType.CONFLICT_DETECTED: conflict_detected,
    MessageType.TEST_RESULTS: make_test_results,
    MessageType.KNOWLEDGE_SHARE: knowledge_share,
    MessageType.SPEC_UPDATE: spec_update,
    MessageType.FENCE_POSTED: fence_posted,
    MessageType.FENCE_RELEASED: fence_released,
    MessageType.BOTTLE_DROPPED: bottle_dropped,
    MessageType.BOTTLE_COLLECTED: bottle_collected,
}


def create_message(
    msg_type: str | MessageType,
    sender: str = "",
    scope: str = "",
    summary: str = "",
    body: str = "",
    **kwargs,
) -> I2IMessage:
    """Create a message of the given type using the appropriate factory."""
    if isinstance(msg_type, str):
        msg_type = MessageType(msg_type)
    factory = _FACTORY.get(msg_type)
    if factory is None:
        raise ValueError(f"Unknown message type: {msg_type}")
    return factory(sender=sender, scope=scope, summary=summary, body=body, **kwargs)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_commit_message(commit_msg: str) -> I2IMessage:
    """Parse an I2I commit message (v1 or v2 format) into an I2IMessage.

    Supports:
      v1: [I2I:TYPE] scope — summary
      v2: [I2I:TYPE:CODE] scope — summary
    """
    # Try v2 first (more specific pattern)
    m = V2_PATTERN.match(commit_msg.strip())
    if m:
        type_name, _code, scope, summary = m.groups()
        try:
            msg_type = MessageType(type_name)
        except ValueError:
            # Unknown v2 type — treat as generic message
            msg_type = _find_v1_type(type_name)
        # Body is everything after the first blank line
        body = _extract_body(commit_msg)
        return I2IMessage(
            msg_type=msg_type,
            scope=scope,
            summary=summary,
            body=body,
        )

    # Try v1
    m = V1_PATTERN.match(commit_msg.strip())
    if m:
        type_name, scope, summary = m.groups()
        try:
            msg_type = MessageType(type_name)
        except ValueError:
            msg_type = _find_v1_type(type_name)
        body = _extract_body(commit_msg)
        return I2IMessage(
            msg_type=msg_type,
            scope=scope,
            summary=summary,
            body=body,
        )

    raise ValueError(f"Cannot parse I2I commit message: {commit_msg!r}")


def _extract_body(commit_msg: str) -> str:
    """Extract body text after the first blank line in a commit message."""
    parts = commit_msg.strip().split("\n\n", 1)
    if len(parts) > 1:
        return parts[1].strip()
    return ""


# v1 type names that map to v2 types
_V1_TYPE_MAP = {
    "PROPOSAL": MessageType.KNOWLEDGE_SHARE,
    "REVIEW": MessageType.CODE_REVIEW_RESPONSE,
    "COMMENT": MessageType.KNOWLEDGE_SHARE,
    "VOCAB": MessageType.KNOWLEDGE_SHARE,
    "DISPUTE": MessageType.COORDINATION_REQUEST,
    "RESOLVE": MessageType.COORDINATION_RESPONSE,
    "WIKI": MessageType.KNOWLEDGE_SHARE,
    "DOJO": MessageType.KNOWLEDGE_SHARE,
    "GROWTH": MessageType.KNOWLEDGE_SHARE,
    "SIGNAL": MessageType.HEARTBEAT,
    "TOMBSTONE": MessageType.SPEC_UPDATE,
    "ACCEPT": MessageType.COORDINATION_RESPONSE,
    "REJECT": MessageType.COORDINATION_RESPONSE,
}


def _find_v1_type(type_name: str) -> MessageType:
    """Map a v1 type name to the closest v2 MessageType."""
    return _V1_TYPE_MAP.get(type_name, MessageType.KNOWLEDGE_SHARE)


def is_valid_i2i_message(commit_msg: str) -> bool:
    """Check if a commit message is a valid I2I message."""
    try:
        parse_commit_message(commit_msg)
        return True
    except ValueError:
        return False


def get_all_types() -> List[MessageType]:
    """Return all 20 v2 message types."""
    return list(MessageType)


def get_types_by_layer(layer: MessageLayer) -> List[MessageType]:
    """Return message types for a given layer."""
    return [mt for mt, l in MESSAGE_LAYERS.items() if l == layer]
