const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend/dist')));

// In-memory data store
let tasks = [
  { id: 1, title: 'Learn Playwright', completed: false, priority: 'high' },
  { id: 2, title: 'Compare with Katalon', completed: false, priority: 'medium' },
  { id: 3, title: 'Write test cases', completed: true, priority: 'high' }
];

let users = [
  { id: 1, email: 'admin@test.com', password: 'admin123', name: 'Admin User' },
  { id: 2, email: 'user@test.com', password: 'user123', name: 'Test User' }
];

// Auth endpoints
app.post('/api/login', (req, res) => {
  const { email, password } = req.body;
  
  if (!email || !password) {
    return res.status(400).json({ error: 'Email and password are required' });
  }
  
  const user = users.find(u => u.email === email && u.password === password);
  
  if (user) {
    res.json({ 
      success: true, 
      user: { id: user.id, email: user.email, name: user.name },
      token: 'mock-jwt-token-' + user.id
    });
  } else {
    res.status(401).json({ error: 'Invalid credentials' });
  }
});

app.post('/api/register', (req, res) => {
  const { email, password, name } = req.body;
  
  if (!email || !password || !name) {
    return res.status(400).json({ error: 'All fields are required' });
  }
  
  if (users.find(u => u.email === email)) {
    return res.status(409).json({ error: 'User already exists' });
  }
  
  const newUser = {
    id: users.length + 1,
    email,
    password,
    name
  };
  
  users.push(newUser);
  res.status(201).json({ 
    success: true, 
    user: { id: newUser.id, email: newUser.email, name: newUser.name }
  });
});

// Task endpoints
app.get('/api/tasks', (req, res) => {
  res.json(tasks);
});

app.get('/api/tasks/:id', (req, res) => {
  const task = tasks.find(t => t.id === parseInt(req.params.id));
  if (task) {
    res.json(task);
  } else {
    res.status(404).json({ error: 'Task not found' });
  }
});

app.post('/api/tasks', (req, res) => {
  const { title, priority = 'medium' } = req.body;
  
  if (!title) {
    return res.status(400).json({ error: 'Title is required' });
  }
  
  const newTask = {
    id: Math.max(...tasks.map(t => t.id), 0) + 1,
    title,
    completed: false,
    priority
  };
  
  tasks.push(newTask);
  res.status(201).json(newTask);
});

app.put('/api/tasks/:id', (req, res) => {
  const taskIndex = tasks.findIndex(t => t.id === parseInt(req.params.id));
  
  if (taskIndex === -1) {
    return res.status(404).json({ error: 'Task not found' });
  }
  
  tasks[taskIndex] = { ...tasks[taskIndex], ...req.body };
  res.json(tasks[taskIndex]);
});

app.delete('/api/tasks/:id', (req, res) => {
  const taskIndex = tasks.findIndex(t => t.id === parseInt(req.params.id));
  
  if (taskIndex === -1) {
    return res.status(404).json({ error: 'Task not found' });
  }
  
  tasks.splice(taskIndex, 1);
  res.status(204).send();
});

// Search endpoint
app.get('/api/search', (req, res) => {
  const { q } = req.query;
  
  if (!q) {
    return res.json([]);
  }
  
  const results = tasks.filter(t => 
    t.title.toLowerCase().includes(q.toLowerCase())
  );
  
  res.json(results);
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Serve frontend for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/dist/index.html'));
});

app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});

module.exports = app;
