# Code Interview Platform

Real-time collaborative coding interview platform with WebSocket synchronization. Multiple users can edit code simultaneously with live updates.

## Features

- **Real-time Collaboration:** Multiple users see code changes instantly via WebSocket
- **8 Languages Supported:** JavaScript, TypeScript, Python, Java, C++, Go, Rust, PHP
- **Code Execution:** Run JavaScript/TypeScript in browser with console output
- **Modern Stack:** FastAPI backend + Vue 3 frontend + MySQL database
- **Docker-First:** Easy development setup with docker-compose

## Tech Stack

**Backend:**
- FastAPI (Python 3.11)
- SQLAlchemy (async)
- WebSocket (native FastAPI)
- MySQL 8.0

**Frontend:**
- Vue 3 + Vite
- TypeScript
- CodeMirror 6 (code editor)
- TailwindCSS

**Infrastructure:**
- Docker & Docker Compose
- Railway (production deployment)

## Quick Start

### Development Mode

```bash
# Start all services
docker-compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# MySQL: localhost:3306
```

### Access the App

- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### Stop Services

```bash
# Stop all
docker-compose down

# Stop and wipe database
docker-compose down -v
```

## Project Structure

```
.
├── backend_fastapi/          # FastAPI backend
│   ├── app/
│   │   ├── main.py          # Main app + routes
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── database.py      # DB connection
│   │   ├── websocket_manager.py  # WebSocket handling
│   │   └── config.py        # Configuration
│   └── requirements.txt
│
├── frontend/                 # Vue 3 frontend
│   ├── src/
│   │   ├── views/           # Page components
│   │   ├── components/      # Reusable components
│   │   ├── api.ts           # API client
│   │   ├── config.ts        # Frontend config
│   │   └── router.ts        # Vue Router
│   └── package.json
│
├── docker-compose.yml        # Development setup
├── Dockerfile.prod           # Production build
├── CLAUDE.md                 # Development notes
└── README.md
```

## API Endpoints

```
POST   /api/sessions                        - Create new session
GET    /api/sessions/{session_id}           - Get session details
PUT    /api/sessions/{session_id}/code      - Update code
PUT    /api/sessions/{session_id}/language  - Change language
GET    /health                              - Health check
WS     /ws/{session_id}?client_id=xxx       - WebSocket connection
```

## Production Deployment

### Quick Deploy to Railway

1. Create Railway project with MySQL
2. Connect GitHub repository
3. Set `DATABASE_URL` environment variable
4. Railway auto-detects `Dockerfile.prod` and deploys

**See [RAILWAY.md](RAILWAY.md) for detailed steps.**

### Test Production Build Locally

```bash
# Build production image
docker build -f Dockerfile.prod -t code-interview:prod .

# Run with external database
docker run -p 8000:8000 \
  -e DATABASE_URL="mysql+aiomysql://user:pass@host:3306/db" \
  code-interview:prod
```

**See [BUILD_TEST.md](BUILD_TEST.md) for full testing guide.**

## How It Works

### Real-Time Synchronization

1. **Client connects** to WebSocket: `/ws/{session_id}?client_id=xxx`
2. **Server assigns** unique `client_id` (if not provided)
3. **Client updates** code via REST API with `?client_id=xxx` parameter
4. **Server broadcasts** changes to all OTHER clients in same session
5. **Clients receive** updates via WebSocket and update editor

This prevents "echo" - sender doesn't receive their own changes back.

### Architecture

```
User 1 Browser                    User 2 Browser
     │                                 │
     ├─── REST API ──┐                 │
     │               ↓                 │
     │          FastAPI Server         │
     │               │                 │
     │               ├── MySQL DB      │
     │               │                 │
     │               ├── WebSocket ────┤
     └─ WebSocket ───┘                 │
         (receive)              (REST + receive)
```

### Code Execution

- **JavaScript:** Executed in browser using `Function()` constructor
- **TypeScript:** Transpiled to JS using lightweight parser, then executed
- **Other languages:** Syntax highlighting only (no execution)

Console output captured via custom `console.log` override.
