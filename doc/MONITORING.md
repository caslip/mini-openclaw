# Monitoring & Observability | 监控与可观测性

---

## 1. Overview | 概述

This document describes monitoring, logging, and alerting strategies for Mini-OpenClaw production environments.

本文档描述 Mini-OpenClaw 生产环境的监控、日志和告警策略。

---

## 2. Metrics Collection | 指标收集

### 2.1 Key Metrics | 关键指标

| Metric | Type | Description |
|--------|------|-------------|
| `request_count` | Counter | Total API requests |
| `request_duration` | Histogram | API response time |
| `active_sessions` | Gauge | Current active sessions |
| `session_messages` | Histogram | Messages per session |
| `tool_execution_count` | Counter | Tool execution frequency |
| `tool_execution_duration` | Histogram | Tool execution time |
| `llm_token_count` | Counter | LLM token usage |
| `error_count` | Counter | Error occurrences |
| `rag_retrieval_time` | Histogram | RAG retrieval latency |

### 2.2 Python Metrics (Prometheus) | Python 指标 (Prometheus)

```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics | 请求指标
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)
request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Session metrics | 会话指标
active_sessions = Gauge(
    'active_sessions',
    'Number of active sessions'
)

# LLM metrics | LLM 指标
llm_token_count = Counter(
    'llm_tokens_total',
    'Total LLM tokens used',
    ['model', 'type']
)

# Tool metrics | 工具指标
tool_execution_count = Counter(
    'tool_executions_total',
    'Total tool executions',
    ['tool_name', 'status']
)
tool_execution_duration = Histogram(
    'tool_execution_duration_seconds',
    'Tool execution duration',
    ['tool_name']
)
```

---

## 3. Logging | 日志记录

### 3.1 Log Levels | 日志级别

| Level | Usage |
|-------|-------|
| `DEBUG` | Detailed diagnostic information |
| `INFO` | General operational events |
| `WARNING` | Unexpected but handled situations |
| `ERROR` | Errors that prevent operation |

### 3.2 Python Logging Configuration | Python 日志配置

```python
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/app.log'),
    ]
)

logger = logging.getLogger(__name__)
```

### 3.3 Structured Logging | 结构化日志

```python
import json
import logging

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_data)
```

### 3.4 Log Rotation | 日志轮转

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10_000_000,  # 10 MB
    backupCount=5
)
```

---

## 4. Health Checks | 健康检查

### 4.1 Health Check Endpoint | 健康检查端点

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "checks": {
            "ollama": check_ollama_connection(),
            "storage": check_storage_access(),
            "memory": check_memory_index()
        }
    }

@app.get("/health/ready")
async def readiness_check():
    # More comprehensive checks
    return {"status": "ready"}
```

### 4.2 Component Health | 组件健康状态

```python
async def check_ollama_connection() -> bool:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{OLLAMA_BASE_URL}/api/tags",
                timeout=5.0
            )
            return response.status_code == 200
    except Exception:
        return False
```

---

## 5. Distributed Tracing | 分布式追踪

### 5.1 OpenTelemetry Setup | OpenTelemetry 设置

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Setup tracing | 设置追踪
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Jaeger exporter | Jaeger 导出器
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)
```

### 5.2 Custom Span | 自定义Span

```python
@tracer.start_as_current_span("process_user_message")
async def process_message(message: str, session_id: str):
    with trace.get_tracer(__name__).start_as_current_span(
        "load_session"
    ) as span:
        span.set_attribute("session_id", session_id)
        # Load session logic
        pass

    with trace.get_tracer(__name__).start_as_current_span(
        "call_llm"
    ) as span:
        span.set_attribute("model", OLLAMA_MODEL)
        # LLM call logic
        pass
```

---

## 6. Alerting | 告警

### 6.1 Alert Rules | 告警规则

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| High Error Rate | error_rate > 5% for 5 min | Critical | Page on-call |
| High Latency | p95_latency > 5s for 5 min | Warning | Investigate |
| Ollama Down | health check fails | Critical | Page on-call |
| Disk Full | disk_usage > 90% | Critical | Alert + cleanup |
| Memory High | memory_usage > 85% | Warning | Investigate |

### 6.2 Prometheus Alert Rules | Prometheus 告警规则

```yaml
groups:
  - name: mini-openclaw
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status="500"}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          API summary: "High latency"

      - alert: OllamaDown
        expr: up{job="ollama"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Ollama is down"
```

---

## 7. Dashboards | 仪表板

### 7.1 Grafana Dashboard | Grafana 仪表板

```json
{
  "dashboard": {
    "title": "Mini-OpenClaw Overview",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time (p95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds)",
            "legendFormat": "p95"
          }
        ]
      },
      {
        "title": "Active Sessions",
        "type": "stat",
        "targets": [
          {
            "expr": "active_sessions"
          }
        ]
      },
      {
        "title": "Tool Execution Time",
        "type": "heatmap",
        "targets": [
          {
            "expr": "rate(tool_execution_duration_seconds_bucket[5m])"
          }
        ]
      }
    ]
  }
}
```

### 7.2 Key Dashboards | 关键仪表板

| Dashboard | Purpose |
|-----------|---------|
| System Overview | CPU, Memory, Disk, Network |
| API Performance | Request rate, latency, errors |
| LLM Performance | Token usage, response time |
| Tool Performance | Execution time by tool type |
| Session Analytics | Active sessions, message volume |

---

## 8. Monitoring Stack | 监控技术栈

### 8.1 Recommended Stack | 推荐技术栈

| Component | Tool | Purpose |
|-----------|------|---------|
| Metrics | Prometheus | Time-series metrics |
| Visualization | Grafana | Dashboards |
| Alerting | Prometheus Alertmanager | Alert routing |
| Logging | ELK Stack / Loki | Log aggregation |
| Tracing | Jaeger / Zipkin | Distributed tracing |

### 8.2 Docker Compose Setup | Docker Compose 配置

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    volumes:
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards

  alertmanager:
    image: prom/alertmanager
    ports:
      - "9093:9093"

  loki:
    image: grafana/loki
    ports:
      - "3100:3100"
```

---

## 9. Performance Monitoring | 性能监控

### 9.1 Key Performance Indicators | 关键性能指标

| KPI | Target | Description |
|-----|--------|-------------|
| API Availability | > 99.9% | Uptime percentage |
| p50 Latency | < 200ms | Median response time |
| p95 Latency | < 1s | 95th percentile response time |
| p99 Latency | < 5s | 99th percentile response time |
| Error Rate | < 0.1% | Percentage of 5xx errors |

### 9.2 Performance Testing | 性能测试

```bash
# Load test with wrk | 使用 wrk 进行负载测试
wrk -t4 -c100 -d30s http://localhost:8002/api/sessions

# Siege benchmark | Siege 基准测试
siege -c 50 -t 30M http://localhost:8002/api/sessions
```

---

## 10. Incident Response | 事件响应

### 10.1 Runbook | 响应手册

| Incident | First Action | Escalation |
|----------|--------------|-------------|
| High error rate | Check logs, identify error type | Team lead |
| Service down | Check health, restart if needed | On-call engineer |
| Slow response | Check Ollama, increase workers | Team lead |
| Disk full | Clean old sessions, archives | System admin |

### 10.2 Post-incident Review | 事件回顾

- Document timeline
- Identify root cause
- Implement fix
- Update monitoring
- Share learnings

---

## 11. Related Documents | 相关文档

- [DEPLOY.md](DEPLOY.md) - Deployment Guide
- [SECURITY.md](SECURITY.md) - Security Configuration
- [API.md](API.md) - API Documentation
