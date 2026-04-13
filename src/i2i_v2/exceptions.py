"""
I2I v2 Protocol - Custom Exceptions

Defines all exception types for the Iron-to-Iron v2 protocol.
"""


class I2IError(Exception):
    """Base exception for all I2I protocol errors."""
    def __init__(self, message: str, code: str = "I2I_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class InvalidMessageTypeError(I2IError):
    """Raised when an unknown or unsupported message type is used."""
    def __init__(self, type_name: str):
        self.type_name = type_name
        super().__init__(
            f"Unknown message type: {type_name}",
            code="INVALID_TYPE"
        )


class MessageValidationError(I2IError):
    """Raised when a message fails validation against its schema."""
    def __init__(self, message: str, errors: list = None):
        self.errors = errors or []
        super().__init__(
            f"Message validation failed: {message}",
            code="VALIDATION_ERROR"
        )


class SerializationError(I2IError):
    """Raised when message serialization/deserialization fails."""
    def __init__(self, message: str, original_error: Exception = None):
        self.original_error = original_error
        super().__init__(
            f"Serialization error: {message}",
            code="SERIALIZATION_ERROR"
        )


class MessageBusError(I2IError):
    """Raised when the message bus encounters an operational error."""
    def __init__(self, message: str):
        super().__init__(
            f"Message bus error: {message}",
            code="BUS_ERROR"
        )


class DuplicateHandlerError(I2IError):
    """Raised when attempting to register a duplicate handler for a message type."""
    def __init__(self, type_name: str):
        self.type_name = type_name
        super().__init__(
            f"Handler already registered for type: {type_name}",
            code="DUPLICATE_HANDLER"
        )


class NoHandlerError(I2IError):
    """Raised when no handler is registered for a dispatched message type."""
    def __init__(self, type_name: str):
        self.type_name = type_name
        super().__init__(
            f"No handler registered for type: {type_name}",
            code="NO_HANDLER"
        )


class VersionMismatchError(I2IError):
    """Raised when message version doesn't match the expected protocol version."""
    def __init__(self, expected: str, actual: str):
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"Version mismatch: expected {expected}, got {actual}",
            code="VERSION_MISMATCH"
        )


class MessageExpiredError(I2IError):
    """Raised when a message has exceeded its TTL."""
    def __init__(self, msg_id: str, ttl: int):
        self.msg_id = msg_id
        self.ttl = ttl
        super().__init__(
            f"Message {msg_id} expired (TTL: {ttl}s)",
            code="MESSAGE_EXPIRED"
        )
