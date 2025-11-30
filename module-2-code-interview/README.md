# Code Interview Platform

A real-time collaborative coding interview platform built with Laravel (PHP) and Nuxt 3 (Vue.js). This platform allows interviewers to create coding sessions, share links with candidates, and collaborate on code in real-time with syntax highlighting and in-browser code execution.

## Features

- **Real-time Collaboration**: Multiple users can edit code simultaneously with instant synchronization
- **Multi-language Support**: Syntax highlighting for JavaScript, TypeScript, Python, Java, C++, Go, Rust, and PHP
- **In-browser Code Execution**: Run JavaScript and TypeScript code directly in the browser
- **Session Sharing**: Generate unique session links to share with candidates
- **WebSocket Integration**: Real-time updates using Laravel Reverb
- **Monaco Editor**: Professional code editor with IntelliSense and syntax highlighting
- **REST API**: Well-documented API following OpenAPI 3.0 specification

## Tech Stack

### Backend
- **PHP 8.2** with Laravel 11
- **MySQL 8.0** for data persistence
- **Redis** for caching and session management
- **Laravel Reverb** for WebSocket connections
- **Docker** for containerization

### Frontend
- **Nuxt 3** with Vue.js 3
- **TypeScript** for type safety
- **Monaco Editor** for code editing
- **Tailwind CSS** for styling
- **Laravel Echo + Pusher** for WebSocket client
- **Docker** for containerization

## Project Structure

```
.
├── openapi.yaml                 # API specification
├── docker-compose.yml           # Docker orchestration
├── backend/                     # Laravel backend
│   ├── app/
│   │   ├── Events/             # WebSocket events
│   │   ├── Http/Controllers/   # API controllers
│   │   └── Models/             # Database models
│   ├── database/migrations/    # Database migrations
│   ├── routes/                 # API routes
│   └── Dockerfile
├── frontend/                    # Nuxt 3 frontend
│   ├── components/             # Vue components
│   ├── composables/            # Reusable logic
│   ├── pages/                  # Application pages
│   └── Dockerfile
└── README.md
```


## Configuration

### Environment Variables

#### Backend (.env)
The backend uses environment variables defined in `backend/.env.example`:

- `DB_HOST`: Database host (default: db)
- `DB_DATABASE`: Database name (default: code_interview)
- `REVERB_HOST`: WebSocket host (default: 0.0.0.0)
- `REVERB_PORT`: WebSocket port (default: 8080)

#### Frontend
Frontend configuration is in `frontend/nuxt.config.ts`:

- `NUXT_PUBLIC_API_BASE`: Backend API URL (default: http://localhost:8000)
- `NUXT_PUBLIC_WS_URL`: WebSocket URL (default: ws://localhost:8080)

### Ports

Default ports used by the application:

- **3000**: Nuxt frontend
- **8000**: Laravel API
- **8080**: WebSocket server (Reverb)
- **3306**: MySQL database
- **6379**: Redis

To change ports, edit `docker-compose.yml`.

## Architecture

### Backend Architecture

```
Request → API Routes → Controllers → Models → Database
                    ↓
                 Events → Broadcasting → WebSocket
```

1. **API Routes**: Defined in `routes/api.php`
2. **Controllers**: Handle business logic in `app/Http/Controllers`
3. **Models**: Eloquent ORM models in `app/Models`
4. **Events**: WebSocket events in `app/Events`
5. **Broadcasting**: Laravel Reverb handles real-time updates

### Frontend Architecture

```
Pages → Components → Composables → API/WebSocket
                         ↓
                    Monaco Editor
```

1. **Pages**: Route-based pages in `pages/`
2. **Components**: Reusable Vue components in `components/`
3. **Composables**: Shared logic (API, WebSocket, execution) in `composables/`
4. **Monaco Editor**: Professional code editor with syntax highlighting

## Code Execution

### Supported Languages

- **JavaScript**: Full support with console output capture
- **TypeScript**: Transpiled to JavaScript and executed
- **Python**: Planned (requires Pyodide integration)
- **Others**: Display-only with syntax highlighting

## Future Enhancements

- [ ] User authentication and session management
- [ ] Save and load interview sessions
- [ ] Video/audio chat integration
- [ ] Server-side code execution for more languages
- [ ] Code review and annotation tools
- [ ] Interview templates and challenges
- [ ] Analytics and reporting
- [ ] Multi-file project support
- [ ] Collaborative debugging tools
- [ ] Integration with GitHub/GitLab

---

Built with ❤️ using Laravel and Nuxt 3
