"""Redis-based session management for WMS."""

import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from app.shared.core.redis import redis_manager
from app.shared.core.settings import settings
from app.shared.core.logging import get_logger

logger = get_logger(__name__)


class SessionManager:
    """Manages user sessions using Redis."""
    
    def __init__(self):
        self.session_prefix = "session:"
        self.user_sessions_prefix = "user_sessions:"
        self.default_ttl = settings.access_token_expire_minutes * 60  # Convert to seconds
    
    async def create_session(
        self, 
        user_id: int, 
        user_data: Dict[str, Any],
        session_id: Optional[str] = None,
        ttl: Optional[int] = None
    ) -> str:
        """Create a new session for user."""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        session_key = f"{self.session_prefix}{session_id}"
        user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
        
        # Session data
        session_data = {
            "user_id": user_id,
            "session_id": session_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_accessed": datetime.now(timezone.utc).isoformat(),
            "user_data": user_data,
            "ip_address": user_data.get("ip_address"),
            "user_agent": user_data.get("user_agent"),
        }
        
        # Store session data
        session_ttl = ttl or self.default_ttl
        await redis_manager.set(session_key, session_data, ex=session_ttl)
        
        # Add session to user's session list
        await redis_manager.client.sadd(user_sessions_key, session_id)
        await redis_manager.expire(user_sessions_key, session_ttl)
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by session ID."""
        session_key = f"{self.session_prefix}{session_id}"
        session_data = await redis_manager.get(session_key)
        
        if session_data is None:
            return None
        
        # Update last accessed time
        if isinstance(session_data, str):
            session_data = json.loads(session_data)
        
        session_data["last_accessed"] = datetime.now(timezone.utc).isoformat()
        await redis_manager.set(session_key, session_data, ex=self.default_ttl)
        
        return session_data
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data."""
        session_key = f"{self.session_prefix}{session_id}"
        session_data = await redis_manager.get(session_key)
        
        if session_data is None:
            return False
        
        if isinstance(session_data, str):
            session_data = json.loads(session_data)
        
        # Update session data
        session_data.update(updates)
        session_data["last_accessed"] = datetime.now(timezone.utc).isoformat()
        
        await redis_manager.set(session_key, session_data, ex=self.default_ttl)
        logger.debug(f"Updated session {session_id}")
        return True
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        session_key = f"{self.session_prefix}{session_id}"
        session_data = await redis_manager.get(session_key)
        
        if session_data is None:
            return False
        
        if isinstance(session_data, str):
            session_data = json.loads(session_data)
        
        user_id = session_data.get("user_id")
        
        # Remove session
        await redis_manager.delete(session_key)
        
        # Remove from user's session list
        if user_id:
            user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
            await redis_manager.client.srem(user_sessions_key, session_id)
        
        logger.info(f"Deleted session {session_id} for user {user_id}")
        return True
    
    async def get_user_sessions(self, user_id: int) -> list:
        """Get all active sessions for a user."""
        user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
        session_ids = await redis_manager.client.smembers(user_sessions_key)
        
        sessions = []
        for session_id in session_ids:
            if isinstance(session_id, bytes):
                session_id = session_id.decode('utf-8')
            session_data = await self.get_session(session_id)
            if session_data:
                sessions.append(session_data)
        
        return sessions
    
    async def revoke_user_sessions(self, user_id: int, except_session: Optional[str] = None) -> int:
        """Revoke all sessions for a user except optionally one session."""
        user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
        session_ids = await redis_manager.client.smembers(user_sessions_key)
        
        revoked_count = 0
        for session_id in session_ids:
            if isinstance(session_id, bytes):
                session_id = session_id.decode('utf-8')
            
            if except_session and session_id == except_session:
                continue
            
            await self.delete_session(session_id)
            revoked_count += 1
        
        logger.info(f"Revoked {revoked_count} sessions for user {user_id}")
        return revoked_count
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions (maintenance task)."""
        # This would typically be run as a background task
        # For now, we rely on Redis TTL for automatic cleanup
        logger.debug("Session cleanup relies on Redis TTL")
        return 0
    
    async def extend_session(self, session_id: str, additional_seconds: int = None) -> bool:
        """Extend session TTL."""
        session_key = f"{self.session_prefix}{session_id}"
        exists = await redis_manager.exists(session_key)
        
        if not exists:
            return False
        
        ttl = additional_seconds or self.default_ttl
        await redis_manager.expire(session_key, ttl)
        
        # Also update last accessed time
        await self.update_session(session_id, {"last_accessed": datetime.now(timezone.utc).isoformat()})
        
        logger.debug(f"Extended session {session_id} by {ttl} seconds")
        return True
    
    async def is_session_valid(self, session_id: str) -> bool:
        """Check if session is valid and not expired."""
        session_data = await self.get_session(session_id)
        return session_data is not None
    
    async def get_active_session_count(self) -> int:
        """Get count of active sessions (for monitoring)."""
        try:
            # This is a rough estimate - counts all session keys
            cursor = 0
            count = 0
            pattern = f"{self.session_prefix}*"
            
            while True:
                cursor, keys = await redis_manager.client.scan(
                    cursor, match=pattern, count=100
                )
                count += len(keys)
                
                if cursor == 0:
                    break
            
            return count
        except Exception as e:
            logger.error(f"Error counting active sessions: {e}")
            return 0


# Global session manager instance
session_manager = SessionManager()
