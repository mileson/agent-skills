# Task Handoff

[English](README.md) | [简体中文](README_CN.md)

> 一个给 Claude Code / Cursor 使用的 Skill：把混乱、冗长、快失控的上下文，整理成别人或另一个 Agent 能立刻接手的交接包。

## 这个 Skill 解决什么问题

大上下文窗口很强，但一旦会话变长、调试分叉、目标切换，真正拖慢效率的往往不是“不会做”，而是：

- 当前上下文太脏
- 历史里有大量已经过时的信息
- 已确认事实、未验证猜测、下一步动作混在一起
- 换人接手 / 换 worktree / 换新 session 时，需要重新读一大坨历史

`task-handoff` 的核心思想是：

- 不再继续往一个脏 session 里叠消息
- 只保留下一步执行真正需要的上下文
- 把事实边界标清楚
- 生成一段可以直接交给下一个执行者的提示词

它本质上是在把“高质量手写 handoff”这件事，变成一个可复用的标准动作。

## Features

- **压缩冗长上下文**：从对话、代码状态、日志、验证记录中提炼最小必要信息
- **生成可复用交接提示词**：给另一个用户、另一个 Agent，或下一次新会话直接接上
- **区分事实边界**：明确标注“已确认 / 未验证 / 待确认”
- **保留关键执行信息**：repo、worktree、branch、命令、日志、任务 ID、限制条件等
- **强调下一步可执行性**：接手的人一眼知道先看什么、先做什么
- **支持多种任务类型**：Bug 排查、功能继续开发、远程运维验收、多环境交接

## 能做什么

- **压缩冗长上下文**：从对话、代码状态、日志、验证记录中提炼最小必要信息
- **生成可复用交接提示词**：给另一个用户、另一个 Agent，或下一次新会话直接接上
- **区分事实边界**：明确标注“已确认 / 未验证 / 待确认”
- **保留关键执行信息**：repo、worktree、branch、命令、日志、任务 ID、限制条件等
- **强调下一步可执行性**：接手的人一眼知道先看什么、先做什么
- **支持多种任务类型**：Bug 排查、功能继续开发、远程运维验收、多环境交接

## 适用场景

### 1. Bug / 故障排查交接
你已经排查了一轮，不想让下一个人重新翻长对话和整段日志。

### 2. 新 Session 继续做
当前会话已经开始“上下文腐化”，想带着干净上下文重开。

### 3. 多 Agent 协作
一个 Agent 先调研，另一个 Agent 再实现，只希望传递结论而不是全部中间垃圾上下文。

### 4. 多 worktree / 多环境切换
接下来必须换分支、换工作区、换机器、换远端环境继续做。

## 默认输出

默认会输出两段：

1. **交接摘要**
   - 5 到 10 行，给人快速扫一眼
2. **完整交接提示词**
   - 可以直接复制给另一个用户或 Agent

必要时还可以附一个极短的验收 checklist。

## 工作方式

Skill 的整理流程是：

1. 判断交接类型
2. 提炼最小必要上下文
3. 收敛真正影响下一步的材料
4. 标注事实边界
5. 输出摘要 + 可执行提示词

## Quick Start

1. 把 `task-handoff` 文件夹复制到本地 skills 目录
2. 如有需要，重启 Claude Code / Cursor
3. 直接让模型把当前任务整理成交接提示词

## 安装方式

把这个文件夹复制到本地 skills 目录即可。

### Claude Code

```bash
cp -R task-handoff ~/.claude/skills/
```

### Cursor / Codex 风格目录

```bash
cp -R task-handoff ~/.cursor/skills/
```

## 使用方式

### 自然语言触发

```text
请把当前任务整理成一个交接提示词，给另一个 agent 接手。
```

```text
整理一下当前上下文，生成一个接手继续做的 handoff prompt。
```

### Skill 命令

```text
/task-handoff
```

## 示例 Prompt

- `Create a handoff package for this unfinished bug investigation.`
- `Summarize the current worktree status and produce a prompt for the next agent.`
- `不要从零分析，帮我把当前进度整理成可直接接手的 handoff prompt。`
- `Prepare a concise handoff for remote ops acceptance, including host, service, logs, and next verification step.`

## 项目结构

```text
task-handoff/
├── SKILL.md        # Skill 行为与工作流定义
├── template.md     # 默认交接模板
├── README.md       # 英文说明
├── README_CN.md    # 中文说明
├── CONTRIBUTING.md # 贡献指南
├── SECURITY.md     # 安全披露方式
└── LICENSE         # MIT 许可证
```

## 设计原则

- **可执行性优先，不追求历史完整复述**
- **对新会话友好**
- **精确事实优于模糊总结**
- **不要把“已经做了什么”和“接下来该做什么”混在一起**
- **上下文尽量小，但下一步必须清楚**

## 推荐 Agent 提示词写法

当你希望模型停止继续污染当前会话，而是转为准备交接包时，可以直接这样说：

```text
Use the task-handoff skill.
Compress the current state into:
1. a short handoff summary
2. a complete handoff prompt
Clearly separate confirmed facts, unverified items, next steps, and things that must not be changed.
```

## 贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 安全

见 [SECURITY.md](SECURITY.md)。

## 许可证

[MIT](LICENSE) © 2026 Mileson

## 作者
- X: [Mileson07](https://x.com/Mileson07)
- 小红书: [超级峰](https://xhslink.com/m/4LnJ9aB1f97)
- 抖音: [超级峰](https://v.douyin.com/rH645q7trd8/)
