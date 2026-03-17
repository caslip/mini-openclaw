# 功能清单 - 测试清单

本文档列出 Mini-OpenClaw 系统的所有功能，用于逐个测试验证。

---

## 1. 核心功能（Core）

| 序号 | 功能 | API 端点 | 测试状态 | 备注 |
|------|------|----------|----------|------|
| 1.1 | 流式对话（SSE） | `POST /api/chat` | [ ] | |
| 1.2 | 会话列表 | `GET /api/sessions` | [ ] | |
| 1.3 | 创建会话 | `POST /api/sessions` | [ ] | |
| 1.4 | 重命名会话 | `PUT /api/sessions/{id}` | [ ] | |
| 1.5 | 删除会话 | `DELETE /api/sessions/{id}` | [ ] | |
| 1.6 | 获取消息历史 | `GET /api/sessions/{id}/history` | [ ] | |
| 1.7 | 生成会话标题 | `POST /api/sessions/{id}/generate-title` | [ ] | |
| 1.8 | 对话压缩 | `POST /api/sessions/{id}/compress` | [ ] | |
| 1.9 | Token 统计 | `GET /api/tokens/session/{id}` | [ ] | |
| 1.10 | 批量 Token 统计 | `POST /api/tokens/files` | [ ] | |

---

## 2. 文件操作（Files）

| 序号 | 功能 | API 端点 | 测试状态 | 备注 |
|------|------|----------|----------|------|
| 2.1 | 读取文件 | `GET /api/files?path=...` | [ ] | |
| 2.2 | 保存文件 | `POST /api/files` | [ ] | |
| 2.3 | 技能列表 | `GET /api/skills` | [ ] | |

---

## 3. 工具能力（Tools）

| 序号 | 工具 | 功能描述 | 测试状态 | 备注 |
|------|------|----------|----------|------|
| 3.1 | `terminal` | 执行 Shell 命令 | [ ] | |
| 3.2 | `python_repl_ast` | 执行 Python 代码 | [ ] | |
| 3.3 | `fetch_url` | 抓取网页内容 | [ ] | |
| 3.4 | `read_file` | 读取项目内文件 | [ ] | |
| 3.5 | `write_file` | 写入项目内文件 | [ ] | |
| 3.6 | `search_knowledge_base` | 搜索知识库 | [ ] | |
| 3.7 | `list_data_files` | 列举数据文件结构 | [ ] | |
| 3.8 | `set_reminder` | 设置定时提醒 | [ ] | |

---

## 4. Skills 系统

| 序号 | Skill | 功能 | 测试状态 | 备注 |
|------|-------|------|----------|------|
| 4.1 | `get_weather` | 天气查询 | [ ] | |
| 4.2 | `data_analysis` | 数据分析 | [ ] | |
| 4.3 | `reminder` | 提醒设置 | [ ] | |

---

## 5. RAG 功能

| 序号 | 功能 | API 端点 | 测试状态 | 备注 |
|------|------|----------|----------|------|
| 5.1 | RAG 模式开关 | `GET /api/config/rag-mode` | [ ] | |
| 5.2 | 切换 RAG 模式 | `PUT /api/config/rag-mode` | [ ] | |
| 5.3 | 语义检索 | 内部调用 | [ ] | |
| 5.4 | Memory 向量索引 | 内部机制 | [ ] | |

---

## 6. 心跳系统（Heartbeat）

| 序号 | 功能 | API 端点 | 测试状态 | 备注 |
|------|------|----------|----------|------|
| 6.1 | 心跳状态 | `GET /api/heartbeat/status` | [ ] | |
| 6.2 | 手动触发心跳 | `POST /api/heartbeat/trigger` | [ ] | |
| 6.3 | 心跳配置 | `POST /api/heartbeat/config` | [ ] | |
| 6.4 | 心跳指标 | `GET /api/heartbeat/metrics` | [ ] | |

---

## 7. 定时任务（Cron）

| 序号 | 功能 | API 端点 | 测试状态 | 备注 |
|------|------|----------|----------|------|
| 7.1 | 任务列表 | `GET /api/cron/jobs` | [ ] | |
| 7.2 | 创建任务 | `POST /api/cron/jobs` | [ ] | |
| 7.3 | 获取任务详情 | `GET /api/cron/jobs/{job_id}` | [ ] | |
| 7.4 | 更新任务 | `PUT /api/cron/jobs/{job_id}` | [ ] | |
| 7.5 | 删除任务 | `DELETE /api/cron/jobs/{job_id}` | [ ] | |
| 7.6 | 手动触发任务 | `POST /api/cron/jobs/{job_id}/trigger` | [ ] | |
| 7.7 | 任务执行历史 | `GET /api/cron/jobs/{job_id}/history` | [ ] | |
| 7.8 | 任务模板列表 | `GET /api/cron/templates` | [ ] | |
| 7.9 | 获取模板详情 | `GET /api/cron/templates/{template_id}` | [ ] | |
| 7.10 | 从模板创建任务 | `POST /api/cron/jobs/from-template` | [ ] | |
| 7.11 | 调度器状态 | `GET /api/cron/status` | [ ] | |
| 7.12 | 导出任务配置 | `GET /api/cron/export` | [ ] | |
| 7.13 | 导入任务配置 | `POST /api/cron/import` | [ ] | |
| 7.14 | 任务指标 | `GET /api/cron/metrics` | [ ] | |

---

## 8. 多渠道通知（Channels）

| 序号 | 功能 | API 端点 | 测试状态 | 备注 |
|------|------|----------|----------|------|
| 8.1 | 渠道状态 | `GET /api/channels/status` | [ ] | |
| 8.2 | 测试消息 | `POST /api/channels/test` | [ ] | |
| 8.3 | 发送消息 | `POST /api/channels/send` | [ ] | |
| 8.4 | 渠道列表 | `GET /api/channels/list` | [ ] | |
| 8.5 | Telegram 配置 | `POST /api/channels/config/telegram` | [ ] | |
| 8.6 | 飞书配置 | `POST /api/channels/config/feishu` | [ ] | |

---

## 9. 进化系统（Evolution）

| 序号 | 功能 | API 端点 | 测试状态 | 备注 |
|------|------|----------|----------|------|
| 9.1 | 技能发现 | `POST /api/evolution/skills/discover` | [ ] | |
| 9.2 | 技能摘要 | `GET /api/evolution/skills/summary` | [ ] | |
| 9.3 | 提示词分析 | `POST /api/evolution/prompt/analyze` | [ ] | |
| 9.4 | 提示词摘要 | `GET /api/evolution/prompt/summary` | [ ] | |
| 9.5 | 工作流分析 | `POST /api/evolution/workflow/analyze` | [ ] | |
| 9.6 | 工作流摘要 | `GET /api/evolution/workflow/summary` | [ ] | |
| 9.7 | 工作流执行记录 | `GET /api/evolution/workflow/executions` | [ ] | |
| 9.8 | 自动进化 | `POST /api/evolution/auto` | [ ] | |
| 9.9 | 进化状态 | `GET /api/evolution/status` | [ ] | |
| 9.10 | 启动进化调度器 | `POST /api/evolution/scheduler/start` | [ ] | |
| 9.11 | 停止进化调度器 | `POST /api/evolution/scheduler/stop` | [ ] | |
| 9.12 | 调度器配置（获取） | `GET /api/evolution/scheduler/config` | [ ] | |
| 9.13 | 调度器配置（设置） | `POST /api/evolution/scheduler/config` | [ ] | |

---

## 10. 前端功能

| 序号 | 功能 | 组件 | 测试状态 | 备注 |
|------|------|------|----------|------|
| 10.1 | 聊天界面 | ChatPanel | [ ] | |
| 10.2 | 消息展示 | ChatMessage | [ ] | |
| 10.3 | 消息输入 | ChatInput | [ ] | |
| 10.4 | 思维链展示 | ThinkingChain | [ ] | |
| 10.5 | 会话列表 | Sidebar | [ ] | |
| 10.6 | RAG 开关 | RagToggle | [ ] | |
| 10.7 | 设置弹窗 | SettingsModal | [ ] | |
| 10.8 | 健康检查 | /health | [ ] | |

---

## 测试记录

| 日期 | 测试人 | 测试功能 | 结果 | 问题 |
|------|--------|----------|------|------|
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |

---

## 使用说明

1. 逐行测试每个功能
2. 测试通过后，在"测试状态"列标记 `[x]`
3. 如发现问题，在"问题"栏记录
4. 定期汇总测试结果
