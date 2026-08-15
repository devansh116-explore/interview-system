# Render.com Deployment Guide

## Prerequisites

1. **GitHub Account** — Push your code to a GitHub repo
2. **Render Account** — Sign up at render.com
3. **Node.js 18+** — For frontend build

---

## Deployment Steps

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/<YOUR-USERNAME>/pgagi-interview-system.git
git branch -M main
git push -u origin main
```

### 2. Connect Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize Render to access your repositories

### 3. Deploy via render.yaml

If you have a `render.yaml` file in your repo root, Render will auto-detect it:

1. Click **New +** → **Blueprint**
2. Select your GitHub repo
3. Name the service: `aptitude`
4. Click **Create Blueprint**
5. Render will parse `render.yaml` and create all services

---

## Manual Alternative (Without render.yaml)

### Backend Service

1. Click **New +** → **Web Service**
2. Connect your GitHub repo
3. Set:
   - **Name**: `aptitude-backend`
   - **Environment**: Python
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`
4. Add Environment Variables:
   - `PYTHONUNBUFFERED` = `true`
   - `FRONTEND_ORIGIN` = `https://aptitude-frontend.onrender.com`
5. Click **Create Web Service**

### Frontend Service

1. Click **New +** → **Static Site**
2. Connect the same GitHub repo
3. Set:
   - **Name**: `aptitude-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish directory**: `frontend/dist`
4. Add Environment Variables:
   - `VITE_API_BASE_URL` = `https://aptitude-backend.onrender.com`
5. Click **Create Static Site**

---

## Environment Variables Reference

### Backend
- `PYTHONUNBUFFERED` = `true` (show logs in real-time)
- `FRONTEND_ORIGIN` = Your frontend URL (for CORS)
- `DATABASE_URL` = Auto-set if using Render Postgres (optional)

### Frontend
- `VITE_API_BASE_URL` = Your backend URL (e.g., `https://aptitude-backend.onrender.com`)

---

## Verify Deployment

1. **Backend URL**: `https://aptitude-backend.onrender.com/api/roles`
   - Should return list of 4 roles (AI/ML, Backend, Data Science, Frontend)

2. **Frontend URL**: `https://aptitude-frontend.onrender.com`
   - Should show the Aptitude logo and resume upload screen

3. **CORS Check**: Upload a resume in the frontend
   - Should connect to backend without CORS errors

---

## Post-Deployment

### Connect to Production Database (Optional)

If you want persistent data across restarts, migrate to Render Postgres:

1. Go to Backend Service → **Data** tab
2. Click **Create Postgres Database**
3. Update `DATABASE_URL` environment variable
4. Render will handle SSL connections automatically

### Monitor Logs

1. Go to Service → **Logs** tab
2. See real-time output of your app
3. Debug any issues here

### Set Custom Domain (Optional)

1. Go to Service → **Settings**
2. Scroll to **Custom Domains**
3. Add your domain (requires DNS CNAME record)

---

## Cost Estimate

| Service | Plan | Cost |
|---------|------|------|
| Backend (FastAPI) | Free | $0 (free tier) / $7/month (paid) |
| Frontend (Static) | Free | $0 (included) |
| Database (SQLite) | Free | $0 (on disk) |
| **Total** | - | **$0/month** (free tier) |

Free tier sleeps after 15 minutes of inactivity. Upgrade to paid for always-on.

---

## Troubleshooting

### Backend won't start
- Check logs: Service → Logs
- Verify `backend/requirements.txt` installs without errors
- Ensure `uvicorn` is in requirements.txt

### Frontend shows blank page
- Check if `VITE_API_BASE_URL` points to correct backend URL
- Verify frontend build succeeded: Frontend Service → Logs
- Check browser console for CORS errors

### CORS errors
- Set `FRONTEND_ORIGIN` in backend to match your frontend URL
- Verify backend is running (test `/api/roles` endpoint)

### Resume upload fails
- Ensure backend has write permissions for database
- Check backend logs for SQLAlchemy errors

---

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Create Render account
3. ✅ Deploy via render.yaml or manually
4. ✅ Test all 4 stages (resume → role → interview → summary)
5. ✅ Monitor logs and add custom domain (optional)

**Your app will be live in 2-3 minutes!**
