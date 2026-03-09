# API Reference | API 接口文档

---

## 1. Overview | 概述

This document describes all REST API endpoints for the Mini-OpenClaw system. All APIs are prefixed with `/api`.

本文档描述 Mini-OpenClaw 系统的所有 REST API 接口。所有接口均以 `/api` 为前缀。

**Base URL**: `http://localhost:8002`

**WebSocket/Server-Sent Events**: Streaming chat uses SSE (Server-Sent Events).

---

## 2. Authentication | 认证

Currently, the system does not implement authentication. All endpoints are publicly accessible.

当前系统未实现认证机制，所有接口均可公开访问。

> **Security Note | 安全说明**: In production, implement authentication (JWT, OAuth2, etc.) before exposing to the public internet.
> 在生产环境中，部署到公网前请实现认证机制（JWT、OAuth2 等）。

---

## 3. Common Headers | 通用请求头

| Header | Type | Description |
|--------|------|-------------|
| `Content-Type` | string | `application/json` |

---

## 4. Error Response Format | 错误响应格式

All error responses follow this structure:

所有错误响应均遵循以下格式：

```json
{
  "error": "Error message | 错误信息",
  "code": "ERROR_CODE",
  "details": {}
}
```

### Error Codes | 错误码

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Invalid request parameters |
| `NOT_FOUND` | 404 | Resource not found |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `TOOL_EXECUTION_ERROR` | 500 | Tool execution failed |
| `SESSION_NOT_FOUND` | 404 | Session does not exist |

---

## 5. Endpoints | 接口列表

### 5.1 Chat | 聊天

#### POST /api/chat

Send a message and receive streaming response.

发送消息并接收流式响应。

**Request Body | 请求体**:

```json
{
  "message": "Hello, how are you? | 你好",
  "session_id": "abc123",
  "stream": true
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | User message content |
| `session_id` | string | Yes | Session ID |
| `stream` | boolean | No | Enable streaming (default: true) |

**Response (SSE) | 响应 (SSE)**:

```
event: token
data: {"content": "Hello"}

event: tool_start
data: {"tool": "terminal", "args": {"command": "ls"}}

event: tool_end
data: {"tool": "terminal", "output": "..."}

event: done
data: {"content": "Final response", "session_id": "abc123"}
```

**Event Types | 事件类型**:

| Event | Description |
|-------|-------------|
| `retrieval` | RAG retrieval results (when RAG mode is enabled) |
| `token` | LLM output token |
| `tool_start` | Tool execution starts |
| `tool_end` | Tool execution ends |
| `done` | Response completed |
| `error` | Error occurred |
| `title` | Generated session title (for first message) |

---

### 5.2 Sessions | 会话管理

#### GET /api/sessions

List all sessions.

列出所有会话。

**Response | 响应**:

```json
{
  "sessions": [
    {
      "id": "abc123",
      "title": "Discussion about weather",
      "created_at": 1706000000.0,
      "updated_at": 1706000100.0
    }
  ]
}
```

#### POST /api/sessions

Create a new session.

创建新会话。

**Response | 响应**:

```json
{
  "id": "new-session-uuid"
}
```

#### PUT /api/sessions/{id}

Rename a session.

重命名会话。

**Request Body | 请求体**:

```json
{
  "title": "New Title"
}
```

#### DELETE /api/sessions/{id}

Delete a session.

删除会话。

**Response | 响应**:

```json
{
  "success": true
}
```

#### GET /api/sessions/{id}/messages

Get full session messages (including System Prompt).

获取完整会话消息（含 System Prompt）。

**Response | 响应**:

```json
{
  "messages": [
    { "role": "system", "content": "You are a helpful AI assistant." },
    { "role": "user", "content": "Hello" },
    { "role": "assistant", "content": "Hi there!" }
  ]
}
```

#### GET /api/sessions/{id}/history

Get conversation history (without System Prompt, includes tool_calls).

获取对话历史（不含 System Prompt，含 tool_calls）。

#### POST /api/sessions/{id}/generate-title

Generate AI title for session.

使用 AI 生成会话标题。

**Request Body | 请求体**:

```json
{
  "message": "First user message content"
}
```

**Response | 响应**:

```json
{
  "title": "Weather Inquiry"
}
```

#### POST /api/sessions/{id}/compress

Compress conversation history.

压缩对话历史。

**Response | 响应**:

```json
{
  "archived_count": 10,
  "remaining_count": 5
}
```

---

### 5.3 Files | 文件操作

#### GET /api/files

Read file content.

读取文件内容。

**Query Parameters | 查询参数**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | string | File path (relative to backend/) |

**Response | 响应**:

```json
{
  "content": "File content here...",
  "path": "memory/MEMORY.md",
  "size": 1234
}
```

#### POST /api/files

Save file content.

保存文件内容。

**Request Body | 请求体**:

```json
{
  "path": "memory/MEMORY.md",
  "content": "Updated content..."
}
```

**Response | 响应**:

```json
{
  "success": true,
  "path": "memory/MEMORY.md"
}
```

#### GET /api/skills

List all available skills.

列出所有可用技能。

**Response | 响应**:

```json
{
  "skills": [
    {
      "name": "get_weather",
      "description": "Get weather information for a city",
      "location": "./skills/get_weather/SKILL.md"
    }
  ]
}
```

---

### 5.4 Tokens | Token 统计

#### GET /api/tokens/session/{id}

Get token count for a session.

获取会话的 Token 数量。

**Response | 响应**:

```json
{
  "system_tokens": 1500,
  "message_tokens": 500,
  "total_tokens": 2000
}
```

#### POST /api/tokens/files

Batch count tokens for files.

批量统计文件 Token 数。

**Request Body | 请求体**:

```json
{
  "paths": ["memory/MEMORY.md", "workspace/SOUL.md"]
}
```

**Response | 响应**:

```json
{
  "files": {
    "memory/MEMORY.md": 1200,
    "workspace/SOUL.md": 300
  },
  "total": 1500
}
```

---

### 5.5 Configuration | 配置管理

#### GET /api/config/rag-mode

Get RAG mode status.

获取 RAG 模式状态。

**Response | 响应**:

```json
{
  "enabled": true
}
```

#### PUT /api/config/rag-mode

Toggle RAG mode.

切换 RAG 模式。

**Request Body | 请求体**:

```json
{
  "enabled": true
}
```

---

## 6. WebSocket Alternative | WebSocket 替代方案

For better real-time support, consider using WebSocket instead of SSE.

为获得更好的实时支持，可考虑使用 WebSocket 替代 SSE。

---

## 7. Rate Limiting | 限流

Currently not implemented. In production, implement rate limiting (e.g., 100 requests/minute per IP).

当前未实现限流。生产环境建议实现限流（如每个 IP 每分钟 100 次请求）。

---

## 8. API Versioning | API 版本控制

Current version: `v1`

All endpoints use `/api/` prefix without version. For backward compatibility, consider:

所有接口使用 `/api/` 前缀，不带版本号。为保持向后兼容，建议：

- `/api/v1/chat`
- `/api/v2/chat`

---

## 9. SDK/Client Examples | SDK/客户端示例

### Python

```python
import requests

def send_message(message: str, session_id: str):
    response = requests.post(
        "http://localhost:8002/api/chat",
        json={"message": message, "session_id": session_id},
        stream=True
    )
    for line in response.iter_lines():
        if line:
            print(line.decode())
```

### JavaScript

```javascript
async function streamChat(message, sessionId) {
  const response = await fetch('http://localhost:8002/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId })
  });
  
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    console.log(decoder.decode(value));
  }
}
```

---

## 10. Changelog | 变更日志

| Version | Date | Changes |
|---------|------|---------|
| v1.0.0 | 2026-03-06 | Initial release |

---

## 11. Support | 支持

For issues or questions, please open an issue on GitHub.

如有问题，请提交 GitHub Issue。
