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

## Prerequisites

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)

That's it! No need for PHP, Composer, Node.js, or npm installed locally.

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd module-2-code-interview
```

### 2. Start the Application

```bash
docker-compose up --build
```

This command will:
- Build all containers (backend, frontend, database, redis)
- Install all PHP and Node.js dependencies
- Start Laravel on port 8000
- Start Reverb WebSocket server on port 8080
- Start Nuxt dev server on port 3000
- Initialize MySQL database on port 3306

### 3. Access the Application

Once all containers are running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Health Check**: http://localhost:8000/health
- **WebSocket**: ws://localhost:8080

## Usage Guide

### Creating a New Interview Session

1. Open http://localhost:3000 in your browser
2. Select the programming language (default: JavaScript)
3. Optionally add starter code
4. Click "Create Interview Session"
5. Share the generated URL with your candidate

### Joining an Existing Session

**Option 1**: Use the shared link directly

**Option 2**: Enter the session ID manually
1. Open http://localhost:3000
2. Enter the session ID in the "Join Session" field
3. Click "Join"

### Using the Code Editor

- **Edit Code**: Type directly in the Monaco editor
- **Change Language**: Use the dropdown in the top-right corner
- **Run Code**: Click "Run Code" button (JavaScript/TypeScript only)
- **Share Link**: Click "Share Link" to copy the session URL

### Real-time Collaboration

- All connected users see changes in real-time
- Code updates are synchronized automatically
- Language changes are broadcast to all participants
- Connection status is displayed in the bottom-right

## API Documentation

The API follows the OpenAPI 3.0 specification. View the complete API documentation in `openapi.yaml`.

### Key Endpoints

#### Create Session
```http
POST /api/sessions
Content-Type: application/json

{
  "language": "javascript",
  "code": "console.log('Hello');"
}
```

#### Get Session
```http
GET /api/sessions/{sessionId}
```

#### Update Code
```http
PUT /api/sessions/{sessionId}/code
Content-Type: application/json

{
  "code": "console.log('Updated code');"
}
```

#### Update Language
```http
PUT /api/sessions/{sessionId}/language
Content-Type: application/json

{
  "language": "python"
}
```

### WebSocket Events

The platform uses WebSocket channels for real-time updates:

**Channel**: `session.{sessionId}`

**Events**:
- `code.updated` - Triggered when code is modified
- `language.changed` - Triggered when language is changed

## Development

### Running Individual Services

```bash
# Start only the backend
docker-compose up backend db redis

# Start only the frontend
docker-compose up frontend

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean database)
docker-compose down -v
```

### Rebuilding Containers

```bash
# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Rebuild all services
docker-compose build
```

### Accessing Container Shells

```bash
# Backend (Laravel)
docker-compose exec backend bash

# Frontend (Nuxt)
docker-compose exec frontend sh

# Database
docker-compose exec db mysql -u root -p
```

### Running Laravel Commands

```bash
# Run migrations
docker-compose exec backend php artisan migrate

# Generate app key
docker-compose exec backend php artisan key:generate

# Clear cache
docker-compose exec backend php artisan cache:clear

# Run Reverb WebSocket server manually
docker-compose exec backend php artisan reverb:start
```

### Installing Dependencies

```bash
# Backend (Composer)
docker-compose exec backend composer install
docker-compose exec backend composer require package-name

# Frontend (npm)
docker-compose exec frontend npm install
docker-compose exec frontend npm install package-name
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

## Troubleshooting

### Database Connection Issues

```bash
# Wait for database to be ready
docker-compose exec backend bash -c "while ! nc -z db 3306; do sleep 1; done"

# Run migrations manually
docker-compose exec backend php artisan migrate
```

### WebSocket Connection Failed

1. Ensure Reverb is running:
   ```bash
   docker-compose logs backend | grep reverb
   ```

2. Check if port 8080 is accessible:
   ```bash
   curl http://localhost:8080
   ```

3. Restart backend:
   ```bash
   docker-compose restart backend
   ```

### Frontend Build Issues

```bash
# Clear Nuxt cache
docker-compose exec frontend rm -rf .nuxt

# Reinstall dependencies
docker-compose exec frontend rm -rf node_modules
docker-compose exec frontend npm install
```

### Permission Issues (Linux/Mac)

```bash
# Fix Laravel storage permissions
docker-compose exec backend chown -R www-data:www-data /var/www/html/storage
docker-compose exec backend chmod -R 755 /var/www/html/storage
```

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

### Execution Environment

Code execution happens entirely in the browser using:
- JavaScript: `eval()` with console capture
- Future languages: WebAssembly-based runtimes (Pyodide, etc.)

**Security Note**: Current implementation uses `eval()` for JavaScript execution. In production, consider using a sandboxed environment or server-side execution.

## Production Deployment

### Building for Production

```bash
# Build optimized containers
docker-compose -f docker-compose.prod.yml build

# Run in production mode
docker-compose -f docker-compose.prod.yml up -d
```

### Production Checklist

- [ ] Set `APP_ENV=production` in backend `.env`
- [ ] Generate secure `APP_KEY`: `php artisan key:generate`
- [ ] Use strong database passwords
- [ ] Enable HTTPS for WebSocket (`wss://`)
- [ ] Configure CORS for production domain
- [ ] Set up proper logging and monitoring
- [ ] Use production-grade database (not Docker MySQL)
- [ ] Implement rate limiting
- [ ] Add authentication if required
- [ ] Set up automated backups

## Testing

### Backend Tests

```bash
# Run PHPUnit tests
docker-compose exec backend php artisan test
```

### Frontend Tests

```bash
# Run Vitest tests
docker-compose exec frontend npm run test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Follow the OpenAPI specification for API changes
5. Test your changes
6. Submit a pull request

## License

MIT License - feel free to use this project for your interviews!

## Support

For issues and questions:
- Check the troubleshooting section
- Review the OpenAPI specification
- Check Docker logs: `docker-compose logs`

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
