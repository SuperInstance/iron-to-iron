"""
I2I v2 Protocol - Message Bus / Broker

Implements a message bus for routing I2I v2 messages between agents.
Supports both synchronous (send/reply) and asynchronous (pub/sub) patterns.
"""

from __future__ import annotations

import asyncio
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set, Tuple

from .message import Message
from .message_types import (
    MessageTypeDefinition,
    get_message_type,
    list_message_types,
)
from .exceptions import (
    DuplicateHandlerError,
    MessageBusError,
    NoHandlerError,
)


# Handler type: sync or async
SyncHandler = Callable[[Message], Optional[Message]]
AsyncHandler = Callable[[Message], Coroutine[Any, Any, Optional[Message]]]
MessageHandler = Callable[[Message], Any]


class DeliveryGuarantee(str, Enum):
    """Message delivery guarantee levels."""
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


@dataclass
class HandlerEntry:
    """Registry entry for a message handler."""
    handler: MessageHandler
    is_async: bool = False
    agent_id: str = ""
    priority: int = 0  # Higher = processed first
    filter_fn: Optional[Callable[[Message], bool]] = None


@dataclass
class Envelope:
    """A message envelope for in-flight messages on the bus."""
    message: Message
    delivered: bool = False
    deliver_count: int = 0
    created_at: float = field(default_factory=time.time)


@dataclass
class BusMetrics:
    """Metrics for the message bus."""
    messages_sent: int = 0
    messages_received: int = 0
    messages_dropped: int = 0
    messages_expired: int = 0
    errors: int = 0
    pending_replies: int = 0


class MessageBus:
    """
    I2I v2 Message Bus / Broker.

    Routes messages between agents with support for:
    - Synchronous request/reply patterns
    - Asynchronous pub/sub patterns
    - Message handlers per type
    - Priority-based handler ordering
    - Delivery guarantees
    - Message filtering
    """

    def __init__(
        self,
        bus_id: str = "default",
        guarantee: DeliveryGuarantee = DeliveryGuarantee.AT_MOST_ONCE,
        max_queue_size: int = 10000,
    ):
        self.bus_id = bus_id
        self.guarantee = guarantee
        self.max_queue_size = max_queue_size

        # Handler registry: type_name -> list of HandlerEntry
        self._handlers: Dict[str, List[HandlerEntry]] = defaultdict(list)

        # Pending reply futures for sync patterns
        self._pending_replies: Dict[str, asyncio.Future] = {}

        # Message history (bounded)
        self._history: List[Envelope] = []
        self._history_lock = threading.Lock()

        # Subscribers for pub/sub
        self._subscribers: Dict[str, Set[str]] = defaultdict(set)

        # Metrics
        self.metrics = BusMetrics()

        # Lock for thread safety
        self._lock = threading.RLock()

        # Async event loop reference
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    # --- Handler Registration ---

    def register_handler(
        self,
        type_name: str,
        handler: MessageHandler,
        agent_id: str = "",
        priority: int = 0,
        filter_fn: Optional[Callable[[Message], bool]] = None,
    ) -> None:
        """
        Register a handler for a specific message type.

        Args:
            type_name: Message type name to handle.
            handler: Callable that takes a Message and returns optional reply.
            agent_id: ID of the agent registering the handler.
            priority: Handler priority (higher = processed first).
            filter_fn: Optional filter - handler only called if filter returns True.

        Raises:
            InvalidMessageTypeError: If type_name is unknown.
        """
        # Validate the type name exists
        get_message_type(type_name)

        # Check for duplicate handler (same agent + same type)
        with self._lock:
            for entry in self._handlers[type_name]:
                if entry.agent_id == agent_id and entry.handler == handler:
                    raise DuplicateHandlerError(type_name)

            is_async = asyncio.iscoroutinefunction(handler)

            entry = HandlerEntry(
                handler=handler,
                is_async=is_async,
                agent_id=agent_id,
                priority=priority,
                filter_fn=filter_fn,
            )
            self._handlers[type_name].append(entry)

            # Sort by priority (descending)
            self._handlers[type_name].sort(key=lambda e: e.priority, reverse=True)

    def unregister_handler(
        self,
        type_name: str,
        agent_id: str = "",
    ) -> None:
        """
        Unregister all handlers for a type/agent combination.

        Args:
            type_name: Message type name.
            agent_id: Agent ID to unregister.
        """
        with self._lock:
            self._handlers[type_name] = [
                e for e in self._handlers[type_name]
                if e.agent_id != agent_id
            ]

    def register_catchall(
        self,
        handler: MessageHandler,
        agent_id: str = "",
        priority: int = -100,
    ) -> None:
        """
        Register a catch-all handler that receives all messages.

        Args:
            handler: Callable that takes any Message.
            agent_id: Agent ID.
            priority: Priority (default: low priority).
        """
        # Register for all known message types
        for mt in list_message_types():
            try:
                self.register_handler(mt.name, handler, agent_id, priority)
            except DuplicateHandlerError:
                pass

    # --- Message Dispatch (Sync) ---

    def send(self, message: Message) -> List[Message]:
        """
        Synchronously dispatch a message to all matching handlers.

        Args:
            message: The message to dispatch.

        Returns:
            List of reply messages from handlers.

        Raises:
            NoHandlerError: If no handler is registered for the message type.
            MessageBusError: If a handler raises an exception.
        """
        type_name = message.header.message_type

        with self._lock:
            handlers = self._handlers.get(type_name, [])

        if not handlers:
            self.metrics.messages_dropped += 1
            raise NoHandlerError(type_name)

        replies: List[Message] = []

        for entry in handlers:
            # Apply filter
            if entry.filter_fn and not entry.filter_fn(message):
                continue

            try:
                self.metrics.messages_sent += 1

                if entry.is_async:
                    # Sync dispatch of async handler
                    if self._loop and self._loop.is_running():
                        reply = asyncio.run_coroutine_threadsafe(
                            entry.handler(message), self._loop
                        ).result(timeout=30)
                    else:
                        reply = asyncio.get_event_loop().run_until_complete(
                            entry.handler(message)
                        )
                else:
                    reply = entry.handler(message)

                if reply is not None:
                    replies.append(reply)

                self.metrics.messages_received += 1

            except Exception as e:
                self.metrics.errors += 1
                raise MessageBusError(
                    f"Handler error for {type_name}: {e}"
                ) from e

        # Record in history
        self._record_envelope(message)

        return replies

    def send_and_wait(
        self,
        message: Message,
        timeout: float = 30.0,
    ) -> Message:
        """
        Send a message and wait for the first reply.

        Args:
            message: Message to send.
            timeout: Maximum time to wait for reply (seconds).

        Returns:
            The first reply message.

        Raises:
            MessageBusError: If timeout or no reply received.
        """
        replies = self.send(message)
        if replies:
            return replies[0]
        raise MessageBusError(
            f"No reply received for {message.type_name} "
            f"within timeout={timeout}s"
        )

    # --- Message Dispatch (Async) ---

    async def send_async(self, message: Message) -> List[Message]:
        """
        Asynchronously dispatch a message to all matching handlers.

        Args:
            message: The message to dispatch.

        Returns:
            List of reply messages from handlers.
        """
        type_name = message.header.message_type

        with self._lock:
            handlers = list(self._handlers.get(type_name, []))

        if not handlers:
            self.metrics.messages_dropped += 1
            raise NoHandlerError(type_name)

        replies: List[Message] = []

        for entry in handlers:
            if entry.filter_fn and not entry.filter_fn(message):
                continue

            try:
                self.metrics.messages_sent += 1

                if entry.is_async:
                    reply = await entry.handler(message)
                else:
                    reply = entry.handler(message)

                if reply is not None:
                    replies.append(reply)

                self.metrics.messages_received += 1

            except Exception as e:
                self.metrics.errors += 1
                raise MessageBusError(
                    f"Handler error for {type_name}: {e}"
                ) from e

        self._record_envelope(message)
        return replies

    async def send_and_wait_async(
        self,
        message: Message,
        timeout: float = 30.0,
    ) -> Message:
        """
        Async send-and-wait with timeout.
        """
        try:
            replies = await asyncio.wait_for(
                self.send_async(message),
                timeout=timeout,
            )
            if replies:
                return replies[0]
        except asyncio.TimeoutError:
            pass
        raise MessageBusError(
            f"No reply received for {message.type_name} "
            f"within timeout={timeout}s"
        )

    # --- Pub/Sub ---

    def subscribe(self, agent_id: str, type_name: str) -> None:
        """
        Subscribe an agent to a message type.

        Args:
            agent_id: Agent ID subscribing.
            type_name: Message type to subscribe to.
        """
        self._subscribers[type_name].add(agent_id)

    def unsubscribe(self, agent_id: str, type_name: str) -> None:
        """Unsubscribe an agent from a message type."""
        self._subscribers[type_name].discard(agent_id)

    def get_subscribers(self, type_name: str) -> Set[str]:
        """Get all subscriber agent IDs for a message type."""
        return self._subscribers[type_name].copy()

    def publish(self, message: Message) -> int:
        """
        Publish a message to all subscribers of its type.

        Args:
            message: Message to publish.

        Returns:
            Number of subscribers notified.
        """
        subscribers = self.get_subscribers(message.header.message_type)
        count = len(subscribers)
        self._record_envelope(message)
        self.metrics.messages_sent += count
        return count

    # --- History and Metrics ---

    def _record_envelope(self, message: Message) -> None:
        """Record a message in the history buffer."""
        with self._history_lock:
            envelope = Envelope(message=message, delivered=True, deliver_count=1)
            self._history.append(envelope)
            # Trim history if too large
            if len(self._history) > self.max_queue_size:
                self._history = self._history[-self.max_queue_size // 2:]

    def get_history(
        self,
        type_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[Message]:
        """
        Get message history, optionally filtered by type.

        Args:
            type_name: Optional type filter.
            limit: Maximum messages to return.

        Returns:
            List of historical messages.
        """
        with self._history_lock:
            msgs = [e.message for e in self._history]

        if type_name:
            msgs = [m for m in msgs if m.header.message_type == type_name]

        return msgs[-limit:]

    def get_handler_count(self, type_name: str) -> int:
        """Get the number of handlers registered for a message type."""
        return len(self._handlers.get(type_name, []))

    def get_registered_types(self) -> List[str]:
        """Get all message types that have at least one handler."""
        return [k for k, v in self._handlers.items() if v]

    def set_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Set the async event loop reference."""
        self._loop = loop

    def reset_metrics(self) -> None:
        """Reset all bus metrics to zero."""
        self.metrics = BusMetrics()

    def __repr__(self) -> str:
        types = self.get_registered_types()
        return (
            f"MessageBus(id={self.bus_id}, "
            f"handlers={len(types)}, "
            f"guarantee={self.guarantee.value})"
        )
