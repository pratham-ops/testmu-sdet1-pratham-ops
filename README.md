## 🚀 Quick Start

### Prerequisites
- Node.js 18+ installed
- npm or yarn package manager

### Installation

```bash
# Install root dependencies
npm install

# Install frontend dependencies
cd frontend && npm install && cd ..

# Install Playwright browsers
npx playwright install
```

### Running the Application

```bash
# Run backend and frontend together
npm run dev

# Or run separately:
npm run dev:backend    # Backend on http://localhost:3001
npm run dev:frontend   # Frontend on http://localhost:5173
```

### Demo Credentials
- Email: `admin@test.com`
- Password: `admin123`

## 🧪 Running Tests

### All Tests
```bash
npm test
```

### Headed Mode (See Browser)
```bash
npm run test:headed
```

### Interactive UI Mode
```bash
npm run test:ui
```

### View Report
```bash
npm run test:report
```

### Run Specific Test File
```bash
npx playwright test tests/auth.spec.js
npx playwright test tests/tasks.spec.js
npx playwright test tests/api.spec.js
```

### Run by Browser
```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

## 📁 Project Structure

```
├── backend/
│   └── server.js          # Express.js API server
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Main React component
│   │   ├── App.css        # Component styles
│   │   └── index.css      # Global styles
│   └── index.html         # HTML template
├── tests/
│   ├── auth.spec.js       # Authentication tests
│   ├── tasks.spec.js      # Task CRUD tests
│   ├── search-filter.spec.js  # Search & filter tests
│   ├── api.spec.js        # API endpoint tests
│   ├── accessibility.spec.js  # Accessibility tests
│   └── responsive.spec.js # Responsive design tests
├── .github/
│   └── workflows/
│       └── playwright.yml # CI/CD pipeline
├── playwright.config.js   # Playwright configuration
└── package.json
```

## 🔬 Test Suites

### 1. Authentication Tests (`auth.spec.js`)
- Login form display
- Invalid credentials handling
- Successful login flow
- Registration flow
- Logout functionality

### 2. Task Management Tests (`tasks.spec.js`)
- Display task statistics
- Create new tasks
- Set task priority
- Toggle task completion
- Delete tasks

### 3. Search & Filter Tests (`search-filter.spec.js`)
- Search functionality
- Case-insensitive search
- Priority filtering
- Combined search + filter

### 4. API Tests (`api.spec.js`)
- Health check endpoint
- Authentication endpoints
- Task CRUD endpoints
- Search endpoint

### 5. Accessibility Tests (`accessibility.spec.js`)
- Form labels
- Keyboard navigation
- ARIA attributes
- Focus management

### 6. Responsive Tests (`responsive.spec.js`)
- Mobile viewport (375px)
- Tablet viewport (768px)
- Desktop viewport (1920px)

## 🔄 CI/CD Integration

The project includes a GitHub Actions workflow (`.github/workflows/playwright.yml`) that:

1. Runs on push/PR to main branch
2. Tests on Chromium, Firefox, and WebKit in parallel
3. Uploads test reports as artifacts
4. Can be triggered manually via `workflow_dispatch`

### Triggering Tests in CI

```bash
# Push to trigger tests
git push origin main

# Or manually trigger via GitHub Actions UI
```
