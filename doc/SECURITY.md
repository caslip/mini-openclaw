# Security | 安全

---

## 1. Overview | 概述

This document describes security measures, best practices, and configuration for Mini-OpenClaw.

本文档描述 Mini-OpenClaw 的安全措施、最佳实践和配置。

---

## 2. Security Architecture | 安全架构

### 2.1 Threat Model | 威胁模型

| Threat | Description | Mitigation |
|--------|-------------|-------------|
| Path Traversal | Attacker attempts to access files outside project root | Path validation, whitelist |
| Command Injection | Malicious shell commands via terminal tool | Command blacklist, timeout |
| Unauthorized Access | Unauthorized access to sessions or data | API authentication |
| Data Exposure | Sensitive data exposure | File permissions, encryption |
| Resource Exhaustion | DoS via large requests | Rate limiting, request size limits |

### 2.2 Security Layers | 安全层

```
┌─────────────────────────────────────────────┐
│              Network Layer                   │
│  - Firewall rules                           │
│  - SSL/TLS encryption                       │
│  - CORS configuration                       │
├─────────────────────────────────────────────┤
│              Application Layer               │
│  - API authentication                       │
│  - Request validation                       │
│  - Rate limiting                            │
├─────────────────────────────────────────────┤
│              Tool Execution Layer            │
│  - Sandboxed execution                     │
│  - Command blacklist                        │
│  - Path whitelist                          │
│  - Execution timeout                        │
├─────────────────────────────────────────────┤
│              Data Layer                     │
│  - File permissions                         │
│  - Encryption at rest                        │
│  - Backup encryption                        │
└─────────────────────────────────────────────┘
```

---

## 3. Tool Security | 工具安全

### 3.1 Terminal Tool | 终端工具

**Command Blacklist | 命令黑名单**:

```python
DANGEROUS_COMMANDS = [
    'rm -rf /',
    'mkfs',
    'dd if=',
    'shutdown',
    'reboot',
    'init 0',
    'init 6',
    'halt',
    'poweroff',
    'telnet',
    'nc -e',
    'bash -i',
    'sh -i',
    'curl | sh',
    'wget | sh',
    ':(){:|:&};:',
    'fork()',
]
```

**Working Directory Restriction | 工作目录限制**:

```python
ALLOWED_ROOT = os.path.abspath(BASE_DIR)

def validate_path(path: str) -> bool:
    abs_path = os.path.abspath(os.path.join(ALLOWED_ROOT, path))
    return abs_path.startswith(ALLOWED_ROOT)
```

**Timeout Configuration | 超时配置**:

```python
COMMAND_TIMEOUT = 30  # seconds
MAX_OUTPUT_SIZE = 5000  # characters
```

### 3.2 File Operations | 文件操作

**Path Whitelist | 路径白名单**:

```python
ALLOWED_WRITE_DIRS = [
    'memory/',
    'workspace/',
    'skills/',
    'knowledge/',
]

ALLOWED_READ_DIRS = [
    'workspace/',
    'memory/',
    'skills/',
    'knowledge/',
    'sessions/',
]

ALLOWED_ROOT_FILES = [
    'SKILLS_SNAPSHOT.md',
]
```

**Path Traversal Prevention | 路径遍历防护**:

```python
def validate_path(path: str) -> bool:
    # Block path traversal | 阻止路径遍历
    if '..' in path or path.startswith('/'):
        return False
    
    # Normalize and check | 规范化并检查
    abs_path = os.path.abspath(os.path.join(BASE_DIR, path))
    return abs_path.startswith(os.path.abspath(BASE_DIR))
```

### 3.3 Python Execution | Python 执行

**Sandboxed Execution | 沙箱执行**:

```python
# Using PythonAstREPLTool with restricted builtins
# 使用 PythonAstREPLTool 并限制内置函数
safe_globals = {
    '__builtins__': {
        'print': print,
        'len': len,
        'range': range,
        'str': str,
        'int': int,
        'float': float,
        'list': list,
        'dict': dict,
        'tuple': tuple,
        'set': set,
        'sum': sum,
        'min': min,
        'max': max,
        'abs': abs,
        'round': round,
        # Add more as needed | 根据需要添加更多
    }
}
```

---

## 4. API Security | API 安全

### 4.1 Authentication | 认证

**API Key Middleware | API Key 中间件**:

```python
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

**Usage | 使用**:

```python
@app.post("/api/chat")
async def chat(
    request: ChatRequest,
    api_key: str = Security(verify_api_key)
):
    # Handle chat | 处理聊天
    pass
```

### 4.2 Rate Limiting | 限流

```python
from fastapi import Request
from fastapi.middlewareiddleware import Middleware
import time

# Simple in-memory rate limiter | 简单内存限流器
rate_limit_store = {}

async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Allow 100 requests per minute | 每分钟允许 100 次请求
    if client_ip in rate_limit_store:
        requests = [t for t in rate_limit_store[client_ip] 
                   if current_time - t < 60]
        if len(requests) >= 100:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"}
            )
        rate_limit_store[client_ip] = requests + [current_time]
    else:
        rate_limit_store[client_ip] = [current_time]
    
    return await call_next(request)
```

### 4.3 CORS Configuration | CORS 配置

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## 5. Data Security | 数据安全

###  Permissions | 文件权限5.1 File

```bash
# Set proper file permissions | 设置正确的文件权限
chmod 600 backend/config.json       # Config - owner only
chmod 700 backend/sessions          # Sessions - owner only
chmod -R 600 backend/memory/        # Memory files - owner only
chmod -R 600 backend/workspace/     # Workspace - owner only
chmod 644 backend/.env.example     # Example - readable
```

### 5.2 Sensitive Data | 敏感数据

**Environment Variables | 环境变量**:

- Never commit `.env` to version control
- Use `.env.example` as template
- Rotate API keys regularly

**Data at Rest | 静态数据加密**:

```bash
# Encrypt sensitive files | 加密敏感文件
gpg --symmetric --cipher-algo AES256 sensitive_data.json

# Or use filesystem encryption | 或使用文件系统加密
# LUKS (Linux), FileVault (macOS), BitLocker (Windows)
```

---

## 6. Network Security | 网络安全

### 6.1 SSL/TLS Configuration | SSL/TLS 配置

**Generate Certificate | 生成证书**:

```bash
# Self-signed for testing | 自签名（测试用）
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Let's Encrypt (production) | Let's Encrypt（生产）
certbot --nginx -d your-domain.com
```

**HTTPS Configuration | HTTPS 配置**:

```python
import uvicorn

uvicorn.run(
    "app:app",
    host="0.0.0.0",
    port=8002,
    ssl_keyfile="key.pem",
    ssl_certfile="cert.pem",
)
```

### 6.2 Firewall Rules | 防火墙规则

```bash
# UFW (Ubuntu)
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable

# iptables
iptables -A INPUT -p tcp --dport 8002 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 8002 -j DROP
```

---

## 7. Monitoring & Incident Response | 监控与事件响应

### 7.1 Security Logging | 安全日志

```python
import logging

security_logger = logging.getLogger('security')

def log_security_event(event_type: str, details: dict):
    security_logger.warning(
        f"Security event: {event_type}",
        extra={
            'event_type': event_type,
            'details': details,
            'timestamp': time.time()
        }
    )

# Log blocked attempts | 记录被阻止的尝试
log_security_event('path_traversal_blocked', {
    'path': attempted_path,
    'ip': client_ip
})

log_security_event('command_blocked', {
    'command': attempted_command,
    'ip': client_ip
})
```

### 7.2 Incident Response | 事件响应

| Incident | Action |
|----------|--------|
| Unauthorized access detected | Block IP, rotate API keys |
| Suspicious file access | Alert, investigate, patch |
| DoS attack | Rate limiting, IP blocking |
| Data breach | Notify users, rotate secrets, audit logs |

---

## 8. Security Checklist | 安全检查清单

### 8.1 Development | 开发

- [ ] Use environment variables for secrets
- [ ] Validate all user inputs
- [ ] Implement proper error handling (don't expose internals)
- [ ] Use parameterized queries (if SQL)
- [ ] Keep dependencies updated

### 8.2 Production | 生产

- [ ] Enable HTTPS/TLS
- [ ] Configure authentication
- [ ] Set up rate limiting
- [ ] Configure firewall
- [ ] Set proper file permissions
- [ ] Enable security logging
- [ ] Regular security audits
- [ ] Backup encryption

---

## 9. Compliance | 合规

### 9.1 Data Privacy | 数据隐私

- User data stored locally (not sent to third parties)
- No analytics or tracking
- User can delete all data by removing session/memory files
- No personally identifiable information (PII) stored by default

### 9.2 Audit Trail | 审计跟踪

- All tool executions logged
- Session creation/modification tracked
- File access attempts logged
- API request logging (with PII filtering)

---

## 10. Related Documents | 相关文档

- [DEPLOY.md](DEPLOY.md) - Deployment Guide
- [ENV.md](ENV.md) - Environment Variables
- [API.md](API.md) - API Documentation
