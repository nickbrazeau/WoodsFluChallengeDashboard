#!/bin/bash

# Deploy Woods Lab Dashboard to GitHub Pages
# This script deploys the public/ folder to the gh-pages branch

set -e  # Exit on error

echo "======================================"
echo "Deploying Dashboard to GitHub Pages"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "public" ]; then
    echo -e "${RED}Error: public/ directory not found!${NC}"
    echo "Please run this script from the WoodsDashboard root directory"
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Git not initialized. Initializing now...${NC}"
    git init
    git add .
    git commit -m "Initial commit: Woods Lab Dashboard"
    echo -e "${GREEN}✓ Git repository initialized${NC}"
else
    echo -e "${GREEN}✓ Git repository already exists${NC}"
fi

# Check if remote exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo ""
    echo -e "${YELLOW}GitHub remote not configured.${NC}"
    echo -e "${YELLOW}Please create a repository on GitHub first, then run:${NC}"
    echo ""
    echo "  git remote add origin https://github.com/YOUR-USERNAME/WoodsDashboard.git"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo -e "${GREEN}✓ GitHub remote configured${NC}"

# Get the remote URL for display
REMOTE_URL=$(git remote get-url origin)
echo "Remote: $REMOTE_URL"

# Ask for confirmation
echo ""
echo -e "${YELLOW}This will deploy the public/ folder to GitHub Pages.${NC}"
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 1
fi

# Save current directory
ROOT_DIR=$(pwd)

# Create a temporary directory for gh-pages
TEMP_DIR=$(mktemp -d)
echo ""
echo "Copying files to temporary directory..."
# Copy all files from public/ including hidden files
cp -R public/. "$TEMP_DIR/"

# Navigate to temp directory
cd "$TEMP_DIR"

# Initialize git in temp directory
git init
git add -f .  # Force add all files including HTML
git commit -m "Deploy dashboard to GitHub Pages"

# Push to gh-pages branch (force push to overwrite)
echo ""
echo "Pushing to gh-pages branch..."
git push -f "$ROOT_DIR/.git" HEAD:gh-pages

# Clean up
cd "$ROOT_DIR"
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}======================================"
echo "✓ Deployment Complete!"
echo "======================================${NC}"
echo ""
echo "Your dashboard will be live at:"
echo -e "${GREEN}https://YOUR-USERNAME.github.io/WoodsDashboard/${NC}"
echo ""
echo "Next steps:"
echo "1. Go to your GitHub repository"
echo "2. Settings → Pages"
echo "3. Set Source to: 'Deploy from a branch'"
echo "4. Set Branch to: 'gh-pages' and folder to '/ (root)'"
echo "5. Click Save"
echo ""
echo "It may take a few minutes for the site to go live."
echo ""
