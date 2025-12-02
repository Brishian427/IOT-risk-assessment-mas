# GitHub Deployment Guide

## Prerequisites

1. **GitHub Account**: Ensure you have a GitHub account
2. **Git Installed**: Verify git is installed (`git --version`)
3. **Repository Created**: Create a new repository on GitHub (or use existing)

## Step-by-Step Deployment

### 1. Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon → "New repository"
3. Repository name: `iot-risk-assessment-mas` (or your preferred name)
4. Description: "Multi-Agent System for IoT Risk Assessment using LangGraph"
5. Choose visibility: Public or Private
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

### 2. Add Remote and Push

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Rename main branch (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

### 3. Verify Deployment

1. Visit your repository on GitHub
2. Verify all files are present
3. Check that `.env` is NOT in the repository (it should be ignored)
4. Verify README.md displays correctly

## Security Checklist

Before pushing, ensure:

- ✅ `.env` file is in `.gitignore` (already done)
- ✅ No API keys in code files
- ✅ `.env.example` exists as template (if you have one)
- ✅ Sensitive data is not committed

## Post-Deployment

### Add Repository Badges (Optional)

Add to README.md:

```markdown
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
```

### Set Up GitHub Actions (Optional)

Create `.github/workflows/ci.yml` for automated testing:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python -m pytest examples/
```

### Add Topics/Tags

On GitHub repository page:
1. Click the gear icon next to "About"
2. Add topics: `multi-agent-system`, `langgraph`, `iot`, `risk-assessment`, `llm`, `python`

## Troubleshooting

### Authentication Issues

If you get authentication errors:

```bash
# Use GitHub CLI (recommended)
gh auth login

# Or use Personal Access Token
git remote set-url origin https://YOUR_TOKEN@github.com/USERNAME/REPO.git
```

### Large Files

If you have large files:

```bash
# Install git-lfs if needed
git lfs install
git lfs track "*.large_file"
git add .gitattributes
```

## Next Steps

1. **Add License**: Consider adding LICENSE file (MIT, Apache 2.0, etc.)
2. **Add Contributing Guide**: Create CONTRIBUTING.md
3. **Set Up Issues**: Enable GitHub Issues for bug reports
4. **Add Wiki**: Optional documentation wiki
5. **Releases**: Tag versions for releases

