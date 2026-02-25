// @ts-check

/**
 * Tasks API - encapsulates tasks API calls for tests
 */
class TasksApi {
  /**
   * @param {import('@playwright/test').APIRequestContext} request
   */
  constructor(request) {
    this.request = request;
  }

  async getTasks() {
    return this.request.get('/api/tasks');
  }

  async getTask(id) {
    return this.request.get(`/api/tasks/${id}`);
  }

  async createTask(data) {
    return this.request.post('/api/tasks', { data });
  }

  async updateTask(id, data) {
    return this.request.put(`/api/tasks/${id}`, { data });
  }

  async deleteTask(id) {
    return this.request.delete(`/api/tasks/${id}`);
  }

  async search(query) {
    return this.request.get(`/api/search?q=${encodeURIComponent(query)}`);
  }

  async searchEmpty() {
    return this.request.get('/api/search');
  }
}

module.exports = { TasksApi };
