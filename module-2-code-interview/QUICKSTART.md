# Quick Start Guide

## Start the Application

```bash
docker-compose up --build
```

Or use the start script:
```bash
./start.sh
```

## Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

## Usage

### Create a Session
1. Go to http://localhost:3000
2. Select language (JavaScript, Python, etc.)
3. Click "Create Interview Session"
4. Share the link with candidates

### Join a Session
1. Open the shared link, OR
2. Go to http://localhost:3000
3. Enter session ID
4. Click "Join"

### During Interview
- **Edit Code**: Type in the editor (changes sync in real-time)
- **Change Language**: Use dropdown menu
- **Run Code**: Click "Run Code" button (JS/TS only)
- **Share**: Click "Share Link" to copy URL

## Common Commands

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop application
docker-compose down

# Restart services
docker-compose restart

# Clean rebuild
docker-compose down -v
docker-compose up --build

# Access backend shell
docker-compose exec backend bash

# Run Laravel commands
docker-compose exec backend php artisan migrate
docker-compose exec backend php artisan key:generate
```

## Troubleshooting

### Backend won't start
```bash
docker-compose logs backend
docker-compose restart backend
```

### Database connection error
```bash
# Wait for database
docker-compose exec backend bash -c "while ! nc -z db 3306; do sleep 1; done"
# Run migrations
docker-compose exec backend php artisan migrate
```

### Frontend build error
```bash
docker-compose exec frontend rm -rf node_modules .nuxt
docker-compose restart frontend
```

### WebSocket not connecting
1. Check Reverb logs: `docker-compose logs backend | grep reverb`
2. Verify port 8080 is not in use: `curl http://localhost:8080`
3. Restart backend: `docker-compose restart backend`

## Features

- ✅ Real-time code synchronization
- ✅ Multi-language syntax highlighting
- ✅ In-browser JavaScript execution
- ✅ Session sharing via URL
- ✅ WebSocket support
- ✅ Monaco Editor (VS Code editor)

## API Endpoints

See `openapi.yaml` for complete API documentation.

```
POST   /api/sessions                  - Create session
GET    /api/sessions/{id}             - Get session
PUT    /api/sessions/{id}/code        - Update code
PUT    /api/sessions/{id}/language    - Change language
GET    /health                        - Health check
```

## Tech Stack

- **Backend**: Laravel 11 + PHP 8.2 + MySQL + Redis + Reverb
- **Frontend**: Nuxt 3 + Vue 3 + TypeScript + Monaco Editor
- **Real-time**: Laravel Reverb WebSocket Server
