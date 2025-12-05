# Production Deployment Guide

## Overview

This guide covers deploying the code interview platform to production using the multi-stage Docker build that combines FastAPI backend and Vue 3 frontend in a single container.

## Architecture

**Production Setup:**
- Single Docker container running both backend (FastAPI) and frontend (Vue 3 static files)
- External MySQL database (Railway, PlanetScale, or any managed MySQL)
- FastAPI serves both API endpoints and static frontend files

## Local Production Build Testing

Before deploying to production, test the build locally:

### Quick Test with Local MySQL

```bash
# Step 1: Start MySQL
docker run -d \
  --name mysql-test \
  -e MYSQL_ROOT_PASSWORD=secret \
  -e MYSQL_DATABASE=code_interview \
  -p 3306:3306 \
  mysql:8.0

# Step 2: Build production image
docker build -f Dockerfile.prod -t code-interview:prod .

# Step 3: Run production container
docker run -d \
  --name code-interview-test \
  -p 8000:8000 \
  -e DATABASE_URL="mysql+aiomysql://root:secret@host.docker.internal:3306/code_interview" \
  code-interview:prod

# Step 4: Test the application
curl http://localhost:8000/health
# Expected: {"status":"healthy","service":"code-interview-api"}

# Open in browser
open http://localhost:8000

# Step 5: Cleanup
docker stop code-interview-test mysql-test
docker rm code-interview-test mysql-test
```

**What to verify:**
- Frontend loads at `http://localhost:8000`
- Can create new session
- Real-time sync works (open same session in 2 tabs)
- Language switching syncs across tabs
- JavaScript/TypeScript code execution works


## Railway

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

## Database Setup

### External MySQL Configuration

The application requires an external MySQL database. Supported providers:

1. **Railway MySQL** (recommended for Railway deployment)
   ```
   mysql+aiomysql://root:password@containers-us-west-xxx.railway.app:3306/railway
   ```

   mysql+aiomysql://user:pass@aws.connect.psdb.cloud/dbname?ssl_ca=/etc/ssl/cert.pem
   ```

3. **AWS RDS / DigitalOcean MySQL**
   ```
   mysql+aiomysql://admin:password@db.region.rds.amazonaws.com:3306/codeinterview
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
