# Prompt Engineering for Test Generation

All prompts used for generating test cases, exactly as written.

---

## Module 1: Authentication (Login/Register/Logout)

### Prompt 1 (Initial)
```
Write Playwright tests for a login page
```

**Result:** Too generic - didn't know our selectors or page structure.

---

### Prompt 2
```
Write Playwright tests for login and registration. 
Use test IDs like login-email, login-password, login-submit.
Test credentials: admin@test.com / admin123
```

---


### What Changed
First prompt was vague. Adding specific test IDs and credentials fixed selector issues. Including the page object path ensured proper imports.

---

## Module 2: Task Management (CRUD)

### Prompt 1 (Initial)
```
Write playwright tests for task CRUD operations
```

**Result:** Generic tests, wrong method names, no login setup.

---

### Prompt 2
```
Generate Playwright tests for task management dashboard.
Tasks have title, priority (high/medium/low), completion status.
Include add, toggle complete, and delete tests.
```


---
```

---

