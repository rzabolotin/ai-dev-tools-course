import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db, init_db
from .models import InterviewSession
from .schemas import (
    CodeUpdate,
    CodeUpdatedEvent,
    LanguageChangedEvent,
    LanguageUpdate,
    SessionCreate,
    SessionResponse,
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
    session = InterviewSession(language=data.language or "javascript", code=data.code or "")
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
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InterviewSession).where(InterviewSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.code = data.code  # type: ignore
    session.updated_at = datetime.utcnow()  # type: ignore
    await db.commit()
    await db.refresh(session)

    # Broadcast to other clients
    event = CodeUpdatedEvent(
        sessionId=session_id, code=data.code, timestamp=datetime.utcnow().isoformat() + "Z"
    )
    await manager.broadcast_to_session(session_id, event.model_dump(), exclude_client_id=client_id)

    return session


# Update language
@app.put("/api/sessions/{session_id}/language", response_model=SessionResponse)
async def update_language(
    session_id: str,
    data: LanguageUpdate,
    client_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InterviewSession).where(InterviewSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.language = data.language  # type: ignore
    session.updated_at = datetime.utcnow()  # type: ignore
    await db.commit()
    await db.refresh(session)

    # Broadcast to other clients
    event = LanguageChangedEvent(
        sessionId=session_id, language=data.language, timestamp=datetime.utcnow().isoformat() + "Z"
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
            _ = await websocket.receive_text()
            # Could handle client-side events here if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "code-interview-api"}


# Mount static files (production only - serves Vue SPA)
# This must be LAST, after all API routes
if os.path.exists("static"):
    # Mount static assets (js, css, images, etc.)
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

    # SPA fallback: serve index.html for all other routes (Vue Router)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """
        Catch-all route for SPA.
        Serves static files if they exist, otherwise returns index.html
        This allows Vue Router to handle client-side routing.
        """
        static_path = Path("static") / full_path

        # If exact file exists, serve it
        if static_path.is_file():
            return FileResponse(static_path)

        # Otherwise, serve index.html (SPA fallback)
        return FileResponse("static/index.html")
