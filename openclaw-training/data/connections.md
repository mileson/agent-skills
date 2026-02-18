# OpenClaw Connection Memory

## Agent: xiaofeng

- **创建时间**: 2026-02-18 20:00
- **最后更新**: 2026-02-18 20:00

### 连接配置

- **连接方式**: SSH
- **连接命令**: `ssh racknerd`
- **额外选项**: `-o ConnectTimeout=30 -o ServerAliveInterval=15`
- **Host 别名**: racknerd (107.175.190.120:2222)

### OpenClaw CLI

- **CLI 前缀**: `openclaw agent --channel feishu`
- **可用渠道**: feishu, discord, telegram
- **默认 timeout**: 600 秒

### 路径配置

- **OpenClaw 根目录**: `/root/.openclaw`
- **工作区根路径**: `/root/.openclaw/workspace`
- **配置文件位置**:
  - AGENTS.md: `/root/.openclaw/workspace/AGENTS.md`
  - TOOLS.md: `/root/.openclaw/workspace/TOOLS.md`
  - MEMORY.md: `/root/.openclaw/workspace/MEMORY.md`
  - HEARTBEAT.md: `/root/.openclaw/workspace/HEARTBEAT.md`
  - SOUL.md: `/root/.openclaw/workspace/SOUL.md`
- **培训报告存放**: `/root/.openclaw/workspace/content/training-report/`

### 已知问题

- SSH 连接偶尔断开（Connection closed），需要 sleep 后重连
- 服务器在美国，网络延迟 ~200ms
- Brave Search API Free 计划有限流（1次/秒），连续搜索需间隔

### 备注

- Agent 底层模型：zai/glm-5（智谱 GLM-5）
- 主要通信渠道：飞书（feishu）
- 即刻工具：`/root/.openclaw/jike/jike-toolkit.mjs`
- 内容创作工作区：`/root/.openclaw/workspace/content/workspace/`
- steer 模式已开启（messages.queue.mode: "steer"）
