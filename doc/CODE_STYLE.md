# Code Style Guide | 代码风格指南

---

## 1. Overview | 概述

This document defines the coding standards and best practices for Mini-OpenClaw.

本文档定义了 Mini-OpenClaw 的编码标准和最佳实践。

---

## 2. General Principles | 一般原则

| Principle | Description |
|-----------|-------------|
| Readability | Code should be easy to read and understand |
| Simplicity | Prefer simple solutions over complex ones |
| Consistency | Follow existing patterns in the codebase |
| Documentation | Document non-obvious decisions |

---

## 3. Python (Backend) | Python（后端）

### 3.1 Style Guide | 风格指南

Follow **PEP 8** with the following additions:

- Maximum line length: 100 characters
- Use 4 spaces for indentation (not tabs)
- Use underscores for variable names (`session_id`, not `sessionId`)
- Use PascalCase for class names (`AgentManager`)
- Use SCREAMING_SNAKE_CASE for constants

### 3.2 Import Order | 导入顺序

```python
# 1. Standard library | 标准库
import os
import sys
from typing import List, Dict

# 2. Third-party packages | 第三方包
import fastapi
from langchain import Agent

# 3. Local application | 本地应用
from app.api import chat
from app.graph import AgentManager
```

### 3.3 Type Hints | 类型提示

Always use type hints for function signatures:

```python
# Good | 好
def process_message(message: str, session_id: str) -> dict:
    pass

def get_sessions() -> List[Session]:
    pass

# Bad | 不好
def process_message(message, session_id):
    pass
```

### 3.4 Docstrings | 文档字符串

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Short description of the function.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is invalid

    Example:
        >>> function_name("test", 5)
        True
    """
    pass
```

### 3.5 Error Handling | 错误处理

```python
# Good | 好
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise CustomError("Operation failed") from e

# Bad | 不好
try:
    result = risky_operation()
except:
    pass  # Never do this!
```

### 3.6 Logging | 日志记录

```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
```

---

## 4. JavaScript/TypeScript (Frontend) | JavaScript/TypeScript（前端）

### 4.1 Style Guide | 风格指南

- Use ESLint with the provided configuration
- Use Prettier for formatting
- Maximum line length: 100 characters
- Use 2 spaces for indentation
- Use camelCase for variable names (`sessionId`)
- Use PascalCase for component names (`ChatPanel`)

### 4.2 Import Order | 导入顺序

```typescript
// 1. React and related | React 相关
import { useState, useEffect } from 'react';
import React from 'react';

// 2. External libraries | 外部库
import axios from 'axios';
import { useQuery } from '@tanstack/react-query';

// 3. Components | 组件
import ChatPanel from '@/components/chat/ChatPanel';
import Sidebar from '@/components/layout/Sidebar';

// 4. Utils and hooks | 工具和钩子
import { useStore } from '@/lib/store';
import { formatDate } from '@/lib/utils';

// 5. Types | 类型
import { Message, Session } from '@/types';
```

### 4.3 TypeScript | TypeScript

Always define types, avoid `any`:

```typescript
// Good | 好
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: ToolCall[];
}

function sendMessage(message: Message): Promise<void> {
  // ...
}

// Bad | 不好
function sendMessage(message: any): Promise<void> {
  // ...
}
```

### 4.4 React Components | React 组件

```typescript
// Functional component with hooks | 使用钩子的函数组件
interface ChatPanelProps {
  sessionId: string;
  onMessage: (message: string) => void;
}

export function ChatPanel({ sessionId, onMessage }: ChatPanelProps) {
  const [input, setInput] = useState('');
  const { messages, isLoading } = useMessages(sessionId);

  const handleSubmit = () => {
    if (input.trim()) {
      onMessage(input);
      setInput('');
    }
  };

  return (
    <div className="chat-panel">
      <MessageList messages={messages} />
      <Input value={input} onChange={setInput} onSubmit={handleSubmit} />
    </div>
  );
}
```

### 4.5 CSS/Tailwind | CSS/Tailwind

- Use Tailwind CSS utility classes
- Keep custom CSS to a minimum
- Use consistent spacing (4px base unit)

```tsx
// Good | 好
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow">
  <span className="text-sm text-gray-600">Hello</span>
</div>

// Avoid | 避免
<div style={{ display: 'flex', padding: '16px', backgroundColor: 'white' }}>
```

---

## 5. Shell/Bash | Shell/Bash

- Use `#!/bin/bash` or `#!/bin/sh`
- Use `set -e` for error handling
- Use quotes around variables

```bash
#!/bin/bash
set -e

# Good | 好
SESSION_ID="${1}"
if [ -z "$SESSION_ID" ]; then
    echo "Usage: $0 <session_id>"
    exit 1
fi

# Bad | 不好
SESSION_ID=$1
if [ -z $SESSION_ID ]; then
    echo Usage: $0 session_id
fi
```

---

## 6. Git Workflow | Git 工作流

### 6.1 Branch Naming | 分支命名

| Type | Example |
|------|---------|
| Feature | `feature/add-session-compression` |
| Bug fix | `fix/path-traversal-vulnerability` |
| Documentation | `docs/add-api-reference` |

### 6.2 Commit Messages | 提交信息

Follow conventional commits:

```
feat(chat): add session compression endpoint
fix(tools): block dangerous terminal commands
docs(api): update endpoint documentation
refactor(agent): simplify prompt builder
test(sessions): add compression tests
```

---

## 7. File Organization | 文件组织

### 7.1 Backend | 后端

```
backend/
├── api/              # API route handlers
├── graph/             # Agent logic
├── tools/            # Tool implementations
├── skills/           # Skill definitions
├── tests/            # Test files
└── utils/            # Utility functions
```

### 7.2 Frontend | 前端

```
frontend/
├── src/
│   ├── app/           # Next.js App Router pages
│   ├── components/   # React components
│   ├── lib/          # Utilities and stores
│   ├── types/         # TypeScript types
│   └── hooks/         # Custom React hooks
```

---

## 8. Linting & Formatting | 代码检查与格式化

### 8.1 Python | Python

```bash
# Install tools | 安装工具
pip install black isort flake8 mypy

# Run formatters | 运行格式化
black .
isort .

# Run linter | 运行检查
flake8 .
mypy .
```

### 8.2 JavaScript/TypeScript | JavaScript/TypeScript

```bash
# Install tools | 安装工具
npm install -D eslint prettier

# Run formatters | 运行格式化
npx prettier --write .

# Run linter | 运行检查
npx eslint .
```

---

## 9. Code Review Checklist | 代码审查检查清单

- [ ] Code follows style guidelines
- [ ] Type hints/types are correct and complete
- [ ] Error handling is appropriate
- [ ] No security vulnerabilities
- [ ] Tests are included or updated
- [ ] Documentation is updated (if needed)
- [ ] No debug code or console.log left behind

---

## 10. Related Documents | 相关文档

- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing Guide
- [TEST_STRATEGY.md](TEST_STRATEGY.md) - Testing Strategy
- [ARCHITECTURE.md](ARCHITECTURE.md) - System Architecture
