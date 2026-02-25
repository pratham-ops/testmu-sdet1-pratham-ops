# Playwright vs Katalon - POC

A proof of concept demonstrating **Playwright** test automation capabilities. This project includes a full-stack Task Manager application with comprehensive test suites to showcase Playwright's features for comparison with Katalon Studio.

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

### View Playwright HTML Report
```bash
npm run test:report
```

### Allure Reports

Allure results are automatically collected every time tests run (via the `allure-playwright` reporter configured in `playwright.config.js`). Results accumulate across runs, giving you a historical trend view.

**Generate and open the Allure report:**
```bash
# 1. Run your tests (results are written to allure-results/)
npm test

# 2. Generate the HTML report from collected results
npm run allure:generate

# 3. Open the report in your browser
npm run allure:report
```

**Reset/clear all Allure data** (start fresh before a new test cycle):
```bash
npm run allure:reset
```

> **Note:** Allure requires the [Allure CLI](https://allurereport.org/docs/install/) to be installed and available on your `PATH`. Install it via:
> ```bash
> npm install -g allure-commandline
> # or via Scoop on Windows:
> scoop install allure
> ```

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

## 📊 Playwright vs Katalon Comparison

| Feature | Playwright | Katalon |
|---------|------------|---------|
| **Language** | JavaScript/TypeScript/Python/Java/.NET | Groovy (Java-based) |
| **Speed** | Very fast, parallel execution | Moderate |
| **Browser Support** | Chromium, Firefox, WebKit | Chrome, Firefox, Edge, Safari |
| **Mobile Testing** | Device emulation | Native mobile support |
| **API Testing** | Built-in | Requires plugins |
| **Learning Curve** | Moderate (code-based) | Low (visual recorder) |
| **CI/CD** | Excellent (native support) | Good |
| **Cost** | Free & Open Source | Free tier + Paid plans |
| **Auto-wait** | Built-in | Requires configuration |
| **Trace Viewer** | Excellent debugging | Limited |

## 🎯 Key Playwright Features Demonstrated

1. **Auto-waiting** - No explicit waits needed
2. **Parallel Execution** - Tests run concurrently
3. **Multiple Browsers** - Single codebase, all browsers
4. **API Testing** - Direct HTTP request support
5. **Visual Testing** - Screenshot comparison
6. **Trace Viewer** - Debugging with traces
7. **Mobile Emulation** - Test responsive designs
8. **CI/CD Ready** - GitHub Actions integration

## 📝 Test Configuration

Key settings in `playwright.config.js`:
- Base URL: `http://localhost:3001`
- Retries: 2 on CI, 0 locally
- Workers: 1 on CI for stability
- Reporters: List, HTML, JSON, **Allure**
- Screenshots: On failure
- Video: On first retry
- Traces: On first retry

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Submit a pull request

## 📄 License

MIT License - Feel free to use this POC for your evaluation needs.
