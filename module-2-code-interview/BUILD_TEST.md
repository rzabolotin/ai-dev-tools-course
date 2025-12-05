# Local Production Build Testing

Quick guide to test the production build locally before deploying.

## Prerequisites

- Docker installed
- External MySQL database (or use local MySQL)

## Option 1: Test with Local MySQL

### Step 1: Start MySQL

```bash
docker run -d \
  --name mysql-test \
  -e MYSQL_ROOT_PASSWORD=secret \
  -e MYSQL_DATABASE=code_interview \
  -p 3306:3306 \
  mysql:8.0
```

### Step 2: Build Production Image

```bash
docker build -f Dockerfile.prod -t code-interview:prod .
```

This will:
- Build Vue frontend with Vite
- Copy built static files to backend
- Create production-ready Python image

**Expected build time:** 2-4 minutes

### Step 3: Run Production Container

```bash
docker run -d \
  --name code-interview-test \
  -p 8000:8000 \
  -e DATABASE_URL="mysql+aiomysql://root:secret@host.docker.internal:3306/code_interview" \
  code-interview:prod
```

**Note:** `host.docker.internal` allows container to access host's MySQL.

### Step 4: Test the Application

Wait ~10 seconds for startup, then test:

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status":"healthy","service":"code-interview-api"}

# Create session
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"language":"javascript","code":"console.log(\"test\")"}'

# Open in browser
open http://localhost:8000
```

### Step 5: Verify Features

1. **Frontend loads:** Visit `http://localhost:8000` → Should see landing page
2. **Create session:** Click "Create Session" → Should redirect to `/session/{id}`
3. **Real-time sync:** Open same session URL in 2 tabs → Type in one, see in other
4. **Language switch:** Change language → Should sync across tabs
5. **Code execution:** Run JavaScript code → Should show output

### Step 6: Check Logs

```bash
docker logs -f code-interview-test
```

Should see:
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 7: Cleanup

```bash
docker stop code-interview-test mysql-test
docker rm code-interview-test mysql-test
```

## Option 2: Test with Docker Compose

Create `docker-compose.test.yml`:

```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: secret
      MYSQL_DATABASE: code_interview
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      timeout: 5s
      retries: 10

  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+aiomysql://root:secret@db:3306/code_interview
    depends_on:
      db:
        condition: service_healthy
```

Run:
```bash
docker-compose -f docker-compose.test.yml up --build
```

Test at: `http://localhost:8000`

Cleanup:
```bash
docker-compose -f docker-compose.test.yml down -v
```

## Option 3: Test with External Database

If you already have Railway/PlanetScale database:

```bash
# Build
docker build -f Dockerfile.prod -t code-interview:test .

# Run with your external DB
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="mysql+aiomysql://user:pass@your-db-host:3306/dbname" \
  code-interview:test

# Test
curl http://localhost:8000/health
open http://localhost:8000
```

## Verify Build Contents

### Check static files are included:

```bash
# List files in built image
docker run --rm code-interview:test ls -la static/

# Should show:
# index.html
# assets/
# favicon.ico
# etc.
```

### Check backend files:

```bash
docker run --rm code-interview:test ls -la app/

# Should show:
# main.py
# models.py
# schemas.py
# database.py
# etc.
```

### Check image size:

```bash
docker images code-interview:test

# Expected size: 400-600 MB
# frontend-build stage not included (multi-stage build)
```

## Troubleshooting

### Build Fails at Frontend Stage

**Error:** `npm ci` fails

**Fix:**
```bash
# Check package-lock.json exists
ls frontend/package-lock.json

# If missing, generate it
cd frontend && npm install && cd ..

# Try build again
docker build -f Dockerfile.prod -t code-interview:test .
```

### Build Fails at Backend Stage

**Error:** `pip install` fails

**Fix:**
```bash
# Check requirements.txt
cat backend_fastapi/requirements.txt

# Test locally
cd backend_fastapi
pip install -r requirements.txt
```

### Container Starts but Frontend Shows 404

**Debug:**
```bash
# Check if static files exist
docker exec code-interview-test ls static/

# Check main.py is mounting static files
docker exec code-interview-test grep -n "StaticFiles" app/main.py
```

**Fix:** Ensure `app.mount("/", StaticFiles...)` is AFTER all API routes in `main.py`

### Database Connection Fails

**Error:** `Can't connect to MySQL server`

**Solutions:**

1. **Check connection string format:**
   - Must be: `mysql+aiomysql://...` (with `+aiomysql`)
   - Not just: `mysql://...`

2. **Check MySQL is accessible:**
   ```bash
   # From host
   mysql -h localhost -u root -p

   # From container
   docker exec code-interview-test ping db  # if using docker-compose
   ```

3. **Check MySQL is ready:**
   ```bash
   docker logs mysql-test | grep "ready for connections"
   ```

### WebSocket Connection Fails in Browser

**Check:**
1. Browser console shows WebSocket errors
2. Container logs show WebSocket connections

**Fix:**
- WebSocket should work automatically on same port (8000)
- Check `config.ts` is using correct protocol (ws:// for http, wss:// for https)

## Performance Testing

### Measure startup time:

```bash
time docker run --rm \
  -e DATABASE_URL="..." \
  code-interview:test \
  python -c "from app.main import app; print('Started')"
```

### Load testing:

```bash
# Install Apache Bench
apt-get install apache2-utils  # Linux
brew install apache2            # Mac

# Test API endpoint
ab -n 1000 -c 10 http://localhost:8000/health

# Test static files
ab -n 1000 -c 10 http://localhost:8000/
```

## Build Optimization

### Check layer sizes:

```bash
docker history code-interview:test
```

### Reduce build time with cache:

```bash
# First build (slow)
docker build -f Dockerfile.prod -t code-interview:test .

# Subsequent builds use cache (fast)
# Only rebuilds changed layers
docker build -f Dockerfile.prod -t code-interview:test .
```

### Build without cache (clean build):

```bash
docker build --no-cache -f Dockerfile.prod -t code-interview:test .
```

## What to Test Before Production

- [ ] Health endpoint returns 200
- [ ] Can create session via API
- [ ] Frontend loads at root `/`
- [ ] Can create session from UI
- [ ] Real-time sync works (open 2 tabs)
- [ ] Language switching works
- [ ] Code execution works (JavaScript/TypeScript)
- [ ] WebSocket connects successfully
- [ ] Database persists data (restart container, session still exists)
- [ ] No errors in container logs
- [ ] Container uses reasonable resources (<512MB RAM)

## CI/CD Testing

If using GitHub Actions:

```yaml
# .github/workflows/test-build.yml
name: Test Production Build

on: [push, pull_request]

jobs:
  test-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build production image
        run: docker build -f Dockerfile.prod -t code-interview:test .

      - name: Start services
        run: |
          docker run -d --name db -e MYSQL_ROOT_PASSWORD=secret -e MYSQL_DATABASE=code_interview mysql:8.0
          sleep 10
          docker run -d --name app -p 8000:8000 --link db \
            -e DATABASE_URL="mysql+aiomysql://root:secret@db:3306/code_interview" \
            code-interview:test
          sleep 5

      - name: Test health endpoint
        run: curl -f http://localhost:8000/health

      - name: Test API
        run: |
          curl -f -X POST http://localhost:8000/api/sessions \
            -H "Content-Type: application/json" \
            -d '{"language":"javascript"}'
```

## Next Steps

After successful local test:
1. ✅ Push to GitHub
2. ✅ Deploy to Railway (see RAILWAY.md)
3. ✅ Test production URL
4. ✅ Monitor for issues
