"""
I2I v2 Protocol - Package Initialization

Iron-to-Iron v2: The Inter-Agent-to-Inter-Agent communication protocol
for the FLUX fleet.

Usage:
    from i2i_v2 import Message, MessageBus, create_heartbeat
"""

from .message_types import (
    PROTOCOL_VERSION,
    MessageCategory,
    MessageTypeDefinition,
    FieldSchema,
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
    get_message_type,
    get_message_type_by_code,
    list_message_types,
    list_message_types_by_category,
    ALL_MESSAGE_TYPES,
)

from .message import (
    Message,
    MessageHeader,
    create_pong,
    create_error_reply,
)

from .bus import (
    MessageBus,
    DeliveryGuarantee,
    BusMetrics,
)

from .exceptions import (
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

# 20 message type names for easy reference
MESSAGE_TYPE_NAMES = [
    "HEARTBEAT",
    "TASK_CLAIM",
    "TASK_COMPLETE",
    "TRUST_UPDATE",
    "SIGNAL_BROADCAST",
    "FLEET_DISCOVERY",
    "MERIT_AWARD",
    "BOTTLE_CAST",
    "NAMESPACE_QUERY",
    "OPCODE_REQUEST",
    "INSTRUCTION_STREAM",
    "CONFIDENCE_REPORT",
    "VIEWPOINT_EXCHANGE",
    "COORDINATE_PROPOSE",
    "COORDINATE_ACCEPT",
    "COORDINATE_REJECT",
    "STATUS_REPORT",
    "ERROR_REPORT",
    "SHUTDOWN",
    "PING",
]

__version__ = "2.0.0"
__protocol_version__ = PROTOCOL_VERSION

__all__ = [
    # Version
    "__version__",
    "__protocol_version__",
    "PROTOCOL_VERSION",
    # Message Types
    "MessageCategory",
    "MessageTypeDefinition",
    "FieldSchema",
    "MESSAGE_TYPE_NAMES",
    "ALL_MESSAGE_TYPES",
    "MESSAGE_TYPE_HEARTBEAT",
    "MESSAGE_TYPE_TASK_CLAIM",
    "MESSAGE_TYPE_TASK_COMPLETE",
    "MESSAGE_TYPE_TRUST_UPDATE",
    "MESSAGE_TYPE_SIGNAL_BROADCAST",
    "MESSAGE_TYPE_FLEET_DISCOVERY",
    "MESSAGE_TYPE_MERIT_AWARD",
    "MESSAGE_TYPE_BOTTLE_CAST",
    "MESSAGE_TYPE_NAMESPACE_QUERY",
    "MESSAGE_TYPE_OPCODE_REQUEST",
    "MESSAGE_TYPE_INSTRUCTION_STREAM",
    "MESSAGE_TYPE_CONFIDENCE_REPORT",
    "MESSAGE_TYPE_VIEWPOINT_EXCHANGE",
    "MESSAGE_TYPE_COORDINATE_PROPOSE",
    "MESSAGE_TYPE_COORDINATE_ACCEPT",
    "MESSAGE_TYPE_COORDINATE_REJECT",
    "MESSAGE_TYPE_STATUS_REPORT",
    "MESSAGE_TYPE_ERROR_REPORT",
    "MESSAGE_TYPE_SHUTDOWN",
    "MESSAGE_TYPE_PING",
    # Lookup functions
    "get_message_type",
    "get_message_type_by_code",
    "list_message_types",
    "list_message_types_by_category",
    # Message
    "Message",
    "MessageHeader",
    "create_pong",
    "create_error_reply",
    # Bus
    "MessageBus",
    "DeliveryGuarantee",
    "BusMetrics",
    # Exceptions
    "I2IError",
    "InvalidMessageTypeError",
    "MessageValidationError",
    "SerializationError",
    "MessageBusError",
    "DuplicateHandlerError",
    "NoHandlerError",
    "VersionMismatchError",
    "MessageExpiredError",
]
