---
name: agent-team-research
description: |
  启动多 Agent 协作进行复杂调研任务。适用于需要多角度分析、交叉验证、专业评审的场景。

  触发条件：
  (1) 需要多角度分析的问题（产品/技术/UX/市场等视角）
  (2) 需要 Peer Review 或交叉验证的决策
  (3) 复杂产品的设计探索和方案评估
  (4) 技术方案选型和可行性评估
  (5) 组建评议委员会评估多个方案

  触发词：调研团队、多角度分析、Agent Team、评议委员会、方案评估、交叉验证
user-invocable: true
---

# Agent Team 调研模式

启动多 Agent 协作进行复杂调研任务，提供三种协作模式适应不同场景。

## 快速选择模式

| 场景 | 推荐模式 | 核心优势 |
|------|----------|----------|
| 产品决策、时间敏感 | **集中调度** | 产出完整、质量稳定 |
| 体验优化、专业深度 | **领域主导** | 专业视角、深度分析 |
| 探索性、创新性任务 | **对等协作** | 多角度、创新性 |

## 模式详解

### 模式 1：集中调度（推荐默认）

**适用**：产品决策、时间敏感任务、需要完整产出

**角色配置**：
- **Coordinator**：协调员，分配任务、整合结果
- **Researcher N**：研究员，各自独立研究不同维度

**工作流**：
```
1. Coordinator 创建团队，定义调研目标
2. 并行生成多个 Researcher（产品/技术/UX/市场等）
3. Researcher 独立完成各自维度的研究
4. Coordinator 收集结果，整合为完整报告
5. 关闭团队，输出最终报告
```

**详细说明**：见 [references/centralized-mode.md](references/centralized-mode.md)

---

### 模式 2：领域主导

**适用**：体验优化、专业性强的任务、需要领域专家深度参与

**角色配置**：
- **Domain Lead**：领域专家，主导调研方向和决策
- **Supporter N**：支持角色，响应主导者需求

**工作流**：
```
1. Domain Lead 创建团队，定义专业需求
2. 生成 Supporters（技术支持/批判分析等）
3. Domain Lead 调度 Supporters 进行专业分析
4. Supporters 向 Domain Lead 汇报
5. Domain Lead 整合输出最终方案
```

**详细说明**：见 [references/domain-led-mode.md](references/domain-led-mode.md)

---

### 模式 3：对等协作

**适用**：探索性任务、创新场景、需要多角度碰撞

**角色配置**：
- **Peer N**：对等角色，各自负责专业领域，地位平等
- **可选：Facilitator**：协调分歧（需要时）

**工作流**：
```
1. 创建共享画布（Markdown 文件）
2. 各 Peer 并行填写自己的专业 section
3. 在辩论区进行结构化辩论（质疑→回应→裁决）
4. 达成共识或由 PM 裁决
5. 输出共识方案
```

**详细说明**：见 [references/peer-collab-mode.md](references/peer-collab-mode.md)

---

## 评议委员会模式（评估专用）

**适用**：评估多个方案、做出最终决策

**角色配置**：
```
Chair（主席）
  ├── Product Judge（产品评委）
  ├── Tech Judge（技术评委）
  └── UX Judge（用户体验评委）
```

**工作流**：
```
1. 各评委独立阅读方案并打分（1-10）
2. 向 Chair 汇报评分和理由
3. Chair 主持讨论，解决分歧
4. Chair 汇总结果，宣布最终排名
5. 输出评估报告
```

**示例**：见 [examples/evaluation-demo.md](examples/evaluation-demo.md)

---

## 使用示例

### 示例 1：产品调研

```
用户：我要设计一个 CLI 工具，创建调研团队从产品、技术、UX 三个角度分析

→ 使用【集中调度模式】
→ Coordinator 创建 3 个 Researcher：product-researcher, tech-researcher, ux-researcher
→ 各自独立研究后，Coordinator 整合报告
```

### 示例 2：方案评估

```
用户：评估这三个设计方案的优劣，选出最佳的

→ 使用【评议委员会模式】
→ 创建 Chair + 3 个 Judge
→ 独立评分 → 讨论 → 宣布结果
```

### 示例 3：探索性设计

```
用户：探索这个产品的设计方向，需要多角度碰撞

→ 使用【对等协作模式】
→ 创建共享画布 + PM/Designer/Engineer/Critic
→ 各自填写 → 结构化辩论 → 共识输出
```

更多示例：见 [examples/](examples/) 目录

---

## 输出模板

调研完成后，使用 [templates/research-report.md](templates/research-report.md) 生成标准化报告。

---

## 最佳实践

### DO ✅

1. **明确目标**：创建团队前，清晰定义调研目标
2. **选择合适模式**：根据任务类型选择协作模式
3. **合理分工**：每个 Agent 职责清晰，避免重叠
4. **设置同步点**：定期检查进度，及时调整
5. **记录决策**：重要决策记录在报告或画布中

### DON'T ❌

1. **过度分工**：Agent 数量不要超过 5 个
2. **模糊职责**：每个 Agent 必须有明确的职责边界
3. **忽略协调**：即使是模式 3，也需要机制解决分歧
4. **过早关闭**：确保所有 Agent 完成工作后再关闭团队
