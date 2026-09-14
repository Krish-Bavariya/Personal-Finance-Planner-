# Phases.md
## Development Roadmap — Personal Finance Planner Project

This project is broken into 4 sequential phases. Each phase has a clear goal, tasks, and an exit criterion (what must be true before moving to the next phase).

---

## Phase 0: Environment Setup (Day 1 - Morning: 1-2 hours)

**Goal:** Get the development environment ready to build the finance planner.

**Tasks:**
- Create project repository and folder structure: `finance-planner/` with subfolders `templates/` and `uploads/`.
- Initialize Git repo (optional but recommended).
- Install Python 3.8 or higher.
- Create Python virtual environment for the project.
- Install core dependencies: `anthropic`, `flask`, `python-dotenv`.
- Create `.env` file and add Anthropic API key.
- Verify all imports work correctly.

**Exit Criterion:** Running `python -c "from anthropic import Anthropic; from flask import Flask; print('All dependencies ready')"` executes successfully without errors.

---

## Phase 1: AI Agent Development (Day 1 - Afternoon: 3-4 hours)

**Goal:** Build the core AI agent that analyzes expense data and answers financial questions.

**Tasks:**
- Create `finance_agent.py` with `FinanceAgent` class.
- Implement CSV expense loading and parsing functionality.
- Build expense categorization and totaling logic.
- Create system prompt for Claude that understands financial analysis.
- Implement conversation history to maintain context across questions.
- Build `ask_agent()` function that sends questions to Claude API.
- Add financial data formatting for Claude to understand user's expenses.
- Test agent with sample expense data manually.

**Exit Criterion:** Running `python finance_agent.py` loads a CSV file, accepts user questions via command line, and returns intelligent financial advice with specific numbers from the data.

---

## Phase 2: Backend Web Server Setup (Day 2 - Morning: 2-3 hours)

**Goal:** Create Flask backend that handles file uploads, stores expenses, and manages API calls.

**Tasks:**
- Create `app.py` with Flask application initialization.
- Set up `/` route that serves the main HTML page.
- Create `/api/upload` endpoint to handle CSV file uploads.
- Implement file validation (must be CSV format).
- Create `/api/chat` endpoint to receive user questions.
- Integrate `FinanceAgent` with Flask routes.
- Add error handling for file uploads and API calls.
- Test endpoints using curl commands or Postman (optional).
- Verify Flask runs without errors on `http://localhost:5000`.

**Exit Criterion:** Running `flask run` or `python app.py` starts server successfully on port 5000 and all routes respond without 500 errors.

---

## Phase 3: Frontend Web Interface (Day 2 - Afternoon: 2-3 hours)

**Goal:** Build a user-friendly web interface with upload functionality and chat interface.

**Tasks:**
- Create `templates/index.html` with complete HTML structure.
- Design responsive layout: header, left sidebar (upload + summary), right sidebar (chat).
- Implement drag-and-drop file upload area using vanilla JavaScript.
- Build chat message display with message bubbles (user vs agent).
- Create chat input form with send button.
- Add CSS styling with gradient backgrounds and modern design.
- Implement fetch API calls to backend endpoints (`/api/upload`, `/api/chat`).
- Add status messages for success/error feedback.
- Add loading indicators while waiting for responses.
- Test all UI interactions in browser.

**Exit Criterion:** Opening `http://localhost:5000` shows the finance planner interface, drag-and-drop works, buttons respond to clicks, and chat sends data to backend without JavaScript errors.

---

## Phase 4: Integration & Testing (Day 3 - Morning: 2-3 hours)

**Goal:** Connect all components and verify the complete workflow functions end-to-end.

**Tasks:**
- Create test CSV file with sample expenses (`expenses.csv`).
- Test full upload workflow: browse/drag file → upload → parse → display summary.
- Verify financial summary displays correctly on frontend.
- Test chat workflow: type question → send → agent processes → response displays.
- Ask 5+ different questions and verify accuracy of responses.
- Test error cases: invalid file type, empty CSV, malformed data.
- Check performance: measure response times, verify no timeouts.
- Test on different browsers (Chrome, Firefox, Safari, Edge).
- Test responsive design on different screen sizes.
- Verify all data calculations are correct.

**Exit Criterion:** Complete end-to-end test passes: upload CSV, ask 3 questions, get intelligent responses with accurate numbers, no errors in console or backend.

---

## Phase 5: Documentation & Cleanup (Day 3 - Afternoon: 1-2 hours)

**Goal:** Document the project, clean up code, and prepare for submission.

**Tasks:**
- Write comprehensive `README.md` with:
  - Project description and goals
  - Features list
  - System requirements
  - Installation instructions (step-by-step)
  - How to run the application
  - How to use the application
  - Example questions to ask
  - Known limitations
- Create `ARCHITECTURE.md` explaining:
  - Component diagram (Agent → Flask → HTML)
  - Data flow diagrams
  - How each component communicates
  - Role of Claude API
- Create `API_FLOW.md` documenting:
  - Upload endpoint request/response
  - Chat endpoint request/response
  - Error responses
  - Example curl commands
- Add code comments to Python files explaining logic.
- Create `.gitignore` file (exclude `.env`, `__pycache__`, `*.pyc`, `venv/`).
- Remove unnecessary files and test data.
- Organize folder structure cleanly.
- Create `DEMO_STEPS.txt` with exact reproduction steps.
- (Optional) Add screenshot placeholders in README.

**Exit Criterion:** README is complete and clear enough that someone unfamiliar with the project can set it up and run it without asking questions. Folder structure is clean. All documentation is in place.

---

## Phase 6: Polish & Presentation (Day 3 - Evening: 30-45 minutes)

**Goal:** Final touches and prepare for demonstration or submission.

**Tasks:**
- Create `SUBMISSION_CHECKLIST.md` verifying all requirements met.
- Add sample data and test cases to repository.
- Create `QUICK_START.md` with fastest way to get running.
- Verify all Python files have no syntax errors (`python -m py_compile filename.py`).
- Test one final time from a fresh clone/copy of the project.
- (Optional) Record a short screen recording showing the app in action.
- (Optional) Take 3-4 screenshots of the interface at different stages.
- Clean up any debug print statements.
- Verify API key is not committed (only in `.env`).
- Prepare final submission folder with all necessary files.

**Exit Criterion:** Project is ready for submission/demonstration. Folder structure is clean, all documentation is complete, app runs without errors, and nothing sensitive is exposed.

---

## Summary Timeline

| Phase | Focus | Duration | When |
|-------|-------|----------|------|
| 0 | Environment Setup | 1-2 hours | Day 1 Morning |
| 1 | AI Agent Development | 3-4 hours | Day 1 Afternoon |
| 2 | Backend Web Server | 2-3 hours | Day 2 Morning |
| 3 | Frontend Interface | 2-3 hours | Day 2 Afternoon |
| 4 | Integration & Testing | 2-3 hours | Day 3 Morning |
| 5 | Documentation & Cleanup | 1-2 hours | Day 3 Afternoon |
| 6 | Polish & Presentation | 30-45 min | Day 3 Evening |

**Total estimated time:** ~15-17 hours over 3 days, adjustable based on experience level.

---

## Key Milestones

✅ **After Phase 0:** Development environment ready, all dependencies installed
✅ **After Phase 1:** CLI-based AI agent working, can answer financial questions
✅ **After Phase 2:** Flask backend running, endpoints responding
✅ **After Phase 3:** Web interface loaded in browser, UI complete
✅ **After Phase 4:** Full end-to-end workflow functioning
✅ **After Phase 5:** Fully documented, ready for any technical interview
✅ **After Phase 6:** Production-ready submission package

---

## Success Criteria By Phase

### Phase 0 Success
- All packages install without errors
- Python imports work
- `.env` file created with API key

### Phase 1 Success
- Agent loads CSV correctly
- Agent responds to questions about finances
- Responses include specific numbers from the data
- Conversation history maintains context

### Phase 2 Success
- Flask server starts on port 5000
- Upload endpoint returns success on valid CSV
- Chat endpoint returns Claude responses
- No backend errors in terminal

### Phase 3 Success
- Website displays in browser
- Upload area is functional
- Chat interface is responsive
- Styling looks professional
- No JavaScript errors in console

### Phase 4 Success
- Complete workflow: upload → questions → answers
- Summary displays correct totals
- Chat responses are accurate
- Error handling works
- Response times are reasonable (<5 seconds)

### Phase 5 Success
- README is complete and clear
- All documentation exists
- Code is commented
- Folder structure is organized
- `.gitignore` prevents sensitive files

### Phase 6 Success
- One final successful test run
- All files are clean and organized
- Project is ready for submission
- Can be set up on fresh machine

---

## Common Challenges & Solutions

### Challenge: Claude API Returns Empty Response
**Solution:** 
- Verify `.env` file exists and API key is correct
- Check internet connection
- Verify financial data is loaded before asking questions
- Wait longer for response (5+ seconds)

### Challenge: File Upload Fails
**Solution:**
- Ensure file is `.csv` format
- Check that `uploads/` folder exists
- Verify file has required columns: date, amount, category, description
- Check file size is reasonable

### Challenge: Web Page Won't Load
**Solution:**
- Verify Flask is running (see "Running on..." message)
- Check correct URL: `http://localhost:5000`
- Try different port if 5000 is in use
- Clear browser cache
- Check no other app is using port 5000

### Challenge: Chat Takes Too Long to Respond
**Solution:**
- Check internet connection
- Verify API key has credits (free tier has limits)
- Reduce amount of expense data
- Check Claude API status page
- Try asking simpler questions first

### Challenge: JavaScript Errors in Browser Console
**Solution:**
- Check Flask is running
- Verify endpoints are returning valid JSON
- Look at Network tab to see actual response
- Check for typos in JavaScript fetch URLs
- Verify API endpoint paths match

---

## Testing Checklist

Before moving to next phase, verify:

**Phase 0:**
- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All pip packages installed
- [ ] `.env` file created with API key
- [ ] `import anthropic` works in Python

**Phase 1:**
- [ ] `finance_agent.py` loads and runs
- [ ] CSV file loads without errors
- [ ] Financial totals are calculated correctly
- [ ] Agent responds to 3+ test questions
- [ ] Responses include specific numbers

**Phase 2:**
- [ ] Flask app starts without errors
- [ ] Can POST to `/api/upload` endpoint
- [ ] Can POST to `/api/chat` endpoint
- [ ] Upload creates file in `uploads/` folder
- [ ] Chat returns JSON response

**Phase 3:**
- [ ] Website loads at `http://localhost:5000`
- [ ] Upload area displays and is interactive
- [ ] Chat area displays message bubbles
- [ ] Buttons respond to clicks
- [ ] No JavaScript errors in console
- [ ] Page looks good on mobile (resize browser)

**Phase 4:**
- [ ] Upload CSV → see summary appear
- [ ] Ask question → see agent response
- [ ] Response includes numbers from data
- [ ] Error handling works for bad files
- [ ] Chat maintains conversation context
- [ ] All 5 test scenarios pass

**Phase 5:**
- [ ] README.md is complete
- [ ] ARCHITECTURE.md explains design
- [ ] API_FLOW.md documents endpoints
- [ ] Code has explanatory comments
- [ ] `.gitignore` is in place
- [ ] Unnecessary files are removed

**Phase 6:**
- [ ] Final test run successful
- [ ] Can start fresh from repo
- [ ] All documentation is accessible
- [ ] No sensitive data exposed
- [ ] Project looks professional
- [ ] Ready for submission

---

## Tips for Success

1. **Complete each phase fully before moving to next** — don't skip steps
2. **Test after each file is created** — don't write everything then test
3. **Save and commit frequently** — especially after reaching phase exit criteria
4. **Take screenshots as you go** — helps with documentation later
5. **Keep a list of what works and what doesn't** — aids troubleshooting
6. **Test with fresh CSV data** — not just the sample data
7. **Document issues as they occur** — easier than remembering later
8. **Verify exit criteria before proceeding** — don't move forward if not ready
9. **Read error messages carefully** — they usually tell you exactly what's wrong
10. **Ask for help early** — better to solve issues than accumulate them

---

**Good luck! You've got this!** 🚀
