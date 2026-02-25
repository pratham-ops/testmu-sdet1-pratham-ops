// @ts-check
const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../pages/LoginPage');
const { DashboardPage } = require('../pages/DashboardPage');

/**
 * Search and Filter Test Suite
 * Tests search functionality and priority filtering
 */

test.describe('Search and Filter', () => {
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

  test.describe('Search Functionality', () => {
    test('should have search input visible', async () => {
      await expect(dashboardPage.searchInput).toBeVisible();
    });

    test('should filter tasks by search term', async () => {
      const uniqueTitle = `Unique Search Term ${Date.now()}`;
      await dashboardPage.addTask(uniqueTitle);
      await expect(dashboardPage.page.getByText(uniqueTitle)).toBeVisible();
      await dashboardPage.search('Unique Search');
      await expect(dashboardPage.page.getByText(uniqueTitle)).toBeVisible();
      await expect(dashboardPage.visibleTaskItems()).toHaveCount(1);
    });

    test('should show empty state when no tasks match search', async () => {
      await dashboardPage.search('xyznonexistent123');
      await expect(dashboardPage.emptyState).toBeVisible();
    });

    test('should clear search and show all tasks', async () => {
      const initialCount = await dashboardPage.allTaskItems().count();
      await dashboardPage.search('test');
      await dashboardPage.clearSearch();
      await expect(dashboardPage.allTaskItems()).toHaveCount(initialCount);
    });

    test('should search case-insensitively', async () => {
      const taskTitle = 'CaseSensitiveTest';
      await dashboardPage.addTask(taskTitle);
      await dashboardPage.search('casesensitivetest');
      await expect(dashboardPage.page.getByText(taskTitle)).toBeVisible();
    });
  });

  test.describe('Priority Filter', () => {
    test('should have priority filter visible', async () => {
      await expect(dashboardPage.priorityFilter).toBeVisible();
    });

    test('should filter tasks by high priority', async () => {
      const highPriorityTask = `High Priority ${Date.now()}`;
      await dashboardPage.addTask(highPriorityTask, 'high');
      await dashboardPage.setPriorityFilter('high');
      await expect(dashboardPage.page.getByText(highPriorityTask)).toBeVisible();
      const visibleTasks = dashboardPage.visibleTaskItems();
      const count = await visibleTasks.count();
      for (let i = 0; i < count; i++) {
        await expect(visibleTasks.nth(i).locator('.priority-high')).toBeVisible();
      }
    });

    test('should filter tasks by medium priority', async () => {
      const mediumPriorityTask = `Medium Priority ${Date.now()}`;
      await dashboardPage.addTask(mediumPriorityTask, 'medium');
      await dashboardPage.setPriorityFilter('medium');
      await expect(dashboardPage.page.getByText(mediumPriorityTask)).toBeVisible();
    });

    test('should filter tasks by low priority', async () => {
      const lowPriorityTask = `Low Priority ${Date.now()}`;
      await dashboardPage.addTask(lowPriorityTask, 'low');
      await dashboardPage.setPriorityFilter('low');
      await expect(dashboardPage.page.getByText(lowPriorityTask)).toBeVisible();
    });

    test('should show all tasks when filter is set to all', async () => {
      await dashboardPage.setPriorityFilter('high');
      await dashboardPage.setPriorityFilter('all');
      await expect(dashboardPage.allTaskItems().first()).toBeVisible();
    });
  });

  test.describe('Combined Search and Filter', () => {
    test('should combine search and priority filter', async () => {
      await dashboardPage.addTask('FilterTest High', 'high');
      await dashboardPage.addTask('FilterTest Low', 'low');
      await dashboardPage.search('FilterTest');
      await dashboardPage.setPriorityFilter('high');
      await expect(dashboardPage.page.getByText('FilterTest High')).toBeVisible();
      await expect(dashboardPage.page.getByText('FilterTest Low')).not.toBeVisible();
    });
  });
});
