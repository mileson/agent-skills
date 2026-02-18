# 领域主导模式

> 适用场景：体验优化、专业性强的任务、需要领域专家深度参与

## 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    领域主导模式                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    ┌─────────────┐                          │
│                    │ Domain Lead │ ← 领域专家主导            │
│                    │   (UX/产品)  │   调度支持角色            │
│                    └──────┬──────┘                          │
│                           │ 调度需求                         │
│         ┌─────────────────┼─────────────────┐               │
│         │                 │                 │               │
│    ┌────┴────┐       ┌────┴────┐       ┌────┴────┐          │
│    │  Tech   │       │ Critic  │       │ Support │          │
│    │Supporter│       │Supporter│       │Supporter│          │
│    │(听命)   │       │(听命)   │       │(听命)   │          │
│    └─────────┘       └─────────┘       └─────────┘          │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           ▼ 汇报                            │
│                    ┌─────────────┐                          │
│                    │  Domain Lead │ ← 整合输出               │
│                    └─────────────┘                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 领域专家类型

| 领域 | Domain Lead | Supporters |
|------|-------------|------------|
| UX 设计 | ux-lead | tech-supporter, critic |
| 技术架构 | architect | feasibility-checker, risk-analyzer |
| 产品定义 | pm | market-researcher, competitor-analyst |
| 数据分析 | data-lead | data-engineer, visualization-expert |

## 实施步骤

### Step 1: 创建团队 + Domain Lead

```
TeamCreate
├── team_name: "{project}-{domain}-led"
└── description: "领域主导调研"

Task (Domain Lead)
├── name: "{domain}-lead"
└── prompt: 包含调度权限说明
```

### Step 2: Domain Lead 生成 Supporters

Domain Lead 根据需求，使用 Task 工具生成 Supporters。

### Step 3: Supporters 响应需求

Supporters 等待 Domain Lead 的指令，完成后向 Domain Lead 汇报。

### Step 4: Domain Lead 整合输出

Domain Lead 整合 Supporters 的分析，形成最终方案。

## 关键配置

Domain Lead 的 prompt 必须包含：

```markdown
## 你的调度权限

你可以使用 SendMessage 工具：
- 给 supporter-a 发送消息：分配任务
- 给 supporter-b 发送消息：分配任务

## 工作流程
1. 先完成你的专业分析
2. 然后调度 Supporters
3. 收集反馈，整合输出
4. 向 team-lead 汇报
```

## 优缺点

| 优点 | 缺点 |
|------|------|
| 专业深度 | Domain Lead 瓶颈 |
| 责任明确 | Supporters 被动 |
| 适合专业任务 | 可能缺乏多角度碰撞 |

## 最佳实践

1. **Domain Lead 选择**：选择最核心的领域专家
2. **Supporters 数量**：2-3 个，不宜过多
3. **明确主从关系**：Supporters 明确"听命于 Domain Lead"
4. **定期检查**：team-lead 需要检查 Domain Lead 进度
