"""
I2I v2 Protocol - Message Type Definitions

Defines all 20 message types for the Iron-to-Iron v2 protocol.
Each message type has a type code, version, payload schema, and metadata.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .exceptions import InvalidMessageTypeError


# Protocol version
PROTOCOL_VERSION = "2.0.0"


class MessageCategory(str, Enum):
    """Categories of I2I messages."""
    HEARTBEAT = "heartbeat"
    TASK = "task"
    TRUST = "trust"
    SIGNAL = "signal"
    FLEET = "fleet"
    KNOWLEDGE = "knowledge"
    COORDINATION = "coordination"
    STATUS = "status"
    ERROR = "error"
    LIFECYCLE = "lifecycle"


@dataclass(frozen=True)
class FieldSchema:
    """Schema definition for a single message field."""
    name: str
    field_type: str  # "string", "integer", "float", "boolean", "array", "object", "enum"
    required: bool = True
    default: Any = None
    description: str = ""
    enum_values: Optional[List[str]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    max_length: Optional[int] = None
    item_type: Optional[str] = None  # For arrays: type of elements

    def validate_value(self, value: Any) -> List[str]:
        """Validate a value against this field schema. Returns list of errors."""
        errors: List[str] = []

        if value is None:
            if self.required:
                errors.append(f"Required field '{self.name}' is missing")
            return errors

        # Type checking
        type_map = {
            "string": str,
            "integer": int,
            "float": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        if self.field_type in type_map:
            expected = type_map[self.field_type]
            if not isinstance(value, expected):
                # Allow int for float fields
                if self.field_type == "float" and isinstance(value, int):
                    pass
                else:
                    errors.append(
                        f"Field '{self.name}' expected {self.field_type}, "
                        f"got {type(value).__name__}"
                    )
                    return errors

        # Enum checking
        if self.enum_values and value not in self.enum_values:
            errors.append(
                f"Field '{self.name}' must be one of {self.enum_values}, "
                f"got '{value}'"
            )

        # String length
        if self.field_type == "string" and self.max_length and isinstance(value, str):
            if len(value) > self.max_length:
                errors.append(
                    f"Field '{self.name}' exceeds max length {self.max_length}"
                )

        # Numeric range
        if isinstance(value, (int, float)):
            if self.min_value is not None and value < self.min_value:
                errors.append(
                    f"Field '{self.name}' below minimum {self.min_value}"
                )
            if self.max_value is not None and value > self.max_value:
                errors.append(
                    f"Field '{self.name}' exceeds maximum {self.max_value}"
                )

        # Array item type
        if self.field_type == "array" and self.item_type and isinstance(value, list):
            expected_item = type_map.get(self.item_type)
            if expected_item:
                for i, item in enumerate(value):
                    if not isinstance(item, expected_item):
                        errors.append(
                            f"Field '{self.name}[{i}]' expected {self.item_type}, "
                            f"got {type(item).__name__}"
                        )

        return errors


@dataclass
class MessageTypeDefinition:
    """Complete definition of an I2I v2 message type."""
    name: str
    code: str
    category: MessageCategory
    description: str
    fields: List[FieldSchema] = field(default_factory=list)
    version: str = PROTOCOL_VERSION
    expects_reply: bool = False
    reply_types: List[str] = field(default_factory=list)
    ttl_seconds: int = 3600  # Default TTL: 1 hour

    def validate_payload(self, payload: Dict[str, Any]) -> List[str]:
        """Validate a payload dict against this message type's schema."""
        errors: List[str] = []
        seen_fields = set()

        # Check all defined fields
        for field_schema in self.fields:
            seen_fields.add(field_schema.name)
            errors.extend(field_schema.validate_value(payload.get(field_schema.name)))

        # Check for unexpected fields (warn, don't error)
        unexpected = set(payload.keys()) - seen_fields
        if unexpected:
            for uf in sorted(unexpected):
                errors.append(f"Unexpected field '{uf}' for message type {self.name}")

        return errors


# ---------------------------------------------------------------------------
# Define all 20 message types
# ---------------------------------------------------------------------------

# 1. HEARTBEAT (HBT) - Periodic alive signal
MESSAGE_TYPE_HEARTBEAT = MessageTypeDefinition(
    name="HEARTBEAT",
    code="HBT",
    category=MessageCategory.HEARTBEAT,
    description="Periodic alive signal from an agent to the fleet.",
    fields=[
        FieldSchema("agent_id", "string", required=True, max_length=256,
                     description="Unique agent identifier"),
        FieldSchema("status", "enum", required=True,
                     enum_values=["active", "idle", "busy", "sleeping"],
                     description="Current agent status"),
        FieldSchema("timestamp", "string", required=True,
                     description="ISO 8601 timestamp"),
        FieldSchema("sequence", "integer", required=False, default=0,
                     min_value=0, description="Monotonic heartbeat counter"),
        FieldSchema("metadata", "object", required=False,
                     description="Optional agent metadata"),
    ],
    ttl_seconds=30,
)

# 2. TASK_CLAIM (TCL) - Agent claims a task from the fleet queue
MESSAGE_TYPE_TASK_CLAIM = MessageTypeDefinition(
    name="TASK_CLAIM",
    code="TCL",
    category=MessageCategory.TASK,
    description="Agent claims/assigns a task from the fleet task queue.",
    fields=[
        FieldSchema("task_id", "string", required=True, max_length=128,
                     description="Unique task identifier"),
        FieldSchema("agent_id", "string", required=True, max_length=256,
                     description="Claiming agent identifier"),
        FieldSchema("task_type", "enum", required=True,
                     enum_values=["code_review", "implementation", "testing",
                                 "documentation", "investigation", "deployment"],
                     description="Type of task being claimed"),
        FieldSchema("priority", "enum", required=False,
                     enum_values=["critical", "high", "medium", "low"],
                     default="medium",
                     description="Task priority level"),
        FieldSchema("artifact_url", "string", required=False,
                     description="Link to the relevant artifact/repo/PR"),
        FieldSchema("estimated_effort", "string", required=False,
                     enum_values=["trivial", "small", "medium", "large", "epic"],
                     description="Estimated effort to complete"),
    ],
    expects_reply=True,
    reply_types=["TASK_COMPLETE", "ERROR_REPORT"],
    ttl_seconds=86400,
)

# 3. TASK_COMPLETE (TCM) - Agent reports task completion
MESSAGE_TYPE_TASK_COMPLETE = MessageTypeDefinition(
    name="TASK_COMPLETE",
    code="TCM",
    category=MessageCategory.TASK,
    description="Agent reports that a previously claimed task is complete.",
    fields=[
        FieldSchema("task_id", "string", required=True, max_length=128,
                     description="Task identifier being completed"),
        FieldSchema("agent_id", "string", required=True, max_length=256,
                     description="Completing agent identifier"),
        FieldSchema("result", "enum", required=True,
                     enum_values=["success", "partial", "failed"],
                     description="Task result status"),
        FieldSchema("summary", "string", required=True, max_length=2048,
                     description="Brief summary of what was done"),
        FieldSchema("artifact_url", "string", required=False,
                     description="Link to the output artifact"),
        FieldSchema("findings", "array", required=False, item_type="string",
                     description="Key findings or observations"),
    ],
    expects_reply=True,
    reply_types=["ACK"],
    ttl_seconds=86400,
)

# 4. TRUST_UPDATE (TRU) - Update trust score between agents
MESSAGE_TYPE_TRUST_UPDATE = MessageTypeDefinition(
    name="TRUST_UPDATE",
    code="TRU",
    category=MessageCategory.TRUST,
    description="Update the trust score between two agents based on interaction.",
    fields=[
        FieldSchema("from_agent", "string", required=True, max_length=256,
                     description="Agent issuing the trust update"),
        FieldSchema("to_agent", "string", required=True, max_length=256,
                     description="Agent being rated"),
        FieldSchema("trust_delta", "float", required=True,
                     min_value=-1.0, max_value=1.0,
                     description="Trust change (-1.0 to +1.0)"),
        FieldSchema("reason", "string", required=True, max_length=1024,
                     description="Explanation for trust change"),
        FieldSchema("interaction_type", "enum", required=False,
                     enum_values=["code_review", "task_completion", "dispute",
                                 "proposal", "handshake", "coordination"],
                     description="Type of interaction that triggered update"),
        FieldSchema("new_trust_score", "float", required=False,
                     min_value=0.0, max_value=1.0,
                     description="Resulting trust score after update"),
    ],
    ttl_seconds=86400,
)

# 5. SIGNAL_BROADCAST (SIG) - Announce capabilities to the fleet
MESSAGE_TYPE_SIGNAL_BROADCAST = MessageTypeDefinition(
    name="SIGNAL_BROADCAST",
    code="SIG",
    category=MessageCategory.SIGNAL,
    description="Agent broadcasts its capabilities and vocabulary to the fleet.",
    fields=[
        FieldSchema("agent_id", "string", required=True, max_length=256,
                     description="Broadcasting agent identifier"),
        FieldSchema("agent_name", "string", required=True, max_length=256,
                     description="Human-readable agent name"),
        FieldSchema("role", "enum", required=True,
                     enum_values=["lighthouse", "vessel", "scout", "barnacle", "ghost"],
                     description="Agent role in the fleet"),
        FieldSchema("capabilities", "array", required=True, item_type="string",
                     description="List of capabilities"),
        FieldSchema("vocab_count", "integer", required=False, min_value=0,
                     description="Number of vocabulary entries"),
        FieldSchema("repo_url", "string", required=False,
                     description="Agent's repository URL"),
        FieldSchema("realm", "string", required=False, max_length=256,
                     description="Agent's domain/organization"),
    ],
    ttl_seconds=3600,
)

# 6. FLEET_DISCOVERY (DSC) - Discover other agents in the fleet
MESSAGE_TYPE_FLEET_DISCOVERY = MessageTypeDefinition(
    name="FLEET_DISCOVERY",
    code="DSC",
    category=MessageCategory.FLEET,
    description="Agent announces presence or queries for fleet members.",
    fields=[
        FieldSchema("agent_id", "string", required=True, max_length=256,
                     description="Discovering agent identifier"),
        FieldSchema("query_type", "enum", required=True,
                     enum_values=["announce", "seek", "ping_all"],
                     description="Type of discovery query"),
        FieldSchema("known_peers", "array", required=False, item_type="string",
                     description="List of already-known peer agent IDs"),
        FieldSchema("seeking_capabilities", "array", required=False,
                     item_type="string",
                     description="Capabilities being sought"),
    ],
    expects_reply=True,
    reply_types=["SIGNAL_BROADCAST"],
    ttl_seconds=300,
)

# 7. MERIT_AWARD (MRT) - Award merit points to an agent
MESSAGE_TYPE_MERIT_AWARD = MessageTypeDefinition(
    name="MERIT_AWARD",
    code="MRT",
    category=MessageCategory.TRUST,
    description="Award merit points to an agent for exceptional work.",
    fields=[
        FieldSchema("from_agent", "string", required=True, max_length=256,
                     description="Agent giving the award"),
        FieldSchema("to_agent", "string", required=True, max_length=256,
                     description="Agent receiving the award"),
        FieldSchema("merit_type", "enum", required=True,
                     enum_values=["code_excellence", "review_quality", "mentorship",
                                 "innovation", "reliability", "collaboration"],
                     description="Type of merit being awarded"),
        FieldSchema("points", "integer", required=True, min_value=1, max_value=100,
                     description="Merit points awarded"),
        FieldSchema("citation", "string", required=True, max_length=1024,
                     description="Reason/citation for the award"),
        FieldSchema("task_id", "string", required=False,
                     description="Related task identifier"),
    ],
    ttl_seconds=86400,
)

# 8. BOTTLE_CAST (BTL) - Message in a bottle (async discovery)
MESSAGE_TYPE_BOTTLE_CAST = MessageTypeDefinition(
    name="BOTTLE_CAST",
    code="BTL",
    category=MessageCategory.KNOWLEDGE,
    description="Cast a message-in-a-bottle for async fleet discovery/knowledge sharing.",
    fields=[
        FieldSchema("from_agent", "string", required=True, max_length=256,
                     description="Agent casting the bottle"),
        FieldSchema("bottle_type", "enum", required=True,
                     enum_values=["status_update", "knowledge_sharing",
                                 "fleet_alert", "task_result", "lesson_learned"],
                     description="Type of bottle message"),
        FieldSchema("content", "string", required=True, max_length=4096,
                     description="Bottle content"),
        FieldSchema("priority", "enum", required=False,
                     enum_values=["urgent", "normal", "low", "fyi"],
                     default="normal",
                     description="Bottle priority"),
        FieldSchema("target_audience", "enum", required=False,
                     enum_values=["all", "lighthouses", "vessels", "specific"],
                     default="all",
                     description="Intended audience"),
        FieldSchema("ttl_hours", "integer", required=False, min_value=1, max_value=168,
                     default=24,
                     description="How long this bottle should remain visible"),
    ],
    ttl_seconds=604800,  # Max 1 week
)

# 9. NAMESPACE_QUERY (NSQ) - Query a namespace/vocabulary
MESSAGE_TYPE_NAMESPACE_QUERY = MessageTypeDefinition(
    name="NAMESPACE_QUERY",
    code="NSQ",
    category=MessageCategory.KNOWLEDGE,
    description="Query an agent's namespace for vocabulary or capability info.",
    fields=[
        FieldSchema("from_agent", "string", required=True, max_length=256,
                     description="Querying agent identifier"),
        FieldSchema("target_agent", "string", required=True, max_length=256,
                     description="Agent being queried"),
        FieldSchema("query_type", "enum", required=True,
                     enum_values=["vocab_list", "vocab_detail", "capability_check",
                                 "compatibility", "schema_request"],
                     description="Type of namespace query"),
        FieldSchema("namespace", "string", required=False, max_length=256,
                     description="Specific namespace to query"),
        FieldSchema("filter", "object", required=False,
                     description="Optional filter parameters"),
    ],
    expects_reply=True,
    reply_types=["SIGNAL_BROADCAST", "NAMESPACE_QUERY"],
    ttl_seconds=300,
)

# 10. OPCODE_REQUEST (OPR) - Request opcode/instruction execution
MESSAGE_TYPE_OPCODE_REQUEST = MessageTypeDefinition(
    name="OPCODE_REQUEST",
    code="OPR",
    category=MessageCategory.KNOWLEDGE,
    description="Request execution of a specific opcode or instruction sequence.",
    fields=[
        FieldSchema("request_id", "string", required=True, max_length=128,
                     description="Unique request identifier"),
        FieldSchema("from_agent", "string", required=True, max_length=256,
                     description="Requesting agent identifier"),
        FieldSchema("target_agent", "string", required=True, max_length=256,
                     description="Agent expected to execute"),
        FieldSchema("opcode", "string", required=True, max_length=64,
                     description="Opcode to execute"),
        FieldSchema("operands", "array", required=False, item_type="string",
                     description="Opcode operands/arguments"),
        FieldSchema("timeout_ms", "integer", required=False, min_value=100,
                     max_value=300000, default=30000,
                     description="Execution timeout in milliseconds"),
    ],
    expects_reply=True,
    reply_types=["INSTRUCTION_STREAM", "ERROR_REPORT"],
    ttl_seconds=3600,
)

# 11. INSTRUCTION_STREAM (INS) - Stream of instructions/opcode results
MESSAGE_TYPE_INSTRUCTION_STREAM = MessageTypeDefinition(
    name="INSTRUCTION_STREAM",
    code="INS",
    category=MessageCategory.KNOWLEDGE,
    description="Stream of instruction results or multi-step instruction payload.",
    fields=[
        FieldSchema("stream_id", "string", required=True, max_length=128,
                     description="Stream identifier (matches request_id)"),
        FieldSchema("agent_id", "string", required=True, max_length=256,
                     description="Streaming agent identifier"),
        FieldSchema("sequence_num", "integer", required=True, min_value=0,
                     description="Sequence number in the stream"),
        FieldSchema("total_steps", "integer", required=False, min_value=0,
                     description="Total steps in stream (if known)"),
        FieldSchema("instruction", "string", required=True, max_length=2048,
                     description="Instruction or result content"),
        FieldSchema("status", "enum", required=True,
                     enum_values=["in_progress", "intermediate", "final", "error"],
                     description="Stream status"),
        FieldSchema("data", "object", required=False,
                     description="Structured data payload"),
    ],
    ttl_seconds=3600,
)

# 12. CONFIDENCE_REPORT (CFR) - Report confidence level on a topic
MESSAGE_TYPE_CONFIDENCE_REPORT = MessageTypeDefinition(
    name="CONFIDENCE_REPORT",
    code="CFR",
    category=MessageCategory.COORDINATION,
    description="Report confidence level for a decision, claim, or assessment.",
    fields=[
        FieldSchema("agent_id", "string", required=True, max_length=256,
                     description="Reporting agent identifier"),
        FieldSchema("topic", "string", required=True, max_length=512,
                     description="Topic of the confidence report"),
        FieldSchema("confidence", "float", required=True, min_value=0.0, max_value=1.0,
                     description="Confidence score (0.0 to 1.0)"),
        FieldSchema("rationale", "string", required=True, max_length=2048,
                     description="Explanation for confidence level"),
        FieldSchema("evidence_count", "integer", required=False, min_value=0,
                     description="Number of evidence pieces considered"),
        FieldSchema("certainty_factors", "object", required=False,
                     description="Breakdown of confidence factors"),
    ],
    ttl_seconds=86400,
)

# 13. VIEWPOINT_EXCHANGE (VPE) - Exchange viewpoints between agents
MESSAGE_TYPE_VIEWPOINT_EXCHANGE = MessageTypeDefinition(
    name="VIEWPOINT_EXCHANGE",
    code="VPE",
    category=MessageCategory.COORDINATION,
    description="Exchange a viewpoint or perspective on a shared topic.",
    fields=[
        FieldSchema("from_agent", "string", required=True, max_length=256,
                     description="Agent sharing the viewpoint"),
        FieldSchema("topic", "string", required=True, max_length=512,
                     description="Topic of discussion"),
        FieldSchema("viewpoint", "string", required=True, max_length=4096,
                     description="The viewpoint being shared"),
        FieldSchema("stance", "enum", required=True,
                     enum_values=["for", "against", "neutral", "concerned",
                                 "enthusiastic", "skeptical"],
                     description="Stance on the topic"),
        FieldSchema("confidence", "float", required=False, min_value=0.0, max_value=1.0,
                     description="Confidence in this viewpoint"),
        FieldSchema("reply_to", "string", required=False, max_length=128,
                     description="ID of the viewpoint being replied to"),
    ],
    expects_reply=True,
    reply_types=["VIEWPOINT_EXCHANGE"],
    ttl_seconds=86400,
)

# 14. COORDINATE_PROPOSE (COP) - Propose coordination with another agent
MESSAGE_TYPE_COORDINATE_PROPOSE = MessageTypeDefinition(
    name="COORDINATE_PROPOSE",
    code="COP",
    category=MessageCategory.COORDINATION,
    description="Propose a coordination action or collaboration with another agent.",
    fields=[
        FieldSchema("from_agent", "string", required=True, max_length=256,
                     description="Proposing agent identifier"),
        FieldSchema("to_agent", "string", required=True, max_length=256,
                     description="Target agent for coordination"),
        FieldSchema("coordination_type", "enum", required=True,
                     enum_values=["pair_programming", "joint_review", "task_split",
                                 "knowledge_transfer", "mentorship", "consensus"],
                     description="Type of coordination proposed"),
        FieldSchema("proposal", "string", required=True, max_length=2048,
                     description="Description of the coordination proposal"),
        FieldSchema("task_id", "string", required=False,
                     description="Related task identifier"),
        FieldSchema("deadline", "string", required=False,
                     description="Proposed deadline (ISO 8601)"),
    ],
    expects_reply=True,
    reply_types=["COORDINATE_ACCEPT", "COORDINATE_REJECT"],
    ttl_seconds=86400,
)

# 15. COORDINATE_ACCEPT (COA) - Accept a coordination proposal
MESSAGE_TYPE_COORDINATE_ACCEPT = MessageTypeDefinition(
    name="COORDINATE_ACCEPT",
    code="COA",
    category=MessageCategory.COORDINATION,
    description="Accept a previously proposed coordination action.",
    fields=[
        FieldSchema("from_agent", "string", required=True, max_length=256,
                     description="Accepting agent identifier"),
        FieldSchema("proposal_id", "string", required=True, max_length=128,
                     description="ID of the accepted proposal"),
        FieldSchema("terms", "string", required=False, max_length=2048,
                     description="Any additional terms or conditions"),
        FieldSchema("available_at", "string", required=False,
                     description="When the agent is available (ISO 8601)"),
    ],
    ttl_seconds=86400,
)

# 16. COORDINATE_REJECT (COR) - Reject a coordination proposal
MESSAGE_TYPE_COORDINATE_REJECT = MessageTypeDefinition(
    name="COORDINATE_REJECT",
    code="COR",
    category=MessageCategory.COORDINATION,
    description="Reject a previously proposed coordination action.",
    fields=[
        FieldSchema("from_agent", "string", required=True, max_length=256,
                     description="Rejecting agent identifier"),
        FieldSchema("proposal_id", "string", required=True, max_length=128,
                     description="ID of the rejected proposal"),
        FieldSchema("reason", "string", required=True, max_length=1024,
                     description="Reason for rejection"),
        FieldSchema("alternative", "string", required=False, max_length=2048,
                     description="Suggested alternative approach"),
    ],
    ttl_seconds=86400,
)

# 17. STATUS_REPORT (STR) - Detailed status report
MESSAGE_TYPE_STATUS_REPORT = MessageTypeDefinition(
    name="STATUS_REPORT",
    code="STR",
    category=MessageCategory.STATUS,
    description="Detailed status report from an agent about its current state.",
    fields=[
        FieldSchema("agent_id", "string", required=True, max_length=256,
                     description="Reporting agent identifier"),
        FieldSchema("status", "enum", required=True,
                     enum_values=["online", "busy", "idle", "error", "offline",
                                 "maintenance", "degraded"],
                     description="Current agent status"),
        FieldSchema("current_task", "string", required=False,
                     description="Currently active task description"),
        FieldSchema("capacity", "integer", required=False, min_value=0, max_value=100,
                     description="Available capacity percentage"),
        FieldSchema("queue_depth", "integer", required=False, min_value=0,
                     description="Number of pending tasks in queue"),
        FieldSchema("uptime_seconds", "integer", required=False, min_value=0,
                     description="Agent uptime in seconds"),
        FieldSchema("metrics", "object", required=False,
                     description="Custom metrics dictionary"),
    ],
    ttl_seconds=300,
)

# 18. ERROR_REPORT (ERR) - Report an error or failure
MESSAGE_TYPE_ERROR_REPORT = MessageTypeDefinition(
    name="ERROR_REPORT",
    code="ERR",
    category=MessageCategory.ERROR,
    description="Report an error, failure, or anomaly encountered by an agent.",
    fields=[
        FieldSchema("agent_id", "string", required=True, max_length=256,
                     description="Reporting agent identifier"),
        FieldSchema("error_code", "string", required=True, max_length=64,
                     description="Machine-readable error code"),
        FieldSchema("severity", "enum", required=True,
                     enum_values=["critical", "high", "medium", "low", "info"],
                     description="Error severity level"),
        FieldSchema("description", "string", required=True, max_length=2048,
                     description="Human-readable error description"),
        FieldSchema("stack_trace", "string", required=False,
                     description="Stack trace or debug info"),
        FieldSchema("related_task_id", "string", required=False,
                     description="Task ID that caused the error"),
        FieldSchema("recoverable", "boolean", required=False, default=True,
                     description="Whether the error is recoverable"),
    ],
    ttl_seconds=86400,
)

# 19. SHUTDOWN (SDN) - Graceful agent shutdown notification
MESSAGE_TYPE_SHUTDOWN = MessageTypeDefinition(
    name="SHUTDOWN",
    code="SDN",
    category=MessageCategory.LIFECYCLE,
    description="Notify the fleet of a graceful agent shutdown.",
    fields=[
        FieldSchema("agent_id", "string", required=True, max_length=256,
                     description="Shutting down agent identifier"),
        FieldSchema("reason", "enum", required=True,
                     enum_values=["maintenance", "decommission", "restart",
                                 "upgrade", "capacity", "error"],
                     description="Reason for shutdown"),
        FieldSchema("eta_seconds", "integer", required=False, min_value=0,
                     description="Estimated seconds until shutdown completes"),
        FieldSchema("message", "string", required=False, max_length=1024,
                     description="Farewell message to the fleet"),
        FieldSchema("will_return", "boolean", required=False, default=True,
                     description="Whether the agent expects to return"),
        FieldSchema("pending_tasks", "array", required=False, item_type="string",
                     description="IDs of tasks being handed off"),
    ],
    ttl_seconds=3600,
)

# 20. PING (PNG) - Simple ping/pong connectivity check
MESSAGE_TYPE_PING = MessageTypeDefinition(
    name="PING",
    code="PNG",
    category=MessageCategory.HEARTBEAT,
    description="Simple ping for connectivity check. Expects PONG reply.",
    fields=[
        FieldSchema("from_agent", "string", required=True, max_length=256,
                     description="Pinging agent identifier"),
        FieldSchema("timestamp", "string", required=True,
                     description="ISO 8601 timestamp of the ping"),
        FieldSchema("nonce", "string", required=False, max_length=64,
                     description="Unique nonce to match request/response"),
    ],
    expects_reply=True,
    reply_types=["PING"],  # PONG is just a PING response
    ttl_seconds=30,
)


# ---------------------------------------------------------------------------
# Registry - lookup by name or code
# ---------------------------------------------------------------------------

ALL_MESSAGE_TYPES: Dict[str, MessageTypeDefinition] = {}

_TYPE_CODE_MAP: Dict[str, MessageTypeDefinition] = {}


def _register_all():
    """Register all 20 message types into the lookup dictionaries."""
    types = [
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
    ]
    for mt in types:
        ALL_MESSAGE_TYPES[mt.name] = mt
        _TYPE_CODE_MAP[mt.code] = mt


_register_all()


def get_message_type(name: str) -> MessageTypeDefinition:
    """Look up a message type definition by name. Raises InvalidMessageTypeError."""
    if name not in ALL_MESSAGE_TYPES:
        raise InvalidMessageTypeError(name)
    return ALL_MESSAGE_TYPES[name]


def get_message_type_by_code(code: str) -> MessageTypeDefinition:
    """Look up a message type definition by its 3-letter code."""
    if code not in _TYPE_CODE_MAP:
        raise InvalidMessageTypeError(code)
    return _TYPE_CODE_MAP[code]


def list_message_types() -> List[MessageTypeDefinition]:
    """Return a list of all registered message types."""
    return list(ALL_MESSAGE_TYPES.values())


def list_message_types_by_category() -> Dict[str, List[str]]:
    """Return message types grouped by category."""
    result: Dict[str, List[str]] = {}
    for mt in ALL_MESSAGE_TYPES.values():
        cat = mt.category.value
        if cat not in result:
            result[cat] = []
        result[cat].append(mt.name)
    return result
