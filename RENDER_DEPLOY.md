# Render Deployment Summary

## What's Ready

✅ **render.yaml** — Deployment blueprint in repo root  
✅ **Backend** — FastAPI app configured for Render  
✅ **Frontend** — React app with environment variables  
✅ **Database** — SQLite configured for persistence  
✅ **RAG Pipeline** — All vector stores pre-built  

---

## Quick Deploy (3 steps)

### 1. Push to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Create Render Blueprint
- Go to [render.com/dashboard](https://render.com/dashboard)
- Click **New +** → **Blueprint**
- Select your repo
- Name it `aptitude`
- Click **Create Blueprint**

### 3. Wait 2-3 minutes
- Render builds backend, frontend, and database
- Both services auto-deploy and connect
- App is live at `https://aptitude-frontend.onrender.com`

---

## Verify It Works

### Backend Health
```
GET https://aptitude-backend.onrender.com/api/roles
```
Should return 4 roles (AI/ML, Backend, Data Science, Frontend)

### Frontend
Visit `https://aptitude-frontend.onrender.com`
Should show resume upload screen

### Full Flow
1. Upload a resume
2. Pick a role
3. Answer 5 interview questions
4. See results summary

---

## Service URLs (After Deploy)

| Service | URL |
|---------|-----|
| **Frontend** | `https://aptitude-frontend.onrender.com` |
| **Backend API** | `https://aptitude-backend.onrender.com/api` |
| **API Docs** | `https://aptitude-backend.onrender.com/docs` |
| **Health Check** | `https://aptitude-backend.onrender.com/api/roles` |

---

## Environment Variables (Auto-set)

### Backend
- `PYTHONUNBUFFERED=true`
- `FRONTEND_ORIGIN=https://aptitude-frontend.onrender.com`

### Frontend  
- `VITE_API_BASE_URL=https://aptitude-backend.onrender.com`

---

## Troubleshooting

**Backend won't build?**
- Check `backend/requirements.txt` is valid
- Verify all imports are correct
- See build logs in Render dashboard

**Frontend blank?**
- Check if `VITE_API_BASE_URL` is set correctly
- Verify backend is running (test `/api/roles`)
- Check browser console for CORS errors

**Resume upload fails?**
- Ensure backend logs show no database errors
- Check disk space on Render (free tier has 1GB)
- Verify file upload endpoint works: test with curl

---

## Monitoring

### Logs
- Backend: Service dashboard → **Logs** tab
- Frontend: Service dashboard → **Logs** tab

### Performance
- Check response times in Render dashboard
- Free tier may have 15-min inactivity sleep

### Upgrades
- Backend: upgrade to Paid plan for always-on ($7/month)
- Frontend: always stays up (static site)

---

## Cost (Free Tier)

| Component | Plan | Cost |
|-----------|------|------|
| Backend | Free | $0/month (sleeps after 15 min) |
| Frontend | Free | $0/month (always on) |
| Database | Disk | $0/month (1GB free) |
| **Total** | | **$0/month** |

To remove sleep: upgrade backend to **Paid** ($7/month)

---

## Next: Custom Domain (Optional)

If you want `aptitude.yourcompany.com` instead of `.onrender.com`:

1. Go to Backend Service → **Settings** → **Custom Domain**
2. Add your domain
3. Add DNS CNAME record to your registrar
4. Wait 5 minutes for DNS propagation
5. Repeat for Frontend Service

---

## Everything You Need

✅ Backend API fully wired  
✅ Frontend fully implemented  
✅ RAG pipeline tested & verified  
✅ Database schema ready  
✅ Environment variables configured  
✅ Deployment config prepared  

**You're ready to deploy!** 🚀
