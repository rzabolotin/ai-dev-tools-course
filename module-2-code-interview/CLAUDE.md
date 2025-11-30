# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Real-time collaborative coding interview platform built as a Docker-first monorepo with Laravel 11 backend and Nuxt 3 frontend. Core feature: Multiple users can edit code simultaneously with WebSocket synchronization via Laravel Reverb.

## Common Commands

### Development (Docker-based)

```bash
# Start all services
docker-compose up --build

# Start specific services
docker-compose up backend db redis    # Backend only
docker-compose up frontend             # Frontend only

# Stop services
docker-compose down                    # Stop all
docker-compose down -v                 # Stop and clean volumes (wipes database)

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Access container shells
docker-compose exec backend bash       # Laravel container
docker-compose exec frontend sh        # Nuxt container
docker-compose exec db mysql -u root -p
```

### Backend (Laravel)

```bash
# Run migrations
docker-compose exec backend php artisan migrate

# Start Reverb WebSocket server (auto-starts in entrypoint, manual restart if needed)
docker-compose exec backend php artisan reverb:start

# Clear cache
docker-compose exec backend php artisan cache:clear

# Install dependencies
docker-compose exec backend composer install
docker-compose exec backend composer require package-name

# Run tests (PHPUnit available, no tests written yet)
docker-compose exec backend php artisan test
```

### Frontend (Nuxt)

```bash
# Install dependencies
docker-compose exec frontend npm install
docker-compose exec frontend npm install package-name

# Build for production
docker-compose exec frontend npm run build

# Run tests (test infrastructure available, no tests written yet)
docker-compose exec frontend npm run test
```

### Ports

- **3000**: Nuxt frontend
- **8000**: Laravel API
- **8080**: Reverb WebSocket server
- **3306**: MySQL
- **6379**: Redis

## Architecture

### Backend Request Flow

```
HTTP Request → routes/api.php → SessionController → InterviewSession Model → MySQL
                                        ↓
                                   Events (CodeUpdated/LanguageChanged)
                                        ↓
                                   broadcast()->toOthers()
                                        ↓
                                   Reverb WebSocket (port 8080)
                                        ↓
                                   channel: session.{sessionId}
```

### Frontend Data Flow

```
User edits → Monaco Editor → Debounced (500ms) → API call → Backend
                                                                ↓
Other users ← Monaco update ← Echo listener ← WebSocket ← Broadcasting
```

### Key Backend Files

**Models** (`backend/app/Models/InterviewSession.php`):
- Single model for all interview sessions
- Custom route key: `session_id` (16-char random string), NOT `id`
- Fields: `session_id` (unique), `code` (text), `language` (string), timestamps
- Important: When querying by route parameter, Laravel uses `session_id` not `id`

**Controllers** (`backend/app/Http/Controllers/SessionController.php`):
- `create()` - Creates session with optional language/code
- `show($sessionId)` - Retrieves session (uses session_id, not id)
- `updateCode($sessionId)` - Updates code + broadcasts event
- `updateLanguage($sessionId)` - Updates language + broadcasts event
- Pattern: After update, broadcasts `new Event($session)->toOthers()` to prevent echo

**Events** (`backend/app/Events/`):
- `CodeUpdated` - Broadcasts on `session.{sessionId}` as `code.updated`
- `LanguageChanged` - Broadcasts on `session.{sessionId}` as `language.changed`
- Both implement `ShouldBroadcast` interface
- Payload includes: sessionId, changed data, ISO 8601 timestamp
- Custom event names via `broadcastAs()` method

**Broadcasting Channels** (`backend/routes/channels.php`):
- `session.{sessionId}` - Public channel (returns true, no auth)
- Each interview session has isolated channel
- No authentication required for MVP

**API Routes** (`backend/routes/api.php`):
```
POST   /api/sessions                    - Create session
GET    /api/sessions/{sessionId}        - Get session
PUT    /api/sessions/{sessionId}/code   - Update code
PUT    /api/sessions/{sessionId}/language - Update language
GET    /health                           - Health check
```

### Key Frontend Files

**Pages** (`frontend/pages/`):
- `index.vue` - Landing page with create/join UI
- `session/[id].vue` - Main editor page with WebSocket integration

**Components** (`frontend/components/CodeEditor.vue`):
- Monaco Editor wrapper with 8 language support
- Props: `modelValue` (code), `language`
- Emits: `update:modelValue`, `update:language`
- External update handling: Preserves cursor position when updating from WebSocket
- Theme: vs-dark, font size: 14px, minimap enabled

**Composables**:
- `useApi.ts` - API client wrapper (SessionsApi, HealthApi)
- `useWebSocket.ts` - Laravel Echo integration with Reverb
  - `initEcho()` - Creates global Echo instance with Pusher transport
  - `joinSession(sessionId, callbacks)` - Subscribes to `session.{sessionId}` channel
  - Listens for: `code.updated`, `language.changed`
- `useCodeExecution.ts` - Browser-based code execution
  - JavaScript: eval() with console capture
  - TypeScript: Auto-transpiled to JS then executed
  - Others: Display-only (Pyodide planned for Python)

**API Layer** (`frontend/api/`):
- `BaseApi.ts` - Abstract HTTP client using `ofetch`
- `SessionsApi.ts` - Session-specific endpoints
- `types.ts` - TypeScript interfaces for Session, requests, responses
- Pattern: All API calls go through typed API classes, not direct fetch

### Real-time Synchronization Pattern

**Critical Implementation Details**:

1. **Preventing Echo Feedback**:
   - Backend uses `broadcast()->toOthers()` to exclude sender
   - Sender sees immediate UI update, others receive via WebSocket

2. **Debouncing Code Updates**:
   - 500ms debounce on code editor changes
   - Prevents API flood during typing
   - Implemented in `session/[id].vue`

3. **Language Changes**:
   - No debounce (immediate)
   - Less frequent, user-initiated action

4. **Session Channel Pattern**:
   - Channel name: `session.{sessionId}`
   - Custom event names: `code.updated`, `language.changed` (defined in Event classes)
   - Laravel Echo automatically prefixes private/presence channels, but not public channels

5. **Connection Flow**:
   ```
   User opens session page
     → API call: Load session data
     → WebSocket: Connect to Echo
     → Channel: Subscribe to session.{sessionId}
     → Listeners: Register callbacks for code.updated, language.changed
   ```

### Database Schema

**interview_sessions table**:
- `id` - Primary key (auto-increment)
- `session_id` - Unique string (16 chars), used in URLs
- `code` - Text field (nullable)
- `language` - String (default: 'javascript')
- `created_at`, `updated_at` - Timestamps

Migration: `backend/database/migrations/2024_01_01_000001_create_interview_sessions_table.php`

### Configuration Files

**Backend** (`.env`):
- `BROADCAST_DRIVER=reverb` - Uses Laravel Reverb, not Pusher/Redis
- `REVERB_HOST=0.0.0.0` - Listens on all interfaces
- `REVERB_PORT=8080` - WebSocket server port
- `DB_HOST=db` - Docker service name for MySQL
- `REDIS_HOST=redis` - Docker service name for Redis

**Frontend** (`nuxt.config.ts`):
- `runtimeConfig.public.apiBase` - Backend API URL (default: http://localhost:8000)
- `runtimeConfig.public.wsUrl` - WebSocket URL (default: ws://localhost:8080)
- Env vars: `NUXT_PUBLIC_API_BASE`, `NUXT_PUBLIC_WS_URL`

**Docker Entrypoint** (`backend/entrypoint.sh`):
- Auto-copies `.env.example` to `.env`
- Generates `APP_KEY` if missing
- Waits for database connection (nc check)
- Runs migrations with `--force`
- Starts Reverb WebSocket server in background
- Starts Laravel dev server on port 8000

### Supported Languages

Monaco Editor supports 8 languages:
- `javascript`, `typescript`, `python`, `java`, `cpp`, `go`, `rust`, `php`

Code execution:
- **JavaScript**: Full execution with console capture
- **TypeScript**: Transpiled to JS, then executed
- **Others**: Syntax highlighting only (no execution)

### Testing

**Current State**: No tests written yet, but infrastructure ready.

**Available Commands**:
```bash
# Backend (PHPUnit)
docker-compose exec backend php artisan test

# Frontend (Vitest expected, check package.json)
docker-compose exec frontend npm run test
```

### Important Notes

1. **Session ID vs Primary Key**: Routes use `session_id` field, not `id`. Model has `getRouteKeyName()` returning 'session_id'.

2. **No Authentication**: Channels are public (return true in channels.php). Anyone with session ID can join.

3. **WebSocket Auto-start**: Reverb starts automatically in Docker entrypoint. Manual restart only needed for debugging.

4. **Database Initialization**: Migrations run automatically on container start. Use `docker-compose down -v` to reset.

5. **Code Execution Security**: Uses browser `eval()` for JavaScript. Not sandboxed. Consider for production.

6. **Monaco Editor Version**: Check `package.json` for version. External updates preserve cursor position (important for UX).

7. **API Validation**: Language field validated against enum in `SessionController` (8 supported languages).

8. **Broadcast Driver**: Uses Reverb (Laravel's WebSocket server), not Pusher. No external service needed.

9. **Frontend State**: No Vuex/Pinia. Uses composables + local component state + props/emits.

10. **Session Persistence**: Sessions stored in MySQL, but no cleanup mechanism. Consider adding TTL or manual deletion.

### API Documentation

Full OpenAPI 3.0.3 specification available in `openapi.yaml` at project root. Includes:
- All REST endpoints with request/response schemas
- WebSocket events documentation
- Example payloads

### Development Workflow

1. Code changes in backend: Container auto-reloads (Laravel dev server)
2. Code changes in frontend: HMR via Vite (Nuxt dev mode)
3. Database changes: Create migration, restart backend container or run manually
4. Dependency changes: Exec into container and run composer/npm install
5. Reverb changes: Restart backend container to restart WebSocket server

### Common Pitfalls

- **Wrong route key**: Don't query by `id`, use `session_id`
- **Missing .toOthers()**: Will cause echo feedback to sender
- **Forgetting debounce**: Code updates without debounce will flood API
- **Channel name mismatch**: Backend broadcasts to `session.{id}`, frontend must listen to same channel name
- **Event name mismatch**: Backend uses `broadcastAs()` for custom names, frontend must match exactly
