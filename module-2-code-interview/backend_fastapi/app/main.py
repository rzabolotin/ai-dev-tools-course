from contextlib import asynccontextmanager
from datetime import datetime
import uuid

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .database import get_db, init_db
from .models import InterviewSession
from .schemas import (
    SessionCreate,
    SessionResponse,
    CodeUpdate,
    LanguageUpdate,
    CodeUpdatedEvent,
    LanguageChangedEvent,
)
from .websocket_manager import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    await init_db()
    yield
    # Shutdown: nothing to do


app = FastAPI(title="Code Interview API", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create session
@app.post("/api/sessions", response_model=SessionResponse, status_code=201)
async def create_session(data: SessionCreate, db: AsyncSession = Depends(get_db)):
    session = InterviewSession(
        language=data.language or "javascript",
        code=data.code or ""
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


# Get session
@app.get("/api/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(InterviewSession).where(InterviewSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


# Update code
@app.put("/api/sessions/{session_id}/code", response_model=SessionResponse)
async def update_code(
    session_id: str,
    data: CodeUpdate,
    client_id: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(InterviewSession).where(InterviewSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.code = data.code
    session.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(session)

    # Broadcast to other clients
    event = CodeUpdatedEvent(
        sessionId=session_id,
        code=data.code,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
    await manager.broadcast_to_session(session_id, event.model_dump(), exclude_client_id=client_id)

    return session


# Update language
@app.put("/api/sessions/{session_id}/language", response_model=SessionResponse)
async def update_language(
    session_id: str,
    data: LanguageUpdate,
    client_id: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(InterviewSession).where(InterviewSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.language = data.language
    session.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(session)

    # Broadcast to other clients
    event = LanguageChangedEvent(
        sessionId=session_id,
        language=data.language,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
    await manager.broadcast_to_session(session_id, event.model_dump(), exclude_client_id=client_id)

    return session


# WebSocket endpoint
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, client_id: str = Query(None)):
    # Generate client_id if not provided
    if not client_id:
        client_id = str(uuid.uuid4())

    await manager.connect(websocket, session_id, client_id)

    # Send client_id to the client
    await websocket.send_json({"event": "connected", "clientId": client_id})

    try:
        while True:
            # Keep connection alive, handle incoming messages if needed
            data = await websocket.receive_text()
            # Could handle client-side events here if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
