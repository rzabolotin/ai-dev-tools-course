"""Integration tests for WebSocket endpoint.

These tests focus on WebSocket functionality without requiring database.
WebSocket endpoint doesn't need DB - it only manages in-memory connections.
"""
import pytest
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.testclient import TestClient
import uuid

from app.websocket_manager import ConnectionManager


# Create a minimal test app with just the WebSocket endpoint
# This avoids MySQL connection issues from the main app's lifespan
def create_test_app():
    """Create minimal FastAPI app for WebSocket testing."""
    test_app = FastAPI()
    test_manager = ConnectionManager()

    @test_app.websocket("/ws/{session_id}")
    async def websocket_endpoint(websocket: WebSocket, session_id: str, client_id: str = Query(None)):
        if not client_id:
            client_id = str(uuid.uuid4())

        await test_manager.connect(websocket, session_id, client_id)
        await websocket.send_json({"event": "connected", "clientId": client_id})

        try:
            while True:
                data = await websocket.receive_text()
        except WebSocketDisconnect:
            test_manager.disconnect(websocket, session_id)

    return test_app, test_manager


@pytest.fixture
def ws_app_and_manager():
    """Create test app and manager."""
    return create_test_app()


@pytest.fixture
def ws_test_client(ws_app_and_manager):
    """Create test client for WebSocket tests."""
    test_app, _ = ws_app_and_manager
    with TestClient(test_app) as client:
        yield client


@pytest.fixture
def ws_manager(ws_app_and_manager):
    """Get the connection manager for testing."""
    _, manager = ws_app_and_manager
    return manager


class TestWebSocketEndpoint:
    """Tests for WebSocket /ws/{session_id} endpoint."""

    def test_websocket_connect_sends_client_id(self, ws_test_client):
        """Test WebSocket connection sends client_id on connect."""
        with ws_test_client.websocket_connect("/ws/test-session") as websocket:
            data = websocket.receive_json()
            assert data["event"] == "connected"
            assert "clientId" in data
            assert len(data["clientId"]) > 0

    def test_websocket_connect_with_provided_client_id(self, ws_test_client):
        """Test WebSocket connection with provided client_id."""
        custom_client_id = "my-custom-client-id"
        with ws_test_client.websocket_connect(f"/ws/test-session?client_id={custom_client_id}") as websocket:
            data = websocket.receive_json()
            assert data["event"] == "connected"
            assert data["clientId"] == custom_client_id

    def test_websocket_connect_generates_uuid_if_no_client_id(self, ws_test_client):
        """Test WebSocket generates UUID if no client_id provided."""
        with ws_test_client.websocket_connect("/ws/test-session") as websocket:
            data = websocket.receive_json()
            # UUID format: 8-4-4-4-12 hex chars
            client_id = data["clientId"]
            assert len(client_id) == 36
            assert client_id.count("-") == 4

    def test_websocket_multiple_connections_same_session(self, ws_test_client):
        """Test multiple WebSocket connections to same session get different client_ids."""
        with ws_test_client.websocket_connect("/ws/multi-session") as ws1:
            data1 = ws1.receive_json()

            with ws_test_client.websocket_connect("/ws/multi-session") as ws2:
                data2 = ws2.receive_json()

                assert data1["clientId"] != data2["clientId"]

    def test_websocket_can_send_messages(self, ws_test_client):
        """Test WebSocket can send text messages."""
        with ws_test_client.websocket_connect("/ws/test-session") as websocket:
            data = websocket.receive_json()
            assert data["event"] == "connected"

            # Send a test message (the server just keeps connection alive)
            websocket.send_text("ping")

    def test_websocket_disconnect_graceful(self, ws_test_client):
        """Test WebSocket disconnects gracefully."""
        with ws_test_client.websocket_connect("/ws/test-session") as websocket:
            data = websocket.receive_json()
            assert data["event"] == "connected"
        # Context manager closes connection - should not raise


class TestWebSocketEdgeCases:
    """Edge case tests for WebSocket endpoint."""

    def test_websocket_any_session_id(self, ws_test_client):
        """Test WebSocket connection allows any session_id."""
        with ws_test_client.websocket_connect("/ws/any-random-id-12345") as websocket:
            data = websocket.receive_json()
            assert data["event"] == "connected"

    def test_websocket_special_chars_in_session_id(self, ws_test_client):
        """Test WebSocket with special characters in session_id."""
        with ws_test_client.websocket_connect("/ws/abc-123_XYZ") as websocket:
            data = websocket.receive_json()
            assert data["event"] == "connected"

    def test_websocket_long_client_id(self, ws_test_client):
        """Test WebSocket with very long client_id."""
        long_client_id = "a" * 500
        with ws_test_client.websocket_connect(f"/ws/session123?client_id={long_client_id}") as websocket:
            data = websocket.receive_json()
            assert data["clientId"] == long_client_id


class TestWebSocketConnectionLifecycle:
    """Tests for WebSocket connection lifecycle management."""

    def test_multiple_connect_disconnect_cycles(self, ws_test_client):
        """Test multiple connect/disconnect cycles."""
        for i in range(3):
            with ws_test_client.websocket_connect(f"/ws/lifecycle-test?client_id=client{i}") as websocket:
                data = websocket.receive_json()
                assert data["event"] == "connected"
                assert data["clientId"] == f"client{i}"

    def test_rapid_connect_disconnect(self, ws_test_client):
        """Test rapid connect/disconnect doesn't cause issues."""
        for _ in range(5):
            with ws_test_client.websocket_connect("/ws/rapid-test") as websocket:
                websocket.receive_json()


class TestConnectionManagerWithEndpoint:
    """Integration tests for ConnectionManager with WebSocket endpoint."""

    def test_connection_tracked_on_connect(self, ws_app_and_manager):
        """Test that connections are tracked in ConnectionManager."""
        test_app, manager = ws_app_and_manager

        with TestClient(test_app) as client:
            session_id = "tracked-session"
            with client.websocket_connect(f"/ws/{session_id}?client_id=test-client") as websocket:
                websocket.receive_json()
                # Connection should be tracked
                assert session_id in manager.active_connections
                assert len(manager.active_connections[session_id]) == 1

    def test_multiple_clients_in_session(self, ws_app_and_manager):
        """Test multiple clients can join same session."""
        test_app, manager = ws_app_and_manager

        with TestClient(test_app) as client:
            session_id = "multi-client-session"
            with client.websocket_connect(f"/ws/{session_id}?client_id=client1") as ws1:
                ws1.receive_json()

                with client.websocket_connect(f"/ws/{session_id}?client_id=client2") as ws2:
                    ws2.receive_json()

                    # Both connections should be tracked
                    assert session_id in manager.active_connections
                    assert len(manager.active_connections[session_id]) == 2

    def test_connection_present_while_connected(self, ws_app_and_manager):
        """Test that connection is present while client is connected."""
        test_app, manager = ws_app_and_manager

        with TestClient(test_app) as client:
            session_id = "cleanup-session"
            with client.websocket_connect(f"/ws/{session_id}?client_id=cleanup-client") as websocket:
                websocket.receive_json()
                # Connection should be present while connected
                assert session_id in manager.active_connections
                assert len(manager.active_connections[session_id]) == 1
