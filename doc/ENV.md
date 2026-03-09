# Environment Variables | 环境变量配置

---

## 1. Overview | 概述

This document describes all environment variables used in Mini-OpenClaw.

本文档描述 Mini-OpenClaw 使用的所有环境变量。

---

## 2. Backend Variables | 后端变量

### 2.1 Required | 必需

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OLLAMA_BASE_URL` | string | - | Ollama API endpoint (e.g., `http://localhost:11434`) |
| `OLLAMA_MODEL` | string | - | Primary LLM model name (e.g., `qwen3.5:9b`) |

### 2.2 Optional - LLM Configuration | 可选 - LLM 配置

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OPENAI_API_KEY` | string | - | OpenAI API key for embedding models |
| `OPENAI_BASE_URL` | string | `https://api.openai.com/v1` | OpenAI-compatible API endpoint |
| `EMBEDDING_MODEL` | string | `text-embedding-3-small` | Embedding model for RAG |
| `TEMPERATURE` | float | `0.7` | LLM generation temperature |
| `MAX_TOKENS` | int | `4096` | Maximum tokens to generate |

### 2.3 Optional - Server Configuration | 可选 - 服务器配置

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HOST` | string | `0.0.0.0` | Server bind address |
| `PORT` | int | `8002` | Server port |
| `WORKERS` | int | `1` | Number of worker processes |
| `LOG_LEVEL` | string | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `RELOAD` | boolean | `false` | Enable auto-reload for development |

### 2.4 Optional - Storage Configuration | 可选 - 存储配置

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `BASE_DIR` | string | `backend` | Base directory for data storage |
| `SESSION_DIR` | string | `sessions` | Directory for session files |
| `MEMORY_DIR` | string | `memory` | Directory for long-term memory |
| `WORKSPACE_DIR` | string | `workspace` | Directory for workspace files |
| `SKILLS_DIR` | string | `skills` | Directory for skills |
| `KNOWLEDGE_DIR` | string | `knowledge` | Directory for knowledge base |
| `STORAGE_DIR` | string | `storage` | Directory for vector index storage |

### 2.5 Optional - Security | 可选 - 安全

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `API_KEY` | string | - | API key for authentication |
| `CORS_ORIGINS` | string | `*` | Allowed CORS origins (comma-separated) |

---

## 3. Frontend Variables | 前端变量

### 3.1 Required | 必需

None required for development.

### 3.2 Optional | 可选

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `NEXT_PUBLIC_API_BASE_URL` | string | `http://localhost:8002` | Backend API base URL |
| `NEXT_PUBLIC_APP_NAME` | string | `Mini-OpenClaw` | Application name |
| `NEXT_PUBLIC_DEBUG` | boolean | `false` | Enable debug mode |

---

## 4. Environment File Template | 环境文件模板

### 4.1 Backend | 后端

Create `.env` file in `backend/` directory:

```bash
# Ollama (Agent Main Model) | Ollama（Agent 主模型）
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:9b

# OpenAI (Embedding Model for RAG) | OpenAI（用于 RAG 检索的 Embedding 模型）
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small

# Server Configuration | 服务器配置
HOST=0.0.0.0
PORT=8002
LOG_LEVEL=INFO

# Directories | 目录配置
BASE_DIR=backend
```

### 4.2 Frontend | 前端

Create `.env.local` file in `frontend/` directory:

```bash
# API Configuration | API 配置
NEXT_PUBLIC_API_BASE_URL=http://localhost:8002
NEXT_PUBLIC_APP_NAME=Mini-OpenClaw
NEXT_PUBLIC_DEBUG=false
```

---

## 5. Development vs Production | 开发 vs 生产

### 5.1 Development | 开发

```bash
# Backend .env | 后端 .env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:9b
OPENAI_API_KEY=sk-dev-key
LOG_LEVEL=DEBUG
RELOAD=true
```

```bash
# Frontend .env.local | 前端 .env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8002
NEXT_PUBLIC_DEBUG=true
```

### 5.2 Production | 生产

```bash
# Backend .env | 后端 .env
OLLAMA_BASE_URL=http://ollama.internal:11434
OLLAMA_MODEL=qwen3.5:9b
OPENAI_API_KEY=sk-prod-key
OPENAI_BASE_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small
HOST=0.0.0.0
PORT=8002
WORKERS=4
LOG_LEVEL=INFO
API_KEY=your-secure-api-key
CORS_ORIGINS=https://your-domain.com
```

```bash
# Frontend .env.local | 前端 .env.local
NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.com
NEXT_PUBLIC_DEBUG=false
```

---

## 6. Ollama Configuration | Ollama 配置

### 6.1 Local Ollama | 本地 Ollama

```bash
# Start Ollama | 启动 Ollama
ollama serve

# Pull model | 下载模型
ollama pull qwen3.5:9b

# Check running models | 查看运行中的模型
ollama list
```

### 6.2 Remote Ollama | 远程 Ollama

```bash
# Environment variable for remote Ollama | 远程 Ollama 环境变量
OLLAMA_BASE_URL=http://remote-server:11434

# Or with authentication | 或带认证
OLLAMA_BASE_URL=http://user:password@remote-server:11434
```

---

## 7. OpenAI Compatible API | OpenAI 兼容 API

### 7.1 OpenAI Official | OpenAI 官方

```bash
OPENAI_API_KEY=sk-xxxx
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 7.2 Third-party Proxies | 第三方代理

```bash
# Example: OpenAI compatible proxy | 示例：OpenAI 兼容代理
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.example.com/v1
```

### 7.3 Local Models | 本地模型

```bash
# Example: Local LM Studio | 示例：本地 LM Studio
OPENAI_API_KEY=not-needed
OPENAI_BASE_URL=http://localhost:1234/v1
```

---

## 8. Troubleshooting | 故障排除

### 8.1 Common Issues | 常见问题

| Error | Cause | Solution |
|-------|-------|----------|
| `Connection refused` | Ollama not running | Start Ollama: `ollama serve` |
| `Model not found` | Wrong model name | Check model name with `ollama list` |
| `Invalid API key` | Wrong OpenAI key | Verify API key in OpenAI dashboard |
| `CORS error` | Wrong CORS origin | Set `CORS_ORIGINS` to your domain |

### 8.2 Testing Connection | 测试连接

```bash
# Test Ollama | 测试 Ollama
curl http://localhost:11434/api/tags

# Test OpenAI | 测试 OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

## 9. Security Best Practices | 安全最佳实践

### 9.1 Never Commit Secrets | 切勿提交 secrets

- Add `.env` to `.gitignore`
- Use `.env.example` for template
- Use secrets management in production (e.g., HashiCorp Vault)

### 9.2 Environment-specific Secrets | 环境特定的 secrets

```bash
# Development | 开发
# .env - never commit

# Production | 生产
# Use environment variables or secrets manager
```

---

## 10. Related Documents | 相关文档

- [DEPLOY.md](DEPLOY.md) - Deployment Guide
- [SECURITY.md](SECURITY.md) - Security Configuration
- [API.md](API.md) - API Documentation
