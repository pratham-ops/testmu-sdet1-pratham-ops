// @ts-check
const { test, expect } = require('@playwright/test');
const { AuthApi } = require('../api/AuthApi');
const { TasksApi } = require('../api/TasksApi');

/**
 * API Test Suite
 * Tests backend API endpoints via API helper classes
 */

test.describe('API Endpoints', () => {
  test.describe('Health Check', () => {
    test('GET /api/health - should return health status', async ({ request }) => {
      const authApi = new AuthApi(request);
      const response = await authApi.getHealth();
      expect(response.ok()).toBeTruthy();
      const data = await response.json();
      expect(data.status).toBe('ok');
      expect(data.timestamp).toBeDefined();
    });
  });

  test.describe('Authentication API', () => {
    test('POST /api/login - should login with valid credentials', async ({ request }) => {
      const authApi = new AuthApi(request);
      const response = await authApi.login('admin@test.com', 'admin123');
      expect(response.ok()).toBeTruthy();
      const data = await response.json();
      expect(data.success).toBe(true);
      expect(data.user.email).toBe('admin@test.com');
      expect(data.token).toBeDefined();
    });

    test('POST /api/login - should reject invalid credentials', async ({ request }) => {
      const authApi = new AuthApi(request);
      const response = await authApi.login('wrong@email.com', 'wrongpass');
      expect(response.status()).toBe(401);
      const data = await response.json();
      expect(data.error).toBe('Invalid credentials');
    });

    test('POST /api/login - should require email and password', async ({ request }) => {
      const authApi = new AuthApi(request);
      const response = await authApi.loginEmpty();
      expect(response.status()).toBe(400);
      const data = await response.json();
      expect(data.error).toBe('Email and password are required');
    });

    test('POST /api/register - should register new user', async ({ request }) => {
      const authApi = new AuthApi(request);
      const uniqueEmail = `test-${Date.now()}@example.com`;
      const response = await authApi.register('Test User', uniqueEmail, 'password123');
      expect(response.status()).toBe(201);
      const data = await response.json();
      expect(data.success).toBe(true);
      expect(data.user.email).toBe(uniqueEmail);
    });

    test('POST /api/register - should reject duplicate email', async ({ request }) => {
      const authApi = new AuthApi(request);
      const response = await authApi.register('Duplicate User', 'admin@test.com', 'password123');
      expect(response.status()).toBe(409);
      const data = await response.json();
      expect(data.error).toBe('User already exists');
    });
  });

  test.describe('Tasks API', () => {
    test('GET /api/tasks - should return tasks array', async ({ request }) => {
      const tasksApi = new TasksApi(request);
      const response = await tasksApi.getTasks();
      expect(response.ok()).toBeTruthy();
      const data = await response.json();
      expect(Array.isArray(data)).toBe(true);
    });

    test('GET /api/tasks/:id - should return specific task', async ({ request }) => {
      const tasksApi = new TasksApi(request);
      const tasksResponse = await tasksApi.getTasks();
      const tasks = await tasksResponse.json();
      if (tasks.length > 0) {
        const taskId = tasks[0].id;
        const response = await tasksApi.getTask(taskId);
        expect(response.ok()).toBeTruthy();
        const task = await response.json();
        expect(task.id).toBe(taskId);
        expect(task.title).toBeDefined();
      }
    });

    test('GET /api/tasks/:id - should return 404 for non-existent task', async ({ request }) => {
      const tasksApi = new TasksApi(request);
      const response = await tasksApi.getTask(99999);
      expect(response.status()).toBe(404);
    });

    test('POST /api/tasks - should create new task', async ({ request }) => {
      const tasksApi = new TasksApi(request);
      const response = await tasksApi.createTask({
        title: `API Test Task ${Date.now()}`,
        priority: 'high',
      });
      expect(response.status()).toBe(201);
      const task = await response.json();
      expect(task.id).toBeDefined();
      expect(task.title).toContain('API Test Task');
      expect(task.priority).toBe('high');
      expect(task.completed).toBe(false);
    });

    test('POST /api/tasks - should require title', async ({ request }) => {
      const tasksApi = new TasksApi(request);
      const response = await tasksApi.createTask({ priority: 'high' });
      expect(response.status()).toBe(400);
      const data = await response.json();
      expect(data.error).toBe('Title is required');
    });

    test('PUT /api/tasks/:id - should update task', async ({ request }) => {
      const tasksApi = new TasksApi(request);
      const createResponse = await tasksApi.createTask({
        title: 'Task to update',
        priority: 'low',
      });
      const task = await createResponse.json();
      const updateResponse = await tasksApi.updateTask(task.id, {
        completed: true,
        priority: 'high',
      });
      expect(updateResponse.ok()).toBeTruthy();
      const updatedTask = await updateResponse.json();
      expect(updatedTask.completed).toBe(true);
      expect(updatedTask.priority).toBe('high');
    });

    test('DELETE /api/tasks/:id - should delete task', async ({ request }) => {
      const tasksApi = new TasksApi(request);
      const createResponse = await tasksApi.createTask({ title: 'Task to delete' });
      const task = await createResponse.json();
      const deleteResponse = await tasksApi.deleteTask(task.id);
      expect(deleteResponse.status()).toBe(204);
      const getResponse = await tasksApi.getTask(task.id);
      expect(getResponse.status()).toBe(404);
    });
  });

  test.describe('Search API', () => {
    test('GET /api/search - should return matching tasks', async ({ request }) => {
      const tasksApi = new TasksApi(request);
      const uniqueTitle = `SearchAPI${Date.now()}`;
      await tasksApi.createTask({ title: uniqueTitle });
      const response = await tasksApi.search(uniqueTitle);
      expect(response.ok()).toBeTruthy();
      const results = await response.json();
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].title).toContain('SearchAPI');
    });

    test('GET /api/search - should return empty array for no query', async ({ request }) => {
      const tasksApi = new TasksApi(request);
      const response = await tasksApi.searchEmpty();
      expect(response.ok()).toBeTruthy();
      const results = await response.json();
      expect(results).toEqual([]);
    });
  });
});
