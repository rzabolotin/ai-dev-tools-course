"""Unit tests for WebSocket ConnectionManager."""
import pytest
from unittest.mock import AsyncMock, MagicMock
import json

from app.websocket_manager import ConnectionManager


class TestConnectionManager:
    """Tests for ConnectionManager class."""

    @pytest.fixture
    def manager(self):
        """Create a fresh ConnectionManager instance."""
        return ConnectionManager()

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket."""
        ws = AsyncMock()
        ws.accept = AsyncMock()
        ws.send_text = AsyncMock()
        return ws

    @pytest.fixture
    def mock_websocket_factory(self):
        """Factory for creating multiple mock WebSockets."""
        def create():
            ws = AsyncMock()
            ws.accept = AsyncMock()
            ws.send_text = AsyncMock()
            return ws
        return create


class TestConnect(TestConnectionManager):
    """Tests for connect method."""

    async def test_connect_accepts_websocket(self, manager, mock_websocket):
        """Test that connect accepts the websocket."""
        await manager.connect(mock_websocket, "session1", "client1")
        mock_websocket.accept.assert_called_once()

    async def test_connect_creates_session_entry(self, manager, mock_websocket):
        """Test that connect creates a new session entry."""
        await manager.connect(mock_websocket, "session1", "client1")
        assert "session1" in manager.active_connections

    async def test_connect_stores_websocket_and_client_id(self, manager, mock_websocket):
        """Test that websocket and client_id are stored together."""
        await manager.connect(mock_websocket, "session1", "client1")
        connections = manager.active_connections["session1"]
        assert len(connections) == 1
        assert connections[0] == (mock_websocket, "client1")

    async def test_connect_multiple_clients_same_session(self, manager, mock_websocket_factory):
        """Test multiple clients can join the same session."""
        ws1 = mock_websocket_factory()
        ws2 = mock_websocket_factory()
        ws3 = mock_websocket_factory()

        await manager.connect(ws1, "session1", "client1")
        await manager.connect(ws2, "session1", "client2")
        await manager.connect(ws3, "session1", "client3")

        assert len(manager.active_connections["session1"]) == 3

    async def test_connect_different_sessions(self, manager, mock_websocket_factory):
        """Test clients can join different sessions."""
        ws1 = mock_websocket_factory()
        ws2 = mock_websocket_factory()

        await manager.connect(ws1, "session1", "client1")
        await manager.connect(ws2, "session2", "client2")

        assert "session1" in manager.active_connections
        assert "session2" in manager.active_connections
        assert len(manager.active_connections["session1"]) == 1
        assert len(manager.active_connections["session2"]) == 1


class TestDisconnect(TestConnectionManager):
    """Tests for disconnect method."""

    async def test_disconnect_removes_websocket(self, manager, mock_websocket):
        """Test that disconnect removes the websocket."""
        await manager.connect(mock_websocket, "session1", "client1")
        manager.disconnect(mock_websocket, "session1")
        assert len(manager.active_connections.get("session1", [])) == 0

    async def test_disconnect_removes_empty_session(self, manager, mock_websocket):
        """Test that empty session is removed from dict."""
        await manager.connect(mock_websocket, "session1", "client1")
        manager.disconnect(mock_websocket, "session1")
        assert "session1" not in manager.active_connections

    async def test_disconnect_keeps_other_clients(self, manager, mock_websocket_factory):
        """Test that other clients remain connected after one disconnects."""
        ws1 = mock_websocket_factory()
        ws2 = mock_websocket_factory()

        await manager.connect(ws1, "session1", "client1")
        await manager.connect(ws2, "session1", "client2")

        manager.disconnect(ws1, "session1")

        assert len(manager.active_connections["session1"]) == 1
        assert manager.active_connections["session1"][0] == (ws2, "client2")

    async def test_disconnect_nonexistent_session(self, manager, mock_websocket):
        """Test disconnect with nonexistent session doesn't raise."""
        manager.disconnect(mock_websocket, "nonexistent")
        # Should not raise an exception

    async def test_disconnect_wrong_websocket(self, manager, mock_websocket_factory):
        """Test disconnect with wrong websocket doesn't remove others."""
        ws1 = mock_websocket_factory()
        ws2 = mock_websocket_factory()

        await manager.connect(ws1, "session1", "client1")
        manager.disconnect(ws2, "session1")

        assert len(manager.active_connections["session1"]) == 1


class TestBroadcastToSession(TestConnectionManager):
    """Tests for broadcast_to_session method."""

    async def test_broadcast_sends_to_all_clients(self, manager, mock_websocket_factory):
        """Test broadcast sends message to all clients in session."""
        ws1 = mock_websocket_factory()
        ws2 = mock_websocket_factory()
        ws3 = mock_websocket_factory()

        await manager.connect(ws1, "session1", "client1")
        await manager.connect(ws2, "session1", "client2")
        await manager.connect(ws3, "session1", "client3")

        message = {"event": "test", "data": "hello"}
        await manager.broadcast_to_session("session1", message)

        expected_json = json.dumps(message)
        ws1.send_text.assert_called_once_with(expected_json)
        ws2.send_text.assert_called_once_with(expected_json)
        ws3.send_text.assert_called_once_with(expected_json)

    async def test_broadcast_excludes_client(self, manager, mock_websocket_factory):
        """Test broadcast excludes specified client."""
        ws1 = mock_websocket_factory()
        ws2 = mock_websocket_factory()
        ws3 = mock_websocket_factory()

        await manager.connect(ws1, "session1", "client1")
        await manager.connect(ws2, "session1", "client2")
        await manager.connect(ws3, "session1", "client3")

        message = {"event": "test", "data": "hello"}
        await manager.broadcast_to_session("session1", message, exclude_client_id="client2")

        expected_json = json.dumps(message)
        ws1.send_text.assert_called_once_with(expected_json)
        ws2.send_text.assert_not_called()
        ws3.send_text.assert_called_once_with(expected_json)

    async def test_broadcast_nonexistent_session(self, manager):
        """Test broadcast to nonexistent session doesn't raise."""
        message = {"event": "test"}
        await manager.broadcast_to_session("nonexistent", message)
        # Should not raise an exception

    async def test_broadcast_only_to_session(self, manager, mock_websocket_factory):
        """Test broadcast only goes to specified session."""
        ws1 = mock_websocket_factory()
        ws2 = mock_websocket_factory()

        await manager.connect(ws1, "session1", "client1")
        await manager.connect(ws2, "session2", "client2")

        message = {"event": "test"}
        await manager.broadcast_to_session("session1", message)

        ws1.send_text.assert_called_once()
        ws2.send_text.assert_not_called()

    async def test_broadcast_handles_send_failure(self, manager, mock_websocket_factory):
        """Test broadcast handles send failure gracefully."""
        ws1 = mock_websocket_factory()
        ws2 = mock_websocket_factory()

        ws1.send_text.side_effect = Exception("Connection closed")

        await manager.connect(ws1, "session1", "client1")
        await manager.connect(ws2, "session1", "client2")

        message = {"event": "test"}
        await manager.broadcast_to_session("session1", message)

        # ws2 should still receive the message
        ws2.send_text.assert_called_once()

    async def test_broadcast_removes_failed_connection(self, manager, mock_websocket_factory):
        """Test broadcast removes connection that failed to send."""
        ws1 = mock_websocket_factory()
        ws2 = mock_websocket_factory()

        ws1.send_text.side_effect = Exception("Connection closed")

        await manager.connect(ws1, "session1", "client1")
        await manager.connect(ws2, "session1", "client2")

        message = {"event": "test"}
        await manager.broadcast_to_session("session1", message)

        # ws1 should be removed from connections
        connections = manager.active_connections["session1"]
        assert len(connections) == 1
        assert connections[0] == (ws2, "client2")


class TestManagerSingleton:
    """Tests for manager singleton instance."""

    def test_manager_instance_exists(self):
        """Test that singleton manager instance exists."""
        from app.websocket_manager import manager
        assert manager is not None
        assert isinstance(manager, ConnectionManager)

    def test_manager_has_empty_connections_initially(self):
        """Test that manager starts with empty connections (after import)."""
        # Note: This test may fail if other tests modified the singleton
        # In a real app, you might want to reset the manager between tests
        manager = ConnectionManager()
        assert manager.active_connections == {}
