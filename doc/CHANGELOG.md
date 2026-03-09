# Changelog | 变更日志

---

## 1. Overview | 概述

All notable changes to this project will be documented in this file.

本项目的所有重要变更都将记录在此文件中。

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)。

---

## 2. Versioning | 版本管理

We use [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

我们使用 [语义化版本控制](http://semver.org/spec/v2.0.0.html)。

Given a version number `MAJOR.MINOR.PATCH`:

- `MAJOR` version: incompatible API changes
- `MINOR` version: new functionality (backward compatible)
- `PATCH` version: bug fixes (backward compatible)

---

## 3. Changelog Categories | 变更日志类别

| Category | Description |
|----------|-------------|
| `Added` | New features |
| `Changed` | Changes in existing functionality |
| `Deprecated` | Soon-to-be removed features |
| `Removed` | Removed features |
| `Fixed` | Bug fixes |
| `Security` | Security-related changes |

---

## 4. [Unreleased] | [未发布]

### Added | 新增

- TBD

### Changed | 变更

- TBD

### Fixed | 修复

- TBD

---

## 5. [1.0.0] - 2026-03-09

### Added | 新增

#### Backend | 后端

- **API Layer | API 层**
  - Chat endpoint with SSE streaming support (`POST /api/chat`)
  - Session management (CRUD operations)
  - File operations (read/write with path validation)
  - Token counting API
  - Session compression API
  - RAG mode configuration API

- **Agent Engine | Agent 引擎**
  - `AgentManager`: Agent lifecycle management
  - `SessionManager`: Session persistence (JSON files)
  - `PromptBuilder`: System prompt assembly
  - `MemoryIndexer`: Vector index for MEMORY.md (RAG)

- **Core Tools | 核心工具**
  - `terminal`: Sandboxed shell command execution
  - `python_repl_ast`: Python code execution (AST-based)
  - `fetch_url`: Web content fetching
  - `read_file`: Sandboxed file reading
  - `search_knowledge_base`: Knowledge base search
  - `write_file`: Whitelist-based file writing
  - `list_data_files_tool`: Data file discovery

- **Skills System | 技能系统**
  - Skills scanner (auto-discovery)
  - SKILLS_SNAPSHOT.md generation
  - Instruction-following skill paradigm

- **Memory System | 记忆系统**
  - Dual-layer memory (session + long-term)
  - File-based storage (JSON + Markdown)
  - Conversation compression
  - Memory change logging

#### Frontend | 前端

- **UI Components | UI 组件**
  - Three-panel IDE-style layout
  - ChatPanel with message bubbles
  - ThoughtChain visualization
  - RetrievalCard for RAG results
  - Sidebar with session list
  - InspectorPanel with Monaco Editor
  - Resizeable panels

- **State Management | 状态管理**
  - React Context-based store
  - Real-time SSE event handling
  - Session management

---

### Changed | 变更

#### Architecture | 架构

- File-first memory approach (no vector DB)
- Skills as Markdown instructions
- Transparent System Prompt assembly

#### Technology Stack | 技术栈

- Backend: FastAPI + Uvicorn + LangGraph
- Frontend: Next.js 14 + React + Tailwind CSS + Shadcn/UI
- LLM: Ollama (qwen3.5:9b)
- Embedding: OpenAI text-embedding-3-small
- Storage: Local JSON/Markdown files

---

### Fixed | 修复

- Initial release - no previous version to compare

---

## 6. [0.0.1] - 2026-01-01

### Added | 新增

- Project initialization
- Basic project structure

---

## 7. Upcoming Features | 计划中的功能

### Planned | 计划中

| Feature | Description | Target Version |
|---------|-------------|----------------|
| Authentication | User authentication system | v1.1.0 |
| WebSocket Support | Real-time bidirectional communication | v1.1.0 |
| Plugin System | Dynamic plugin loading | v1.2.0 |
| Multi-language UI | i18n support | v1.2.0 |
| Mobile Support | Responsive design improvements | v1.3.0 |
| Performance Optimization | Caching, connection pooling | v1.3.0 |

---

## 8. Deprecations | 废弃

### Deprecated | 废弃中

None currently.

---

## 9. Security | 安全

### Security | 安全

| Version | Description |
|---------|-------------|
| 1.0.0 | Initial security measures: path traversal protection, command blacklist, file permission guidance |

---

## 10. Upgrade Guide | 升级指南

### Upgrading from v0.x to v1.0 | 从 v0.x 升级到 v1.0

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. Start services:
   ```bash
   # Backend
   uvicorn app:app --port 8002

   # Frontend
   npm run dev
   ```

---

## 11. Contributing | 贡献

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

## 12. Related Documents | 相关文档

- [ARCHITECTURE.md](ARCHITECTURE.md) - System Architecture
- [API.md](API.md) - API Documentation
- [DEPLOY.md](DEPLOY.md) - Deployment Guide
