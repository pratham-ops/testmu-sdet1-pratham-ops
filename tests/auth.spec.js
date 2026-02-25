// @ts-check
const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../pages/LoginPage');

/**
 * Authentication Test Suite
 * Tests login, registration, and authentication flows
 */

test.describe('Authentication', () => {
  /** @type {LoginPage} */
  let loginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto('/');
  });

  test.describe('Login Flow', () => {
    test('should display login form by default', async () => {
      await expect(loginPage.loginForm).toBeVisible();
      await expect(loginPage.loginEmail).toBeVisible();
      await expect(loginPage.loginPassword).toBeVisible();
      await expect(loginPage.loginSubmit).toBeVisible();
    });

    test('should show error for invalid credentials', async () => {
      await loginPage.login('wrong@email.com', 'wrongpassword');
      await expect(loginPage.notification).toBeVisible();
      await expect(loginPage.notification).toHaveClass(/error/);
    });

    test('should login successfully with valid credentials', async () => {
      await loginPage.login('admin@test.com', 'admin123');
      await expect(loginPage.notification).toBeVisible();
      await expect(loginPage.notification).toHaveClass(/success/);
      await expect(loginPage.page.getByTestId('user-name')).toHaveText('Admin User');
      await expect(loginPage.page.getByTestId('logout-btn')).toBeVisible();
    });

    test('should validate required fields', async () => {
      await loginPage.submitLoginWithEmptyFields();
      await expect(loginPage.loginForm).toBeVisible();
    });
  });

  test.describe('Registration Flow', () => {
    test('should switch to register tab', async () => {
      await loginPage.switchToRegister();
      await expect(loginPage.registerForm).toBeVisible();
      await expect(loginPage.registerName).toBeVisible();
      await expect(loginPage.registerEmail).toBeVisible();
      await expect(loginPage.registerPassword).toBeVisible();
    });

    test('should register a new user successfully', async () => {
      const uniqueEmail = `test-${Date.now()}@example.com`;
      await loginPage.register('New User', uniqueEmail, 'password123');
      await expect(loginPage.notification).toBeVisible();
      await expect(loginPage.notification).toHaveText(/Account created/);
      await expect(loginPage.loginForm).toBeVisible();
    });

    test('should show error for duplicate email', async () => {
      await loginPage.register('Duplicate User', 'admin@test.com', 'password123');
      await expect(loginPage.notification).toBeVisible();
      await expect(loginPage.notification).toHaveClass(/error/);
    });
  });

  test.describe('Logout Flow', () => {
    test('should logout successfully', async () => {
      await loginPage.login('admin@test.com', 'admin123');
      await expect(loginPage.page.getByTestId('logout-btn')).toBeVisible();
      await loginPage.page.getByTestId('logout-btn').click();
      await expect(loginPage.loginForm).toBeVisible();
      await expect(loginPage.notification).toHaveText(/Logged out/);
    });
  });
});
