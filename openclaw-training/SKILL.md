---
name: openclaw-training
description: |
  OpenClaw Agent 专题培训标准化框架，提供多轮递进式培训方案设计、学员档案管理、100分制任务评分和标准报告生成。
  This skill should be used when: (1) 用户要求对 OpenClaw Agent 进行培训或考核,
  (2) 用户提到"专题培训"、"训练 OpenClaw"、"考核 Agent"等关键词,
  (3) 需要为 OpenClaw Agent 设计结构化的能力验证方案。
  包含：学员档案与成长追踪、多轮递进培训框架、六维度评分标准、过程记录与标准报告模板、连接记忆机制。
---

# OpenClaw Agent Training

## Prerequisites

- 可连接到目标 OpenClaw Agent 所在环境（SSH / API / 本地等）
- OpenClaw CLI (`openclaw agent`) 可用
- 目标 Agent 的通信渠道已配置（feishu / discord / telegram）

## Core Workflow

### Step 1: 读取连接记忆

读取 `data/connections.md`。若不存在，询问用户：
1. 连接方式（SSH / API / 本地，含具体命令和参数）
2. Agent 通信渠道和 CLI 前缀
3. 工作区根路径和配置文件位置

用 [templates/connection-memory.md](templates/connection-memory.md) 填写后写入 `data/connections.md`。

### Step 2: 读取远程 Agent 配置

通过连接信息连接到目标环境，**实时读取**目标 Agent 的核心配置：
- `AGENTS.md` — 行为规则、任务定义、铁律
- `TOOLS.md` — 可用工具、使用规范
- `MEMORY.md` — 长期记忆、已掌握能力
- `HEARTBEAT.md` — 心跳任务定义
- `SOUL.md` — Agent 身份与价值观（如存在）

了解 Agent 当前的能力边界和规则约束，作为培训方案设计的输入。

### Step 3: 加载学员档案

读取 `data/profiles/[agent-alias].md`。

- **已有档案**：了解该学员的能力认证矩阵、已知弱项、历史评分趋势、上次培训的改善建议。本次培训方案应针对弱项设计、避免重复考核已认证能力。
- **无档案（新学员）**：基于 Step 2 读取的远程配置，用 [templates/agent-profile.md](templates/agent-profile.md) 创建初始档案，能力矩阵全部标记为 ⬜ 未考核。

### Step 4: 查阅历史培训报告

读取 `references/training-history/` 下该学员的报告：
- 上次培训的具体成绩和教练评语
- 未解决的问题和持续关注项
- 改善建议的落实情况

### Step 5: 设计培训方案

基于培训主题 + 学员档案 + 历史报告，用 [templates/training-plan.md](templates/training-plan.md) 设计方案。
轮次设计原则和任务规范见 [references/training-framework.md](references/training-framework.md)。

核心要求：
- 分 2-4 轮递进（基础确认 → 实战考核 → 压力测试）
- 针对学员档案中 ⚠️ 需关注和 ❌ 未通过的能力重点设计任务
- 每任务有唯一 ID（`T1-1`）、明确交付物、评分维度
- **展示方案给用户确认后再执行**

### Step 6: 执行培训并记录过程

通过 `data/connections.md` 中的连接信息发送任务指令，同时用 [templates/training-session-log.md](templates/training-session-log.md) 实时记录：
- 每个任务的下达指令、Agent 响应、产出物检查结果
- 过程中的异常和观察

**关键原则**：教练下达指令，Agent 自主执行。不替 Agent 操作或决策。

### Step 7: 产出物实地验证（必须）

> ⚠️ **铁律：教练必须亲自验证所有可观测的产出物，不得仅凭 Agent 的文字报告评分。**
> 此规则源自 2026-02-18 培训教训：Agent 报告"发帖成功"但配图中文全部乱码，教练未验证直接打高分。

每个任务完成后、评分之前，教练必须按产出类型执行对应的验证动作：

| 产出类型 | 验证方法 | 工具 |
|---------|---------|------|
| **服务器文件** | `cat` 读取文件内容，确认非空且有实质内容 | SSH |
| **图片文件** | `scp` 下载到本地 → Read 工具查看图片 → 确认文字渲染正常、无乱码 | scp + Read |
| **社交平台帖子** | 通过 URL 或平台工具获取帖子实际内容，确认文字/图片/链接均正常 | jike-toolkit `my-posts` / 浏览器 / MCP |
| **代码/脚本** | `cat` 读取 + 在远程环境执行验证命令，确认可运行 | SSH |
| **目录结构** | `find` 或 `ls -R` 检查完整目录树 | SSH |
| **API 调用结果** | 查看 API 响应原文，确认状态码和内容正确 | SSH / curl |

**验证记录格式**（写入 session-log）：
```markdown
**教练验证 T{X}-{Y}**:
- 验证方式：[下载图片本地查看 / SSH cat 文件 / 访问帖子链接 ...]
- 验证结果：[✅ 通过 / ❌ 发现问题: {具体描述}]
- 截图/证据：[如有]
```

如果验证发现问题：
1. 在 session-log 中记录问题详情
2. 根据问题严重程度调整评分
3. 决定是否要求 Agent 修正后重新提交

### Step 8: 逐任务评分

按 [references/scoring-rubric.md](references/scoring-rubric.md) 对每个任务打分（100 分制，六维度加权）。

**前置条件**：Step 7 的实地验证必须完成。未经验证的任务不得评分。

### Step 9: 生成报告、更新档案、汇报

1. 用 [templates/training-report.md](templates/training-report.md) 生成标准报告
2. **更新学员档案**（`data/profiles/[agent-alias].md`）：
   - 能力认证矩阵：新认证 / 状态变更
   - 培训历史：追加本次记录
   - 评分趋势：追加本次各维度分数
   - 已知问题：新发现 / 状态更新
   - 关键里程碑：如有突破性进步
3. 报告存两份：远程 Agent 的 `training-report/` 目录 + 本 Skill 的 `references/training-history/`
4. 向用户呈现综合评分、关键发现、与上次对比的成长变化、改善建议

## References

| 文件 | 读取时机 |
|------|---------|
| [training-framework.md](references/training-framework.md) | 设计培训方案时，了解轮次设计和递进逻辑 |
| [scoring-rubric.md](references/scoring-rubric.md) | 评分时，了解六维度权重和评分标准 |
| [training-history/](references/training-history/) | 培训前了解历史记录 |

## Templates

| 文件 | 用途 |
|------|------|
| [agent-profile.md](templates/agent-profile.md) | 新学员建档或更新现有档案 |
| [training-plan.md](templates/training-plan.md) | 每次培训前设计方案 |
| [training-session-log.md](templates/training-session-log.md) | 培训过程中实时记录 |
| [training-report.md](templates/training-report.md) | 培训结束后生成报告 |
| [connection-memory.md](templates/connection-memory.md) | 首次连接时记录配置 |

## Runtime Data

- `data/connections.md` — 连接记忆，首次运行时创建，记录各 Agent 连接配置
- `data/profiles/[agent-alias].md` — 学员档案，每个 Agent 一份，培训后更新

每次培训前必须先读取连接记忆和学员档案。

## Important Rules

1. **通用化**：不绑定具体 Agent 名称，用 `[agent-alias]` 占位；不假设特定连接方式
2. **档案驱动**：每次培训必须基于学员档案设计方案，培训后必须更新档案
3. **先调研后执行**：每次培训先读远程配置 + 学员档案 + 历史报告，再设计方案
4. **用户确认**：培训方案必须用户确认后才执行
5. **教练不代劳**：下达指令让 Agent 执行，不替 Agent 操作
6. **产出物为证**：评分基于实际产出文件，不凭印象
7. **教练实地验证**：凡涉及图片、外部平台发布、可视化产出的任务，教练必须亲自下载/访问/查看后才能评分。绝不仅凭 Agent 的文字报告（"发布成功"）打分
8. **过程记录**：培训过程必须用 session-log 模板实时记录
9. **报告归档**：每次报告存两份（远程 Agent 环境 + 本 Skill 的 training-history）
10. **档案持久化**：学员档案是跨培训的长期记忆，每次培训结束必须更新
