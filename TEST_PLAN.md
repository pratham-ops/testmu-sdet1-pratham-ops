# Comprehensive Test Plan - Task Manager POC Application

**Document Version:** 1.0  
**Date:** February 4, 2026  
**Application:** Task Manager (React Frontend + Express.js Backend)  
**Testing Framework:** Playwright  
**Status:** Ready for Execution

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Application Overview](#application-overview)
3. [Test Strategy](#test-strategy)
4. [Scope & Objectives](#scope--objectives)
5. [Test Categories & Scenarios](#test-categories--scenarios)
6. [Test Data & Environment](#test-data--environment)
7. [Test Execution Plan](#test-execution-plan)
8. [Success Criteria](#success-criteria)
9. [Risks & Mitigation](#risks--mitigation)

---

## Executive Summary

This test plan defines comprehensive test coverage for the Task Manager POC application. It covers:
- **14 critical smoke tests** for basic operations
- **42+ detailed test scenarios** across 6 major categories
- **API contract validation** (6 endpoints)
- **UI/UX testing** (responsive design, accessibility)
- **Edge cases & error handling**

**Estimated Test Duration:** 3-5 minutes (automated)  
**Browser Coverage:** Chromium (primary), Firefox & WebKit (optional)  
**Prerequisites:** Node.js 18+, npm, Playwright installed

---

## Application Overview

### Architecture
- **Frontend:** React 18 with Vite (port 5173)
- **Backend:** Express.js REST API (port 3001)
- **State Management:** React hooks (useState, useEffect)
- **Data Storage:** In-memory (mock database)
- **Styling:** CSS modules with responsive design

### Core Features
1. **Authentication:** Login, Register, Logout
2. **Task Management:** Create, Read, Update (completion), Delete
3. **Search & Filter:** Full-text search by title + priority filtering
4. **Dashboard:** Task statistics (total, completed, pending, urgent)
5. **Responsive Design:** Mobile (375px), Tablet (768px), Desktop (1280px+)
6. **Accessibility:** Keyboard navigation, ARIA labels, contrast compliance

### Pre-seeded Test Data

**Users:**
| Email | Password | Name | Role |
|-------|----------|------|------|
| admin@test.com | admin123 | Admin User | Default test user |
| user@test.com | user123 | Test User | Secondary test user |

**Initial Tasks:**
| Task Title | Priority | Status | Created By |
|------------|----------|--------|-----------|
| Learn Playwright | high | pending | System |
| Compare with Katalon | medium | pending | System |
| Write test cases | high | completed | System |

---

## Test Strategy

### Approach
1. **Test-First Validation:** API tests verify contract before UI tests
2. **Layered Testing:** Unit → Integration (API) → E2E (UI)
3. **Isolation:** Each test is independent and can run in any order
4. **Data Cleanup:** Pre-seeded data resets between test runs
5. **Parallel Execution:** Tests grouped by category; can run in parallel

### Test Pyramid
```
        ┌─────────────────┐
        │    E2E UI Tests │  (10-15 tests)
        │  (Responsive,   │
        │ Accessibility)  │
        ├─────────────────┤
        │  Integration    │  (15-20 tests)
        │  Tests (API +   │
        │   UI Workflows) │
        ├─────────────────┤
        │   API Unit      │  (15+ tests)
        │   Tests         │
        └─────────────────┘
```

### Tool Usage
- **Playwright Test Runner:** Primary automation framework
- **Accessibility Auditor:** axe-core (via Playwright a11y plugin)
- **Network Monitoring:** Playwright request/response validation
- **Screenshots/Video:** Capture on failure for debugging

---

## Scope & Objectives

### In Scope ✓
- ✅ Authentication flows (login, register, logout)
- ✅ Task CRUD operations (Create, Read, Update, Delete)
- ✅ Search and filter functionality
- ✅ Task statistics and dashboard display
- ✅ Priority badges and visual indicators
- ✅ API endpoint validation (6 endpoints)
- ✅ Responsive design (3 breakpoints)
- ✅ Basic accessibility (keyboard nav, ARIA)
- ✅ Error handling and validation messages
- ✅ Session management and token handling

### Out of Scope ✗
- ❌ Performance/load testing (>100 concurrent users)
- ❌ Security testing (SQL injection, XSS detailed penetration)
- ❌ Mobile app (iOS/Android native)
- ❌ Internationalization (multi-language support)
- ❌ Browser extensions/plugins compatibility
- ❌ Advanced analytics tracking

### Objectives
1. **Ensure Functionality:** All core features work as designed
2. **Validate Data Integrity:** API responses match expected schema
3. **Verify UX:** UI is responsive, accessible, and intuitive
4. **Establish Baseline:** Provide regression test baseline for future releases
5. **Demonstrate Playwright Capabilities:** Compare with Katalon Studio alternatives

---

## Test Categories & Scenarios

---

### Category 1: Authentication (6 Scenarios)

#### Scenario 1.1: Login with Valid Credentials
**Precondition:** User navigates to application homepage  
**Steps:**
1. Click "Login" tab (or verify default view)
2. Enter email: `admin@test.com`
3. Enter password: `admin123`
4. Click "Login" button
5. Wait for dashboard to load

**Expected Results:**
- Login form closes/disappears
- Dashboard displays with task list
- Success notification: "Welcome back, Admin User!"
- User name "Admin User" visible in header
- Logout button is visible
- Tasks from pre-seeded data appear in the list

**Test Data:**
- Email: admin@test.com
- Password: admin123

**Pass Criteria:** All assertions pass without error  
**Fail Criteria:** Any assertion fails or timeout occurs

---

#### Scenario 1.2: Login with Invalid Credentials
**Precondition:** User at login form  
**Steps:**
1. Enter email: `invalid@email.com`
2. Enter password: `wrongpassword123`
3. Click "Login" button
4. Observe response

**Expected Results:**
- Error notification appears with message: "Invalid credentials"
- Notification styled with error (red/warning color)
- User remains on login page (dashboard NOT loaded)
- Login form fields retain entered values
- No token is created

**Test Data:**
- Invalid email/password combination

**Pass Criteria:** Error message displays; user stays on login page  
**Fail Criteria:** Dashboard loads or no error shown

---

#### Scenario 1.3: Login with Missing Email
**Precondition:** User at login form  
**Steps:**
1. Leave email field empty
2. Enter password: `admin123`
3. Click "Login" button

**Expected Results:**
- Validation error or API error response
- Error notification: "Email and password are required"
- User remains on login page

**Pass Criteria:** Error validation triggered  
**Fail Criteria:** Login proceeds with empty email

---

#### Scenario 1.4: Login with Missing Password
**Precondition:** User at login form  
**Steps:**
1. Enter email: `admin@test.com`
2. Leave password field empty
3. Click "Login" button

**Expected Results:**
- Validation error: "Email and password are required"
- User remains on login page
- No dashboard loaded

**Pass Criteria:** Validation catches missing password  
**Fail Criteria:** Login succeeds

---

#### Scenario 1.5: Register New User
**Precondition:** User at login/register form  
**Steps:**
1. Click "Register" tab
2. Enter name: `Test User ${timestamp}`
3. Enter email: `testuser${timestamp}@test.com`
4. Enter password: `TestPass123`
5. Confirm password: `TestPass123`
6. Click "Register" button
7. Wait for success message

**Expected Results:**
- Success notification: "Account created! Please login."
- Register form clears
- Redirected to login tab automatically
- New user can login with registered credentials

**Test Data:**
- Name: Unique per run (use timestamp)
- Email: Unique per run
- Password: TestPass123

**Pass Criteria:** New user account created and login succeeds  
**Fail Criteria:** Registration fails or user cannot login

---

#### Scenario 1.6: Register with Existing Email
**Precondition:** User at register form  
**Steps:**
1. Enter name: `Duplicate User`
2. Enter email: `admin@test.com` (pre-existing)
3. Enter password: `TestPass123`
4. Click "Register" button

**Expected Results:**
- Error notification: "User already exists"
- Registration fails
- User remains on register form
- No new account created

**Pass Criteria:** Duplicate email validation works  
**Fail Criteria:** Account created despite duplicate

---

### Category 2: Task Management (8 Scenarios)

#### Scenario 2.1: Display Task List on Login
**Precondition:** User logged in (admin@test.com)  
**Steps:**
1. Verify dashboard displays
2. Check task list visibility
3. Count displayed tasks

**Expected Results:**
- Task list visible with pre-seeded tasks:
  - "Learn Playwright" (high priority, pending)
  - "Compare with Katalon" (medium priority, pending)
  - "Write test cases" (high priority, completed)
- Tasks display in consistent order
- Each task shows: title, priority badge, completion checkbox, delete button

**Pass Criteria:** All pre-seeded tasks display correctly  
**Fail Criteria:** Tasks missing or incorrect count

---

#### Scenario 2.2: Create New Task
**Precondition:** User logged in, on dashboard  
**Steps:**
1. Locate task input form
2. Enter title: `Test Task - ${timestamp}`
3. Select priority: `high`
4. Click "Add Task" button
5. Wait for task to appear in list

**Expected Results:**
- New task appears at top/bottom of task list
- Task displays with:
  - Entered title
  - Selected priority (high)
  - Completion status: unchecked
  - Delete button ready
- Success notification: "Task added!"
- Input field clears for next task
- Task count incremented

**Test Data:**
- Title: Unique per run
- Priority: high

**Pass Criteria:** Task created and appears in list immediately  
**Fail Criteria:** Task not created or not visible

---

#### Scenario 2.3: Create Task with Default Priority
**Precondition:** User on dashboard  
**Steps:**
1. Enter task title: `Default Priority Task`
2. Leave priority as default (medium)
3. Click "Add Task"

**Expected Results:**
- Task created with medium priority
- Priority badge displays as "medium"
- Task functional and deletable

**Pass Criteria:** Task defaults to medium priority  
**Fail Criteria:** Priority is different or task not created

---

#### Scenario 2.4: Create Task with Empty Title
**Precondition:** User on dashboard  
**Steps:**
1. Leave task title empty
2. Click "Add Task" button

**Expected Results:**
- Task NOT created
- No error notification (silently fails)
- Task list unchanged

**Pass Criteria:** Empty title rejected  
**Fail Criteria:** Task created with empty title

---

#### Scenario 2.5: Mark Task as Complete
**Precondition:** User logged in, incomplete task visible ("Learn Playwright")  
**Steps:**
1. Locate "Learn Playwright" task
2. Click completion checkbox
3. Observe visual change

**Expected Results:**
- Checkbox becomes checked
- Task title shows strikethrough styling
- Task status updates immediately
- Task count: pending decrements, completed increments
- No page refresh needed

**Pass Criteria:** Task marked complete with visual feedback  
**Fail Criteria:** Checkbox doesn't check or visual doesn't update

---

#### Scenario 2.6: Mark Task as Incomplete
**Precondition:** User logged in, completed task visible ("Write test cases")  
**Steps:**
1. Locate "Write test cases" task (pre-completed)
2. Click completion checkbox to uncheck
3. Observe changes

**Expected Results:**
- Checkbox becomes unchecked
- Strikethrough removed from title
- Task appearance returns to normal
- Statistics update

**Pass Criteria:** Task marked incomplete  
**Fail Criteria:** Status doesn't toggle

---

#### Scenario 2.7: Delete Task
**Precondition:** User logged in, task visible  
**Steps:**
1. Create a new task (or select existing)
2. Click delete button for that task
3. Confirm if prompted

**Expected Results:**
- Task removed from list immediately
- Task no longer appears anywhere on dashboard
- Success notification shown
- Task count decremented
- No other tasks affected

**Pass Criteria:** Task deleted and removed from UI  
**Fail Criteria:** Task still visible or count unchanged

---

#### Scenario 2.8: View Task Statistics
**Precondition:** User logged in on dashboard  
**Steps:**
1. Locate statistics section
2. Note displayed values:
   - Total tasks
   - Completed tasks
   - Pending tasks
   - Urgent (high priority) tasks
3. Manually count tasks to verify

**Expected Results:**
- Statistics display correct counts:
  - Total: 3 (initial pre-seeded tasks)
  - Completed: 1
  - Pending: 2
  - Urgent: 2 (both "Learn Playwright" and "Write test cases" are high priority)
- Statistics update in real-time when tasks are added/modified
- All numbers are non-negative integers

**Pass Criteria:** Statistics accurate and update correctly  
**Fail Criteria:** Stats incorrect or don't update

---

### Category 3: Search & Filter (4 Scenarios)

#### Scenario 3.1: Search by Task Title
**Precondition:** User logged in with multiple tasks visible  
**Steps:**
1. Locate search input field
2. Type: `Playwright`
3. Observe task list updates

**Expected Results:**
- Task list filters to show only "Learn Playwright"
- Other tasks hidden (not deleted)
- Search is real-time (no button click needed)
- Clear search reveals all tasks again

**Test Data:**
- Search term: "Playwright"

**Pass Criteria:** Search filters tasks correctly  
**Fail Criteria:** Wrong tasks shown or search doesn't work

---

#### Scenario 3.2: Search with No Matches
**Precondition:** User on dashboard  
**Steps:**
1. Enter search term: `NonexistentTask`
2. Observe result

**Expected Results:**
- Task list becomes empty
- Clear message or empty state shown
- No error message
- Clearing search restores task list

**Pass Criteria:** No matches handled gracefully  
**Fail Criteria:** Error shown or wrong tasks displayed

---

#### Scenario 3.3: Filter by Priority - High
**Precondition:** User logged in with mixed priority tasks  
**Steps:**
1. Locate priority filter dropdown
2. Select "high"
3. Observe task list

**Expected Results:**
- Only high-priority tasks shown:
  - "Learn Playwright"
  - "Write test cases"
- Medium-priority task "Compare with Katalon" hidden
- Filter persists until changed

**Test Data:**
- Filter: high

**Pass Criteria:** High priority filter works  
**Fail Criteria:** Wrong tasks shown

---

#### Scenario 3.4: Filter by Priority - Medium
**Precondition:** User on dashboard  
**Steps:**
1. Select priority filter: "medium"

**Expected Results:**
- Only "Compare with Katalon" visible
- High-priority tasks hidden
- Filter is case-insensitive/consistent

**Pass Criteria:** Medium filter isolates correct task  
**Fail Criteria:** Other priority tasks shown

---

#### Scenario 3.5: Combine Search + Filter
**Precondition:** User logged in  
**Steps:**
1. Type search: `test` (matches "Write test cases")
2. Select priority: `high`
3. Observe result

**Expected Results:**
- "Write test cases" (matches both criteria) shown
- No medium-priority "test" task shown (different priority)
- Filters work together (AND logic)

**Pass Criteria:** Combined filters work correctly  
**Fail Criteria:** Wrong results or filters conflict

---

### Category 4: API Validation (6 Scenarios)

#### Scenario 4.1: GET /api/tasks - Retrieve All Tasks
**Precondition:** Backend running, no authentication required  
**Steps:**
1. Send GET request to `/api/tasks`
2. Capture response

**Expected Results:**
- Status: 200 OK
- Response type: JSON array
- Contains 3 pre-seeded tasks:
  - Each task has: id, title, priority, completed (boolean)
- Example response:
```json
[
  {
    "id": 1,
    "title": "Learn Playwright",
    "priority": "high",
    "completed": false
  },
  ...
]
```

**Pass Criteria:** Correct status, schema, and data  
**Fail Criteria:** Wrong status, missing fields, or incorrect data

---

#### Scenario 4.2: POST /api/login - Valid Credentials
**Precondition:** Backend running  
**Steps:**
1. Send POST to `/api/login`
2. Payload: `{ "email": "admin@test.com", "password": "admin123" }`
3. Capture response

**Expected Results:**
- Status: 200 OK
- Response includes:
  - `success: true`
  - `user: { id, email, name }`
  - `token: "mock-jwt-token-1"` (or similar)
- No error field

**Pass Criteria:** Login API returns token and user  
**Fail Criteria:** Missing token or wrong status

---

#### Scenario 4.3: POST /api/login - Invalid Credentials
**Precondition:** Backend running  
**Steps:**
1. Send POST to `/api/login`
2. Payload: `{ "email": "wrong@email.com", "password": "wrong" }`

**Expected Results:**
- Status: 401 Unauthorized
- Response: `{ "error": "Invalid credentials" }`
- No token or user in response

**Pass Criteria:** Invalid login rejected with 401  
**Fail Criteria:** Wrong status or token issued

---

#### Scenario 4.4: POST /api/tasks - Create Task
**Precondition:** Backend running  
**Steps:**
1. Send POST to `/api/tasks`
2. Payload: `{ "title": "API Test Task", "priority": "high" }`

**Expected Results:**
- Status: 201 Created
- Response includes created task with:
  - `id: (number)` (auto-generated)
  - `title: "API Test Task"`
  - `priority: "high"`
  - `completed: false`

**Pass Criteria:** Task created with auto-generated ID  
**Fail Criteria:** Wrong status or missing fields

---

#### Scenario 4.5: PUT /api/tasks/:id - Update Task Completion
**Precondition:** Task with ID 1 exists  
**Steps:**
1. Send PUT to `/api/tasks/1`
2. Payload: `{ "completed": true }`

**Expected Results:**
- Status: 200 OK
- Response returns updated task with `completed: true`
- Subsequent GET /api/tasks shows task as completed

**Pass Criteria:** Task completion status updated  
**Fail Criteria:** Status not changed or wrong HTTP code

---

#### Scenario 4.6: DELETE /api/tasks/:id - Delete Task
**Precondition:** Task with ID 4 exists  
**Steps:**
1. Send DELETE to `/api/tasks/4`
2. Send GET to `/api/tasks` to verify

**Expected Results:**
- Status: 204 No Content (or 200)
- Task no longer appears in GET /api/tasks
- Other tasks unaffected

**Pass Criteria:** Task deleted and removed from list  
**Fail Criteria:** Task still exists or error returned

---

### Category 5: Responsive Design (3 Scenarios)

#### Scenario 5.1: Mobile View (375px)
**Precondition:** Application loaded at 375px viewport  
**Steps:**
1. Set browser width: 375px (iPhone SE)
2. Set browser height: 667px
3. Login with admin credentials
4. Navigate through all major screens:
   - Login form
   - Dashboard
   - Task list
   - Add task form
5. Verify no horizontal scrolling needed
6. Test button/input interactivity
7. Check form layout stacking

**Expected Results:**
- All content visible without horizontal scrolling
- Buttons and inputs remain accessible
- Text readable at normal zoom (16px+)
- Forms stack vertically
- Task list items stack vertically
- No elements overlap
- Touch targets ≥ 48px (recommended)

**Pass Criteria:** No horizontal scroll; all elements accessible  
**Fail Criteria:** Horizontal scroll required or content hidden

---

#### Scenario 5.2: Tablet View (768px)
**Precondition:** Application loaded at 768px viewport  
**Steps:**
1. Set browser width: 768px (iPad)
2. Set browser height: 1024px
3. Complete same checks as mobile
4. Verify layout is optimized for mid-size screen

**Expected Results:**
- Content may use 2-column or optimized layout
- Better spacing than mobile
- All elements still accessible
- Task cards may display differently (side-by-side if applicable)
- Navigation and controls remain prominent

**Pass Criteria:** Tablet layout optimized  
**Fail Criteria:** Layout breaks or elements misaligned

---

#### Scenario 5.3: Desktop View (1280px)
**Precondition:** Application loaded at 1280px+ viewport  
**Steps:**
1. Set browser width: 1280px (full desktop)
2. Set browser height: 720px
3. Verify full layout utilization
4. Check spacing and proportions

**Expected Results:**
- Full desktop layout displayed
- Adequate white space
- No wasted space
- Sidebar (if present) or full-width layout appropriate
- Task cards may display in grid or list format
- Statistics prominently displayed

**Pass Criteria:** Desktop layout clean and well-spaced  
**Fail Criteria:** Layout doesn't scale properly

---

### Category 6: Accessibility (4 Scenarios)

#### Scenario 6.1: Keyboard Navigation - Login Form
**Precondition:** User at login page  
**Steps:**
1. Press Tab from page start
2. Verify focus order: Email input → Password input → Login button → Register tab
3. Click "Register" tab with keyboard (Space/Enter on focused tab)
4. Verify Register form tab focused and form visible
5. Press Tab through Register form: Name → Email → Password → Register button
6. Click Register button with Space/Enter

**Expected Results:**
- All interactive elements reachable via Tab
- Focus visible (outline or highlight)
- Tab order is logical (left-to-right, top-to-bottom)
- Enter/Space activates buttons
- No keyboard traps (can always Tab to next element)

**Pass Criteria:** Full keyboard navigation without mouse  
**Fail Criteria:** Keyboard trap or skipped elements

---

#### Scenario 6.2: Keyboard Navigation - Task Management
**Precondition:** User logged in on dashboard  
**Steps:**
1. Press Tab to reach task list
2. Navigate to first task
3. Press Tab to reach task checkbox
4. Press Space to toggle completion
5. Press Tab to reach delete button
6. Use arrow keys (if implemented) or Tab to navigate tasks
7. Verify search and filter inputs are reachable via Tab

**Expected Results:**
- Checkboxes can be toggled via Space key
- Delete buttons can be activated via Space/Enter
- Search input focuses with Tab
- Filter dropdown navigable via Tab + arrow keys
- All interactive task controls accessible

**Pass Criteria:** Task controls fully keyboard-accessible  
**Fail Criteria:** Mouse required for any control

---

#### Scenario 6.3: Form Labels & ARIA Attributes
**Precondition:** Inspect HTML source  
**Steps:**
1. Open browser DevTools
2. Inspect login email input: verify associated label
3. Inspect login password input: verify associated label
4. Inspect task title input: verify label or aria-label
5. Check for aria-label on icon buttons (delete, etc.)
6. Verify form has aria-labelledby or legend (if fieldset)

**Expected Results:**
- All form inputs have associated labels (via `<label>` or aria-label)
- Example: `<input id="email" /> <label for="email">Email</label>`
- Icon buttons have aria-label describing purpose
- Form sections use semantic HTML (fieldset, legend if applicable)
- Error messages linked to inputs via aria-describedby

**Pass Criteria:** All inputs properly labeled  
**Fail Criteria:** Missing labels or ARIA attributes

---

#### Scenario 6.4: Screen Reader Compatibility
**Precondition:** Screen reader enabled (NVDA, JAWS, or Mac VoiceOver)  
**Steps:**
1. Enable screen reader
2. Navigate to login page
3. Verify screen reader announces:
   - Page title/heading
   - Form labels before inputs
   - Button purposes
   - Notification messages
4. Login and navigate to dashboard
5. Verify task list is announced with context
6. Verify priority badge is read (e.g., "Learn Playwright, high priority")

**Expected Results:**
- Screen reader announces all form elements
- Headings and structure announced correctly
- Notifications announced immediately
- Task information complete and in logical order
- No silent or invisible elements blocking navigation

**Pass Criteria:** Full screen reader support  
**Fail Criteria:** Missing announcements or unclear structure

---

## Test Data & Environment

### Test Data Definition

**Users:**
```javascript
{
  "admin": {
    "email": "admin@test.com",
    "password": "admin123",
    "name": "Admin User",
    "id": 1
  },
  "user": {
    "email": "user@test.com",
    "password": "user123",
    "name": "Test User",
    "id": 2
  }
}
```

**Pre-seeded Tasks:**
```javascript
[
  {
    "id": 1,
    "title": "Learn Playwright",
    "priority": "high",
    "completed": false
  },
  {
    "id": 2,
    "title": "Compare with Katalon",
    "priority": "medium",
    "completed": false
  },
  {
    "id": 3,
    "title": "Write test cases",
    "priority": "high",
    "completed": true
  }
]
```

### Environment Configuration

**Local Development:**
```bash
# Install all dependencies
npm install
cd frontend && npm install && cd ..

# Install Playwright browsers
npx playwright install

# Start backend and frontend
npm run dev
# Backend: http://localhost:3001
# Frontend: http://localhost:5173
```

**Playwright Config Locations:**
- Config file: `playwright.config.js`
- Tests directory: `tests/`
- Report directory: `playwright-report/`

**Environment Variables:**
| Variable | Local Value | CI Value |
|----------|-------------|----------|
| FRONTEND_URL | http://localhost:5173 | https://app.example.com |
| BACKEND_URL | http://localhost:3001 | https://api.example.com |
| NODE_ENV | development | ci |

---

## Test Execution Plan

### Pre-Test Setup
```bash
# 1. Install dependencies
npm install && cd frontend && npm install && cd ..

# 2. Install Playwright browsers
npx playwright install

# 3. Start application
npm run dev          # Runs backend + frontend concurrently
# OR separately:
npm run dev:backend  # Terminal 1
npm run dev:frontend # Terminal 2

# 4. Verify app is accessible
# Open http://localhost:5173 in browser
```

### Test Execution Commands

**Run All Tests (Headless):**
```bash
npm test
# OR
npx playwright test
```

**Run Specific Test File:**
```bash
npx playwright test tests/auth.spec.js
npx playwright test tests/tasks.spec.js
npx playwright test tests/api.spec.js
npx playwright test tests/search-filter.spec.js
npx playwright test tests/responsive.spec.js
npx playwright test tests/accessibility.spec.js
```

**Run in Headed Mode (See Browser):**
```bash
npm run test:headed
# OR
npx playwright test --headed
```

**Run with UI Mode (Interactive):**
```bash
npm run test:ui
# OR
npx playwright test --ui
```

**Run Specific Test by Name:**
```bash
npx playwright test -g "Login with Valid Credentials"
npx playwright test -g "Create New Task"
```

**Run by Browser:**
```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

**Debug Mode (Step Through):**
```bash
npx playwright test --debug
```

**Generate & View HTML Report:**
```bash
npm run test:report
# OR
npx playwright show-report
```

### Parallel Execution Strategy

**Group 1 - Fast API Tests (5-10s):**
```bash
npx playwright test tests/api.spec.js --workers=4
```

**Group 2 - Auth Tests (15-20s):**
```bash
npx playwright test tests/auth.spec.js --workers=2
```

**Group 3 - Core Functionality (30-45s):**
```bash
npx playwright test tests/tasks.spec.js tests/search-filter.spec.js --workers=2
```

**Group 4 - Responsive & A11y (20-30s):**
```bash
npx playwright test tests/responsive.spec.js tests/accessibility.spec.js --workers=1
```

**Total Parallel Time:** ~30-40 seconds (vs. 2-3 minutes sequential)

### CI/CD Integration

**GitHub Actions Workflow (`.github/workflows/playwright.yml`):**
```yaml
name: Playwright Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          npm install
          cd frontend && npm install && cd ..
          npx playwright install --with-deps
      
      - name: Start application
        run: npm run dev &
      
      - name: Wait for app to be ready
        run: npx wait-on http://localhost:5173 http://localhost:3001
      
      - name: Run Playwright tests
        run: npm test
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

---

## Success Criteria

### Test Execution Success
- ✅ All 42+ test scenarios pass
- ✅ No timeout failures (default 30s per test)
- ✅ Zero flaky tests (no random failures)
- ✅ Code coverage ≥ 80% for core flows
- ✅ All critical scenarios pass (auth, CRUD, API)

### Quality Gates
| Metric | Threshold | Target |
|--------|-----------|--------|
| Tests Passed | ≥ 95% | 100% |
| Execution Time | < 5 min | < 3 min |
| Flakiness | 0% | 0% |
| API Schema Compliance | 100% | 100% |
| Responsive Viewports | 3/3 | Pass all |
| Accessibility Issues | 0 critical | 0 total |

### Regression Prevention
- All scenarios pass before merge to main
- New features must include corresponding tests
- Failing tests block PR until fixed
- Reports archived for baseline comparison

---

## Risks & Mitigation

### Risk 1: Flaky Tests due to Timing
**Severity:** High  
**Impact:** Unreliable test results; false negatives  
**Mitigation:**
- Use Playwright's auto-waiting (built-in)
- Add explicit `waitFor` for critical elements
- Implement retry logic for network-dependent tests
- Set reasonable timeouts (30s for E2E, 10s for API)

### Risk 2: State Leakage Between Tests
**Severity:** High  
**Impact:** Test interdependency; cascading failures  
**Mitigation:**
- Use `beforeEach` hooks to reset state
- Clear localStorage and cookies between tests
- Use unique test data (timestamps for emails/titles)
- Isolate tests with fresh database state

### Risk 3: In-Memory Database Doesn't Persist
**Severity:** Medium  
**Impact:** Data loss between app restarts  
**Mitigation:**
- Accept in-memory for POC (limitations documented)
- Pre-seed data in `beforeEach`
- Plan migration to persistent DB for production
- Document database limitations in test comments

### Risk 4: Browser Compatibility Issues
**Severity:** Medium  
**Impact:** Tests pass in Chrome but fail in Firefox/Safari  
**Mitigation:**
- Include Firefox and WebKit in test matrix (optional for MVP)
- Test responsive design across all browsers
- Use Playwright's cross-browser testing
- Document browser-specific limitations

### Risk 5: Port Conflicts (3001, 5173)
**Severity:** Low  
**Impact:** Tests fail if ports already in use  
**Mitigation:**
- Use dynamic port assignment in config
- Document port requirements
- Add port availability check before test run
- Use Docker for isolated CI environment

### Risk 6: Accessibility Testing Coverage
**Severity:** Medium  
**Impact:** A11y issues missed in automated tests  
**Mitigation:**
- Use axe-core plugin for automated checks
- Include manual keyboard navigation tests
- Test with screen readers (NVDA, VoiceOver)
- Involve QA with a11y expertise

---

## Test Execution Summary

### Quick Reference

| Task | Command | Duration |
|------|---------|----------|
| Setup | `npm install && npm run dev` | 2-3 min |
| All Tests | `npm test` | 3-5 min |
| Quick Smoke | `npx playwright test -g "Login\|Create Task"` | 30s |
| Headed Mode | `npm run test:headed` | 3-5 min |
| UI Mode | `npm run test:ui` | Interactive |
| View Report | `npm run test:report` | Instant |

### Expected Results
- **Pass Rate:** 100% (42+ scenarios)
- **Flakiness:** 0%
- **Coverage:** Core functionality, API, UI, A11y, Responsive
- **Time:** ~5 minutes for full suite

### Sign-Off
This test plan is approved for implementation and provides comprehensive coverage for the Task Manager POC application using Playwright.

**Test Plan Version:** 1.0  
**Date Created:** February 4, 2026  
**Status:** Ready for Execution

---

## Appendix: Test File Mapping

```
tests/
├── auth.spec.js           → Scenarios 1.1-1.6 (Authentication)
├── tasks.spec.js          → Scenarios 2.1-2.8 (Task Management)
├── search-filter.spec.js  → Scenarios 3.1-3.5 (Search & Filter)
├── api.spec.js            → Scenarios 4.1-4.6 (API Validation)
├── responsive.spec.js     → Scenarios 5.1-5.3 (Responsive Design)
├── accessibility.spec.js  → Scenarios 6.1-6.4 (Accessibility)
└── seed.spec.ts           → Data seeding (optional for future use)
```

---

**Document End**
