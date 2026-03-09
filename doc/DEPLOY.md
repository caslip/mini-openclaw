# Deployment Guide | 部署指南

---

## 1. Overview | 概述

This document covers deployment options for Mini-OpenClaw, from local development to production environments.

本文档涵盖 Mini-OpenClaw 的部署方案，从本地开发到生产环境。

---

## 2. Prerequisites | 前置条件

### 2.1 System Requirements | 系统要求

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Disk | 10 GB | 50+ GB (for data files) |
| OS | Windows 10+, macOS 10.15+, Ubuntu 20.04+ | Same |

### 2.2 Required Software | 必需软件

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend runtime |
| Ollama | Latest | LLM inference server |
| Git | 2.0+ | Version control |

---

## 3. Local Development | 本地开发

### 3.1 Quick Start | 快速开始

```bash
# 1. Clone repository | 克隆仓库
git clone <repository-url>
cd mini-openClaw

# 2. Backend setup | 后端设置
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

# 3. Configure environment | 配置环境
copy .env.example .env
# Edit .env with your settings

# 4. Start backend | 启动后端
uvicorn app:app --port 8002 --host 0.0.0.0 --reload

# 5. Frontend setup (new terminal) | 前端设置（新终端）
cd frontend
npm install
npm run dev
```

### 3.2 Verify Installation | 验证安装

| Service | URL | Expected |
|---------|-----|----------|
| Backend | http://localhost:8002/docs | FastAPI Swagger UI |
| Frontend | http://localhost:3000 | Main application |
| Ollama | http://localhost:11434 | Ollama running |

---

## 4. Production Deployment | 生产部署

### 4.1 Backend Deployment | 后端部署

#### Option A: Systemd Service (Linux) | 选项 A：Systemd 服务（Linux）

Create service file `/etc/systemd/system/mini-openclaw.service`:

```ini
[Unit]
Description=Mini-OpenClaw Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/mini-openclaw/backend
Environment="PATH=/opt/mini-openclaw/backend/.venv/bin"
ExecStart=/opt/mini-openclaw/backend/.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8002 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service | 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable mini-openclaw
sudo systemctl start mini-openclaw
```

#### Option B: Docker Container | 选项 B：Docker 容器

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8002

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]
```

Build and run:

```bash
cd backend
docker build -t mini-openclaw-backend .
docker run -d \
  --name mini-openclaw-backend \
  -p 8002:8002 \
  -v $(pwd)/sessions:/app/sessions \
  -v $(pwd)/memory:/app/memory \
  -v $(pwd)/config.json:/app/config.json \
  --restart unless-stopped \
  mini-openclaw-backend
```

#### Option C: Docker Compose | 选项 C：Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8002:8002"
    volumes:
      - ./sessions:/app/sessions
      - ./memory:/app/memory
      - ./workspace:/app/workspace
      - ./skills:/app/skills
      - ./knowledge:/app/knowledge
      - ./config.json:/app/config.json
    environment:
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - API_BASE_URL=http://backend:8002
    depends_on:
      - backend
    restart: unless-stopped
```

### 4.2 Frontend Deployment | 前端部署

#### Static Hosting | 静态托管

```bash
cd frontend
npm run build
# Output in frontend/out/
```

Deploy to various static hosting services:

| Service | Command | Notes |
|---------|---------|-------|
| Vercel | `vercel deploy` | Zero-config |
| Netlify | `netlify deploy --prod` | Drag & drop |
| Cloudflare Pages | `wrangler pages deploy` | Global CDN |

#### Nginx Configuration | Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /var/www/mini-openclaw/out;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## 5. Production Checklist | 生产环境检查清单

### 5.1 Security | 安全

- [ ] Change default ports (8002, 3000) if exposed to internet
- [ ] Enable authentication (JWT, OAuth2)
- [ ] Configure SSL/TLS certificate
- [ ] Set proper file permissions
- [ ] Enable rate limiting
- [ ] Configure firewall rules

### 5.2 Performance | 性能

- [ ] Set appropriate worker count (2-4 x CPU cores)
- [ ] Configure connection pooling
- [ ] Enable response compression (gzip)
- [ ] Set up CDN for static assets
- [ ] Monitor memory usage

### 5.3 Reliability | 可靠性

- [ ] Configure health check endpoints
- [ ] Set up monitoring and alerting
- [ ] Configure log rotation
- [ ] Set up automated backups
- [ ] Test disaster recovery plan

---

## 6. Environment Configuration | 环境配置

### 6.1 Production Environment Variables | 生产环境变量

```bash
# Backend | 后端
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3.5:9b
OPENAI_API_KEY=sk-xxxx
OPENAI_BASE_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small

# Optional | 可选
LOG_LEVEL=INFO
WORKERS=4
HOST=0.0.0.0
PORT=8002

# Frontend | 前端
NEXT_PUBLIC_API_BASE_URL=http://your-domain.com
```

### 6.2 Backend Configuration | 后端配置

Update `config.json` for production:

```json
{
  "rag_mode": true,
  "ollama_base_url": "http://localhost:11434",
  "ollama_model": "qwen3.5:9b",
  "embedding_model": "text-embedding-3-small",
  "max_tokens_per_component": 20000,
  "log_level": "INFO"
}
```

---

## 7. SSL/TLS Configuration | SSL/TLS 配置

### 7.1 Let's Encrypt (Free) | Let's Encrypt（免费）

```bash
# Install certbot | 安装 certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificate | 生成证书
sudo certbot --nginx -d your-domain.com

# Auto-renewal | 自动续期
sudo certbot renew --dry-run
```

### 7.2 Redirect HTTP to HTTPS | HTTP 重定向到 HTTPS

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 8. Monitoring & Health Checks | 监控与健康检查

### 8.1 Health Check Endpoint | 健康检查端点

```bash
# Add to backend
curl http://localhost:8002/health
# Expected: {"status": "ok"}
```

### 8.2 Log Management | 日志管理

```bash
# View logs (systemd)
journalctl -u mini-openclaw -f

# View logs (docker)
docker logs -f mini-openclaw-backend
```

---

## 9. Backup & Restore | 备份与恢复

### 9.1 Automated Backup | 自动备份

```bash
# Create backup script | 创建备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf mini-openclaw-backup-$DATE.tar.gz \
  backend/sessions \
  backend/memory \
  backend/workspace \
  backend/config.json

# Add to crontab | 添加到定时任务
0 2 * * * /path/to/backup.sh
```

### 9.2 Restore from Backup | 从备份恢复

```bash
# Extract backup | 解压备份
tar -xzf mini-openclaw-backup-20260309.tar.gz

# Restore files | 恢复文件
cp -r sessions/* backend/sessions/
cp -r memory/* backend/memory/
```

---

## 10. Troubleshooting | 故障排除

### Common Issues | 常见问题

| Issue | Solution |
|-------|----------|
| Ollama not accessible | Check firewall, verify URL in config |
| Frontend cannot connect to backend | Check API_BASE_URL environment variable |
| Memory errors | Increase RAM or reduce concurrent sessions |
| Slow responses | Add more workers, check Ollama model performance |

### Debug Mode | 调试模式

```bash
# Backend with verbose logging | 后端详细日志
uvicorn app:app --log-level debug --reload

# Frontend with debugging | 前端调试
cd frontend
NEXT_PUBLIC_DEBUG=true npm run dev
```

---

## 11. Support | 支持

For deployment issues, please:
- Check logs first
- Review this document
- Open an issue on GitHub

---

## 12. Related Documents | 相关文档

- [ENV.md](ENV.md) - Environment Variables
- [SECURITY.md](SECURITY.md) - Security Configuration
- [MONITORING.md](MONITORING.md) - Monitoring Setup
