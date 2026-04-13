"""
I2I v2 Protocol - Message Implementation

Provides the core Message class for creating, serializing, and deserializing
I2I v2 protocol messages. Supports both wire format (JSON) and commit format.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .message_types import (
    MessageTypeDefinition,
    PROTOCOL_VERSION,
    get_message_type,
    get_message_type_by_code,
)
from .exceptions import (
    MessageValidationError,
    SerializationError,
    InvalidMessageTypeError,
    VersionMismatchError,
    MessageExpiredError,
)


@dataclass
class MessageHeader:
    """I2I v2 message header with routing and metadata."""
    protocol_version: str = PROTOCOL_VERSION
    message_type: str = ""
    message_code: str = ""
    message_id: str = ""
    timestamp: str = ""
    source_agent: str = ""
    target_agent: str = ""
    reply_to: str = ""
    correlation_id: str = ""
    ttl: int = 3600
    priority: str = "normal"

    def __post_init__(self):
        if not self.message_id:
            self.message_id = _generate_message_id()
        if not self.timestamp:
            self.timestamp = _generate_timestamp()


@dataclass
class Message:
    """
    I2I v2 Protocol Message.

    Represents a complete I2I v2 message with header, payload, and metadata.
    Supports serialization to/from JSON wire format and I2I commit format.
    """
    header: MessageHeader = field(default_factory=MessageHeader)
    payload: Dict[str, Any] = field(default_factory=dict)
    signature: str = ""

    # --- Factory methods ---

    @classmethod
    def create(
        cls,
        type_name: str,
        payload: Dict[str, Any],
        source_agent: str = "",
        target_agent: str = "",
        reply_to: str = "",
        correlation_id: str = "",
        ttl: Optional[int] = None,
        priority: str = "normal",
    ) -> "Message":
        """
        Create a new I2I v2 message with the given type and payload.

        Args:
            type_name: Name of the message type (e.g., "HEARTBEAT").
            payload: Dictionary of payload fields.
            source_agent: ID of the sending agent.
            target_agent: ID of the receiving agent (optional).
            reply_to: Message ID this is a reply to (optional).
            correlation_id: Correlation ID for request/response pairing.
            ttl: Time-to-live in seconds (uses type default if not provided).
            priority: Message priority (normal, high, low, urgent).

        Returns:
            A validated Message instance.

        Raises:
            InvalidMessageTypeError: If type_name is unknown.
            MessageValidationError: If payload doesn't match schema.
        """
        type_def = get_message_type(type_name)

        header = MessageHeader(
            message_type=type_name,
            message_code=type_def.code,
            source_agent=source_agent,
            target_agent=target_agent,
            reply_to=reply_to,
            correlation_id=correlation_id,
            ttl=ttl if ttl is not None else type_def.ttl_seconds,
            priority=priority,
        )

        if correlation_id:
            header.correlation_id = correlation_id
        elif reply_to:
            header.correlation_id = reply_to

        msg = cls(header=header, payload=dict(payload))
        msg.validate()
        return msg

    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """
        Deserialize a message from JSON string.

        Args:
            json_str: JSON-encoded message.

        Returns:
            Deserialized Message instance.

        Raises:
            SerializationError: If deserialization fails.
        """
        try:
            data = json.loads(json_str)
        except (json.JSONDecodeError, TypeError) as e:
            raise SerializationError(f"Invalid JSON: {e}", original_error=e)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """
        Deserialize a message from a dictionary.

        Args:
            data: Dictionary with 'header' and 'payload' keys.

        Returns:
            Deserialized Message instance.

        Raises:
            SerializationError: If deserialization fails.
        """
        try:
            header_data = data.get("header", {})
            header = MessageHeader(
                protocol_version=header_data.get("protocol_version", PROTOCOL_VERSION),
                message_type=header_data.get("message_type", ""),
                message_code=header_data.get("message_code", ""),
                message_id=header_data.get("message_id", _generate_message_id()),
                timestamp=header_data.get("timestamp", _generate_timestamp()),
                source_agent=header_data.get("source_agent", ""),
                target_agent=header_data.get("target_agent", ""),
                reply_to=header_data.get("reply_to", ""),
                correlation_id=header_data.get("correlation_id", ""),
                ttl=header_data.get("ttl", 3600),
                priority=header_data.get("priority", "normal"),
            )

            payload = data.get("payload", {})
            signature = data.get("signature", "")

            return cls(header=header, payload=payload, signature=signature)

        except (AttributeError, KeyError, TypeError) as e:
            raise SerializationError(f"Invalid message structure: {e}", original_error=e)

    # --- Serialization ---

    def to_json(self, pretty: bool = False) -> str:
        """
        Serialize the message to a JSON string.

        Args:
            pretty: If True, use indentation for readability.

        Returns:
            JSON string representation.
        """
        indent = 2 if pretty else None
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the message to a dictionary."""
        return {
            "header": asdict(self.header),
            "payload": self.payload,
            "signature": self.signature,
        }

    def to_commit_message(self) -> str:
        """
        Format the message as an I2I commit message.

        Format: [I2I:{TYPE}:{CODE}] scope — summary

        Returns:
            Commit-message formatted string.
        """
        summary = self.payload.get("summary", "")
        if not summary:
            # Build summary from key fields
            parts = []
            for k, v in self.payload.items():
                if k in ("summary", "description", "rationale", "content",
                          "viewpoint", "proposal"):
                    parts.append(str(v)[:100])
                    break
            summary = parts[0] if parts else self.header.message_type

        scope = self.header.source_agent or self.header.message_type.lower()

        header_line = (
            f"[I2I:{self.header.message_type}:{self.header.message_code}] "
            f"{scope} \u2014 {summary}"
        )

        # Build body from payload
        body_lines = []
        for key, value in self.payload.items():
            if key == "summary":
                continue
            if isinstance(value, (str, int, float, bool)):
                body_lines.append(f"{key}: {value}")
            elif isinstance(value, list):
                body_lines.append(f"{key}: {json.dumps(value)}")
            elif isinstance(value, dict):
                body_lines.append(f"{key}: {json.dumps(value)}")

        body = "\n".join(body_lines)

        if self.header.source_agent:
            body += f"\n\nCo-Authored-By: {self.header.source_agent} <i2i-v2>"

        return f"{header_line}\n\n{body}" if body else header_line

    # --- Validation ---

    def validate(self) -> List[str]:
        """
        Validate the message against its type schema.

        Returns:
            List of validation error strings (empty if valid).

        Raises:
            InvalidMessageTypeError: If message type is unknown.
            VersionMismatchError: If protocol version doesn't match.
        """
        errors: List[str] = []

        # Check protocol version
        if self.header.protocol_version != PROTOCOL_VERSION:
            raise VersionMismatchError(PROTOCOL_VERSION, self.header.protocol_version)

        # Get type definition
        try:
            type_def = get_message_type(self.header.message_type)
        except InvalidMessageTypeError:
            raise InvalidMessageTypeError(self.header.message_type)

        # Validate message code matches type
        if self.header.message_code != type_def.code:
            errors.append(
                f"Message code mismatch: header has '{self.header.message_code}', "
                f"expected '{type_def.code}'"
            )

        # Validate payload against type schema
        payload_errors = type_def.validate_payload(self.payload)
        errors.extend(payload_errors)

        return errors

    def is_valid(self) -> bool:
        """Check if message is valid (no validation errors)."""
        try:
            return len(self.validate()) == 0
        except (InvalidMessageTypeError, VersionMismatchError):
            return False

    def check_ttl(self) -> bool:
        """
        Check if the message has not expired.

        Returns:
            True if message is still within its TTL.

        Raises:
            MessageExpiredError: If message has expired.
        """
        msg_time = datetime.fromisoformat(self.header.timestamp.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        elapsed = (now - msg_time).total_seconds()

        if elapsed > self.header.ttl:
            raise MessageExpiredError(self.header.message_id, self.header.ttl)

        return True

    # --- Signing ---

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of the message content for signing.

        The signature field is excluded from the hash to avoid
        circular dependency (sign -> includes sig -> different hash).
        """
        data = self.to_dict()
        data["signature"] = ""
        content = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def sign(self, key: str = "default") -> str:
        """
        Sign the message with a key.

        Args:
            key: Signing key identifier.

        Returns:
            The computed signature hash.
        """
        self.signature = self.compute_hash()
        return self.signature

    def verify_signature(self) -> bool:
        """
        Verify the message signature.

        Returns:
            True if signature matches content, False otherwise.
        """
        if not self.signature:
            return False
        return self.signature == self.compute_hash()

    # --- Convenience ---

    @property
    def type_name(self) -> str:
        return self.header.message_type

    @property
    def type_code(self) -> str:
        return self.header.message_code

    @property
    def msg_id(self) -> str:
        return self.header.message_id

    @property
    def is_expired(self) -> bool:
        """Check expiration without raising."""
        try:
            self.check_ttl()
            return False
        except MessageExpiredError:
            return True

    def __repr__(self) -> str:
        return (
            f"Message(type={self.header.message_type}, "
            f"id={self.header.message_id[:8]}..., "
            f"from={self.header.source_agent})"
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _generate_message_id() -> str:
    """Generate a unique message ID."""
    return str(uuid.uuid4())


def _generate_timestamp() -> str:
    """Generate current ISO 8601 timestamp."""
    return datetime.now(timezone.utc).isoformat()


def create_pong(ping: Message) -> Message:
    """Create a PONG response from a PING message."""
    return Message.create(
        type_name="PING",
        payload={
            "from_agent": ping.header.target_agent or "",
            "timestamp": _generate_timestamp(),
            "nonce": ping.payload.get("nonce", ""),
        },
        source_agent=ping.header.target_agent or "",
        target_agent=ping.header.source_agent,
        reply_to=ping.header.message_id,
    )


def create_error_reply(
    original: Message,
    error_code: str,
    severity: str = "medium",
    description: str = "",
    recoverable: bool = True,
) -> Message:
    """Create an ERROR_REPORT reply to any message."""
    return Message.create(
        type_name="ERROR_REPORT",
        payload={
            "agent_id": original.header.target_agent or "",
            "error_code": error_code,
            "severity": severity,
            "description": description,
            "related_task_id": original.payload.get("task_id", ""),
            "recoverable": recoverable,
        },
        source_agent=original.header.target_agent or "",
        target_agent=original.header.source_agent,
        reply_to=original.header.message_id,
    )
