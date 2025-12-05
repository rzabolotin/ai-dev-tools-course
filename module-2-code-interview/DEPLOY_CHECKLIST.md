# Production Deployment Checklist

Quick checklist to ensure successful deployment.

## Pre-Deployment

- [ ] All changes committed to git
- [ ] Tests passing (if any)
- [ ] `Dockerfile.prod` exists in repository root
- [ ] `.dockerignore` configured
- [ ] Frontend builds successfully locally: `cd frontend && npm run build`
- [ ] Backend starts without errors locally

## Railway Setup

- [ ] Railway account created
- [ ] MySQL database provisioned in Railway
- [ ] `DATABASE_URL` copied from MySQL variables
- [ ] GitHub repository connected to Railway
- [ ] `Dockerfile.prod` detected by Railway

## Environment Configuration

- [ ] `DATABASE_URL` environment variable set in Railway
  - Format: `mysql+aiomysql://user:pass@host:3306/dbname`
  - **Important:** Must have `+aiomysql`, not just `mysql://`
- [ ] No other environment variables needed (production auto-detected)

## Deployment

- [ ] Railway deployment triggered (auto or manual)
- [ ] Build logs show no errors
- [ ] Both frontend and backend stages complete
- [ ] Container starts successfully
- [ ] No error logs in Railway dashboard

## Post-Deployment Verification

### Health Check
- [ ] `/health` endpoint returns 200
  ```bash
  curl https://your-app.up.railway.app/health
  ```
  Expected: `{"status":"healthy","service":"code-interview-api"}`

### API Tests
- [ ] Can create session via API
  ```bash
  curl -X POST https://your-app.up.railway.app/api/sessions \
    -H "Content-Type: application/json" \
    -d '{"language":"javascript","code":"console.log(\"test\")"}'
  ```
  Expected: JSON with `session_id`

### Frontend Tests
- [ ] Root URL loads landing page
- [ ] Can click "Create Session"
- [ ] Redirects to `/session/{id}`
- [ ] Code editor loads
- [ ] Can type in editor

### Real-Time Sync Tests
- [ ] Open session URL in 2 browser tabs/windows
- [ ] Type in tab 1, appears in tab 2 (within ~100ms)
- [ ] Change language in tab 1, updates in tab 2
- [ ] No duplicate characters (no "echo")
- [ ] Console shows WebSocket connected

### WebSocket Tests
- [ ] Browser console shows: `WebSocket connection established`
- [ ] No WebSocket errors in console
- [ ] No WebSocket errors in Railway logs
- [ ] WebSocket auto-reconnects after brief disconnection

### Database Tests
- [ ] Session data persists after page refresh
- [ ] Can join existing session from different device
- [ ] Code remains after app restart (Railway redeploy)

## Performance Checks

- [ ] Page load time < 3 seconds
- [ ] API response time < 500ms
- [ ] WebSocket latency < 200ms
- [ ] No memory leaks (check Railway metrics after 10 min)
- [ ] Container uses < 512MB RAM

## Security Checks

- [ ] HTTPS enabled (Railway provides automatically)
- [ ] WebSocket uses WSS (secure WebSocket)
- [ ] No sensitive data in logs
- [ ] No API keys exposed in frontend
- [ ] CORS configured (currently allows all - OK for demo)

## Documentation

- [ ] README.md up to date
- [ ] RAILWAY.md has correct instructions
- [ ] Production URL documented
- [ ] Known issues documented (if any)

## Monitoring Setup

- [ ] Railway logs accessible
- [ ] Health endpoint can be pinged by monitoring service
- [ ] Alerts configured for downtime (optional)

## Rollback Plan

- [ ] Know how to rollback in Railway (Deployments → Redeploy previous)
- [ ] Previous deployment still available
- [ ] Database backup available (optional)

## Optional Enhancements

- [ ] Custom domain configured
- [ ] SSL certificate verified
- [ ] CDN configured (if needed)
- [ ] Analytics added (optional)
- [ ] Error tracking (Sentry, etc.) - optional

## Common Issues & Solutions

### Build Fails

**Symptom:** Red deployment in Railway

**Check:**
1. Build logs show specific error
2. `Dockerfile.prod` exists in repo
3. All files referenced in Dockerfile exist

**Fix:** Check build logs, fix error, push to git

### App Starts But 404 on Root

**Symptom:** API works (`/health` returns 200) but `/` shows 404

**Check:**
1. Frontend build succeeded (check logs for "npm run build")
2. `dist/` files copied to `static/` (check Dockerfile)
3. `main.py` mounts static files AFTER API routes

**Fix:** Check Dockerfile stage 2, ensure COPY command correct

### Database Connection Fails

**Symptom:** App starts but crashes immediately, logs show MySQL error

**Check:**
1. `DATABASE_URL` format: `mysql+aiomysql://...`
2. MySQL service is running in Railway
3. Both services in same Railway project

**Fix:** Update `DATABASE_URL` format, redeploy

### WebSocket Doesn't Connect

**Symptom:** Editor works but changes don't sync

**Check:**
1. Browser console shows WebSocket error
2. Check URL protocol (should be `wss://` for https)
3. `config.ts` auto-detection working

**Fix:** Check `frontend/src/config.ts`, ensure `window.location.protocol` logic correct

### Changes Sync But Echo Back

**Symptom:** Typing shows duplicate characters

**Check:**
1. `client_id` query parameter in API calls
2. Backend using `exclude_client_id` in broadcast
3. WebSocket sending `clientId` on connect

**Fix:** Check `api.ts` includes `clientId` in URLs

## Success Criteria

All must be ✅:

- [x] Health endpoint returns 200
- [x] Can create and join sessions
- [x] Real-time sync works between 2+ clients
- [x] Code persists after page refresh
- [x] No errors in browser console
- [x] No errors in Railway logs
- [x] WebSocket connection stable
- [x] Performance acceptable (< 3s page load)

## Next Steps After Successful Deploy

1. Share URL with users
2. Monitor Railway logs for first hour
3. Test with real users
4. Gather feedback
5. Plan improvements

## Emergency Contacts

- Railway Status: https://status.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: (your repo issues page)

---

**Deployment Date:** _______________

**Deployed By:** _______________

**Production URL:** _______________

**Railway Project:** _______________

**Notes:**
