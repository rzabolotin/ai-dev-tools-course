# Production Deployment Guide

## Overview

This guide covers deploying the code interview platform to production using the multi-stage Docker build that combines FastAPI backend and Nuxt 3 frontend in a single container.

## Architecture

**Production Setup:**
- Single Docker container running both backend (FastAPI) and frontend (Nuxt static files)
- External MySQL database (Railway, PlanetScale, or any managed MySQL)
- FastAPI serves both API endpoints and static frontend files

## Building the Production Image

```bash
# Build the production image
docker build -f Dockerfile.prod -t code-interview:latest .

# Test locally with external database
docker run -p 8000:8000 \
  -e DATABASE_URL="mysql+aiomysql://user:pass@host:3306/dbname" \
  code-interview:latest
```

## Deployment Options

### Option 1: Railway (Recommended)

Railway provides managed MySQL and easy Docker deployments.

**Steps:**

1. **Create MySQL Database:**
   - Go to Railway dashboard → New → Database → MySQL
   - Note the connection string from variables tab

2. **Deploy Application:**
   - Connect your GitHub repository
   - Railway will auto-detect `Dockerfile.prod`
   - Add environment variable: `DATABASE_URL=<your-mysql-url>`
   - Format: `mysql+aiomysql://root:password@containers-us-west-xxx.railway.app:3306/railway`

3. **Configure:**
   - Railway will automatically assign a public domain
   - Port 8000 will be exposed automatically
   - SSL/HTTPS handled by Railway

**Railway-specific tips:**
- Use Railway's MySQL addon for automatic configuration
- Enable "Watchpaths" if you want to trigger rebuilds on specific file changes
- Check logs via `railway logs`

### Option 2: Docker Compose with External DB

If you have your own server with Docker:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+aiomysql://user:pass@external-db-host:3306/dbname
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Deploy:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Option 3: Manual Docker Deployment

```bash
# Build
docker build -f Dockerfile.prod -t code-interview:prod .

# Run with external database
docker run -d \
  --name code-interview \
  -p 8000:8000 \
  -e DATABASE_URL="mysql+aiomysql://user:pass@host:3306/dbname" \
  --restart unless-stopped \
  code-interview:prod

# Check logs
docker logs -f code-interview
```

## Database Setup

### External MySQL Configuration

The application requires an external MySQL database. Supported providers:

1. **Railway MySQL** (recommended for Railway deployment)
   ```
   mysql+aiomysql://root:password@containers-us-west-xxx.railway.app:3306/railway
   ```

2. **PlanetScale** (serverless MySQL)
   ```
   mysql+aiomysql://user:pass@aws.connect.psdb.cloud/dbname?ssl_ca=/etc/ssl/cert.pem
   ```

3. **AWS RDS / DigitalOcean MySQL**
   ```
   mysql+aiomysql://admin:password@db.region.rds.amazonaws.com:3306/codeinterview
   ```

### Database Initialization

Tables are created automatically on first startup via SQLAlchemy's `create_all()`.

**Manual table creation (if needed):**
```sql
CREATE TABLE interview_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(16) UNIQUE NOT NULL,
    code TEXT,
    language VARCHAR(50) DEFAULT 'javascript',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## Environment Variables

Required environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | MySQL connection string | `mysql+aiomysql://user:pass@host:3306/db` |

Optional:

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Runtime environment | `production` |
| `CORS_ORIGINS` | Allowed CORS origins | `*` (all origins) |

## Configuration Files

- `.env.production.example` - Template for environment variables
- `Dockerfile.prod` - Multi-stage production build
- `.dockerignore` - Excludes unnecessary files from build

## Post-Deployment Checks

1. **Health Check:**
   ```bash
   curl https://your-domain.com/health
   # Should return: {"status":"healthy","service":"code-interview-api"}
   ```

2. **API Test:**
   ```bash
   curl -X POST https://your-domain.com/api/sessions \
     -H "Content-Type: application/json" \
     -d '{"language":"javascript","code":"console.log(\"test\")"}'
   ```

3. **Frontend Test:**
   - Visit `https://your-domain.com` in browser
   - Should see the landing page

4. **WebSocket Test:**
   - Create a session
   - Open in two browser tabs
   - Verify real-time code synchronization

## Troubleshooting

### Database Connection Issues

**Error:** `Can't connect to MySQL server`

**Solutions:**
- Verify `DATABASE_URL` format: `mysql+aiomysql://...`
- Check database host is accessible from container
- Ensure database user has permissions
- For Railway: check database is in same project

### Static Files Not Serving

**Error:** 404 on root path

**Solutions:**
- Verify Nuxt build succeeded: `ls frontend/.output/public`
- Check `static` directory exists in container: `docker exec <container> ls static`
- Ensure `app.mount("/", ...)` is AFTER all API routes in `main.py`

### WebSocket Connection Fails

**Error:** WebSocket connection refused

**Solutions:**
- WebSocket uses same port as HTTP (8000)
- Check `--proxy-headers` flag in uvicorn command
- Verify reverse proxy (if used) supports WebSocket upgrade
- Railway automatically handles WebSocket proxying

## Monitoring

### Logs
```bash
# Railway
railway logs

# Docker
docker logs -f code-interview

# Docker Compose
docker-compose -f docker-compose.prod.yml logs -f
```

### Health Endpoint
The `/health` endpoint can be used for monitoring:
```bash
# Add to monitoring tool (UptimeRobot, etc.)
GET https://your-domain.com/health
```

### Metrics to Monitor
- Response time for `/health`
- Database connection pool status
- WebSocket connection count
- Container CPU/memory usage

## Scaling Considerations

### Horizontal Scaling

**Current limitation:** WebSocket connections are in-memory.

**For multi-instance deployment, add Redis:**

1. Install Redis client: `pip install redis`
2. Update `websocket_manager.py` to use Redis pub/sub
3. Broadcast messages via Redis instead of in-memory dict

**Without Redis:** Deploy as single instance (sufficient for most use cases)

### Vertical Scaling

Increase container resources:
```bash
# Railway: Adjust in dashboard
# Docker: Add resource limits
docker run --cpus=2 --memory=2g ...
```

## Security

**Production checklist:**

- ✅ Non-root user in container (appuser:1000)
- ✅ Health checks enabled
- ✅ Database connection uses external managed service
- ✅ SSL/HTTPS (handled by Railway/reverse proxy)
- ⚠️ CORS set to `*` (restrict in production if needed)
- ⚠️ No authentication (add if needed for private use)

**To restrict CORS:**
```python
# In main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Rollback

### Railway
- Go to deployments → select previous deployment → "Redeploy"

### Docker
```bash
# Tag previous version
docker tag code-interview:prod code-interview:v1

# Rollback
docker stop code-interview
docker rm code-interview
docker run -d --name code-interview code-interview:v1
```

## Cost Estimation

### Railway (Hobby Plan - $5/mo)
- 500MB MySQL database
- $5 credit includes ~100 hours of app runtime
- Additional usage: $0.000231/GB-hour

### Railway (Pro Plan - $20/mo)
- Larger database options
- More execution hours
- Priority support

### Self-Hosted (DigitalOcean/AWS)
- Droplet/EC2: $5-10/mo
- Managed MySQL: $15-25/mo
- **Total:** ~$20-35/mo

## Support

**Issues?**
- Check logs first
- Verify environment variables
- Test database connectivity
- Review Railway/platform-specific docs

**Common commands:**
```bash
# Railway
railway logs --tail 100
railway shell  # SSH into container

# Docker
docker exec -it code-interview bash
docker inspect code-interview
```
