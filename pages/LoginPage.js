// @ts-check
const { BasePage } = require('./BasePage');

/**
 * Login / Auth Page Object
 * Covers login form, register tab, and auth actions
 */
class LoginPage extends BasePage {
  constructor(page) {
    super(page);
  }

  // --- Selectors ---
  get loginForm() {
    return this.page.getByTestId('login-form');
  }
  get loginEmail() {
    return this.page.getByTestId('login-email');
  }
  get loginPassword() {
    return this.page.getByTestId('login-password');
  }
  get loginSubmit() {
    return this.page.getByTestId('login-submit');
  }
  get registerTab() {
    return this.page.getByTestId('register-tab');
  }
  get registerForm() {
    return this.page.getByTestId('register-form');
  }
  get registerName() {
    return this.page.getByTestId('register-name');
  }
  get registerEmail() {
    return this.page.getByTestId('register-email');
  }
  get registerPassword() {
    return this.page.getByTestId('register-password');
  }
  get registerSubmit() {
    return this.page.getByTestId('register-submit');
  }
  get notification() {
    return this.page.getByTestId('notification');
  }
  get emailLabel() {
    return this.page.locator('label[for="login-email"]');
  }
  get passwordLabel() {
    return this.page.locator('label[for="login-password"]');
  }

  // --- Actions ---
  async login(email, password) {
    await this.loginEmail.fill(email);
    await this.loginPassword.fill(password);
    await this.loginSubmit.click();
  }

  async switchToRegister() {
    await this.registerTab.click();
  }

  async register(name, email, password) {
    await this.switchToRegister();
    await this.registerName.fill(name);
    await this.registerEmail.fill(email);
    await this.registerPassword.fill(password);
    await this.registerSubmit.click();
  }

  async submitLoginWithEmptyFields() {
    await this.loginSubmit.click();
  }
}

module.exports = { LoginPage };
