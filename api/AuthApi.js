// @ts-check

/**
 * Auth API - encapsulates auth API calls for tests
 */
class AuthApi {
  /**
   * @param {import('@playwright/test').APIRequestContext} request
   */
  constructor(request) {
    this.request = request;
  }

  async getHealth() {
    return this.request.get('/api/health');
  }

  async login(email, password) {
    return this.request.post('/api/login', {
      data: { email, password },
    });
  }

  async loginEmpty() {
    return this.request.post('/api/login', { data: {} });
  }

  async register(name, email, password) {
    return this.request.post('/api/register', {
      data: { name, email, password },
    });
  }
}

module.exports = { AuthApi };
