// @ts-check
const path = require('path');
const os = require('os');
const { defineConfig, devices } = require('@playwright/test');

// Use a directory outside OneDrive to avoid EPERM when Playwright cleans up test-results
const outputDir = path.join(os.tmpdir(), 'playwright-poc-output');

/**
 * Playwright Configuration for Task Manager POC
 * @see https://playwright.dev/docs/test-configuration
 */
module.exports = defineConfig({
  testDir: './tests',

  /* Output artifacts (traces, videos, etc.) outside OneDrive to prevent EPERM on cleanup */
  outputDir,

  /* Run tests in parallel */
  fullyParallel: true,
  
  /* Fail the build on CI if you accidentally left test.only in the source code */
  forbidOnly: !!process.env.CI,
  
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  
  /* Opt out of parallel tests on CI */
  workers: process.env.CI ? 1 : undefined,
  
  /* Reporter to use. HTML report: playwright-report/ (npm run test:report). Allure: results append to allure-results/ each run → collective report. */
  reporter: [
    ['list'],
    ['html', { open: 'on-failure', outputFolder: 'playwright-report' }],
    ['json', { outputFile: path.join(outputDir, 'results.json') }],
    ['allure-playwright', { outputFolder: 'allure-results' }],
  ],
  
  /* Shared settings for all the projects below */
  use: {
    /* Base URL to use in actions like `await page.goto('/')` */
    baseURL: 'http://localhost:3001',

    /* Collect trace when retrying the failed test */
    trace: 'on-first-retry',
    
    /* Take screenshot on failure */
    screenshot: 'only-on-failure',
    
    /* Video recording */
    video: 'on-first-retry',
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    }
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'npm run dev:backend',
    url: 'http://localhost:3001/api/health',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
