# Mini-OpenClaw

轻量级、全透明的本地 AI Agent 系统。拥有真实记忆、可插拔技能，所有状态以人类可读的文件形式存在，拒绝黑盒。

---

## 核心理念

| 理念 | 说明 |
|------|------|
| **文件即记忆** | 摒弃不透明的向量数据库，对话历史、长期记忆、技能定义全部以 Markdown/JSON 文件存储，可直接查看和编辑 |
| **技能即插件** | 遵循 Instruction-following 范式，将一个文件夹 + 一个 `SKILL.md` 视为一个技能，拖入即用 |
| **透明可控** | System Prompt 拼接、工具调用过程、记忆读写操作对开发者完全透明 |

---

## 技术栈

| 层级 | 技术 |
|------|------|
| Web 框架 | FastAPI + Uvicorn |
| Agent 引擎 | LangGraph `create_react_agent`（ReAct 循环） |
| LLM | Ollama `qwen3.5:9b`（通过 `langchain-ollama` 接入） |
| 工具层 | `langchain-core @tool` + `langchain-experimental PythonAstREPLTool` |
| 存储 | 本地文件系统（JSON + Markdown），无 MySQL / Redis |
| 测试 | pytest |

---

## 快速开始

### 环境要求

- Python 3.11+
- Ollama 服务（本地或远程，默认地址见 `backend/graph/agent.py`）

### 安装与启动

```bash
# 1. 克隆并进入项目
cd LocalAgent

# 2. 创建虚拟环境并激活
python -m venv .venv
# Windows
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

# 3. 安装依赖
cd backend
pip install -r requirements.txt

# 4. 启动后端
uvicorn app:app --host 0.0.0.0 --port 8002 --reload
```

### 验证服务

```bash
curl http://localhost:8002/health
# {"status":"ok"}
```

### 发送第一条消息

**第一步：创建会话，获取 session_id**

```bash
curl -X POST http://localhost:8002/api/sessions
# 返回：{"session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", ...}
```

**第二步：携带 session_id 发送消息**

```bash
curl -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好", "session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"}'
```

响应为 SSE 流，每行格式：`data: {"type":"token","content":"..."}`

> 同一个 `session_id` 可持续复用，后端会自动保存对话历史。

---

## 目录结构

```
LocalAgent/
├── .venv/                    # 虚拟环境（不提交）
└── backend/
    ├── app.py                # FastAPI 入口，lifespan 三步初始化
    ├── config.py             # RAG 模式等全局配置
    ├── requirements.txt      # Python 依赖
    ├── pytest.ini            # pytest 配置
    │
    ├── api/                  # 6 个路由模块（17 个端点）
    │   ├── chat.py           # POST /api/chat（SSE 流式对话）
    │   ├── sessions.py       # 会话 CRUD
    │   ├── files.py          # 文件读写（memory/workspace/skills）
    │   ├── tokens.py         # Token 数量统计
    │   ├── compress.py       # 历史消息压缩
    │   └── config_api.py     # RAG 模式开关
    │
    ├── graph/                # Agent 引擎
    │   ├── agent.py          # AgentManager：create_react_agent 封装 + SSE 事件流
    │   ├── prompt_builder.py # System Prompt 动态拼接（6 组件）
    │   ├── session_manager.py# 会话存储与加载（JSON v2）
    │   ├── memory_indexer.py # 长期记忆 MD5 索引
    │   └── memory_logger.py  # MEMORY.md 变更日志（memory/logs/YYYY-MM-DD.md）
    │
    ├── tools/                # 6 个核心工具
    │   ├── terminal_tool.py
    │   ├── python_repl_tool.py
    │   ├── fetch_url_tool.py
    │   ├── read_file_tool.py
    │   ├── search_knowledge_tool.py
    │   └── write_file_tool.py
    │
    ├── memory/               # 长期记忆
    │   ├── MEMORY.md         # 用户偏好与决策（Agent 可直接读写）
    │   └── logs/             # 每次 MEMORY.md 变更的 Markdown 日志
    │
    ├── workspace/            # System Prompt 组件文件
    │   ├── SOUL.md           # Agent 价值观
    │   ├── IDENTITY.md       # Agent 身份定义
    │   ├── USER.md           # 用户画像
    │   └── AGENTS.md         # 技能调用 & 记忆写入协议
    │
    ├── skills/               # 可插拔技能（每个子目录 = 一个技能）
    │   ├── get_weather/
    │   │   └── SKILL.md
    │   └── data_analysis/
    │       └── SKILL.md      # 数据分析技能（pandas + Excel/CSV）
    │
    ├── data/                 # 数据文件目录（Excel / CSV），将数据文件放在此处
    │
    ├── knowledge/            # 知识库（.md / .txt 文件，供 search_knowledge_base 检索）
    ├── sessions/             # 会话历史 JSON 文件
    ├── storage/              # 索引元数据
    ├── doc/                  # 技术文档
    │   ├── ARCHITECTURE.md
    │   └── AGENT_SELF_CORRECTION.md
    └── tests/                # pytest 测试套件
        ├── conftest.py
        ├── test_terminal.py
        ├── test_python_repl.py
        ├── test_read_file.py
        ├── test_write_file.py
        ├── test_fetch_url.py
        ├── test_search_knowledge.py
        └── test_memory_logger.py
```

---

## 核心工具

| 工具名 | 说明 |
|--------|------|
| `terminal` | 在项目沙箱中执行 Shell 命令，屏蔽危险指令（`rm -rf /`、`mkfs`、`shutdown`） |
| `python_repl_ast` | 基于 `PythonAstREPLTool`，AST 解析执行 Python，自动捕获 stdout，输入自动去除 backtick |
| `fetch_url` | 抓取 URL 内容（HTTP GET），返回最多 5000 字符的文本 |
| `read_file` | 读取项目目录内的文件，带路径穿越防护，最多返回 10000 字符 |
| `search_knowledge_base` | 在 `knowledge/` 目录中关键词搜索 .md / .txt 文件，最多返回 3 条匹配 |
| `write_file` | 写入文件（路径白名单：`memory/`、`workspace/`、`skills/`、`knowledge/`），写入 MEMORY.md 时自动记录变更日志 |
| `list_data_files` | 扫描 `data/` 目录，返回每个 Excel/CSV 文件的 Sheet 列表、列名和行数，供数据分析前感知数据结构 |

---

## API 端点速查

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查 |
| `POST` | `/api/chat` | 发送消息，SSE 流式返回（token / tool_start / tool_end / done） |
| `POST` | `/api/sessions` | 创建新会话，返回 `session_id` |
| `GET` | `/api/sessions` | 获取所有会话列表 |
| `GET` | `/api/sessions/{id}` | 获取指定会话消息 |
| `DELETE` | `/api/sessions/{id}` | 删除指定会话 |
| `POST` | `/api/sessions/{id}/compress` | 压缩会话历史 |
| `GET` | `/api/files` | 读取文件内容 |
| `POST` | `/api/files` | 写入文件内容 |
| `GET` | `/api/tokens/session/{id}` | 统计会话 token 数 |
| `POST` | `/api/tokens/files` | 统计多个文件 token 数 |
| `GET` | `/api/config/rag` | 获取 RAG 模式状态 |
| `POST` | `/api/config/rag` | 切换 RAG 模式开关 |

---

## 测试

```bash
cd backend

# 运行全部测试（含网络请求）
pytest tests/ -v

# 仅运行本地测试（跳过需要外网的 fetch_url 测试）
pytest tests/ -v -m "not network"
```

测试覆盖 6 个工具 + memory_logger，共 32 个用例，全部使用 `tmp_path` 临时目录隔离，不污染项目文件。

---

## 文档

- [系统架构文档](backend/doc/ARCHITECTURE.md) — 技术选型、模块详解、数据流、API 速查表、关键设计决策
- [Agent 自我纠错机制](backend/doc/AGENT_SELF_CORRECTION.md) — ReAct 循环、工具错误处理、重试、Plan B 回退、Human-in-the-Loop 五层纠错机制精讲
