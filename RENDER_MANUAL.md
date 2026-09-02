# Render Deployment - Manual Setup (Corrected)

**Note:** Blueprint parsing had issues, so we'll deploy manually. This is actually simpler and more reliable.

---

## Step 1: Push Code to GitHub

```bash
cd pgagi-interview-system
git add .
git commit -m "Fix Render deployment configuration"
git push origin main
```

---

## Step 2: Create Backend Service on Render

### 2.1 Go to Dashboard
1. Visit [render.com/dashboard](https://render.com/dashboard)
2. Click **New +** button (top right)
3. Select **Web Service**

### 2.2 Connect GitHub
1. Choose **GitHub**
2. Search for `pgagi-interview-system`
3. Click **Connect**

### 2.3 Configure Backend

Fill in these fields:

| Field | Value |
|-------|-------|
| **Name** | `aptitude-backend-1` |
| **Environment** | `Python` |
| **Root Directory** | `backend` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | `Free` |
| **Region** | `Ohio` (or your choice) |

### 2.4 Add Environment Variables
Click **Advanced** → **Add Environment Variable**

Add these:
```
PYTHONUNBUFFERED = true
FRONTEND_ORIGIN = https://aptitude-frontend-1.onrender.com
```

(We'll update the frontend URL after we know it)

### 2.5 Deploy
Click **Create Web Service**

**Wait 2-3 minutes for build to complete.**

---

## Step 3: Get Backend URL

1. After build finishes, your service URL will appear (e.g., `https://aptitude-backend-xxxx.onrender.com`)
2. **Save this URL** — you'll need it for frontend
3. Test it: Visit `https://aptitude-backend-xxxx.onrender.com/api/roles`
   - Should return JSON with 4 roles ✅

---

## Step 4: Create Frontend Service on Render

### 4.1 Create Static Site
1. Click **New +** → **Static Site**
2. Select **Static Site** and choose your repo again
3. Click **Connect**

### 4.2 Configure Frontend

Fill in these fields:

| Field | Value |
|-------|-------|
| **Name** | `aptitude-frontend-1` |
| **Root Directory** | `frontend` |
| **Build Command** | `npm ci && npm run build` |
| **Publish Directory** | `dist` |
| **Node Version** | `20.18.0` (also defined in `frontend/.node-version`) |
| **Plan** | `Free` |
| **Region** | `Ohio` |

Configure the SPA rewrite from `/*` to `/index.html` so client-side routes resolve correctly.

### 4.3 Add Environment Variables
Click **Advanced** → **Add Environment Variable**

Add this:
```
VITE_API_BASE_URL = https://aptitude-backend-1.onrender.com
```
(Replace `xxxx` with actual backend service name from Step 3)

### 4.4 Deploy
Click **Create Web Service**

**Wait 2-3 minutes for build to complete.**

---

## Step 5: Update Backend FRONTEND_ORIGIN

Now that we have the frontend URL, update the backend:

### 5.1 Get Frontend URL
After frontend build completes, you'll have a URL like:
`https://aptitude-frontend-yyyy.onrender.com`

### 5.2 Update Backend Environment Variable
1. Go to Backend Service (`aptitude-backend-1`)
2. Click **Settings** (left sidebar)
3. Find `FRONTEND_ORIGIN`
4. Change value to your frontend URL
5. Click **Save**
6. Service will auto-restart

---

## Step 6: Test Everything

### 6.1 Backend Health Check
```
GET https://aptitude-backend-xxxx.onrender.com/api/roles
```
Should return 4 roles in JSON format ✅

### 6.2 Frontend Load
Visit `https://aptitude-frontend-yyyy.onrender.com`
Should show Aptitude logo and "Start with your resume" ✅

### 6.3 Full Flow Test
1. Upload a test resume (any PDF or TXT file)
2. Select a role
3. Get a question (verify it loads without errors)
4. Submit an answer
5. See next question and summary

**If all works → Deployment successful! 🎉**

---

## Troubleshooting

### Backend won't build
**Check logs:**
1. Go to Backend Service
2. Click **Logs** tab
3. Look for red error text

**Common fixes:**
- Ensure `backend/runtime.txt` contains `python-3.11.0`
- Verify `backend/requirements.txt` is valid
- Check Python imports are correct

### Frontend build fails
**Check logs:**
1. Go to Frontend Service
2. Click **Logs** tab
3. Look for `npm ERR`

**Common fixes:**
- Verify `frontend/package.json` exists
- Check `npm install` doesn't have errors
- Ensure `npm run build` works locally

### Resume upload gives CORS error
**Fix:**
1. Go to Backend Service → **Settings**
2. Update `FRONTEND_ORIGIN` to match your frontend URL exactly
3. Save and restart service
4. Wait 30 seconds
5. Try upload again

### Questions won't load
**Check:**
1. Backend logs for errors
2. Verify `/api/roles` works
3. Check if resume was parsed (should show extracted skills)
4. Ensure knowledge base files exist in repo

---

## Final Checklist

- [ ] Backend service created and building
- [ ] Backend URL accessible at `/api/roles`
- [ ] Frontend service created and building
- [ ] Frontend URL loading successfully
- [ ] `VITE_API_BASE_URL` set in frontend
- [ ] `FRONTEND_ORIGIN` set in backend
- [ ] Both services have restarted
- [ ] Resume upload works
- [ ] Interview flow completes
- [ ] Summary page displays results

---

## Service Status Links

After deployment, you can always check status:

| Service | Dashboard Link |
|---------|---|
| Backend | `render.com/dashboard` → `aptitude-backend-1` → Logs |
| Frontend | `render.com/dashboard` → `aptitude-frontend-1` → Logs |

---

## Cost Breakdown

| Service | Cost |
|---------|------|
| Backend (Python) | $0/month (free) - sleeps after 15 min inactivity |
| Frontend (Static) | $0/month (free) - always on |
| **Total** | **$0/month** |

**To always keep backend awake:** Upgrade to $7/month paid plan

---

## Success! 🚀

Your Aptitude interview system is now live and ready for use!

### Next Steps (Optional)
- Add custom domain (see DEPLOY.md)
- Monitor performance in dashboard
- Upgrade to paid if needed
- Set up alerts for errors
