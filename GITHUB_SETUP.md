# Quick GitHub Setup Guide

## ✅ Pre-Deployment Checklist

- [x] Git repository initialized
- [x] Initial commit created
- [x] `.env` file is in `.gitignore`
- [x] `.env.example` template created
- [x] All sensitive data excluded

## 🚀 Deploy to GitHub

### Option 1: Using GitHub CLI (Recommended)

```bash
# Install GitHub CLI if not installed
# Windows: winget install GitHub.cli
# Mac: brew install gh
# Linux: sudo apt install gh

# Authenticate
gh auth login

# Create repository and push
gh repo create iot-risk-assessment-mas --public --source=. --remote=origin --push
```

### Option 2: Manual Setup

1. **Create Repository on GitHub**:
   - Go to https://github.com/new
   - Repository name: `iot-risk-assessment-mas` (or your choice)
   - Description: "Multi-Agent System for IoT Risk Assessment using LangGraph"
   - Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license
   - Click "Create repository"

2. **Connect and Push**:
   ```bash
   # Add remote (replace YOUR_USERNAME with your GitHub username)
   git remote add origin https://github.com/YOUR_USERNAME/iot-risk-assessment-mas.git
   
   # Rename branch to main (if needed)
   git branch -M main
   
   # Push to GitHub
   git push -u origin main
   ```

### Option 3: Using SSH

```bash
# Add SSH remote
git remote add origin git@github.com:YOUR_USERNAME/iot-risk-assessment-mas.git

# Push
git push -u origin main
```

## 🔒 Security Verification

After pushing, verify on GitHub:
- ✅ `.env` file is NOT visible in repository
- ✅ `.env.example` is visible (template only)
- ✅ No API keys in any code files
- ✅ `.gitignore` is working correctly

## 📝 Post-Deployment Steps

1. **Add Repository Description**:
   - Go to repository Settings → General
   - Add description and topics: `multi-agent-system`, `langgraph`, `iot`, `risk-assessment`

2. **Add License** (Optional):
   ```bash
   # Create LICENSE file (MIT example)
   # Then commit and push
   git add LICENSE
   git commit -m "Add MIT license"
   git push
   ```

3. **Enable GitHub Pages** (Optional, for documentation):
   - Settings → Pages
   - Source: `main` branch, `/docs` folder

4. **Set Up GitHub Actions** (Optional):
   - Create `.github/workflows/ci.yml` for automated testing
   - See `DEPLOYMENT.md` for example

## 🎯 Quick Commands Reference

```bash
# Check status
git status

# View commits
git log --oneline

# View remote
git remote -v

# Push updates
git add .
git commit -m "Your commit message"
git push

# Pull updates
git pull
```

## ❓ Troubleshooting

### Authentication Error
```bash
# Use Personal Access Token
git remote set-url origin https://YOUR_TOKEN@github.com/USERNAME/REPO.git
```

### Branch Name Mismatch
```bash
# Rename branch
git branch -M main
git push -u origin main
```

### Large Files
```bash
# Install git-lfs if needed
git lfs install
```

## 📚 Additional Resources

- [GitHub Docs](https://docs.github.com)
- [Git Handbook](https://guides.github.com/introduction/git-handbook/)
- See `DEPLOYMENT.md` for detailed deployment guide

