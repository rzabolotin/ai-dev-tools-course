"""Unit tests for Pydantic schemas validation."""
import pytest
from pydantic import ValidationError

from app.schemas import (
    SessionCreate,
    SessionResponse,
    CodeUpdate,
    LanguageUpdate,
    CodeUpdatedEvent,
    LanguageChangedEvent,
    SUPPORTED_LANGUAGES,
)


class TestSupportedLanguages:
    """Tests for SUPPORTED_LANGUAGES constant."""

    def test_supported_languages_list(self):
        """Verify all expected languages are in the list."""
        expected = ["javascript", "typescript", "python", "java", "cpp", "go", "rust", "php"]
        assert SUPPORTED_LANGUAGES == expected

    def test_supported_languages_count(self):
        """Verify we have 8 supported languages."""
        assert len(SUPPORTED_LANGUAGES) == 8


class TestSessionCreate:
    """Tests for SessionCreate schema."""

    def test_default_values(self):
        """Test that defaults are applied correctly."""
        session = SessionCreate()
        assert session.language == "javascript"
        assert session.code == ""

    def test_custom_values(self):
        """Test with custom values."""
        session = SessionCreate(language="python", code="print('hello')")
        assert session.language == "python"
        assert session.code == "print('hello')"

    def test_valid_languages(self):
        """Test all supported languages are accepted."""
        for lang in SUPPORTED_LANGUAGES:
            session = SessionCreate(language=lang)
            assert session.language == lang

    def test_invalid_language_raises_error(self):
        """Test that invalid language raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SessionCreate(language="cobol")
        assert "Language must be one of" in str(exc_info.value)

    def test_none_language_uses_default(self):
        """Test that None language defaults to javascript."""
        session = SessionCreate(language=None)
        assert session.language is None  # Validator allows None

    def test_empty_code(self):
        """Test with empty code string."""
        session = SessionCreate(code="")
        assert session.code == ""

    def test_multiline_code(self):
        """Test with multiline code."""
        code = """def hello():
    print('world')

hello()"""
        session = SessionCreate(code=code)
        assert session.code == code


class TestCodeUpdate:
    """Tests for CodeUpdate schema."""

    def test_code_required(self):
        """Test that code field is required."""
        with pytest.raises(ValidationError):
            CodeUpdate()

    def test_code_accepts_string(self):
        """Test that code accepts string value."""
        update = CodeUpdate(code="console.log('test')")
        assert update.code == "console.log('test')"

    def test_code_accepts_empty_string(self):
        """Test that code accepts empty string."""
        update = CodeUpdate(code="")
        assert update.code == ""

    def test_code_multiline(self):
        """Test with multiline code."""
        code = "line1\nline2\nline3"
        update = CodeUpdate(code=code)
        assert update.code == code


class TestLanguageUpdate:
    """Tests for LanguageUpdate schema."""

    def test_language_required(self):
        """Test that language field is required."""
        with pytest.raises(ValidationError):
            LanguageUpdate()

    def test_valid_languages(self):
        """Test all supported languages are accepted."""
        for lang in SUPPORTED_LANGUAGES:
            update = LanguageUpdate(language=lang)
            assert update.language == lang

    def test_invalid_language_raises_error(self):
        """Test that invalid language raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            LanguageUpdate(language="brainfuck")
        assert "Language must be one of" in str(exc_info.value)

    def test_empty_language_raises_error(self):
        """Test that empty language raises ValidationError."""
        with pytest.raises(ValidationError):
            LanguageUpdate(language="")


class TestSessionResponse:
    """Tests for SessionResponse schema."""

    def test_from_attributes_config(self):
        """Test that from_attributes is enabled for ORM mode."""
        assert SessionResponse.model_config.get("from_attributes") is True

    def test_all_fields_present(self):
        """Test that all required fields are in the schema."""
        from datetime import datetime
        response = SessionResponse(
            id=1,
            session_id="abc123",
            code="test code",
            language="python",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        assert response.id == 1
        assert response.session_id == "abc123"
        assert response.code == "test code"
        assert response.language == "python"

    def test_code_can_be_none(self):
        """Test that code field can be None."""
        from datetime import datetime
        response = SessionResponse(
            id=1,
            session_id="abc123",
            code=None,
            language="python",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        assert response.code is None


class TestCodeUpdatedEvent:
    """Tests for CodeUpdatedEvent WebSocket schema."""

    def test_default_event_name(self):
        """Test default event name is set."""
        event = CodeUpdatedEvent(sessionId="sess1", code="test", timestamp="2024-01-01T00:00:00Z")
        assert event.event == "code.updated"

    def test_all_fields(self):
        """Test all fields are set correctly."""
        event = CodeUpdatedEvent(
            sessionId="session123",
            code="console.log('hello')",
            timestamp="2024-01-01T12:00:00Z"
        )
        assert event.sessionId == "session123"
        assert event.code == "console.log('hello')"
        assert event.timestamp == "2024-01-01T12:00:00Z"

    def test_model_dump(self):
        """Test serialization to dict."""
        event = CodeUpdatedEvent(sessionId="s1", code="test", timestamp="2024-01-01T00:00:00Z")
        data = event.model_dump()
        assert data["event"] == "code.updated"
        assert data["sessionId"] == "s1"
        assert data["code"] == "test"


class TestLanguageChangedEvent:
    """Tests for LanguageChangedEvent WebSocket schema."""

    def test_default_event_name(self):
        """Test default event name is set."""
        event = LanguageChangedEvent(sessionId="sess1", language="python", timestamp="2024-01-01T00:00:00Z")
        assert event.event == "language.changed"

    def test_all_fields(self):
        """Test all fields are set correctly."""
        event = LanguageChangedEvent(
            sessionId="session456",
            language="rust",
            timestamp="2024-01-01T12:00:00Z"
        )
        assert event.sessionId == "session456"
        assert event.language == "rust"
        assert event.timestamp == "2024-01-01T12:00:00Z"

    def test_model_dump(self):
        """Test serialization to dict."""
        event = LanguageChangedEvent(sessionId="s1", language="go", timestamp="2024-01-01T00:00:00Z")
        data = event.model_dump()
        assert data["event"] == "language.changed"
        assert data["sessionId"] == "s1"
        assert data["language"] == "go"
