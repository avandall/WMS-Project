"""WebSocket endpoints for real-time updates."""

import json
import asyncio
from typing import Dict, Set, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from app.shared.core.pubsub import pubsub_manager, EventType
from app.shared.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.user_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int, channels: List[str]):
        """Accept WebSocket connection and subscribe to channels."""
        await websocket.accept()
        
        # Add to general connections
        if "general" not in self.active_connections:
            self.active_connections["general"] = set()
        self.active_connections["general"].add(websocket)
        
        # Add to user-specific connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)
        
        # Add to channel-specific connections
        for channel in channels:
            if channel not in self.active_connections:
                self.active_connections[channel] = set()
            self.active_connections[channel].add(websocket)
        
        logger.info(f"WebSocket connected for user {user_id}, channels: {channels}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove WebSocket connection."""
        # Remove from all connection sets
        for channel_connections in self.active_connections.values():
            channel_connections.discard(websocket)
        
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_personal_message(self, message: str, user_id: int):
        """Send message to specific user."""
        if user_id in self.user_connections:
            disconnected = set()
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_text(message)
                except Exception:
                    disconnected.add(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.user_connections[user_id].discard(conn)
    
    async def broadcast_to_channel(self, message: str, channel: str):
        """Broadcast message to all connections in a channel."""
        if channel in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[channel]:
                try:
                    await connection.send_text(message)
                except Exception:
                    disconnected.add(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.active_connections[channel].discard(conn)
    
    async def broadcast_to_all(self, message: str):
        """Broadcast message to all connected clients."""
        disconnected = set()
        for connection in self.active_connections.get("general", set()):
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.active_connections["general"].discard(conn)


manager = ConnectionManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for real-time updates."""
    channels = ["general", f"user_{user_id}"]
    
    # Subscribe to pub/sub events
    def on_stock_change(data):
        message = json.dumps({
            "type": "stock_change",
            "data": data,
            "timestamp": data.get("timestamp")
        })
        asyncio.create_task(manager.broadcast_to_channel(message, "stock_changes"))
    
    def on_inventory_update(data):
        message = json.dumps({
            "type": "inventory_update", 
            "data": data,
            "timestamp": data.get("timestamp")
        })
        asyncio.create_task(manager.broadcast_to_channel(message, "inventory"))
    
    def on_system_alert(data):
        message = json.dumps({
            "type": "system_alert",
            "data": data,
            "timestamp": data.get("timestamp")
        })
        asyncio.create_task(manager.broadcast_to_all(message))
    
    # Subscribe to events
    pubsub_manager.subscribe(EventType.STOCK_CHANGE, on_stock_change)
    pubsub_manager.subscribe(EventType.INVENTORY_UPDATE, on_inventory_update)
    pubsub_manager.subscribe(EventType.SYSTEM_ALERT, on_system_alert)
    
    try:
        await manager.connect(websocket, user_id, channels)
        
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "connection",
            "message": "Connected to WMS real-time updates",
            "user_id": user_id,
            "channels": channels
        }))
        
        # Keep connection alive
        while True:
            try:
                # Receive client messages (could be for subscription changes)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "subscribe":
                    # Handle dynamic subscription changes
                    new_channels = message.get("channels", [])
                    for channel in new_channels:
                        if channel not in channels:
                            channels.append(channel)
                            if channel not in manager.active_connections:
                                manager.active_connections[channel] = set()
                            manager.active_connections[channel].add(websocket)
                    
                    await websocket.send_text(json.dumps({
                        "type": "subscription_updated",
                        "channels": channels
                    }))
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error for user {user_id}: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, user_id)


@router.get("/ws-test", response_class=HTMLResponse)
async def websocket_test_page():
    """Simple WebSocket test page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WMS WebSocket Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .messages { 
                border: 1px solid #ccc; 
                height: 300px; 
                overflow-y: scroll; 
                padding: 10px; 
                margin: 10px 0;
                background-color: #f9f9f9;
            }
            .message { 
                margin: 5px 0; 
                padding: 5px;
                border-radius: 3px;
            }
            .stock-change { background-color: #e3f2fd; }
            .inventory-update { background-color: #f3e5f5; }
            .system-alert { background-color: #fff3e0; }
            .connection { background-color: #e8f5e8; }
        </style>
    </head>
    <body>
        <h1>WMS Real-time Updates Test</h1>
        <div>
            <label>User ID: </label>
            <input type="number" id="userId" value="1" min="1">
            <button onclick="connect()">Connect</button>
            <button onclick="disconnect()">Disconnect</button>
        </div>
        <div id="messages" class="messages"></div>
        <div>
            <input type="text" id="messageInput" placeholder="Type a message..." style="width: 300px;">
            <button onclick="sendMessage()">Send Test Message</button>
        </div>
        
        <script>
            let ws = null;
            let userId = 1;
            
            function connect() {
                userId = document.getElementById('userId').value;
                const wsUrl = `ws://localhost:8000/ws/v1/ws/${userId}`;
                
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function(event) {
                    addMessage('Connected to WebSocket', 'connection');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    addMessage(JSON.stringify(data, null, 2), data.type);
                };
                
                ws.onclose = function(event) {
                    addMessage('Disconnected from WebSocket', 'connection');
                };
                
                ws.onerror = function(error) {
                    addMessage('WebSocket Error: ' + error, 'error');
                };
            }
            
            function disconnect() {
                if (ws) {
                    ws.close();
                    ws = null;
                }
            }
            
            function sendMessage() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const message = document.getElementById('messageInput').value;
                    ws.send(message);
                    document.getElementById('messageInput').value = '';
                } else {
                    addMessage('WebSocket not connected', 'error');
                }
            }
            
            function addMessage(message, type = 'info') {
                const messages = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}`;
                messageDiv.innerHTML = `<strong>${new Date().toLocaleTimeString()}</strong><br>${message}`;
                messages.appendChild(messageDiv);
                messages.scrollTop = messages.scrollHeight;
            }
            
            // Auto-connect on page load
            window.onload = function() {
                connect();
            };
        </script>
    </body>
    </html>
    """
