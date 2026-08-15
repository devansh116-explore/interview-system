# Render Deployment - Step by Step

## Prerequisites
- GitHub account with repo pushed
- Render.com account (free)
- The `render.yaml` file in repo root

---

## Step 1: Prepare GitHub Repository

### 1.1 Initialize Git (if not done)
```bash
cd pgagi-interview-system
git init
git add .
git commit -m "Initial commit: Aptitude interview system"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/pgagi-interview-system.git
git push -u origin main
```

### 1.2 Verify Files in Repo
Ensure these files exist in repo root:
- ✅ `render.yaml` — Deployment config
- ✅ `backend/requirements.txt` — Python dependencies
- ✅ `frontend/package.json` — Node.js dependencies
- ✅ `frontend/vite.config.js` — Vite build config
- ✅ `DEPLOY.md` — Documentation

---

## Step 2: Create Render Account

### 2.1 Sign Up
1. Go to [render.com](https://render.com)
2. Click **Sign up**
3. Choose **Sign up with GitHub**
4. Authorize Render to access your GitHub account
5. Complete profile setup

### 2.2 Verify Authorization
1. After signup, go to [Dashboard](https://render.com/dashboard)
2. You should see "Connected to GitHub"

---

## Step 3: Deploy Using Blueprint

### 3.1 Create Blueprint
1. On Render Dashboard, click **New +** button (top right)
2. Select **Blueprint**
3. You'll see a list of your GitHub repos

### 3.2 Select Your Repository
1. Find `pgagi-interview-system` in the list
2. Click it to select
3. Confirm the branch is `main`

### 3.3 Configure Blueprint
A form will appear with 2 fields:
- **Service name**: `aptitude` (or your choice)
- **GitHub branch**: `main` (keep default)

Click **Create Blueprint**

### 3.4 Wait for Auto-Build
Render will parse `render.yaml` and create these services automatically:

```
✅ aptitude-backend      (FastAPI)
✅ aptitude-frontend     (React static site)
✅ aptitude-db          (SQLite)
```

**Build takes 2-3 minutes.** Monitor the logs in the dashboard.

---

## Step 4: Verify Deployment

### 4.1 Check Backend Status
1. Go to Dashboard
2. Click **aptitude-backend**
3. Wait for status to show **Live**
4. Click the URL (e.g., `https://aptitude-backend-xxxx.onrender.com`)
5. Visit `/api/roles` endpoint:
   ```
   https://aptitude-backend-xxxx.onrender.com/api/roles
   ```
   Should return: 4 roles (AI/ML, Backend, Data Science, Frontend)

### 4.2 Check Frontend Status
1. Go to Dashboard
2. Click **aptitude-frontend**
3. Wait for status to show **Live**
4. Click the URL (e.g., `https://aptitude-frontend-xxxx.onrender.com`)
5. Should show Aptitude logo and resume upload screen

### 4.3 Test Full Flow
1. Go to frontend URL
2. Upload a test resume (PDF or TXT)
3. Select a role
4. Try to get a question
5. If all works → **Deployment is successful! 🎉**

---

## Step 5: Fix Common Issues

### Issue: Backend build fails
**Solution:**
1. Go to Backend Service → **Logs** tab
2. Look for error messages
3. Common causes:
   - Missing Python version → Add `runtime.txt` with `python-3.11.0`
   - Missing dependency → Check `backend/requirements.txt`
4. Fix and push to GitHub
5. Render auto-redeploys on push

### Issue: Frontend shows blank page
**Solution:**
1. Go to Frontend Service → **Logs** tab
2. Check for build errors
3. Verify `npm install` succeeded
4. Check browser console (F12) for CORS errors
5. If CORS error → Backend URL might be wrong in code

### Issue: CORS errors when uploading resume
**Solution:**
1. Go to Backend Service → **Environment**
2. Verify `FRONTEND_ORIGIN` is set to your frontend URL
3. Example: `https://aptitude-frontend-xxxx.onrender.com`
4. If missing, add it manually
5. Restart backend service

### Issue: Interview questions won't load
**Solution:**
1. Check backend logs for database errors
2. Verify vector store files are building
3. Try uploading a different resume format
4. Check if knowledge base files exist in repo

---

## Step 6: Optional - Custom Domain

### 6.1 Add Custom Domain
1. Go to Backend Service → **Settings**
2. Scroll to **Custom Domains**
3. Enter your domain (e.g., `api.aptitude.com`)
4. Render will show DNS instructions

### 6.2 Add DNS CNAME Record
1. Go to your domain registrar (GoDaddy, Namecheap, etc.)
2. Find DNS settings
3. Add CNAME record:
   - **Name**: `api` (or subdomain you chose)
   - **Value**: `cname.onrender.com`
4. Wait 5-30 minutes for DNS to propagate
5. Test: `https://api.aptitude.com/api/roles`

### 6.3 Repeat for Frontend
1. Go to Frontend Service → **Settings**
2. Add custom domain for frontend
3. Add corresponding DNS CNAME record
4. Wait for propagation

---

## Step 7: Monitor & Maintain

### 7.1 View Logs
- Backend logs: Service → **Logs** tab
- Frontend logs: Service → **Logs** tab
- Database errors: Check backend logs

### 7.2 Check Performance
- Dashboard shows response times
- Free tier may have cold starts (30 sec first request after idle)
- Upgrade to Paid for always-on

### 7.3 Restart Services
If something seems stuck:
1. Go to Service → **Settings**
2. Scroll down → **Restart**
3. Service will restart in 30 seconds

### 7.4 View Disk Usage
1. Go to Backend Service → **Settings**
2. Scroll to **Disk Usage**
3. Shows SQLite database size
4. Free tier has 1GB limit

---

## Step 8: Upgrade to Paid (Optional)

### When to Upgrade
- ❌ Free tier sleeps after 15 min of inactivity
- ✅ Paid tier ($7/month) is always-on
- ✅ Better for production use

### How to Upgrade
1. Go to Backend Service → **Settings**
2. Scroll to **Plan**
3. Click **Upgrade**
4. Select **Pro** or **Standard**
5. Enter billing info
6. Service upgrades immediately

---

## Final Checklist

- [ ] Repo pushed to GitHub
- [ ] Render account created
- [ ] Blueprint deployed
- [ ] Backend shows **Live**
- [ ] Frontend shows **Live**
- [ ] `/api/roles` endpoint returns 4 roles
- [ ] Frontend homepage loads
- [ ] Resume upload works
- [ ] Interview flow works end-to-end
- [ ] Summary page loads with results

**✅ All checks pass? Your app is live and ready!**

---

## URLs After Deploy

| Service | URL Format |
|---------|-----------|
| Frontend | `https://aptitude-frontend-xxxx.onrender.com` |
| Backend API | `https://aptitude-backend-xxxx.onrender.com` |
| API Docs | `https://aptitude-backend-xxxx.onrender.com/docs` |
| Health Check | `https://aptitude-backend-xxxx.onrender.com/api/roles` |

---

## Need Help?

**Common Resources:**
- Render Docs: https://render.com/docs
- GitHub Integration: https://render.com/docs/github
- Blueprint Reference: https://render.com/docs/blueprint-spec
- Troubleshooting: https://render.com/docs/troubleshooting

**For this project:**
- See `DEPLOY.md` for detailed troubleshooting
- See `RENDER_DEPLOY.md` for quick reference
- Check backend logs for errors
- Check frontend console (F12) for errors

---

## Success! 🚀

Your Aptitude interview system is now live on the internet and ready for candidates to use!
