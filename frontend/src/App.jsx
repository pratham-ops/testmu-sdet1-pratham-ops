import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [user, setUser] = useState(null)
  const [view, setView] = useState('login')
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(false)
  const [notification, setNotification] = useState(null)

  // Login form state
  const [loginEmail, setLoginEmail] = useState('')
  const [loginPassword, setLoginPassword] = useState('')

  // Register form state
  const [regName, setRegName] = useState('')
  const [regEmail, setRegEmail] = useState('')
  const [regPassword, setRegPassword] = useState('')

  // Task form state
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [newTaskPriority, setNewTaskPriority] = useState('medium')
  const [searchQuery, setSearchQuery] = useState('')
  const [filterPriority, setFilterPriority] = useState('all')

  const showNotification = (message, type = 'success') => {
    setNotification({ message, type })
    setTimeout(() => setNotification(null), 3000)
  }

  const fetchTasks = async () => {
    try {
      const res = await fetch('/api/tasks')
      const data = await res.json()
      setTasks(data)
    } catch (error) {
      showNotification('Failed to fetch tasks', 'error')
    }
  }

  useEffect(() => {
    if (user) {
      fetchTasks()
    }
  }, [user])

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: loginEmail, password: loginPassword })
      })
      
      const data = await res.json()
      
      if (res.ok) {
        setUser(data.user)
        setView('dashboard')
        showNotification(`Welcome back, ${data.user.name}!`)
      } else {
        showNotification(data.error, 'error')
      }
    } catch (error) {
      showNotification('Login failed', 'error')
    }
    
    setLoading(false)
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: regName, email: regEmail, password: regPassword })
      })
      
      const data = await res.json()
      
      if (res.ok) {
        showNotification('Account created! Please login.')
        setView('login')
        setRegName('')
        setRegEmail('')
        setRegPassword('')
      } else {
        showNotification(data.error, 'error')
      }
    } catch (error) {
      showNotification('Registration failed', 'error')
    }
    
    setLoading(false)
  }

  const handleAddTask = async (e) => {
    e.preventDefault()
    if (!newTaskTitle.trim()) return
    
    try {
      const res = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTaskTitle, priority: newTaskPriority })
      })
      
      if (res.ok) {
        const task = await res.json()
        setTasks([...tasks, task])
        setNewTaskTitle('')
        showNotification('Task added!')
      }
    } catch (error) {
      showNotification('Failed to add task', 'error')
    }
  }

  const toggleTaskComplete = async (taskId) => {
    const task = tasks.find(t => t.id === taskId)
    
    try {
      const res = await fetch(`/api/tasks/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed: !task.completed })
      })
      
      if (res.ok) {
        setTasks(tasks.map(t => 
          t.id === taskId ? { ...t, completed: !t.completed } : t
        ))
      }
    } catch (error) {
      showNotification('Failed to update task', 'error')
    }
  }

  const deleteTask = async (taskId) => {
    try {
      const res = await fetch(`/api/tasks/${taskId}`, {
        method: 'DELETE'
      })
      
      if (res.ok) {
        setTasks(tasks.filter(t => t.id !== taskId))
        showNotification('Task deleted!')
      }
    } catch (error) {
      showNotification('Failed to delete task', 'error')
    }
  }

  const handleLogout = () => {
    setUser(null)
    setView('login')
    setTasks([])
    showNotification('Logged out successfully')
  }

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesPriority = filterPriority === 'all' || task.priority === filterPriority
    return matchesSearch && matchesPriority
  })

  const taskStats = {
    total: tasks.length,
    completed: tasks.filter(t => t.completed).length,
    pending: tasks.filter(t => !t.completed).length,
    highPriority: tasks.filter(t => t.priority === 'high' && !t.completed).length
  }

  return (
    <div className="app">
      {notification && (
        <div className={`notification ${notification.type}`} data-testid="notification">
          {notification.message}
        </div>
      )}

      {!user ? (
        <div className="auth-container">
          <div className="auth-card">
            <div className="auth-header">
              <div className="logo">
                <span className="logo-icon">⚡</span>
                <span className="logo-text">TaskFlow</span>
              </div>
             
            </div>

            <div className="auth-tabs">
              <button 
                className={`auth-tab ${view === 'login' ? 'active' : ''}`}
                onClick={() => setView('login')}
                data-testid="login-tab"
              >
                Login
              </button>
              <button 
                className={`auth-tab ${view === 'register' ? 'active' : ''}`}
                onClick={() => setView('register')}
                data-testid="register-tab"
              >
                Register
              </button>
            </div>

            {view === 'login' && (
              <form onSubmit={handleLogin} className="auth-form" data-testid="login-form">
                <div className="form-group">
                  <label htmlFor="login-email">Email</label>
                  <input
                    id="login-email"
                    type="email"
                    placeholder="you@example.com"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    data-testid="login-email"
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="login-password">Password</label>
                  <input
                    id="login-password"
                    type="password"
                    placeholder="••••••••"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    data-testid="login-password"
                    required
                  />
                </div>
                <button type="submit" className="btn-primary" disabled={loading} data-testid="login-submit">
                  {loading ? 'Signing in...' : 'Sign In'}
                </button>
                <p className="auth-hint">
                  Demo: admin@test.com / admin123
                </p>
              </form>
            )}

            {view === 'register' && (
              <form onSubmit={handleRegister} className="auth-form" data-testid="register-form">
                <div className="form-group">
                  <label htmlFor="reg-name">Full Name</label>
                  <input
                    id="reg-name"
                    type="text"
                    placeholder="John Doe"
                    value={regName}
                    onChange={(e) => setRegName(e.target.value)}
                    data-testid="register-name"
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="reg-email">Email</label>
                  <input
                    id="reg-email"
                    type="email"
                    placeholder="you@example.com"
                    value={regEmail}
                    onChange={(e) => setRegEmail(e.target.value)}
                    data-testid="register-email"
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="reg-password">Password</label>
                  <input
                    id="reg-password"
                    type="password"
                    placeholder="••••••••"
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    data-testid="register-password"
                    required
                  />
                </div>
                <button type="submit" className="btn-primary" disabled={loading} data-testid="register-submit">
                  {loading ? 'Creating...' : 'Create Account'}
                </button>
              </form>
            )}
          </div>
        </div>
      ) : (
        <div className="dashboard">
          <header className="dashboard-header">
            <div className="header-left">
              <div className="logo">
                <span className="logo-icon">⚡</span>
                <span className="logo-text">TaskFlow</span>
              </div>
            </div>
            <div className="header-right">
              <span className="user-name" data-testid="user-name">{user.name}</span>
              <button className="btn-logout" onClick={handleLogout} data-testid="logout-btn">
                Logout
              </button>
            </div>
          </header>

          <main className="dashboard-main">
            <div className="stats-grid">
              <div className="stat-card" data-testid="stat-total">
                <span className="stat-value">{taskStats.total}</span>
                <span className="stat-label">Total Tasks</span>
              </div>
              <div className="stat-card completed" data-testid="stat-completed">
                <span className="stat-value">{taskStats.completed}</span>
                <span className="stat-label">Completed</span>
              </div>
              <div className="stat-card pending" data-testid="stat-pending">
                <span className="stat-value">{taskStats.pending}</span>
                <span className="stat-label">Pending</span>
              </div>
              <div className="stat-card urgent" data-testid="stat-urgent">
                <span className="stat-value">{taskStats.highPriority}</span>
                <span className="stat-label">High Priority</span>
              </div>
            </div>

            <div className="tasks-section">
              <div className="tasks-header">
                <h2>Your Tasks</h2>
                <div className="tasks-controls">
                  <input
                    type="text"
                    placeholder="Search tasks..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="search-input"
                    data-testid="search-input"
                  />
                  <select
                    value={filterPriority}
                    onChange={(e) => setFilterPriority(e.target.value)}
                    className="filter-select"
                    data-testid="priority-filter"
                  >
                    <option value="all">All Priorities</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>
                </div>
              </div>

              <form onSubmit={handleAddTask} className="add-task-form" data-testid="add-task-form">
                <input
                  type="text"
                  placeholder="Add a new task..."
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  className="task-input"
                  data-testid="new-task-input"
                />
                <select
                  value={newTaskPriority}
                  onChange={(e) => setNewTaskPriority(e.target.value)}
                  className="priority-select"
                  data-testid="new-task-priority"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
                <button type="submit" className="btn-add" data-testid="add-task-btn">
                  Add Task
                </button>
              </form>

              <div className="tasks-list" data-testid="tasks-list">
                {filteredTasks.length === 0 ? (
                  <div className="empty-state" data-testid="empty-state">
                    <span>No tasks found</span>
                  </div>
                ) : (
                  filteredTasks.map(task => (
                    <div 
                      key={task.id} 
                      className={`task-item ${task.completed ? 'completed' : ''}`}
                      data-testid={`task-${task.id}`}
                    >
                      <button
                        className={`task-checkbox ${task.completed ? 'checked' : ''}`}
                        onClick={() => toggleTaskComplete(task.id)}
                        data-testid={`task-toggle-${task.id}`}
                        aria-label={task.completed ? 'Mark incomplete' : 'Mark complete'}
                      >
                        {task.completed && '✓'}
                      </button>
                      <span className="task-title">{task.title}</span>
                      <span className={`task-priority priority-${task.priority}`}>
                        {task.priority}
                      </span>
                      <button
                        className="task-delete"
                        onClick={() => deleteTask(task.id)}
                        data-testid={`task-delete-${task.id}`}
                        aria-label="Delete task"
                      >
                        ×
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </main>
        </div>
      )}
    </div>
  )
}

export default App
