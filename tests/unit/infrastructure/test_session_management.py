"""Tests for Redis session management."""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.shared.core.session import SessionManager, session_manager
from app.shared.core.settings import settings


class TestSessionManager:
    """Test cases for SessionManager."""
    
    @pytest.fixture
    def mock_redis_manager(self):
        """Mock redis manager."""
        mock_manager = AsyncMock()
        mock_manager.get.return_value = None
        mock_manager.set.return_value = True
        mock_manager.delete.return_value = True
        mock_manager.exists.return_value = True
        mock_manager.expire.return_value = True
        mock_manager.client.sadd.return_value = 1
        mock_manager.client.srem.return_value = 1
        mock_manager.client.smembers.return_value = set()
        mock_manager.client.scan.return_value = (0, [])
        return mock_manager
    
    @pytest.fixture
    def setup_redis_mock(self, mock_redis_manager):
        """Setup redis manager mock."""
        with patch('app.shared.core.session.redis_manager', mock_redis_manager):
            yield mock_redis_manager
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings."""
        mock_settings = MagicMock()
        mock_settings.access_token_expire_minutes = 60
        return mock_settings
    
    @pytest.fixture
    def setup_settings_mock(self, mock_settings):
        """Setup settings mock."""
        with patch('app.shared.core.session.settings', mock_settings):
            yield mock_settings
    
    @pytest.mark.asyncio
    async def test_create_session_success(self, setup_redis_mock, setup_settings_mock):
        """Test successful session creation."""
        mock_manager = setup_redis_mock
        mock_settings = setup_settings_mock
        
        manager = SessionManager()
        user_data = {
            "email": "test@example.com",
            "role": "user",
            "ip_address": "127.0.0.1",
            "user_agent": "Mozilla/5.0"
        }
        
        session_id = await manager.create_session(1, user_data)
        
        assert session_id is not None
        assert len(session_id) > 0
        
        # Check session data was stored
        mock_manager.set.assert_called_once()
        call_args = mock_manager.set.call_args
        assert call_args[0][0].startswith("session:")
        assert call_args[0][1]["user_id"] == 1
        assert call_args[0][1]["user_data"]["email"] == "test@example.com"
        assert call_args[1]["ex"] == 3600  # 60 minutes * 60 seconds
        
        # Check session was added to user's session list
        mock_manager.client.sadd.assert_called_once()
        assert mock_manager.client.sadd.call_args[0][0] == "user_sessions:1"
        assert session_id in mock_manager.client.sadd.call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_create_session_with_custom_id(self, setup_redis_mock, setup_settings_mock):
        """Test session creation with custom session ID."""
        mock_manager = setup_redis_mock
        custom_session_id = "custom-session-123"
        
        manager = SessionManager()
        user_data = {"email": "test@example.com"}
        
        session_id = await manager.create_session(1, user_data, session_id=custom_session_id)
        
        assert session_id == custom_session_id
        call_args = mock_manager.set.call_args
        assert call_args[0][0] == f"session:{custom_session_id}"
        assert call_args[0][1]["session_id"] == custom_session_id
    
    @pytest.mark.asyncio
    async def test_create_session_with_custom_ttl(self, setup_redis_mock, setup_settings_mock):
        """Test session creation with custom TTL."""
        mock_manager = setup_redis_mock
        
        manager = SessionManager()
        user_data = {"email": "test@example.com"}
        
        session_id = await manager.create_session(1, user_data, ttl=7200)
        
        call_args = mock_manager.set.call_args
        assert call_args[1]["ex"] == 7200
    
    @pytest.mark.asyncio
    async def test_get_session_success(self, setup_redis_mock):
        """Test successful session retrieval."""
        mock_manager = setup_redis_mock
        session_data = {
            "user_id": 1,
            "session_id": "test-session",
            "created_at": "2023-01-01T00:00:00",
            "last_accessed": "2023-01-01T00:30:00",
            "user_data": {"email": "test@example.com"}
        }
        mock_manager.get.return_value = json.dumps(session_data)
        
        manager = SessionManager()
        result = await manager.get_session("test-session")
        
        assert result is not None
        assert result["user_id"] == 1
        assert result["session_id"] == "test-session"
        assert result["user_data"]["email"] == "test@example.com"
        
        # Check last_accessed was updated
        mock_manager.set.assert_called_once()
        call_args = mock_manager.set.call_args
        updated_session = call_args[0][1]
        assert updated_session["last_accessed"] != "2023-01-01T00:30:00"
    
    @pytest.mark.asyncio
    async def test_get_session_not_found(self, setup_redis_mock):
        """Test getting non-existent session."""
        mock_manager = setup_redis_mock
        mock_manager.get.return_value = None
        
        manager = SessionManager()
        result = await manager.get_session("nonexistent-session")
        
        assert result is None
        mock_manager.set.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_session_with_bytes_response(self, setup_redis_mock):
        """Test getting session when Redis returns bytes."""
        mock_manager = setup_redis_mock
        session_data = {"user_id": 1, "session_id": "test-session"}
        mock_manager.get.return_value = json.dumps(session_data)
        
        manager = SessionManager()
        result = await manager.get_session("test-session")
        
        assert result is not None
        assert result["user_id"] == 1
    
    @pytest.mark.asyncio
    async def test_update_session_success(self, setup_redis_mock):
        """Test successful session update."""
        mock_manager = setup_redis_mock
        session_data = {"user_id": 1, "session_id": "test-session"}
        mock_manager.get.return_value = json.dumps(session_data)
        
        manager = SessionManager()
        updates = {"last_activity": "login", "ip_address": "192.168.1.1"}
        
        result = await manager.update_session("test-session", updates)
        
        assert result is True
        
        # Check session was updated
        mock_manager.set.assert_called_once()
        call_args = mock_manager.set.call_args
        updated_session = call_args[0][1]
        assert updated_session["last_activity"] == "login"
        assert updated_session["ip_address"] == "192.168.1.1"
        assert "last_accessed" in updated_session
    
    @pytest.mark.asyncio
    async def test_update_session_not_found(self, setup_redis_mock):
        """Test updating non-existent session."""
        mock_manager = setup_redis_mock
        mock_manager.get.return_value = None
        
        manager = SessionManager()
        result = await manager.update_session("nonexistent-session", {"test": "data"})
        
        assert result is False
        mock_manager.set.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_delete_session_success(self, setup_redis_mock):
        """Test successful session deletion."""
        mock_manager = setup_redis_mock
        session_data = {"user_id": 1, "session_id": "test-session"}
        mock_manager.get.return_value = json.dumps(session_data)
        
        manager = SessionManager()
        result = await manager.delete_session("test-session")
        
        assert result is True
        
        # Check session was deleted
        mock_manager.delete.assert_called_once_with("session:test-session")
        
        # Check session was removed from user's session list
        mock_manager.client.srem.assert_called_once_with("user_sessions:1", "test-session")
    
    @pytest.mark.asyncio
    async def test_delete_session_not_found(self, setup_redis_mock):
        """Test deleting non-existent session."""
        mock_manager = setup_redis_mock
        mock_manager.get.return_value = None
        
        manager = SessionManager()
        result = await manager.delete_session("nonexistent-session")
        
        assert result is False
        mock_manager.delete.assert_not_called()
        mock_manager.client.srem.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_user_sessions_empty(self, setup_redis_mock):
        """Test getting user sessions when none exist."""
        mock_manager = setup_redis_mock
        mock_manager.client.smembers.return_value = set()
        
        manager = SessionManager()
        sessions = await manager.get_user_sessions(1)
        
        assert sessions == []
        mock_manager.client.smembers.assert_called_once_with("user_sessions:1")
    
    @pytest.mark.asyncio
    async def test_get_user_sessions_with_sessions(self, setup_redis_mock):
        """Test getting user sessions with existing sessions."""
        mock_manager = setup_redis_mock
        session_ids = {"session1", "session2"}
        mock_manager.client.smembers.return_value = session_ids
        
        # Mock session data
        session1_data = {"user_id": 1, "session_id": "session1"}
        session2_data = {"user_id": 1, "session_id": "session2"}
        
        def mock_get(session_key):
            if "session1" in session_key:
                return json.dumps(session1_data)
            elif "session2" in session_key:
                return json.dumps(session2_data)
            return None
        
        mock_manager.get.side_effect = mock_get
        
        manager = SessionManager()
        sessions = await manager.get_user_sessions(1)
        
        assert len(sessions) == 2
        session_ids = {session["session_id"] for session in sessions}
        assert "session1" in session_ids
        assert "session2" in session_ids
    
    @pytest.mark.asyncio
    async def test_get_user_sessions_with_bytes(self, setup_redis_mock):
        """Test getting user sessions when Redis returns bytes."""
        mock_manager = setup_redis_mock
        session_ids = {b"session1", b"session2"}
        mock_manager.client.smembers.return_value = session_ids
        
        session_data = {"user_id": 1, "session_id": "session1"}
        mock_manager.get.return_value = json.dumps(session_data)
        
        manager = SessionManager()
        sessions = await manager.get_user_sessions(1)
        
        assert len(sessions) == 2
    
    @pytest.mark.asyncio
    async def test_revoke_user_sessions_all(self, setup_redis_mock):
        """Test revoking all user sessions."""
        mock_manager = setup_redis_mock
        session_ids = {"session1", "session2", "session3"}
        mock_manager.client.smembers.return_value = session_ids
        
        # Mock session data for get calls
        session_data = {"user_id": 1, "session_id": "test"}
        def mock_get(session_key):
            if any(session in session_key for session in session_ids):
                return json.dumps(session_data)
            return None
        
        mock_manager.get.side_effect = mock_get
        
        manager = SessionManager()
        revoked_count = await manager.revoke_user_sessions(1)
        
        assert revoked_count == 3
        assert mock_manager.delete.call_count == 3
        assert mock_manager.client.srem.call_count == 3
    
    @pytest.mark.asyncio
    async def test_revoke_user_sessions_except_one(self, setup_redis_mock):
        """Test revoking user sessions except one."""
        mock_manager = setup_redis_mock
        session_ids = {"session1", "session2", "session3"}
        mock_manager.client.smembers.return_value = session_ids
        
        # Mock session data for get calls
        session_data = {"user_id": 1, "session_id": "test"}
        def mock_get(session_key):
            if "session1" in session_key or "session3" in session_key:
                return json.dumps(session_data)
            elif "session2" in session_key:
                return json.dumps(session_data)
            return None
        
        mock_manager.get.side_effect = mock_get
        
        manager = SessionManager()
        revoked_count = await manager.revoke_user_sessions(1, except_session="session2")
        
        assert revoked_count == 2
        assert mock_manager.delete.call_count == 2
        
        # Check that session2 was not deleted
        deleted_keys = [call[0][0] for call in mock_manager.delete.call_args_list]
        assert "session:session2" not in deleted_keys
    
    @pytest.mark.asyncio
    async def test_extend_session_success(self, setup_redis_mock):
        """Test successful session extension."""
        mock_manager = setup_redis_mock
        mock_manager.exists.return_value = True
        
        # Mock session data for get calls
        session_data = {"user_id": 1, "session_id": "test-session"}
        mock_manager.get.return_value = json.dumps(session_data)
        
        manager = SessionManager()
        result = await manager.extend_session("test-session", 1800)
        
        assert result is True
        mock_manager.expire.assert_called_once_with("session:test-session", 1800)
        mock_manager.set.assert_called_once()  # For updating last_accessed
    
    @pytest.mark.asyncio
    async def test_extend_session_not_found(self, setup_redis_mock):
        """Test extending non-existent session."""
        mock_manager = setup_redis_mock
        mock_manager.exists.return_value = False
        
        manager = SessionManager()
        result = await manager.extend_session("nonexistent-session")
        
        assert result is False
        mock_manager.expire.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_is_session_valid_true(self, setup_redis_mock):
        """Test session validation when session is valid."""
        mock_manager = setup_redis_mock
        session_data = {"user_id": 1}
        mock_manager.get.return_value = json.dumps(session_data)
        
        manager = SessionManager()
        result = await manager.is_session_valid("test-session")
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_is_session_valid_false(self, setup_redis_mock):
        """Test session validation when session is invalid."""
        mock_manager = setup_redis_mock
        mock_manager.get.return_value = None
        
        manager = SessionManager()
        result = await manager.is_session_valid("test-session")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_active_session_count(self, setup_redis_mock):
        """Test getting active session count."""
        mock_manager = setup_redis_mock
        mock_manager.client.scan.side_effect = [
            (1, ["session:abc", "session:def"]),
            (0, [])
        ]
        
        manager = SessionManager()
        count = await manager.get_active_session_count()
        
        assert count == 2
        assert mock_manager.client.scan.call_count == 2
    
    @pytest.mark.asyncio
    async def test_get_active_session_count_error(self, setup_redis_mock):
        """Test getting active session count with error."""
        mock_manager = setup_redis_mock
        mock_manager.client.scan.side_effect = Exception("Redis error")
        
        manager = SessionManager()
        count = await manager.get_active_session_count()
        
        assert count == 0
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self, setup_redis_mock):
        """Test cleanup of expired sessions."""
        mock_manager = setup_redis_mock
        
        manager = SessionManager()
        count = await manager.cleanup_expired_sessions()
        
        assert count == 0
        # Cleanup relies on Redis TTL, so no explicit calls expected
