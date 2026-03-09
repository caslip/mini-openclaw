# Testing Strategy | 测试策略

---

## 1. Overview | 概述

This document outlines the testing strategy for Mini-OpenClaw, including testing principles, test types, and implementation guidelines.

本文档概述了 Mini-OpenClaw 的测试策略，包括测试原则、测试类型和实施指南。

---

## 2. Testing Principles | 测试原则

| Principle | Description |
|-----------|-------------|
| Test Coverage | Aim for 80%+ code coverage |
| Fast Tests | Tests should run in seconds, not minutes |
| Isolated | Each test should be independent |
| Reproducible | Tests should produce consistent results |
| Self-documenting | Test names should describe what is being tested |

---

## 3. Test Types | 测试类型

### 3.1 Unit Tests | 单元测试

| Scope | Description |
|--------|-------------|
| Function | Test individual functions in isolation |
| Class | Test class methods and properties |
| Module | Test module-level functions |

### 3.2 Integration Tests | 集成测试

| Scope | Description |
|--------|-------------|
| API | Test API endpoints with HTTP requests |
| Tool | Test tool execution |
| Agent | Test agent behavior |

### 3.3 End-to-End Tests | 端到端测试

| Scope | Description |
|--------|-------------|
| Full Flow | Test complete user workflows |
| UI | Test frontend interactions |

---

## 4. Test Organization | 测试组织

### 4.1 Directory Structure | 目录结构

```
backend/
├── tests/
│   ├── unit/               # Unit tests
│   │   ├── test_tools.py
│   │   ├── test_agent.py
│   │   └── test_session.py
│   ├── integration/        # Integration tests
│   │   ├── test_api.py
│   │   └── test_tools_integration.py
│   ├── conftest.py        # Shared fixtures
│   └── pytest.ini         # Pytest configuration
frontend/
├── __tests__/             # Frontend tests
│   ├── components/
│   └── hooks/
```

### 4.2 Naming Conventions | 命名约定

| Type | Pattern |
|------|----------|
| Test files | `test_<module>.py` |
| Test functions | `test_<functionality>_<expected_result>` |
| Test classes | `Test<ClassName>` |
| Fixtures | `fixture_<name>` |

---

## 5. Backend Testing | 后端测试

### 5.1 Setup | 设置

```bash
# Install test dependencies | 安装测试依赖
pip install pytest pytest-cov pytest-asyncio httpx
```

### 5.2 Pytest Configuration | Pytest 配置

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --cov=. --cov-report=html
asyncio_mode = auto
```

### 5.3 Fixtures | 夹具

```python
# conftest.py
import pytest
import os
import tempfile

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def mock_session():
    """Create a mock session for testing."""
    return {
        "id": "test-session-123",
        "title": "Test Session",
        "messages": []
    }

@pytest.fixture
async def client():
    """Create a test client."""
    from httpx import AsyncClient
    from app import app
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

### 5.4 Example Tests | 示例测试

```python
# test_session_manager.py
import pytest
from app.graph.session_manager import SessionManager

def test_create_session(temp_dir):
    """Test session creation."""
    sm = SessionManager(temp_dir)
    session = sm.create_session("Test Session")
    assert session["title"] == "Test Session"
    assert "id" in session

def test_save_message(temp_dir):
    """Test message saving."""
    sm = SessionManager(temp_dir)
    session_id = sm.create_session("Test")["id"]
    sm.save_message(session_id, "user", "Hello")
    session = sm.load_session(session_id)
    assert len(session["messages"]) == 1
    assert session["messages"][0]["content"] == "Hello"

# test_tools.py
import pytest
from app.tools.terminal_tool import TerminalTool

def test_command_blacklist():
    """Test dangerous commands are blocked."""
    tool = TerminalTool()
    with pytest.raises(ValueError, match="Command not allowed"):
        tool.execute("rm -rf /")

def test_timeout():
    """Test command timeout."""
    tool = TerminalTool()
    with pytest.raises(TimeoutError):
        tool.execute("sleep 100", timeout=1)
```

### 5.5 Async Tests | 异步测试

```python
# test_agent.py
import pytest
from app.graph.agent_manager import AgentManager

@pytest.mark.asyncio
async def test_agent_response():
    """Test agent can generate response."""
    # Requires Ollama running | 需要运行 Ollama
    manager = AgentManager()
    await manager.initialize()
    response = await manager.astream("Hello", [], "test-session")
    assert response is not None
```

---

## 6. Frontend Testing | 前端测试

### 6.1 Setup | 设置

```bash
# Install test dependencies | 安装测试依赖
npm install -D @testing-library/react @testing-library/jest-dom jest
```

### 6.2 Jest Configuration | Jest 配置

```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testMatch: ['**/__tests__/**/*.test.{js,ts,jsx,tsx}'],
};
```

### 6.3 Component Tests | 组件测试

```typescript
// ChatInput.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInput } from '../ChatInput';

describe('ChatInput', () => {
  it('renders input field', () => {
    render(<ChatInput onSend={jest.fn()} />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('calls onSend when submit button clicked', () => {
    const mockSend = jest.fn();
    render(<ChatInput onSend={mockSend} />);
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'Hello' } });
    fireEvent.click(screen.getByText('Send'));
    expect(mockSend).toHaveBeenCalledWith('Hello');
  });
});
```

### 6.4 Hook Tests | 钩子测试

```typescript
// useMessages.test.ts
import { renderHook, act } from '@testing-library/react';
import { useMessages } from '../useMessages';

describe('useMessages', () => {
  it('loads messages on mount', async () => {
    const { result } = renderHook(() => useMessages('test-session'));
    expect(result.current.isLoading).toBe(true);
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 100));
    });
    expect(result.current.isLoading).toBe(false);
  });
});
```

---

## 7. CI/CD Integration | CI/CD 集成

### 7.1 GitHub Actions | GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          cd backend
          pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v4

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage
```

---

## 8. Test Coverage | 测试覆盖率

### 8.1 Coverage Goals | 覆盖率目标

| Type | Target |
|------|--------|
| Backend | 80%+ |
| Frontend | 70%+ |
| Critical paths | 90%+ |

### 8.2 Coverage Report | 覆盖率报告

```bash
# Generate HTML report | 生成 HTML 报告
pytest --cov=. --cov-report=html

# View in browser | 在浏览器中查看
open htmlcov/index.html
```

---

## 9. Performance Testing | 性能测试

### 9.1 Load Testing | 负载测试

```bash
# Using wrk | 使用 wrk
wrk -t4 -c100 -d30s http://localhost:8002/api/sessions

# Using locust | 使用 locust
locust -f locustfile.py --host=http://localhost:8002
```

### 9.2 Benchmarking | 基准测试

```python
# benchmark.py
import time
import pytest

def benchmark_agent_response():
    """Benchmark agent response time."""
    times = []
    for _ in range(10):
        start = time.time()
        # Run agent
        result = asyncio.run(agent.astream("Hello"))
        elapsed = time.time() - start
        times.append(elapsed)

    avg = sum(times) / len(times)
    assert avg < 5.0, f"Average response time {avg}s exceeds 5s"
```

---

## 10. Test Maintenance | 测试维护

### 10.1 When to Update Tests | 何时更新测试

- When adding new features
- When fixing bugs
- When refactoring code
- When changing APIs

### 10.2 Test Review Checklist | 测试审查检查清单

- [ ] Tests cover main functionality
- [ ] Tests are maintainable
- [ ] Tests run in reasonable time
- [ ] Tests are properly documented
- [ ] Edge cases are covered
- [ ] Error cases are tested

---

## 11. Related Documents | 相关文档

- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing Guide
- [CODE_STYLE.md](CODE_STYLE.md) - Code Style Guide
- [API.md](API.md) - API Documentation
