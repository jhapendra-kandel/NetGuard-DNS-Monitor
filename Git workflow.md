# 🚀 Git Workflow Guide - NetGuard DNS Monitor

Complete guide for setting up and managing your GitHub repository.

---

## 📋 Table of Contents

- [Initial Setup](#initial-setup)
- [First Time Push](#first-time-push)
- [Daily Workflow](#daily-workflow)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Branch Management](#branch-management)
- [Common Git Commands](#common-git-commands)

---

## 🎯 Initial Setup

### Step 1: Configure Git

```bash
# Set your name and email (one-time setup)
git config --global user.name "Jhapendra Kandel"
git config --global user.email "your-email@example.com"

# Verify configuration
git config --list
```

### Step 2: Initialize Repository

If starting fresh:

```bash
# Navigate to project directory
cd NetGuard-DNS-Monitor

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "chore: Initial project setup with documentation"
```

If cloning existing repository:

```bash
git clone https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor.git
cd NetGuard-DNS-Monitor
```

---

## 📤 First Time Push to GitHub

### Method 1: New Repository

1. **Create repository on GitHub** (github.com)
   - Click "New Repository"
   - Name: `NetGuard-DNS-Monitor`
   - Description: "DNS Network Monitor - Python Project"
   - Keep it public (or private)
   - Don't initialize with README (we have one)
   - Click "Create repository"

2. **Connect local to remote**

```bash
# Add remote origin
git remote add origin https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

### Method 2: Existing Repository

```bash
# If you already have the repo, just push
git push origin main
```

---

## 📁 Complete File Addition Guide

### Add All Documentation Files

```bash
# First, check status to see what's new
git status

# Add all documentation files
git add README.md
git add INSTALLATION.md
git add USAGE.md
git add CONTRIBUTING.md
git add ARCHITECTURE.md
git add CHANGELOG.md
git add QUICK_SETUP.md
git add PROJECT_SUMMARY.md
git add GIT_WORKFLOW.md

# Add Python files
git add main.py
git add dns_server.py
git add gui.py
git add stats.py

# Add configuration files
git add requirements.txt
git add setup.py
git add .gitignore
git add LICENSE

# Or add everything at once
git add .

# Commit with proper message
git commit -m "docs: Add comprehensive project documentation v2.0

- Added detailed README with installation and usage
- Added INSTALLATION.md for step-by-step setup
- Added USAGE.md user manual
- Added CONTRIBUTING.md for contributors
- Added ARCHITECTURE.md technical documentation
- Added CHANGELOG.md version history
- Added setup.py for automated installation
- Updated project info for 1st year Python project
- Fixed all file paths and structure"

# Push to GitHub
git push origin main
```

---

## 📝 Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples

```bash
# Feature addition
git commit -m "feat(cache): Add TTL-based DNS caching

Implemented automatic cache expiration based on TTL values.
Cache entries now expire after their designated time.

Closes #123"

# Bug fix
git commit -m "fix(gui): Prevent crash on empty logs

Added null check before accessing log data.
Prevents IndexError when no logs exist.

Fixes #456"

# Documentation
git commit -m "docs(readme): Update installation instructions

- Added virtual environment setup
- Added platform-specific commands
- Updated troubleshooting section"

# Code cleanup
git commit -m "refactor(dns): Improve error handling

- Added try-catch blocks
- Better error messages
- Graceful degradation"
```

---

## 🌿 Daily Workflow

### Making Changes

```bash
# 1. Check current status
git status

# 2. Make your changes to files
# ... edit code ...

# 3. Check what changed
git diff

# 4. Add changed files
git add main.py          # Add specific file
git add .                # Add all changes

# 5. Commit changes
git commit -m "feat(gui): Add dark mode support"

# 6. Push to GitHub
git push origin main
```

### Step-by-Step Example

```bash
# Morning: Start work
git pull origin main     # Get latest changes

# Make changes to gui.py
# ... coding ...

# Check what changed
git status
git diff gui.py

# Stage changes
git add gui.py

# Commit
git commit -m "feat(gui): Add statistics auto-refresh

Automatically refresh statistics when tab is active.
Updates every 5 seconds for real-time monitoring."

# Push to GitHub
git push origin main

# Continue working...
```

---

## 🔄 Common Scenarios

### Scenario 1: Add New Feature

```bash
# 1. Create feature branch (optional)
git checkout -b feature/new-blocklist-ui

# 2. Make changes
# ... code ...

# 3. Commit changes
git add gui.py
git commit -m "feat(blocklist): Redesign blocklist UI"

# 4. Push branch
git push origin feature/new-blocklist-ui

# 5. Merge to main (after testing)
git checkout main
git merge feature/new-blocklist-ui
git push origin main
```

### Scenario 2: Fix Bug

```bash
# 1. Identify bug
# 2. Fix in code
# 3. Test fix

# 4. Commit fix
git add dns_server.py
git commit -m "fix(dns): Resolve timeout issue

Fixed UDP socket timeout causing connection drops.
Increased timeout from 2s to 5s.

Fixes #789"

# 5. Push
git push origin main
```

### Scenario 3: Update Documentation

```bash
# Update README.md
# ... edit ...

git add README.md
git commit -m "docs(readme): Add troubleshooting section"
git push origin main
```

### Scenario 4: Release New Version

```bash
# 1. Update version number in files
# 2. Update CHANGELOG.md

git add CHANGELOG.md main.py
git commit -m "chore: Release version 2.1.0

- Updated version number
- Updated changelog
- Prepared for release"

# 3. Create tag
git tag -a v2.1.0 -m "Version 2.1.0 - Enhanced caching"

# 4. Push with tags
git push origin main --tags
```

---

## 🎯 Complete Setup Workflow

### From Scratch to GitHub

```bash
# Step 1: Create project directory
mkdir NetGuard-DNS-Monitor
cd NetGuard-DNS-Monitor

# Step 2: Add your files
# (Copy all .py files, .md files, etc.)

# Step 3: Initialize git
git init

# Step 4: Configure .gitignore
# (Already have .gitignore file)

# Step 5: Add all files
git add .

# Step 6: Initial commit
git commit -m "chore: Initial project setup

- Added core DNS server functionality
- Added GUI interface
- Added comprehensive documentation
- Configured virtual environment support
- Added setup script for easy installation

Project: NetGuard DNS Monitor v2.0
Module: Introduction to Programming
Institution: Softwarica College (Coventry University)"

# Step 7: Create repo on GitHub
# (Do this on github.com)

# Step 8: Connect and push
git remote add origin https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor.git
git branch -M main
git push -u origin main

# Step 9: Verify on GitHub
# Visit: https://github.com/jhapendra-kandel/NetGuard-DNS-Monitor
```

---

## 🔧 Common Git Commands

### Checking Status

```bash
git status              # See what's changed
git log                 # View commit history
git log --oneline       # Compact history
git diff                # See changes not staged
git diff --staged       # See staged changes
```

### Undoing Changes

```bash
# Undo changes in working directory
git checkout -- filename.py

# Unstage file (keep changes)
git reset HEAD filename.py

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes) - CAREFUL!
git reset --hard HEAD~1
```

### Branches

```bash
git branch              # List branches
git branch feature-name # Create branch
git checkout feature-name # Switch to branch
git checkout -b feature-name # Create and switch
git merge feature-name  # Merge branch to current
git branch -d feature-name # Delete branch
```

### Remote Operations

```bash
git pull origin main    # Pull latest changes
git push origin main    # Push to remote
git remote -v           # View remotes
git fetch origin        # Fetch without merge
```

---

## 📊 Recommended Commit Frequency

### During Development

```bash
# After each logical change
- Fixed a bug → commit
- Added a feature → commit  
- Updated docs → commit
- Refactored code → commit
```

### Good Practice

```bash
# Commit at least:
- End of each coding session
- Before taking a break
- After completing a task
- Before trying something risky
```

---

## 🎓 Project-Specific Workflow

### For Your University Project

```bash
# Initial setup (Day 1)
git init
git add .
git commit -m "chore: Initial project setup"
git push origin main

# Adding features (Day 2-10)
git add dns_server.py
git commit -m "feat(dns): Implement DNS caching"
git push origin main

git add gui.py
git commit -m "feat(gui): Add live logs tab"
git push origin main

# Documentation (Day 11-12)
git add README.md USAGE.md
git commit -m "docs: Add comprehensive documentation"
git push origin main

# Final polish (Day 13-14)
git add .
git commit -m "chore: Final polish and testing

- Fixed all bugs
- Updated documentation
- Added setup script
- Ready for submission"
git push origin main

# Create release tag
git tag -a v2.0.0 -m "Version 2.0.0 - Final submission"
git push origin main --tags
```

---

## 🚨 Troubleshooting

### Problem: Can't push to GitHub

```bash
# Solution: Pull first
git pull origin main
# Resolve conflicts if any
git push origin main
```

### Problem: Committed wrong files

```bash
# Remove from staging
git reset HEAD filename

# Or undo last commit
git reset --soft HEAD~1
```

### Problem: Need to change commit message

```bash
# Change last commit message
git commit --amend -m "New message"

# Force push (if already pushed)
git push --force origin main
```

---

## ✅ Pre-Submission Checklist

```bash
# Before submitting project:

[ ] All code files added and committed
[ ] All documentation files added
[ ] .gitignore properly configured
[ ] No sensitive data in commits
[ ] README.md complete and accurate
[ ] Requirements.txt up to date
[ ] All commits have proper messages
[ ] Code is tested and working
[ ] Repository is public (or submitted link)
[ ] Latest changes pushed to GitHub
```

---

## 📚 Quick Reference

### Most Used Commands

```bash
# Daily workflow
git status
git add .
git commit -m "message"
git push origin main

# Before starting work
git pull origin main

# Check history
git log --oneline

# Undo changes
git checkout -- filename
```

---

<div align="center">

**Git Workflow Guide** | NetGuard DNS Monitor

[Back to README](README.md) | [Contributing](CONTRIBUTING.md)

---

*Happy Coding! 🚀*

</div>