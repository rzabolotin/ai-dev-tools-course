from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

SUPPORTED_LANGUAGES = ["javascript", "typescript", "python", "java", "cpp", "go", "rust", "php"]


class SessionCreate(BaseModel):
    language: Optional[str] = "javascript"
    code: Optional[str] = ""

    @field_validator("language")
    @classmethod
    def validate_language(cls, v):
        if v and v not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Language must be one of: {', '.join(SUPPORTED_LANGUAGES)}")
        return v


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    code: Optional[str]
    language: str
    created_at: datetime
    updated_at: datetime


class CodeUpdate(BaseModel):
    code: str


class LanguageUpdate(BaseModel):
    language: str

    @field_validator("language")
    @classmethod
    def validate_language(cls, v):
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Language must be one of: {', '.join(SUPPORTED_LANGUAGES)}")
        return v


# WebSocket event schemas
class CodeUpdatedEvent(BaseModel):
    event: str = "code.updated"
    sessionId: str
    code: str
    timestamp: str


class LanguageChangedEvent(BaseModel):
    event: str = "language.changed"
    sessionId: str
    language: str
    timestamp: str
