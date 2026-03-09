# Contributing Guide | 贡献指南

---

## 1. Welcome | 欢迎

Thank you for your interest in contributing to Mini-OpenClaw. This document outlines the process for contributing to the project.

感谢您对贡献 Mini-OpenClaw 感兴趣。本文档概述了向项目贡献的流程。

---

## 2. Code of Conduct | 行为准则

### 2.1 Our Pledge | 我们的承诺

We are committed to providing a welcoming and inclusive experience for everyone.

我们承诺为每个人提供热情和包容的体验。

### 2.2 Standards | 标准

- Be respectful and inclusive
- Use welcoming and inclusive language
- Be graceful when accepting constructive criticism
- Focus on what is best for the community

### 2.3 Unacceptable Behavior | 不可接受的行为

- Harassment of any kind
- Offensive comments related to personal characteristics
- Deliberate intimidation or bullying
- Publishing others' private information

---

## 3. How to Contribute | 如何贡献

### 3.1 Ways to Contribute | 贡献方式

| Type | Description |
|------|-------------|
| Bug Reports | Report bugs you find |
| Feature Requests | Suggest new features |
| Code Contributions | Submit pull requests |
| Documentation | Improve docs |
| Testing | Write or improve tests |

### 3.2 Contribution Workflow | 贡献流程

```
1. Fork the repository | Fork 仓库
       │
       ▼
2. Clone your fork | 克隆你的 fork
       │
       ▼
3. Create a branch | 创建分支
       │
       ▼
4. Make changes | 做出更改
       │
       ▼
5. Test your changes | 测试更改
       │
       ▼
6. Commit with clear messages | 提交并附带清晰信息
       │
       ▼
7. Push to your fork | 推送到你的 fork
       │
       ▼
8. Submit Pull Request | 提交 Pull Request
```

---

## 4. Development Setup | 开发环境设置

### 4.1 Prerequisites | 前置条件

- Python 3.11+
- Node.js 18+
- Git

### 4.2 Local Development | 本地开发

```bash
# Fork and clone | Fork 并克隆
git clone https://github.com/YOUR_USERNAME/mini-openclaw.git
cd mini-openclaw

# Create virtual environment | 创建虚拟环境
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies | 安装依赖
pip install -r requirements.txt

# Setup frontend | 设置前端
cd ../frontend
npm install

# Run development servers | 运行开发服务器
# Terminal 1: Backend | 终端 1：后端
cd backend
uvicorn app:app --reload --port 8002

# Terminal 2: Frontend | 终端 2：前端
cd frontend
npm run dev
```

---

## 5. Coding Standards | 编码标准

### 5.1 Python (Backend) | Python（后端）

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions small and focused

### 5.2 JavaScript/TypeScript (Frontend) | JavaScript/TypeScript（前端）

- Follow ESLint configuration
- Use Prettier for formatting
- Prefer functional components in React
- Use TypeScript for new code

### 5.3 Git Commit Messages | Git 提交信息

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types | 类型**:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

**Example | 示例**:

```
feat(chat): add session compression endpoint

Add POST /api/sessions/{id}/compress to allow users to
compress their conversation history and reduce storage.

Closes #123
```

---

## 6. Pull Request Process | Pull Request 流程

### 6.1 Before Submitting | 提交前

1. **Run tests locally** - Ensure all tests pass
2. **Update documentation** - If needed
3. **Check code formatting** - Lint and format
4. **Write descriptive commit messages**

### 6.2 PR Checklist | PR 检查清单

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated (if needed)
- [ ] Commit messages are clear
- [ ] PR description explains the changes

### 6.3 PR Template | PR 模板

```markdown
## Description
<!-- Describe your changes -->

## Type of Change
<!-- Check one -->
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
<!-- Describe testing done -->

## Screenshots (if applicable)
```

---

## 7. Testing | 测试

### 7.1 Running Tests | 运行测试

```bash
# Backend tests | 后端测试
cd backend
pytest

# Specific test file | 特定测试文件
pytest tests/test_chat.py

# With coverage | 带覆盖率
pytest --cov=. --cov-report=html
```

### 7.2 Writing Tests | 编写测试

```python
import pytest
from app.api import chat

def test_chat_endpoint():
    response = client.post("/api/chat", json={
        "message": "Hello",
        "session_id": "test-session"
    })
    assert response.status_code == 200
```

---

## 8. Documentation | 文档

### 8.1 Code Documentation | 代码文档

```python
def process_message(message: str, session_id: str) -> dict:
    """Process a user message and return response.
    
    Args:
        message: The user's message content
        session_id: The session identifier
        
    Returns:
        Dictionary containing the response and metadata
    """
    pass
```

### 8.2 API Documentation | API 文档

Use docstrings and type hints for API endpoints:

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    session_id: str
    stream: bool = True
```

---

## 9. Recognition | 认可

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- GitHub profile

---

## 10. Questions | 问题

- Open an issue for bugs or feature requests
- Use discussions for questions
- Join our community chat (if available)

---

## 11. Related Documents | 相关文档

- [CODE_STYLE.md](CODE_STYLE.md) - Code Style Guide
- [TEST_STRATEGY.md](TEST_STRATEGY.md) - Testing Strategy
- [ARCHITECTURE.md](ARCHITECTURE.md) - System Architecture
