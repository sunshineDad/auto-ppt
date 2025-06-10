"""
WebSocket Manager for Real-time Communication
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Set
from fastapi import WebSocket
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Store connection info
        self.connection_info[websocket] = {
            'connected_at': datetime.utcnow(),
            'user_id': None,
            'session_id': None,
            'subscriptions': set()
        }
        
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message({
            'type': 'welcome',
            'message': 'Connected to AI-PPT System',
            'timestamp': datetime.utcnow().isoformat()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
        if websocket in self.connection_info:
            del self.connection_info[websocket]
            
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific WebSocket"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected WebSockets"""
        if not self.active_connections:
            return
            
        # Add timestamp if not present
        if 'timestamp' not in message:
            message['timestamp'] = datetime.utcnow().isoformat()
        
        message_text = json.dumps(message)
        
        # Send to all connections
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.error(f"Failed to broadcast to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_to_user(self, message: Dict[str, Any], user_id: str):
        """Broadcast a message to all connections for a specific user"""
        user_connections = [
            ws for ws, info in self.connection_info.items()
            if info.get('user_id') == user_id
        ]
        
        if not user_connections:
            return
        
        message_text = json.dumps(message)
        
        for connection in user_connections:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.error(f"Failed to send to user {user_id}: {e}")
                self.disconnect(connection)
    
    async def broadcast_to_session(self, message: Dict[str, Any], session_id: str):
        """Broadcast a message to all connections for a specific session"""
        session_connections = [
            ws for ws, info in self.connection_info.items()
            if info.get('session_id') == session_id
        ]
        
        if not session_connections:
            return
        
        message_text = json.dumps(message)
        
        for connection in session_connections:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.error(f"Failed to send to session {session_id}: {e}")
                self.disconnect(connection)
    
    def set_user_info(self, websocket: WebSocket, user_id: str, session_id: str = None):
        """Set user information for a WebSocket connection"""
        if websocket in self.connection_info:
            self.connection_info[websocket]['user_id'] = user_id
            if session_id:
                self.connection_info[websocket]['session_id'] = session_id
    
    def subscribe_to_events(self, websocket: WebSocket, events: List[str]):
        """Subscribe a WebSocket to specific events"""
        if websocket in self.connection_info:
            self.connection_info[websocket]['subscriptions'].update(events)
    
    def unsubscribe_from_events(self, websocket: WebSocket, events: List[str]):
        """Unsubscribe a WebSocket from specific events"""
        if websocket in self.connection_info:
            self.connection_info[websocket]['subscriptions'].difference_update(events)
    
    async def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast an event to subscribed connections"""
        message = {
            'type': 'event',
            'event_type': event_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Find connections subscribed to this event
        subscribed_connections = [
            ws for ws, info in self.connection_info.items()
            if event_type in info.get('subscriptions', set())
        ]
        
        if not subscribed_connections:
            # If no specific subscriptions, broadcast to all
            await self.broadcast(message)
            return
        
        message_text = json.dumps(message)
        
        for connection in subscribed_connections:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.error(f"Failed to broadcast event {event_type}: {e}")
                self.disconnect(connection)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        total_connections = len(self.active_connections)
        unique_users = len(set(
            info.get('user_id') for info in self.connection_info.values()
            if info.get('user_id')
        ))
        unique_sessions = len(set(
            info.get('session_id') for info in self.connection_info.values()
            if info.get('session_id')
        ))
        
        return {
            'total_connections': total_connections,
            'unique_users': unique_users,
            'unique_sessions': unique_sessions,
            'average_connections_per_user': unique_users and total_connections / unique_users or 0
        }
    
    async def send_ai_prediction(self, prediction: Dict[str, Any], user_id: str = None):
        """Send AI prediction to relevant connections"""
        message = {
            'type': 'ai_prediction',
            'prediction': prediction,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if user_id:
            await self.broadcast_to_user(message, user_id)
        else:
            await self.broadcast_event('ai_prediction', prediction)
    
    async def send_operation_update(self, operation: Dict[str, Any], session_id: str = None):
        """Send operation update to relevant connections"""
        message = {
            'type': 'operation_update',
            'operation': operation,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if session_id:
            await self.broadcast_to_session(message, session_id)
        else:
            await self.broadcast_event('operation_update', operation)
    
    async def send_presentation_sync(self, presentation_data: Dict[str, Any], session_id: str):
        """Send presentation synchronization data"""
        message = {
            'type': 'presentation_sync',
            'presentation': presentation_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.broadcast_to_session(message, session_id)
    
    async def send_system_notification(self, notification: Dict[str, Any]):
        """Send system-wide notification"""
        message = {
            'type': 'system_notification',
            'notification': notification,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        await self.broadcast(message)
    
    async def handle_ping(self, websocket: WebSocket):
        """Handle ping message"""
        await self.send_personal_message({
            'type': 'pong',
            'timestamp': datetime.utcnow().isoformat()
        }, websocket)
    
    async def cleanup_stale_connections(self):
        """Clean up stale connections (run periodically)"""
        current_time = datetime.utcnow()
        stale_connections = []
        
        for websocket, info in self.connection_info.items():
            # Consider connections older than 1 hour as potentially stale
            if (current_time - info['connected_at']).total_seconds() > 3600:
                try:
                    # Try to send a ping to check if connection is alive
                    await self.send_personal_message({
                        'type': 'ping',
                        'timestamp': current_time.isoformat()
                    }, websocket)
                except:
                    stale_connections.append(websocket)
        
        # Remove stale connections
        for websocket in stale_connections:
            self.disconnect(websocket)
        
        if stale_connections:
            logger.info(f"Cleaned up {len(stale_connections)} stale connections")

# Global WebSocket manager instance
websocket_manager = WebSocketManager()

# Periodic cleanup task
async def periodic_cleanup():
    """Periodic cleanup of stale connections"""
    while True:
        try:
            await asyncio.sleep(300)  # Run every 5 minutes
            await websocket_manager.cleanup_stale_connections()
        except Exception as e:
            logger.error(f"Periodic cleanup failed: {e}")

# Function to start cleanup task when event loop is running
def start_cleanup_task():
    """Start the cleanup task when event loop is available"""
    try:
        asyncio.create_task(periodic_cleanup())
    except RuntimeError:
        # No event loop running, will be started later
        pass