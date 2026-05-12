"""Redis pub/sub system for real-time notifications and events."""

import json
import asyncio
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import time

from app.shared.core.redis import redis_manager
from app.shared.core.logging import get_logger

logger = get_logger(__name__)


class EventType(Enum):
    """Event types for pub/sub system."""
    STOCK_CHANGE = "stock_change"
    INVENTORY_UPDATE = "inventory_update"
    WAREHOUSE_UPDATE = "warehouse_update"
    USER_ACTIVITY = "user_activity"
    DOCUMENT_STATUS = "document_status"
    SYSTEM_ALERT = "system_alert"


@dataclass
class Event:
    """Event data structure."""
    event_type: EventType
    data: Dict[str, Any]
    timestamp: float
    source: str
    user_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    product_id: Optional[int] = None


class PubSubManager:
    """Manages Redis pub/sub subscriptions and publishing."""
    
    def __init__(self):
        self._subscriptions: Dict[str, List[Callable]] = {}
        self._pubsub = None
        self._listener_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize pub/sub manager."""
        if self._running:
            return
        
        # Subscribe to all event type channels
        event_channels = [f"wms_events:{event_type.value}" for event_type in EventType]
        self._pubsub = await redis_manager.subscribe(*event_channels)
        self._listener_task = asyncio.create_task(self._listen_for_messages())
        self._running = True
        logger.info("PubSub manager initialized")
    
    async def shutdown(self) -> None:
        """Shutdown pub/sub manager."""
        self._running = False
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        
        if self._pubsub:
            await self._pubsub.aclose()
        
        logger.info("PubSub manager shutdown")
    
    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        """Subscribe to specific event type."""
        channel = f"wms_events:{event_type.value}"
        if channel not in self._subscriptions:
            self._subscriptions[channel] = []
        self._subscriptions[channel].append(callback)
        logger.info(f"Subscribed to {channel}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """Unsubscribe from specific event type."""
        channel = f"wms_events:{event_type.value}"
        if channel in self._subscriptions:
            try:
                self._subscriptions[channel].remove(callback)
                logger.info(f"Unsubscribed from {channel}")
                # Clean up empty subscription lists
                if not self._subscriptions[channel]:
                    del self._subscriptions[channel]
            except ValueError:
                logger.warning(f"Callback not found in subscriptions for {channel}")
        else:
            logger.warning(f"No subscriptions found for {channel}")
    
    async def publish(self, event: Event) -> None:
        """Publish event to Redis."""
        try:
            channel = f"wms_events:{event.event_type.value}"
            message = {
                "event_type": event.event_type.value,
                "data": event.data,
                "timestamp": event.timestamp,
                "source": event.source,
                "user_id": event.user_id,
                "warehouse_id": event.warehouse_id,
                "product_id": event.product_id,
            }
            
            published = await redis_manager.publish(channel, json.dumps(message, default=str))
            if published > 0:
                logger.debug(f"Published event to {channel}, {published} subscribers")
            else:
                logger.warning(f"No subscribers for {channel}")
                
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
    
    async def _listen_for_messages(self) -> None:
        """Listen for pub/sub messages."""
        try:
            async for message in self._pubsub.listen():
                if message["type"] == "message":
                    await self._handle_message(message)
        except Exception as e:
            if self._running:
                logger.error(f"Error in pub/sub listener: {e}")
    
    async def _handle_message(self, message: Dict[str, Any]) -> None:
        """Handle incoming pub/sub message."""
        try:
            # Handle both string and bytes channel names
            channel = message["channel"]
            if isinstance(channel, bytes):
                channel = channel.decode("utf-8")
            
            # Handle both string and bytes data
            data = message["data"]
            if isinstance(data, bytes):
                data = data.decode("utf-8")
            data = json.loads(data)
            
            # Find callbacks for this channel
            callbacks = self._subscriptions.get(channel, [])
            for callback in callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    logger.error(f"Error in callback for {channel}: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling message: {e}")


class EventPublisher:
    """Helper class for publishing events."""
    
    @staticmethod
    async def publish_stock_change(
        product_id: int,
        old_quantity: int,
        new_quantity: int,
        warehouse_id: Optional[int] = None,
        user_id: Optional[int] = None,
        source: str = "inventory_service"
    ) -> None:
        """Publish stock change event."""
        event = Event(
            event_type=EventType.STOCK_CHANGE,
            data={
                "product_id": product_id,
                "old_quantity": old_quantity,
                "new_quantity": new_quantity,
                "change": new_quantity - old_quantity,
                "warehouse_id": warehouse_id,
            },
            timestamp=time.time(),
            source=source,
            user_id=user_id,
            warehouse_id=warehouse_id,
            product_id=product_id,
        )
        await pubsub_manager.publish(event)
    
    @staticmethod
    async def publish_inventory_update(
        product_id: int,
        warehouse_id: int,
        quantity: int,
        operation: str,  # "add", "remove", "transfer"
        user_id: Optional[int] = None,
        source: str = "inventory_service"
    ) -> None:
        """Publish inventory update event."""
        event = Event(
            event_type=EventType.INVENTORY_UPDATE,
            data={
                "product_id": product_id,
                "warehouse_id": warehouse_id,
                "quantity": quantity,
                "operation": operation,
            },
            timestamp=time.time(),
            source=source,
            user_id=user_id,
            warehouse_id=warehouse_id,
            product_id=product_id,
        )
        await pubsub_manager.publish(event)
    
    @staticmethod
    async def publish_document_status(
        document_id: int,
        status: str,
        user_id: Optional[int] = None,
        source: str = "document_service"
    ) -> None:
        """Publish document status change event."""
        event = Event(
            event_type=EventType.DOCUMENT_STATUS,
            data={
                "document_id": document_id,
                "status": status,
            },
            timestamp=time.time(),
            source=source,
            user_id=user_id,
        )
        await pubsub_manager.publish(event)
    
    @staticmethod
    async def publish_system_alert(
        message: str,
        level: str = "info",  # "info", "warning", "error", "critical"
        source: str = "system"
    ) -> None:
        """Publish system alert event."""
        event = Event(
            event_type=EventType.SYSTEM_ALERT,
            data={
                "message": message,
                "level": level,
            },
            timestamp=time.time(),
            source=source,
        )
        await pubsub_manager.publish(event)


# Global pub/sub manager instance
pubsub_manager = PubSubManager()
