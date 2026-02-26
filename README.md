#Test Automation POC

A comprehensive Playwright test automation framework featuring AI-powered test failure analysis, GitHub Copilot agents for test generation/healing, and multi-browser support with Allure reporting.

## Features

- **End-to-End Testing** with Playwright across Chromium, Firefox, and WebKit
- **AI-Powered Failure Analysis** using Azure OpenAI for intelligent debugging
- **GitHub Copilot Agents** for automated test generation and self-healing tests
- **Page Object Model** architecture for maintainable tests.
- **CI/CD Ready** with GitHub Actions workflow

## Quick Start

### Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Python 3.8+ (for AI failure explainer)

### Installation

```bash
# Install root dependencies
npm install

# Install frontend dependencies
cd frontend && npm install && cd ..

# Install Playwright browsers
npx playwright install

# Install Python dependencies (for AI failure explainer)
pip install openai python-dotenv
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

## Running Tests

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

### Run with AI Failure Explanation
```bash
# Run tests and generate AI-powered failure explanations
npm run test

# Or generate explanations for existing test results
npm run explain
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

## AI-Powered Features

### Test Failure Explainer

The AI failure explainer analyzes test failures using Azure OpenAI and provides:
- **Root Cause Analysis** - Identifies the underlying cause of failures
- **Plain English Explanations** - Describes what went wrong
- **Suggested Fixes** - Actionable steps to resolve issues
- **Visual Reports** - Interactive HTML report with screenshots and traces

#### Setup

Create a `.env` file with your Azure OpenAI credentials:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=o3-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

#### Usage

```bash
# Run tests and automatically generate AI explanations
npm run test:explain

# Generate explanations for existing test results
npm run explain
```

Reports are saved to `test-failure-explanations/` with both HTML and JSON formats.


## Project Structure

```
├── backend/
│   └── server.js              # Express.js API server
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main React component
│   │   ├── App.css            # Component styles
│   │   └── index.css          # Global styles
│   └── index.html             # HTML template
├── tests/
│   ├── auth.spec.js           # Authentication tests
│   ├── tasks.spec.js          # Task CRUD tests
│   ├── search-filter.spec.js  # Search & filter tests
│   ├── api.spec.js            # API endpoint tests
│   ├── accessibility.spec.js  # Accessibility tests
│   ├── responsive.spec.js     # Responsive design tests
│   └── seed.spec.js           # Seed/setup test
├── pages/
│   ├── BasePage.js            # Base page object
│   ├── LoginPage.js           # Login page object
│   └── DashboardPage.js       # Dashboard page object
├── scripts/
│   └── failure_explainer.py   # AI-powered failure analysis
|
├── test-failure-explanations/ # AI analysis output
├── allure-results/            # Allure test results
├── playwright-report/         # Playwright HTML report
├── playwright.config.js       # Playwright configuration
├── PROMPTS.md                 # Test generation prompts
└── package.json
```

