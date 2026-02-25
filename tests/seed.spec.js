// @ts-check
const { test } = require('@playwright/test');
const { LoginPage } = require('../pages/LoginPage');

test.describe('Test group', () => {
  test('seed', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto('/');
  });
});
