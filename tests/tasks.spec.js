// @ts-check
const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../pages/LoginPage');
const { DashboardPage } = require('../pages/DashboardPage');

/**
 * Task Management Test Suite
 * Tests CRUD operations for tasks
 */

test.describe('Task Management', () => {
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

  test.describe('Task Display', () => {
    test('should display task statistics', async () => {
      await expect(dashboardPage.statTotal).toBeVisible();
      await expect(dashboardPage.statCompleted).toBeVisible();
      await expect(dashboardPage.statPending).toBeVisible();
      await expect(dashboardPage.statUrgent).toBeVisible();
    });

    test('should display existing tasks', async () => {
      await expect(dashboardPage.tasksList).toBeVisible();
      await expect(dashboardPage.taskItems().first()).toBeVisible();
    });

    test('should display task with priority badge', async () => {
      const taskItem = dashboardPage.firstTaskItem();
      await expect(taskItem).toBeVisible();
      await expect(taskItem.locator('.task-priority')).toBeVisible();
    });
  });

  test.describe('Create Task', () => {
    test('should add a new task', async () => {
      const taskTitle = `Test Task ${Date.now()}`;
      await dashboardPage.addTask(taskTitle);
      await expect(dashboardPage.notification).toHaveText(/Task added/);
      await expect(dashboardPage.page.getByText(taskTitle)).toBeVisible();
    });

    test('should add task with specific priority', async () => {
      const taskTitle = `High Priority Task ${Date.now()}`;
      await dashboardPage.addTask(taskTitle, 'high');
      await expect(dashboardPage.page.getByText(taskTitle)).toBeVisible();
      const taskElement = dashboardPage.taskItemByTitle(taskTitle);
      await expect(taskElement.locator('.priority-high')).toBeVisible();
    });

    test('should not add empty task', async () => {
      const initialTasks = await dashboardPage.taskItems().count();
      await dashboardPage.addEmptyTask();
      const finalTasks = await dashboardPage.taskItems().count();
      expect(finalTasks).toBe(initialTasks);
    });
  });

  test.describe('Update Task', () => {
    test('should toggle task completion', async () => {
      const taskItem = dashboardPage.firstTaskItem();
      const wasCompleted = await taskItem.evaluate((el) => el.classList.contains('completed'));
      await dashboardPage.toggleFirstTask();
      if (wasCompleted) {
        await expect(taskItem).not.toHaveClass(/completed/);
      } else {
        await expect(taskItem).toHaveClass(/completed/);
      }
    });

    test('should update statistics when task is completed', async () => {
      const completedStat = dashboardPage.completedStatValue();
      const initialCompleted = parseInt((await completedStat.textContent()) || '0', 10);
      const taskItem = dashboardPage.taskItemNotCompleted();
      if (await taskItem.isVisible()) {
        const taskId = await taskItem.getAttribute('data-testid');
        const id = taskId?.replace('task-', '');
        await dashboardPage.page.getByTestId(`task-toggle-${id}`).click();
        await expect(completedStat).toHaveText(String(initialCompleted + 1));
      }
    });
  });

  test.describe('Delete Task', () => {
    test('should delete a task', async () => {
      const taskTitle = `Delete Me ${Date.now()}`;
      await dashboardPage.addTask(taskTitle);
      await expect(dashboardPage.page.getByText(taskTitle)).toBeVisible();
      await dashboardPage.deleteTaskByTitle(taskTitle);
      await expect(dashboardPage.notification).toHaveText(/Task deleted/);
      await expect(dashboardPage.page.getByText(taskTitle)).not.toBeVisible();
    });
  });
});
