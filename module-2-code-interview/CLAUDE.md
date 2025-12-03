# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Real-time collaborative coding interview platform built as a Docker-first monorepo with FastAPI backend and Nuxt 3 frontend. Core feature: Multiple users can edit code simultaneously with WebSocket synchronization.

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
docker-compose exec frontend sh        # Nuxt container
docker-compose exec db mysql -u root -p
```

### Backend (FastAPI)

```bash
# The backend auto-starts with uvicorn --reload
# No manual commands needed for development

# Run migrations (handled automatically on startup via SQLAlchemy)
# Tables are created automatically when the app starts

# Install dependencies
docker-compose exec backend pip install package-name
```

### Frontend (Nuxt)

```bash
# Install dependencies
docker-compose exec frontend npm install
docker-compose exec frontend npm install package-name

# Build for production
docker-compose exec frontend npm run build
```

### Ports

- **3000**: Nuxt frontend
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
User edits → Monaco Editor → Debounced (500ms) → API call → Backend
                                                               ↓
Other users ← Monaco update ← WebSocket message ← FastAPI WebSocket
```

### Key Backend Files

**Main App** (`backend_fastapi/app/main.py`):
- FastAPI application with lifespan for DB initialization
- All REST endpoints and WebSocket endpoint
- CORS middleware configured

**Models** (`backend_fastapi/app/models.py`):
- `InterviewSession` - SQLAlchemy model
- Fields: `id`, `session_id` (16-char unique), `code`, `language`, timestamps
- `session_id` auto-generated on creation

**Schemas** (`backend_fastapi/app/schemas.py`):
- Pydantic models for request/response validation
- `SUPPORTED_LANGUAGES` list for validation
- WebSocket event schemas

**WebSocket Manager** (`backend_fastapi/app/websocket_manager.py`):
- `ConnectionManager` class for managing WebSocket connections
- `broadcast_to_session()` - sends to all clients except sender
- Tracks connections by session_id and client_id

**Database** (`backend_fastapi/app/database.py`):
- Async SQLAlchemy setup with aiomysql
- `init_db()` creates tables on startup

**Config** (`backend_fastapi/app/config.py`):
- Pydantic settings from environment variables
- `DATABASE_URL` configuration

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

**Pages** (`frontend/pages/`):
- `index.vue` - Landing page with create/join UI
- `session/[id].vue` - Main editor page with WebSocket integration

**Components** (`frontend/components/CodeEditor.vue`):
- Monaco Editor wrapper with 8 language support
- Props: `modelValue` (code), `language`
- Emits: `update:modelValue`, `update:language`

**Composables**:
- `useApi.ts` - API client wrapper with clientId support
- `useWebSocket.ts` - Native WebSocket integration (no Laravel Echo)
  - `joinSession(sessionId, callbacks)` - Connects to `ws://host/ws/{sessionId}`
  - `getClientId()` - Returns client ID assigned by server
  - Events: `connected`, `code.updated`, `language.changed`
- `useCodeExecution.ts` - Browser-based code execution

**API Layer** (`frontend/api/`):
- `BaseApi.ts` - Abstract HTTP client using `ofetch`
- `SessionsApi.ts` - Session-specific endpoints with clientId support
- `types.ts` - TypeScript interfaces

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

**Backend** (environment variables):
- `DATABASE_URL=mysql+aiomysql://root:secret@db:3306/code_interview`

**Frontend** (`nuxt.config.ts`):
- `runtimeConfig.public.apiBase` - Backend API URL (default: http://localhost:8000)
- `runtimeConfig.public.wsUrl` - WebSocket URL (default: ws://localhost:8000)
- Note: Both HTTP and WebSocket use the same port now!

### Docker Services

```yaml
services:
  backend:    # FastAPI + Uvicorn (HTTP + WebSocket, port 8000)
  frontend:   # Nuxt 3 (port 3000)
  db:         # MySQL 8.0 (port 3306)
```

No Redis needed - WebSocket connections managed in-memory.

### Supported Languages

Monaco Editor supports 8 languages:
- `javascript`, `typescript`, `python`, `java`, `cpp`, `go`, `rust`, `php`

Code execution:
- **JavaScript**: Full execution with console capture
- **TypeScript**: Transpiled to JS, then executed
- **Others**: Syntax highlighting only (no execution)

### Important Notes

1. **Single Port for HTTP + WebSocket**: FastAPI serves both on port 8000. No separate WebSocket server needed.

2. **Client ID Pattern**: Each WebSocket client gets a unique ID. Pass it in API calls to prevent echo.

3. **No Authentication**: Sessions are public. Anyone with session ID can join.

4. **Auto Table Creation**: SQLAlchemy creates tables on app startup via `init_db()`.

5. **Hot Reload**: Both backend (uvicorn --reload) and frontend (Nuxt HMR) support hot reload.

6. **Native WebSocket**: Frontend uses browser's native WebSocket API, no Laravel Echo or Pusher.

7. **Database Health Check**: Backend waits for MySQL to be healthy before starting.

### Development Workflow

1. Code changes in backend: Uvicorn auto-reloads
2. Code changes in frontend: Nuxt HMR
3. Database changes: Update models.py, restart backend (tables auto-created)
4. Dependency changes: Rebuild containers or exec into them

### Common Pitfalls

- **Missing client_id**: Without it, sender receives their own changes (echo)
- **WebSocket URL**: Must be `ws://` not `http://`, same port as API
- **MySQL startup**: Backend waits for db healthcheck before starting
