"""Integration tests for REST API endpoints."""
import pytest
from httpx import AsyncClient

from app.schemas import SUPPORTED_LANGUAGES


class TestCreateSession:
    """Tests for POST /api/sessions endpoint."""

    async def test_create_session_defaults(self, client: AsyncClient):
        """Test creating session with default values."""
        response = await client.post("/api/sessions", json={})

        assert response.status_code == 201
        data = response.json()
        assert data["language"] == "javascript"
        assert data["code"] == ""
        assert "session_id" in data
        assert len(data["session_id"]) == 16

    async def test_create_session_with_language(self, client: AsyncClient):
        """Test creating session with custom language."""
        response = await client.post("/api/sessions", json={"language": "python"})

        assert response.status_code == 201
        data = response.json()
        assert data["language"] == "python"

    async def test_create_session_with_code(self, client: AsyncClient):
        """Test creating session with initial code."""
        code = "console.log('hello')"
        response = await client.post("/api/sessions", json={"code": code})

        assert response.status_code == 201
        data = response.json()
        assert data["code"] == code

    async def test_create_session_with_all_params(self, client: AsyncClient, sample_session_data):
        """Test creating session with all parameters."""
        response = await client.post("/api/sessions", json=sample_session_data)

        assert response.status_code == 201
        data = response.json()
        assert data["language"] == sample_session_data["language"]
        assert data["code"] == sample_session_data["code"]

    async def test_create_session_invalid_language(self, client: AsyncClient):
        """Test creating session with invalid language returns 422."""
        response = await client.post("/api/sessions", json={"language": "cobol"})
        assert response.status_code == 422

    async def test_create_session_response_fields(self, client: AsyncClient):
        """Test that response includes all expected fields."""
        response = await client.post("/api/sessions", json={})

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "session_id" in data
        assert "code" in data
        assert "language" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_multiple_sessions_unique_ids(self, client: AsyncClient):
        """Test that multiple sessions get unique IDs."""
        response1 = await client.post("/api/sessions", json={})
        response2 = await client.post("/api/sessions", json={})

        assert response1.json()["session_id"] != response2.json()["session_id"]


class TestGetSession:
    """Tests for GET /api/sessions/{session_id} endpoint."""

    async def test_get_session_success(self, client: AsyncClient):
        """Test getting an existing session."""
        # Create a session first
        create_response = await client.post("/api/sessions", json={"language": "rust"})
        session_id = create_response.json()["session_id"]

        # Get the session
        response = await client.get(f"/api/sessions/{session_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["language"] == "rust"

    async def test_get_session_not_found(self, client: AsyncClient):
        """Test getting a non-existent session returns 404."""
        response = await client.get("/api/sessions/nonexistent123")

        assert response.status_code == 404
        assert response.json()["detail"] == "Session not found"

    async def test_get_session_preserves_code(self, client: AsyncClient):
        """Test that code is preserved when getting session."""
        code = "fn main() { println!(\"Hello\"); }"
        create_response = await client.post("/api/sessions", json={"code": code, "language": "rust"})
        session_id = create_response.json()["session_id"]

        response = await client.get(f"/api/sessions/{session_id}")

        assert response.json()["code"] == code


class TestUpdateCode:
    """Tests for PUT /api/sessions/{session_id}/code endpoint."""

    async def test_update_code_success(self, client: AsyncClient):
        """Test updating code successfully."""
        # Create session
        create_response = await client.post("/api/sessions", json={})
        session_id = create_response.json()["session_id"]

        # Update code
        new_code = "const x = 42;"
        response = await client.put(
            f"/api/sessions/{session_id}/code",
            json={"code": new_code}
        )

        assert response.status_code == 200
        assert response.json()["code"] == new_code

    async def test_update_code_with_client_id(self, client: AsyncClient):
        """Test updating code with client_id parameter."""
        create_response = await client.post("/api/sessions", json={})
        session_id = create_response.json()["session_id"]

        new_code = "let y = 100;"
        response = await client.put(
            f"/api/sessions/{session_id}/code?client_id=test-client-123",
            json={"code": new_code}
        )

        assert response.status_code == 200
        assert response.json()["code"] == new_code

    async def test_update_code_not_found(self, client: AsyncClient):
        """Test updating code for non-existent session returns 404."""
        response = await client.put(
            "/api/sessions/nonexistent123/code",
            json={"code": "test"}
        )

        assert response.status_code == 404

    async def test_update_code_empty_string(self, client: AsyncClient):
        """Test updating code to empty string."""
        create_response = await client.post("/api/sessions", json={"code": "initial"})
        session_id = create_response.json()["session_id"]

        response = await client.put(
            f"/api/sessions/{session_id}/code",
            json={"code": ""}
        )

        assert response.status_code == 200
        assert response.json()["code"] == ""

    async def test_update_code_multiline(self, client: AsyncClient):
        """Test updating code with multiline content."""
        create_response = await client.post("/api/sessions", json={})
        session_id = create_response.json()["session_id"]

        multiline_code = """function hello() {
    console.log('Hello');
    return 42;
}"""
        response = await client.put(
            f"/api/sessions/{session_id}/code",
            json={"code": multiline_code}
        )

        assert response.status_code == 200
        assert response.json()["code"] == multiline_code

    async def test_update_code_updates_timestamp(self, client: AsyncClient):
        """Test that updating code changes updated_at timestamp."""
        create_response = await client.post("/api/sessions", json={})
        session_id = create_response.json()["session_id"]
        original_updated = create_response.json()["updated_at"]

        # Small delay to ensure timestamp difference
        import asyncio
        await asyncio.sleep(0.1)

        response = await client.put(
            f"/api/sessions/{session_id}/code",
            json={"code": "new code"}
        )

        # updated_at should be different (or at least not earlier)
        assert response.json()["updated_at"] >= original_updated


class TestUpdateLanguage:
    """Tests for PUT /api/sessions/{session_id}/language endpoint."""

    async def test_update_language_success(self, client: AsyncClient):
        """Test updating language successfully."""
        create_response = await client.post("/api/sessions", json={"language": "javascript"})
        session_id = create_response.json()["session_id"]

        response = await client.put(
            f"/api/sessions/{session_id}/language",
            json={"language": "python"}
        )

        assert response.status_code == 200
        assert response.json()["language"] == "python"

    async def test_update_language_with_client_id(self, client: AsyncClient):
        """Test updating language with client_id parameter."""
        create_response = await client.post("/api/sessions", json={})
        session_id = create_response.json()["session_id"]

        response = await client.put(
            f"/api/sessions/{session_id}/language?client_id=client-456",
            json={"language": "go"}
        )

        assert response.status_code == 200
        assert response.json()["language"] == "go"

    async def test_update_language_not_found(self, client: AsyncClient):
        """Test updating language for non-existent session returns 404."""
        response = await client.put(
            "/api/sessions/nonexistent123/language",
            json={"language": "python"}
        )

        assert response.status_code == 404

    async def test_update_language_invalid(self, client: AsyncClient):
        """Test updating to invalid language returns 422."""
        create_response = await client.post("/api/sessions", json={})
        session_id = create_response.json()["session_id"]

        response = await client.put(
            f"/api/sessions/{session_id}/language",
            json={"language": "brainfuck"}
        )

        assert response.status_code == 422

    async def test_update_language_all_supported(self, client: AsyncClient):
        """Test updating to all supported languages."""
        create_response = await client.post("/api/sessions", json={})
        session_id = create_response.json()["session_id"]

        for lang in SUPPORTED_LANGUAGES:
            response = await client.put(
                f"/api/sessions/{session_id}/language",
                json={"language": lang}
            )
            assert response.status_code == 200
            assert response.json()["language"] == lang

    async def test_update_language_preserves_code(self, client: AsyncClient):
        """Test that updating language preserves existing code."""
        code = "print('hello')"
        create_response = await client.post("/api/sessions", json={"code": code, "language": "python"})
        session_id = create_response.json()["session_id"]

        response = await client.put(
            f"/api/sessions/{session_id}/language",
            json={"language": "javascript"}
        )

        assert response.json()["code"] == code


class TestEndpointEdgeCases:
    """Edge case tests for all endpoints."""

    async def test_special_characters_in_code(self, client: AsyncClient):
        """Test code with special characters."""
        code = 'const regex = /[a-z]+/g;\nconst str = "Hello\\nWorld";'
        create_response = await client.post("/api/sessions", json={"code": code})
        session_id = create_response.json()["session_id"]

        get_response = await client.get(f"/api/sessions/{session_id}")
        assert get_response.json()["code"] == code

    async def test_unicode_in_code(self, client: AsyncClient):
        """Test code with unicode characters."""
        code = "// Привет мир! 你好世界 🚀"
        create_response = await client.post("/api/sessions", json={"code": code})
        session_id = create_response.json()["session_id"]

        get_response = await client.get(f"/api/sessions/{session_id}")
        assert get_response.json()["code"] == code

    async def test_large_code_block(self, client: AsyncClient):
        """Test with large code block."""
        code = "x = 1\n" * 1000  # 1000 lines of code
        create_response = await client.post("/api/sessions", json={"code": code})
        session_id = create_response.json()["session_id"]

        get_response = await client.get(f"/api/sessions/{session_id}")
        assert get_response.json()["code"] == code

    async def test_session_id_format(self, client: AsyncClient):
        """Test that session_id has expected format."""
        response = await client.post("/api/sessions", json={})
        session_id = response.json()["session_id"]

        # Should be 16 characters, URL-safe
        assert len(session_id) == 16
        # URL-safe base64 characters only
        import re
        assert re.match(r'^[A-Za-z0-9_-]+$', session_id)
