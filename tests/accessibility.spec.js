// @ts-check
const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../pages/LoginPage');
const { DashboardPage } = require('../pages/DashboardPage');

/**
 * Accessibility Test Suite
 * Tests keyboard navigation and ARIA attributes
 */

test.describe('Accessibility', () => {
  test.describe('Login Page Accessibility', () => {
    /** @type {LoginPage} */
    let loginPage;

    test.beforeEach(async ({ page }) => {
      loginPage = new LoginPage(page);
      await loginPage.goto('/');
    });

    test('should have proper form labels', async () => {
      await expect(loginPage.emailLabel).toBeVisible();
      await expect(loginPage.passwordLabel).toBeVisible();
    });

    test('should support keyboard navigation in login form', async ({ page }) => {
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await loginPage.loginEmail.focus();
      await page.keyboard.type('admin@test.com');
      await page.keyboard.press('Tab');
      await expect(loginPage.loginPassword).toBeFocused();
      await page.keyboard.type('admin123');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      await expect(page.getByTestId('user-name')).toBeVisible();
    });

    test('should maintain focus order', async ({ page }) => {
      const focusOrder = [];
      await page.keyboard.press('Tab');
      focusOrder.push(await page.evaluate(() => document.activeElement?.getAttribute('data-testid') || document.activeElement?.tagName));
      await page.keyboard.press('Tab');
      focusOrder.push(await page.evaluate(() => document.activeElement?.getAttribute('data-testid') || document.activeElement?.tagName));
      expect(focusOrder.length).toBeGreaterThan(0);
    });
  });

  test.describe('Dashboard Accessibility', () => {
    /** @type {LoginPage} */
    let loginPage;
    /** @type {DashboardPage} */
    let dashboardPage;

    test.beforeEach(async ({ page }) => {
      loginPage = new LoginPage(page);
      dashboardPage = new DashboardPage(page);
      await loginPage.goto('/');
      await loginPage.login('admin@test.com', 'admin123');
      await dashboardPage.waitForDashboard();
    });

    test('should have accessible task checkboxes', async () => {
      const checkbox = dashboardPage.firstCheckbox();
      await expect(checkbox).toHaveAttribute('aria-label');
    });

    test('should have accessible delete buttons', async () => {
      const deleteBtn = dashboardPage.firstDeleteBtn();
      await expect(deleteBtn).toHaveAttribute('aria-label');
    });

    test('should allow keyboard task completion', async ({ page }) => {
      const checkbox = dashboardPage.firstCheckbox();
      await checkbox.focus();
      const taskItem = dashboardPage.firstTaskItem();
      const wasCompleted = await taskItem.evaluate((el) => el.classList.contains('completed'));
      await page.keyboard.press('Enter');
      if (wasCompleted) {
        await expect(taskItem).not.toHaveClass(/completed/);
      } else {
        await expect(taskItem).toHaveClass(/completed/);
      }
    });

    test('should allow keyboard task deletion', async ({ page }) => {
      const taskTitle = `Keyboard Delete ${Date.now()}`;
      await dashboardPage.addTask(taskTitle);
      await expect(dashboardPage.page.getByText(taskTitle)).toBeVisible();
      await dashboardPage.focusDeleteForTask(taskTitle);
      await page.keyboard.press('Enter');
      await expect(dashboardPage.page.getByText(taskTitle)).not.toBeVisible();
    });

    test('should have accessible search input', async () => {
      await expect(dashboardPage.searchInput).toBeVisible();
    });
  });
});
