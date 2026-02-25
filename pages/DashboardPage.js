// @ts-check
const { BasePage } = require('./BasePage');

/**
 * Dashboard / Tasks Page Object
 * Covers task list, add task, search, filter, stats, logout
 */
class DashboardPage extends BasePage {
  constructor(page) {
    super(page);
  }

  // --- Selectors ---
  get tasksList() {
    return this.page.getByTestId('tasks-list');
  }
  get userName() {
    return this.page.getByTestId('user-name');
  }
  get logoutBtn() {
    return this.page.getByTestId('logout-btn');
  }
  get newTaskInput() {
    return this.page.getByTestId('new-task-input');
  }
  get newTaskPriority() {
    return this.page.getByTestId('new-task-priority');
  }
  get addTaskBtn() {
    return this.page.getByTestId('add-task-btn');
  }
  get searchInput() {
    return this.page.getByTestId('search-input');
  }
  get priorityFilter() {
    return this.page.getByTestId('priority-filter');
  }
  get statTotal() {
    return this.page.getByTestId('stat-total');
  }
  get statCompleted() {
    return this.page.getByTestId('stat-completed');
  }
  get statPending() {
    return this.page.getByTestId('stat-pending');
  }
  get statUrgent() {
    return this.page.getByTestId('stat-urgent');
  }
  get notification() {
    return this.page.getByTestId('notification');
  }
  get emptyState() {
    return this.page.getByTestId('empty-state');
  }

  taskItemByTitle(title) {
    return this.page.locator('.task-item', { hasText: title });
  }

  taskToggleSelector(id) {
    return this.page.getByTestId(`task-toggle-${id}`);
  }

  taskDeleteForItem(taskLocator) {
    return taskLocator.locator('.task-delete');
  }

  firstTaskToggle() {
    return this.page.locator('[data-testid^="task-toggle-"]').first();
  }

  firstTaskItem() {
    return this.page.locator('[data-testid^="task-"]:not([data-testid*="toggle"]):not([data-testid*="delete"])').first();
  }

  taskItems() {
    return this.page.locator('[data-testid^="task-"]:not([data-testid*="toggle"]):not([data-testid*="delete"])');
  }

  firstCheckbox() {
    return this.page.locator('[data-testid^="task-toggle-"]').first();
  }

  firstDeleteBtn() {
    return this.page.locator('[data-testid^="task-delete-"]').first();
  }

  visibleTaskItems() {
    return this.page.locator('.task-item:visible');
  }

  allTaskItems() {
    return this.page.locator('.task-item');
  }

  completedStatValue() {
    return this.statCompleted.locator('.stat-value');
  }

  taskItemNotCompleted() {
    return this.page.locator('.task-item:not(.completed)').first();
  }

  taskItemWithSelector(selector) {
    return this.page.locator('[data-testid^="task-"]:not([data-testid*="toggle"]):not([data-testid*="delete"])').first();
  }

  taskRowForKeyboardDelete(title) {
    return this.page.locator('.task-item', { hasText: title });
  }

  // --- Actions ---
  async waitForDashboard() {
    await this.tasksList.waitFor({ state: 'visible' });
  }

  /**
   * @param {string} title
   * @param {string | null | undefined} [priority] - e.g. 'high', 'medium', 'low'
   */
  async addTask(title, priority = null) {
    await this.newTaskInput.fill(title);
    if (priority) {
      await this.newTaskPriority.selectOption(priority);
    }
    await this.addTaskBtn.click();
  }

  async addEmptyTask() {
    await this.newTaskInput.fill('');
    await this.addTaskBtn.click();
  }

  async search(term) {
    await this.searchInput.fill(term);
  }

  async clearSearch() {
    await this.searchInput.clear();
  }

  async setPriorityFilter(value) {
    await this.priorityFilter.selectOption(value);
  }

  async toggleFirstTask() {
    await this.firstTaskToggle().click();
  }

  async deleteTaskByTitle(title) {
    const taskEl = this.taskItemByTitle(title);
    await taskEl.locator('.task-delete').click();
  }

  async logout() {
    await this.logoutBtn.click();
  }

  async focusDeleteForTask(title) {
    const taskEl = this.taskRowForKeyboardDelete(title);
    await taskEl.locator('.task-delete').focus();
  }
}

module.exports = { DashboardPage };
