// @ts-check

/**
 * Base Page Object - shared behavior for all pages
 */
class BasePage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page;
  }

  /**
   * Navigate to a path (relative to baseURL)
   * @param {string} path
   */
  async goto(path = '/') {
    await this.page.goto(path);
  }
}

module.exports = { BasePage };
