# Render Deployment - Issue & Fix

## What Went Wrong

The initial `render.yaml` used unsupported service types:

```yaml
- type: static_site      # ❌ Not valid - Render doesn't support this
- type: pserv           # ❌ Not valid - SQLite auto-provision not available
```

**Error message from Render:**
```
A Blueprint file was found, but there was an issue.
unknown type "static_site"
```

---

## What We Fixed

### Original (Broken)
```yaml
services:
  - type: web              # ✅ Valid
  - type: static_site      # ❌ INVALID - REMOVED
  - type: pserv           # ❌ INVALID - REMOVED
```

### Fixed Version
```yaml
services:
  - type: web              # Backend (Python + FastAPI)
  - type: web              # Frontend (Node + static build)
```

---

## Key Changes

### 1. Frontend Service
**Before:**
```yaml
type: static_site
env: static
```

**After:**
```yaml
type: web
env: static
staticPublishPath: frontend/dist
```

### 2. Database Service
**Before:**
```yaml
- type: pserv
  env: sqlite
  sqlite:
    dbName: aptitude
```

**After:**
**Removed** — SQLite runs on the backend service (persists to `/data/app.db`)

### 3. Environment Variables
Simplified to only what's needed:
- `PYTHONUNBUFFERED` — For real-time logging
- `FRONTEND_ORIGIN` — For CORS

Removed:
- `DATABASE_URL` — No separate DB service needed

---

## How to Deploy Now

### Option 1: Manual Setup (Recommended)
Follow `RENDER_MANUAL.md` for step-by-step instructions:
1. Create Backend Web Service
2. Create Frontend Web Service
3. Configure environment variables
4. Test both services

**Pros:**
- ✅ Clear, visual process
- ✅ Better control over settings
- ✅ Easier to debug issues
- ✅ Works reliably

**Time:** ~10 minutes

### Option 2: Blueprint (Updated)
If you want to use the corrected `render.yaml`:
1. Push updated code to GitHub
2. Go to Render Dashboard
3. Click **New +** → **Blueprint**
4. Select your repo
5. Wait for auto-deploy

**Pros:**
- ✅ One-click deploy
- ✅ Reproducible

**Cons:**
- ❌ Still experimental for complex setups
- ❌ Harder to debug if issues occur

---

## Updated render.yaml

The corrected file now has:
- 2 Web Services (backend + frontend)
- Proper environment variables
- No unsupported types
- Simplified configuration

```yaml
services:
  - type: web
    name: aptitude-backend
    env: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
    envVars:
      - key: PYTHONUNBUFFERED
        value: "true"
      - key: FRONTEND_ORIGIN
        value: https://aptitude-frontend.onrender.com

  - type: web
    name: aptitude-frontend
    env: static
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: frontend/dist
    envVars:
      - key: VITE_API_BASE_URL
        value: https://aptitude-backend.onrender.com
```

---

## Deployment Guides

| File | Use Case |
|------|----------|
| `RENDER_MANUAL.md` | **Start here** — Step-by-step visual guide |
| `RENDER_STEPS.md` | Detailed walk-through with screenshots |
| `RENDER_DEPLOY.md` | Quick reference card |
| `DEPLOY.md` | Advanced troubleshooting |

---

## Quick Deploy (Manual)

```bash
# 1. Push code
git add .
git commit -m "Fix Render deployment"
git push origin main

# 2. Go to render.com/dashboard
# 3. Create Backend Web Service
# 4. Create Frontend Web Service
# 5. Test

# Takes ~10 minutes total
```

---

## Verification

After deploy, verify both services:

### Backend
```bash
curl https://aptitude-backend-xxxx.onrender.com/api/roles
# Should return: [{"role_id": "aiml_engineer", ...}, ...]
```

### Frontend
```bash
Visit: https://aptitude-frontend-yyyy.onrender.com
# Should show: Resume upload screen
```

---

## Success! ✅

Everything is now ready to deploy. Choose your preferred method:

1. **Manual (Recommended)** → Follow `RENDER_MANUAL.md`
2. **Blueprint** → Update `render.yaml` in settings
3. **Quick** → Copy commands from `RENDER_STEPS.md`

The fixed `render.yaml` is now in your repo. Both approaches will work!
