# GitHub Pages Deployment Guide

## 🚀 Automatic Deployment (Now Active!)

### How It Works
A GitHub Actions workflow automatically deploys your site whenever you push to the `main` branch.

**Workflow File**: `.github/workflows/deploy.yml`

### From Now On - Just Push to Main!

```bash
# Make your changes to files in public/
git add public/
git commit -m "Your changes"
git push origin main

# GitHub Actions automatically deploys to gh-pages
# Site updates in 1-3 minutes at:
# https://nicholasbrazeau.com/WoodsFluChallengeDashboard/
```

### Monitor Deployments
- View status: https://github.com/nickbrazeau/WoodsFluChallengeDashboard/actions
- ✅ Green checkmark = successful deployment
- ❌ Red X = check the logs

---

## 🔧 One-Time Setup (Already Done!)

✅ Created `.github/workflows/deploy.yml`  
✅ Configured to deploy `public/` folder to `gh-pages` branch  
✅ Workflow has write permissions  
✅ Pushed to GitHub  

**You're all set!** Future pushes to `main` will automatically deploy.

---

## 📝 Best Practices

1. **Test locally first**:
   ```bash
   cd public && python3 -m http.server 8000
   ```

2. **Check browser console** for errors before committing

3. **Hard refresh** after deployment: `Cmd + Shift + R`

---

**Last Updated**: December 1, 2025  
**Status**: ✅ Automatic deployment active
