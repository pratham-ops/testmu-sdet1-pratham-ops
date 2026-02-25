// @ts-check
const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../pages/LoginPage');
const { DashboardPage } = require('../pages/DashboardPage');

/**
 * Responsive Design Test Suite
 * Tests UI on different screen sizes
 */

test.describe('Responsive Design', () => {
  test.describe('Mobile View', () => {
    test.use({ viewport: { width: 375, height: 667 } });

    test('should display login form properly on mobile', async ({ page }) => {
      const loginPage = new LoginPage(page);
      await loginPage.goto('/');
      await expect(loginPage.loginForm).toBeVisible();
      await expect(loginPage.loginEmail).toBeVisible();
      await expect(loginPage.loginPassword).toBeVisible();
      await expect(loginPage.loginSubmit).toBeVisible();
    });

    test('should display dashboard properly on mobile', async ({ page }) => {
      const loginPage = new LoginPage(page);
      const dashboardPage = new DashboardPage(page);
      await loginPage.goto('/');
      await loginPage.login('admin@test.com', 'admin123');
      await dashboardPage.waitForDashboard();
      await expect(dashboardPage.logoutBtn).toBeVisible();
      await expect(dashboardPage.newTaskInput).toBeVisible();
      await expect(dashboardPage.addTaskBtn).toBeVisible();
    });

    test('should allow task creation on mobile', async ({ page }) => {
      const loginPage = new LoginPage(page);
      const dashboardPage = new DashboardPage(page);
      await loginPage.goto('/');
      await loginPage.login('admin@test.com', 'admin123');
      await dashboardPage.waitForDashboard();
      const taskTitle = `Mobile Task ${Date.now()}`;
      await dashboardPage.addTask(taskTitle);
      await expect(dashboardPage.page.getByText(taskTitle)).toBeVisible();
    });
  });

  test.describe('Tablet View', () => {
    test.use({ viewport: { width: 768, height: 1024 } });

    test('should display stats grid properly on tablet', async ({ page }) => {
      const loginPage = new LoginPage(page);
      const dashboardPage = new DashboardPage(page);
      await loginPage.goto('/');
      await loginPage.login('admin@test.com', 'admin123');
      await dashboardPage.waitForDashboard();
      await expect(dashboardPage.statTotal).toBeVisible();
      await expect(dashboardPage.statCompleted).toBeVisible();
      await expect(dashboardPage.statPending).toBeVisible();
      await expect(dashboardPage.statUrgent).toBeVisible();
    });
  });

  test.describe('Desktop View', () => {
    test.use({ viewport: { width: 1920, height: 1080 } });

    test('should display full layout on desktop', async ({ page }) => {
      const loginPage = new LoginPage(page);
      const dashboardPage = new DashboardPage(page);
      await loginPage.goto('/');
      await loginPage.login('admin@test.com', 'admin123');
      await dashboardPage.waitForDashboard();
      await expect(dashboardPage.userName).toBeVisible();
      await expect(dashboardPage.logoutBtn).toBeVisible();
      await expect(dashboardPage.searchInput).toBeVisible();
      await expect(dashboardPage.priorityFilter).toBeVisible();
    });
  });
});
