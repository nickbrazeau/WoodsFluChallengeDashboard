# Dashboard Deployment Guide

## Quick Deploy Options

Your dashboard is a static website in the `public/` folder. Here are the easiest ways to deploy it:

---

## Option 1: Netlify Drop (Easiest - 2 minutes)

**No command line, no git required!**

1. Go to: https://app.netlify.com/drop
2. Drag the entire `public/` folder onto the page
3. Done! You'll get a URL like `https://random-name-123.netlify.app`

**To customize the URL:**
- Click "Site settings" → "Change site name"
- Choose something like `woods-lab-dashboard.netlify.app`

**To update later:**
- Just drag the `public/` folder again to the same site

---

## Option 2: GitHub Pages (Free, Custom Domain)

### Step 1: Create GitHub Repository

```bash
# From the WoodsDashboard directory
git init
git add .
git commit -m "Initial commit: Woods Lab Dashboard"
```

### Step 2: Push to GitHub

```bash
# Create a new repo on github.com, then:
git remote add origin https://github.com/YOUR-USERNAME/WoodsDashboard.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy `public/` folder to GitHub Pages

```bash
cd public
git init
git add .
git commit -m "Deploy dashboard"
git branch -M gh-pages
git remote add origin https://github.com/YOUR-USERNAME/WoodsDashboard.git
git push -u origin gh-pages
```

### Step 4: Enable GitHub Pages

1. Go to your repo on GitHub
2. Settings → Pages
3. Source: "Deploy from a branch"
4. Branch: `gh-pages` / `root`
5. Save

Your site will be at: `https://YOUR-USERNAME.github.io/WoodsDashboard/`

---

## Option 3: Vercel (Fast, Professional)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd public
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (your account)
# - Link to existing project? No
# - What's your project's name? woods-lab-dashboard
# - In which directory is your code located? ./
```

You'll get a URL like `https://woods-lab-dashboard.vercel.app`

**To update:**
```bash
cd public
vercel --prod
```

---

## Option 4: AWS S3 (If You Have AWS)

### Step 1: Create S3 Bucket

```bash
aws s3 mb s3://woods-lab-dashboard
```

### Step 2: Enable Static Website Hosting

```bash
aws s3 website s3://woods-lab-dashboard \
  --index-document index.html \
  --error-document index.html
```

### Step 3: Upload Files

```bash
cd public
aws s3 sync . s3://woods-lab-dashboard --acl public-read
```

### Step 4: Set Bucket Policy

Save this as `bucket-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::woods-lab-dashboard/*"
    }
  ]
}
```

Apply it:
```bash
aws s3api put-bucket-policy \
  --bucket woods-lab-dashboard \
  --policy file://bucket-policy.json
```

Your site will be at: `http://woods-lab-dashboard.s3-website-us-east-1.amazonaws.com`

---

## Option 5: Local Network (Lab Internal)

If you want to host on a lab server:

### Using Python (Simple)

```bash
cd public
python3 -m http.server 8000
```

Access at: `http://your-server-ip:8000`

### Using Nginx (Production)

```bash
# Install nginx
sudo apt install nginx  # Ubuntu/Debian
# or
brew install nginx      # macOS

# Copy files
sudo cp -r public/* /var/www/html/

# Start nginx
sudo systemctl start nginx  # Linux
# or
brew services start nginx   # macOS
```

Access at: `http://your-server-ip`

---

## Recommended: Netlify Drop

For the fastest deployment with zero configuration:

1. Go to https://app.netlify.com/drop
2. Drag `public/` folder
3. Done!

---

## Updating After Deployment

Whenever you update the data:

```bash
# Re-run conversion script
source venv/bin/activate
python src/data-munging/convert_data_for_dashboard.py

# Then redeploy using your chosen method:
# - Netlify: Drag the public/ folder again
# - GitHub Pages: git push from public/
# - Vercel: vercel --prod from public/
# - S3: aws s3 sync . s3://bucket-name
```

---

## Custom Domain (Optional)

All these services support custom domains:

**Netlify:**
- Settings → Domain management → Add custom domain
- Add DNS records at your domain provider

**GitHub Pages:**
- Settings → Pages → Custom domain
- Add CNAME record at your domain provider

**Vercel:**
- Settings → Domains → Add domain
- Add DNS records at your domain provider

---

## Need Help?

- **Netlify docs**: https://docs.netlify.com/
- **GitHub Pages docs**: https://docs.github.com/en/pages
- **Vercel docs**: https://vercel.com/docs

**Recommended for you**: Start with Netlify Drop - it's the easiest and you can always migrate later!
