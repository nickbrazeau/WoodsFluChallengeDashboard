# Deploy Dashboard to GitHub Pages

## Simple 3-Step Process

Your dashboard is ready to deploy! Follow these steps:

---

## Step 1: Create GitHub Repository (2 minutes)

### Option A: Via GitHub Website (Easiest)

1. Go to https://github.com/new
2. **Repository name**: `WoodsDashboard` (or any name you prefer)
3. **Description**: "Woods Lab Influenza Challenge Studies Dashboard"
4. **Visibility**: Choose Public or Private
5. **DO NOT** check "Initialize with README" (we already have files)
6. Click **"Create repository"**

### Option B: Via GitHub CLI

```bash
# If you have gh CLI installed
gh repo create WoodsDashboard --public --source=. --remote=origin
```

---

## Step 2: Connect Your Local Repository (1 minute)

After creating the GitHub repository, you'll see a URL like:
`https://github.com/YOUR-USERNAME/WoodsDashboard.git`

Run these commands from the `WoodsDashboard` directory:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Woods Lab Dashboard"

# Connect to GitHub (replace YOUR-USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR-USERNAME/WoodsDashboard.git

# Push main branch
git branch -M main
git push -u origin main
```

---

## Step 3: Deploy to GitHub Pages (30 seconds)

### Automated Deployment (Recommended)

Run the deployment script I created:

```bash
./deploy-to-github.sh
```

This script will:
- ✅ Check your git configuration
- ✅ Copy `public/` folder to gh-pages branch
- ✅ Push to GitHub
- ✅ Give you the live URL

### Manual Deployment (If you prefer)

```bash
cd public
git init
git add .
git commit -m "Deploy dashboard"
git branch -M gh-pages
git remote add origin https://github.com/YOUR-USERNAME/WoodsDashboard.git
git push -u origin gh-pages
cd ..
```

---

## Step 4: Enable GitHub Pages (1 minute)

1. Go to your GitHub repository: `https://github.com/YOUR-USERNAME/WoodsDashboard`
2. Click **Settings** (top menu)
3. Click **Pages** (left sidebar)
4. Under "Build and deployment":
   - **Source**: "Deploy from a branch"
   - **Branch**: Select `gh-pages`
   - **Folder**: Select `/ (root)`
5. Click **Save**

### Wait for Deployment

GitHub will show: "Your site is live at https://YOUR-USERNAME.github.io/WoodsDashboard/"

⏱️ **Note**: First deployment takes 1-3 minutes. Refresh the Settings → Pages to see status.

---

## 🎉 Your Dashboard is Live!

Visit: `https://YOUR-USERNAME.github.io/WoodsDashboard/`

---

## Updating the Dashboard Later

When you update data or make changes:

### Option 1: Use Deployment Script (Easiest)

```bash
# Update data
source venv/bin/activate
python src/data-munging/convert_data_for_dashboard.py

# Deploy
./deploy-to-github.sh
```

### Option 2: Manual Update

```bash
# Update data
source venv/bin/activate
python src/data-munging/convert_data_for_dashboard.py

# Deploy manually
cd public
git add .
git commit -m "Update dashboard data"
git push origin gh-pages
cd ..
```

---

## Troubleshooting

### "remote: Permission denied"

You need to authenticate with GitHub. Options:

**Option A: Use Personal Access Token**
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Use token as password when pushing

**Option B: Use SSH**
```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
cat ~/.ssh/id_ed25519.pub

# Change remote to SSH
git remote set-url origin git@github.com:YOUR-USERNAME/WoodsDashboard.git
```

### "gh-pages branch already exists"

```bash
# Delete and recreate
git branch -D gh-pages
./deploy-to-github.sh
```

### "Site not loading after deployment"

- Wait 2-3 minutes for GitHub to build
- Check Settings → Pages for deployment status
- Ensure branch is set to `gh-pages` and folder is `/ (root)`
- Try accessing `https://YOUR-USERNAME.github.io/WoodsDashboard/index.html`

---

## Custom Domain (Optional)

If you want to use your own domain (e.g., `dashboard.woodslab.org`):

1. **In GitHub**:
   - Settings → Pages → Custom domain
   - Enter your domain: `dashboard.woodslab.org`
   - Click Save

2. **In Your DNS Provider**:
   - Add CNAME record:
     - Name: `dashboard` (or `@` for root domain)
     - Value: `YOUR-USERNAME.github.io`
   - Or add A records for apex domain:
     ```
     185.199.108.153
     185.199.109.153
     185.199.110.153
     185.199.111.153
     ```

3. **Wait for DNS propagation** (5 minutes to 24 hours)

4. **Enable HTTPS** in GitHub Pages settings (automatic)

---

## Comparison: This Method vs Hugo

**This Method (Direct Static Site):**
- ✅ Simpler - no build step
- ✅ Faster - just copy files
- ✅ Easier to update - change HTML/CSS directly
- ✅ No dependencies (Hugo installation)
- ✅ Dashboard already built and ready

**Hugo Method:**
- 📝 Requires Hugo installation
- 📝 Need to create Hugo templates
- 📝 Need to run `hugo build` each time
- 📝 More complex file structure
- ✅ Better for blogs/documentation sites

**For this dashboard**: Direct deployment is better because it's already a complete static site!

---

## Next Steps After Deployment

Once live, you can:

1. **Share the URL** with lab members and collaborators
2. **Add to project README** for visibility
3. **Set up custom domain** if needed
4. **Update data regularly** using the deployment script

---

## Quick Reference Commands

```bash
# Initial Setup (one time)
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR-USERNAME/WoodsDashboard.git
git push -u origin main

# Deploy Dashboard (first time and updates)
./deploy-to-github.sh

# Update Data (when needed)
source venv/bin/activate
python src/data-munging/convert_data_for_dashboard.py
./deploy-to-github.sh
```

---

## Need Help?

- **GitHub Pages docs**: https://docs.github.com/en/pages
- **GitHub authentication**: https://docs.github.com/en/authentication
- **Custom domains**: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site

---

**Ready to deploy? Start with Step 1 above!** 🚀
