# 4-Day GitHub Commit Plan — Personal Finance Planner

---

## ONE-TIME SETUP (Do this before Day 1)

### 1. Create .gitignore
Create a file named `.gitignore` in your project root:
```
venv/
.env
__pycache__/
*.pyc
*.pyo
uploads/*
!uploads/.gitkeep
.DS_Store
Thumbs.db
*.log
```

### 2. Create .env.example
Create a file named `.env.example`:
```
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
```

### 3. Create uploads folder placeholder
```powershell
New-Item -ItemType Directory -Force -Path "uploads"
New-Item -ItemType File -Force -Path "uploads\.gitkeep"
```

### 4. Initialize Git and connect to GitHub
```powershell
cd "c:\Users\ROG\Desktop\PROJECTS\Personal Finance Planner"

git init
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/personal-finance-planner.git
```
> Replace YOUR_USERNAME with your actual GitHub username.

---

## DAY 1 — Project Setup and AI Core

Theme: Initialize project structure and add the core AI finance agent.

```powershell
cd "c:\Users\ROG\Desktop\PROJECTS\Personal Finance Planner"

git add .gitignore
git add .env.example
git add requirements.txt
git add finance_agent.py
git add README.md

git commit -m "feat: initialize project and add core AI finance agent

- Set up project structure with Python dependencies
- Implement FinanceAgent class backed by Google Gemini API
- CSV parsing with required columns: date, amount, category, description
- Expense summarization: totals, category breakdown, monthly grouping
- Multi-turn conversation history with context retention
- Date parsing supporting multiple date formats
- Auto-detect currency symbols from CSV data"

git push -u origin main
```

---

## DAY 2 — Flask Backend API

Theme: Build the REST API server with all endpoints.

```powershell
cd "c:\Users\ROG\Desktop\PROJECTS\Personal Finance Planner"

git add app.py
git add uploads/.gitkeep

git commit -m "feat: add Flask backend with full REST API

- POST /api/upload  - CSV upload with validation, parsing, currency detection
- POST /api/chat    - AI chat endpoint with session-isolated agents
- GET  /api/status  - Returns session state and loaded data info
- GET  /api/summary - Returns full expense summary as JSON
- POST /api/reset   - Clears conversation history, keeps expense data
- Per-session FinanceAgent instances for multi-user isolation
- File size limit 5MB, encoding validation, graceful error handling
- Supported currencies: USD, GBP, EUR, INR, JPY, KRW, TRY and more"

git push
```

---

## DAY 3 — Frontend Web Interface

Theme: Build the complete dark UI with charts and chat.

```powershell
cd "c:\Users\ROG\Desktop\PROJECTS\Personal Finance Planner"

git add templates/index.html

git commit -m "feat: add dark frontend with charts and AI chat interface

- Two-panel layout: sidebar (upload + summary) + main (chat/charts)
- Drag-and-drop CSV upload zone with progress indicator
- Expense summary sidebar: total, transactions, avg, top category
- Category breakdown with animated bar indicators
- Chat/Charts tab toggle in main panel
- AI chat with markdown rendering via marked.js
- Donut chart: spending by category (Chart.js)
- Bar chart: top 8 categories ranked by amount
- Monthly spending trend bar chart (full history)
- Typing indicator with animated dots
- Dynamic currency symbol in all number formatting
- Session restore on page refresh via /api/status
- Keyboard shortcuts: Enter to send, Shift+Enter for newline
- Responsive layout with Inter + JetBrains Mono typography"

git push
```

---

## DAY 4 — Sample Data, README and Final Polish

Theme: Add documentation, sample data, and polish for sharing.

```powershell
cd "c:\Users\ROG\Desktop\PROJECTS\Personal Finance Planner"

git add sample_expenses.csv
git add README.md
git add commit.md

git commit -m "docs: add sample data, full README and commit plan

- Add sample_expenses.csv for instant demo (1278 transactions)
- Complete README with feature list, setup guide, CSV format spec
- Document all supported currency symbols
- Add commit.md with 4-day git commit plan
- Document required CSV columns and accepted date formats"

git push
```

---

## Verify everything pushed correctly

```powershell
git log --oneline
git status
```

Expected output of git log --oneline:
```
abc1234 (HEAD -> main, origin/main) docs: add sample data, full README and commit plan
def5678 feat: add dark frontend with charts and AI chat interface
ghi9012 feat: add Flask backend with full REST API
jkl3456 feat: initialize project and add core AI finance agent
```

---

## IMPORTANT — What NOT to commit

| Rule | Why |
|------|-----|
| Never: git add .env | Your real API key is inside — keep it private |
| Use .env.example instead | Shows others what variables are needed |
| Never commit venv/ folder | It is 100MB+ and machine-specific |
| Never commit uploads/ contents | User data should stay local |
| Run git status before every commit | Confirms only right files are staged |

---

## Useful Git Commands

```powershell
# Check what files are staged
git status

# See what changed in a file before staging
git diff finance_agent.py

# Unstage a file added by mistake
git restore --staged .env

# Check your full commit history
git log --oneline

# Check remote connection
git remote -v
```
