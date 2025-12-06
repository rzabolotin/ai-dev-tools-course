# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Real-time collaborative coding interview platform built as a Docker-first monorepo with FastAPI backend and Vue 3 + Vite frontend. Core feature: Multiple users can edit code simultaneously with WebSocket synchronization.

## Common Commands

### Development (Docker-based)

```bash
# Start all services
docker-compose up --build

# Start specific services
docker-compose up backend db    # Backend only
docker-compose up frontend      # Frontend only

# Stop services
docker-compose down             # Stop all
docker-compose down -v          # Stop and clean volumes (wipes database)

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Access container shells
docker-compose exec backend bash       # FastAPI container
docker-compose exec frontend sh        # Vue container
docker-compose exec db mysql -u root -p root
```

### Backend (FastAPI)

```bash
# The backend auto-starts with uvicorn --reload
# No manual commands needed for development

# Run migrations (handled automatically on startup via SQLAlchemy)
# Tables are created automatically when the app starts

# Install dependencies
docker-compose exec backend pip install package-name

# Run tests
docker-compose exec backend pytest

# Linting and type checking
docker-compose exec backend flake8 app/
docker-compose exec backend mypy app/
```

### Frontend (Vue 3 + Vite)

```bash
# Install dependencies
docker-compose exec frontend npm install
docker-compose exec frontend npm install package-name

# Build for production
docker-compose exec frontend npm run build

# Run tests
docker-compose exec frontend npm run test

# Linting and formatting
docker-compose exec frontend npm run lint
docker-compose exec frontend npm run format
```

### Ports

- **3000**: Vue 3 frontend (Vite dev server)
- **8000**: FastAPI (HTTP + WebSocket on same port)
- **3306**: MySQL

## Architecture

### Backend Request Flow

```
HTTP Request → FastAPI Router → SQLAlchemy → MySQL
                    ↓
            WebSocket broadcast
                    ↓
            ConnectionManager.broadcast_to_session()
                    ↓
            Other connected clients
```

### Frontend Data Flow

```
User edits → CodeMirror Editor → API call → Backend
                                               ↓
Other users ← CodeMirror update ← WebSocket message ← FastAPI WebSocket
```

### Key Backend Files

**Main App** (`backend_fastapi/app/main.py`):
- FastAPI application with lifespan for DB initialization
- All REST endpoints and WebSocket endpoint
- CORS middleware configured
- Production: Serves static Vue SPA files from `/static` directory

**Models** (`backend_fastapi/app/models.py`):
- `InterviewSession` - SQLAlchemy model
- Fields: `id`, `session_id` (16-char unique), `code`, `language`, timestamps
- `session_id` auto-generated on creation using `secrets.token_urlsafe`

**Schemas** (`backend_fastapi/app/schemas.py`):
- Pydantic models for request/response validation
- `SUPPORTED_LANGUAGES` list: `javascript`, `typescript`, `python`, `java`, `cpp`, `go`, `rust`, `php`
- WebSocket event schemas: `CodeUpdatedEvent`, `LanguageChangedEvent`

**WebSocket Manager** (`backend_fastapi/app/websocket_manager.py`):
- `ConnectionManager` class for managing WebSocket connections
- `broadcast_to_session()` - sends to all clients except sender (prevents echo)
- Tracks connections by session_id and client_id in memory

**Database** (`backend_fastapi/app/database.py`):
- Async SQLAlchemy setup with aiomysql
- `init_db()` creates tables on startup

**API Routes**:
```
POST   /api/sessions                    - Create session
GET    /api/sessions/{session_id}       - Get session
PUT    /api/sessions/{session_id}/code?client_id=xxx   - Update code
PUT    /api/sessions/{session_id}/language?client_id=xxx - Update language
GET    /health                          - Health check
WS     /ws/{session_id}?client_id=xxx   - WebSocket connection
```

### Key Frontend Files

**Views** (`frontend/src/views/`):
- `HomeView.vue` - Landing page with create/join UI
- `SessionView.vue` - Main editor page with WebSocket integration

**Components** (`frontend/src/components/CodeEditor.vue`):
- CodeMirror 6 editor with 8 language support
- Props: `modelValue` (code), `language`, `readOnly`
- Emits: `update:modelValue`
- Uses Compartment API for dynamic language switching

**Composables** (`frontend/src/composables/`):
- `useWebSocket.ts` - Native WebSocket integration
  - `joinSession(sessionId, callbacks)` - Connects to `ws://host/ws/{sessionId}`
  - `getClientId()` - Returns client ID assigned by server
  - Events: `connected`, `code.updated`, `language.changed`
- `useCodeExecution.ts` - Browser-based code execution
  - JavaScript/TypeScript: Native execution with console capture
  - Python: Via Pyodide (WebAssembly). Lazy-loads interpreter (~6MB, cached after first load)
  - Captures stdout/stderr and return values for all supported languages

**API Layer** (`frontend/src/api.ts`):
- Simple `fetch`-based API client
- Functions: `createSession`, `getSession`, `updateCode`, `updateLanguage`
- Automatically includes `client_id` query parameter to prevent echo

**Router** (`frontend/src/router.ts`):
- Vue Router with two routes: `/` (home) and `/session/:id` (editor)

### Real-time Synchronization Pattern

**How it works**:

1. Client connects to WebSocket, receives `clientId` from server
2. Client makes API calls with `?client_id=xxx` query parameter
3. Backend broadcasts to all clients EXCEPT the one with matching `client_id`
4. This prevents echo (sender doesn't receive their own changes)

**WebSocket Message Format**:
```json
// Connection established
{"event": "connected", "clientId": "uuid-here"}

// Code updated
{"event": "code.updated", "sessionId": "xxx", "code": "...", "timestamp": "..."}

// Language changed
{"event": "language.changed", "sessionId": "xxx", "language": "python", "timestamp": "..."}
```

**Connection Flow**:
```
User opens session page
  → API call: GET /api/sessions/{id}
  → WebSocket: Connect to /ws/{sessionId}
  → Server: Sends {"event": "connected", "clientId": "..."}
  → Client: Stores clientId, uses it in API calls
```

### Database Schema

**interview_sessions table**:
- `id` - Primary key (auto-increment)
- `session_id` - Unique string (16 chars), used in URLs
- `code` - Text field (nullable)
- `language` - String (default: 'javascript')
- `created_at`, `updated_at` - Timestamps

### Configuration

**Backend** (environment variables in docker-compose.yml):
- `DATABASE_URL=mysql+aiomysql://root:secret@db:3306/code_interview`

**Frontend** (`frontend/src/config.ts`):
- Development: Uses `VITE_API_BASE` and `VITE_WS_URL` env vars
- Production: Auto-detects same origin for API, builds WebSocket URL from window.location
- Note: Both HTTP and WebSocket use the same port (8000)!

**Vite Config** (`frontend/vite.config.ts`):
- `@` alias points to `src/` directory
- Dev server runs on port 3000 with host `0.0.0.0` (accessible from Docker)

### Docker Services

```yaml
services:
  backend:    # FastAPI + Uvicorn (HTTP + WebSocket, port 8000)
  frontend:   # Vue 3 + Vite (port 3000)
  db:         # MySQL 8.0 (port 3306)
```

No Redis needed - WebSocket connections managed in-memory.

### Supported Languages

CodeMirror 6 supports 8 languages:
- `javascript`, `typescript`, `python`, `java`, `cpp`, `go`, `rust`, `php`

Code execution:
- **JavaScript**: Full execution with console capture using `Function()` constructor
- **TypeScript**: Transpiled to JS with basic parser, then executed
- **Python**: Full execution via Pyodide (Python compiled to WebAssembly). First run loads ~6MB interpreter from CDN, subsequent runs are instant. Supports print(), standard library, and most Python features.
- **Others**: Syntax highlighting only (no execution)

### Important Notes

1. **Single Port for HTTP + WebSocket**: FastAPI serves both on port 8000. No separate WebSocket server needed.

2. **Client ID Pattern**: Each WebSocket client gets a unique ID on connection. Pass it in API calls with `?client_id=xxx` to prevent echo (sender won't receive their own changes).

3. **No Authentication**: Sessions are public. Anyone with session ID can join.

4. **Auto Table Creation**: SQLAlchemy creates tables on app startup via `init_db()`.

5. **Hot Reload**: Both backend (uvicorn --reload) and frontend (Vite HMR) support hot reload.

6. **Native WebSocket**: Frontend uses browser's native WebSocket API directly.

7. **Production Build**: Uses multi-stage Dockerfile (`Dockerfile.prod`) that builds Vue frontend and serves it via FastAPI backend. See DEPLOYMENT.md for testing and deployment instructions.

### Development Workflow

1. Code changes in backend: Uvicorn auto-reloads
2. Code changes in frontend: Vite HMR
3. Database changes: Update models.py, restart backend (tables auto-created)
4. Dependency changes: Rebuild containers or exec into them

### Testing

- **Backend**: pytest with test files in `backend_fastapi/tests/`
- **Frontend**: vitest with test files alongside source (e.g., `*.test.ts`)
- **Linting**: flake8 + mypy for backend, ESLint for frontend

### Production Deployment

- Multi-stage Docker build (`Dockerfile.prod`)
- Stage 1: Build Vue 3 frontend with Vite (generates `dist/`)
- Stage 2: Copy backend + built frontend to Python image
- FastAPI serves static files from `/static` directory
- See DEPLOYMENT.md for local testing and Railway deployment instructions

### Common Pitfalls

- **Missing client_id**: Without it, sender receives their own changes (echo effect)
- **WebSocket URL**: Must be `ws://` not `http://`, same port as API (8000)
- **MySQL password**: Use `secret` for root password (defined in docker-compose.yml)
- **Frontend env vars**: Use `VITE_API_BASE` and `VITE_WS_URL` (Vite prefix required)
