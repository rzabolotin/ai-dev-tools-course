import secrets
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

from .database import Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(16), unique=True, index=True, default=lambda: secrets.token_urlsafe(12)[:16])
    code = Column(Text, nullable=True, default="")
    language = Column(String(50), default="javascript")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
