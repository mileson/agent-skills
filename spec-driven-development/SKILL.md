---
name: spec-driven-development
argument-hint: "[项目描述/需求说明] 例如: 做一个电商平台 | 在现有系统上新增XX功能"
description: |
  基于 Spec 驱动的复杂功能开发 Skill，支持两种模式：
  
  **模式1 - 从0到1全新项目开发 (Greenfield)**：
  先做产品定位与需求澄清，再初始化 `/Documentation`，输出 `Basic / Framework / Modules / DevLogs` 四层文档资产。
  
  **模式2 - 基于已有系统的迭代优化 (Brownfield)**：
  先读取现有文档并输出“产品定位审计摘要”，确认新需求与现有定位的关系后，再更新主文档与执行跟踪。
  
  **文档驱动原则**：
  产品业务优先由用户深度梳理，Agent 基于业务文档继续生成稳定的数据建模、架构设计、技术规格、技术逻辑与技术选型，保证后续开发可参考、可落地。
  业务模块采用双文档模型：`模块需求文档 + 模块技术文档`。偏业务的 ASCII 和 Mermaid 流程放需求文档，偏技术的状态/关系/流程图放技术文档。
  
  **执行跟踪**：
  不再默认维护 `feature_list.json + PROGRESS.md` 双文件，统一收敛到版本化主文档与 TODO 分片，例如：
  `Documentation/DevLogs/v1.0_执行跟踪.md`
  `Documentation/DevLogs/v1.0_TODO_01.md`
  
  **触发场景**：
  (1) 用户说"我想做一个XX系统"、"从0到1开发"、"新项目"
  (2) 用户说"优化XX功能"、"在现有系统上新增XX"、"系统迭代"、"v2.0开发"
  (3) 用户说"需求沟通"、"需求拆解"、"长任务开发"
  (4) 用户请求生成 PRD、技术方案、开发计划
  (5) 复杂的多模块功能开发（跨多个迭代）

allowed-tools: ["Shell", "Read", "Write", "StrReplace", "Glob", "Delete"]

hooks:
  PostToolUse:
    - matcher: "Write|StrReplace"
      hooks:
        - type: command
          command: |
            if echo "$tool_input" | grep -Eq '"path".*"(Documentation/|doc/)'; then
              doc_dir="Documentation"
              if echo "$tool_input" | grep -q '"path".*"doc/'; then
                doc_dir="doc"
              fi
              python3 "$CLAUDE_PROJECT_DIR/.cursor/skills/spec-driven-development/scripts/check_doc_size.py" \
                --doc-path "$CLAUDE_PROJECT_DIR/$doc_dir" \
                --warn 400 \
                --max 500 2>/dev/null || true
            fi
          timeout: 10
---

# Spec-Driven Development Skill

基于文档、规范、问题方案、轻量评估和回写闭环驱动的复杂开发 Skill，适用于 Greenfield 和 Brownfield 两类场景。

## 核心原则

1. 产品业务优先：用户负责深度梳理产品目标、业务规则、业务场景和验收边界。
2. Agent 负责技术落地：Agent 基于业务文档继续生成数据建模、系统架构、技术规格、技术逻辑与技术选型。
3. 文档先于开发：先形成稳定的模块需求文档与模块技术文档，再进入任务拆解和编码执行。
4. TODO 顺序执行：最终必须形成穷尽业务与技术范围的版本化 TODO 清单，按明确先后顺序推进长程任务。

## 核心结构

```text
Documentation/
├── Basic/
├── Framework/
│   ├── Standards/
│   ├── CommonCapabilities/
│   └── ProblemSolutions/
├── Modules/
│   └── <模块名>/
│       ├── <模块名>_README.md
│       ├── <模块名>_需求文档.md
│       └── <模块名>_技术文档.md
└── DevLogs/
    ├── v1.0_执行跟踪.md
    └── v1.0_TODO_01.md
```

### 分层职责

- `Basic/`：系统级基础共识，不承载模块页面级细节
- `Framework/Standards/`：项目级规范与范式
- `Framework/CommonCapabilities/`：跨模块通用能力
- `Framework/ProblemSolutions/`：历史坑、反模式、标准解法
- `Modules/`：模块级知识闭环
- `DevLogs/`：版本化执行跟踪、TODO 分片与错误日志

### 文件夹说明书命名规则

- 不再生成通用 `README.md`
- 所有目录说明文档统一使用“文件夹前缀 + `_README.md`”
- 例如：
  - `Basic/Basic_README.md`
  - `Basic/PRD/PRD_README.md`
  - `Framework/CommonCapabilities/CommonCapabilities_README.md`
  - `Modules/<模块名>/<模块名>_README.md`

### 文件夹说明书格式

所有文件夹说明文档统一采用 `Folder Manual` 结构，至少包含：

1. 核心功能 (Core Function)
2. 输入 (Input)
3. 输出 (Output)
4. 定位 (Position)
5. 依赖 (Dependency)

## 双模式智能切换

Skill 自动检测项目模式：

- **Greenfield**：无 `/Documentation`，或仅存在 v1.0 初始文档骨架
- **Brownfield**：存在 `/Documentation` 且已有正式文档或历史修订
- **兼容规则**：旧项目若使用 `doc/`，脚本层继续兼容读取，但新项目统一使用 `/Documentation`

## 需求沟通总原则

### 禁止行为

- 用户一提需求就直接写文档
- 先运行 `init_project_structure.py` 再补问问题
- 在高歧义状态下直接生成 PRD / Mermaid / ASCII

### 每轮访谈固定呈现规则

每轮面向用户的输出必须遵守：

1. 先给简短的当前理解摘要
2. 再列出已确认内容
3. 再列出仍需用户确认的点
4. 最后再输出“本轮问题清单”
5. 问题清单必须放在消息最后，并使用代码块包裹，方便用户集中阅读和逐条回答

### 禁止的用户侧输出

以下内容属于 Agent 内部判断，不直接展示给用户：

- `是否允许进入下一轮：conditional / pass / fail`
- `当前歧义等级：高 / 中 / 低`
- `当前风险等级：高 / 中 / 低`
- 任何只对 Agent 推进有意义、但不要求用户配合的内部状态标签

这些信息可以在 Agent 内部用于门禁判断，但不应直接抛给用户。

### 推荐的用户侧输出顺序

1. 当前理解摘要
2. 已确认内容
3. 仍需你确认的点
4. ASCII / Mermaid 草图（如当前轮需要）
5. 本轮问题清单（代码块，放在最后）

### 本轮问题清单格式

问题清单数量规则：

- 每轮最多 5 个问题
- 推荐 3-5 个问题
- 如果剩余问题超过 5 个，必须按优先级拆到下一轮
- 优先问最影响方向判断、边界判断和验收判断的问题

不要为了“一次问全”而堆长清单，降低用户回答负担。

```text
请你按顺序回答下面这些问题：

1. ...
2. ...
3. ...
```

## 模式1：Greenfield

### 阶段1：需求沟通

先完成 4 轮访谈，再允许初始化 `Documentation/`。

#### Round 1：产品定位访谈（战略层 / 范围层 / 交互认知预判）

融合《用户体验五要素》的：

- 战略层
- 范围层
- 结构层预判

如需求涉及交互、页面、流转，还必须应用《Don’t Make Me Think》的认知负担原则，追问：

- 用户是否一眼知道下一步做什么
- 页面最重要的信息是否清楚
- 命名是否自解释
- 核心路径是否最短
- 哪些地方最容易让用户困惑或误操作
- 失败后恢复路径是否清楚

#### Round 2：目标 / 边界 / 验收访谈

问清：

- 首版真正要解决什么
- 明确不做什么
- 哪些边界不能碰
- 什么叫成功

#### Round 3：业务场景循环访谈

至少覆盖：

- 主成功场景
- 关键分支场景
- 异常场景
- 边界场景

#### Round 4：业务场景流程澄清

每个关键流程必须覆盖：

- 前置条件
- 触发动作
- 主流程
- 分支流程
- 异常流程
- 结束状态
- 用户可见反馈

#### 放行门禁

只有以下内容清楚后，才允许初始化 `Documentation/`：

- 产品定位清楚
- 用户群体清楚
- 典型场景清楚
- 首版目标清楚
- 首版边界清楚
- 验收标准清楚
- 至少 3 个关键业务场景走通
- 至少 1 个关键异常流程走通
- 如涉及交互，核心认知路径已初步澄清

### 阶段2：架构设计

输出：

- `Documentation/Basic/Architecture/1_技术选型.md`
- `Documentation/Basic/Architecture/2_系统架构.md`
- `Documentation/Basic/Architecture/3_交互时序图.md`
- `Documentation/Basic/UI/1_信息架构总览.md`

同时完成核心模块双文档：

- `Documentation/Modules/<模块名>/<模块名>_需求文档.md`
- `Documentation/Modules/<模块名>/<模块名>_技术文档.md`

#### ASCII / Mermaid 职责

- `Basic/PRD/1_产品概述.md`：产品级 ASCII 草图
- `Basic/UI/1_信息架构总览.md`：全局信息架构 / 全局导航 / 全局交互规范
- 模块需求文档：业务场景流程（Mermaid）+ 业务 ASCII
- 模块技术文档：技术流程 / 状态 / 关系图

### 阶段3：执行跟踪与 TODO 初始化

初始化版本化执行跟踪文档与首个 TODO 分片：

- `Documentation/DevLogs/v1.0_执行跟踪.md`
- `Documentation/DevLogs/v1.0_TODO_01.md`

其中：

- `执行跟踪.md`：只维护总体状态、当前 TODO 分片、当前任务指针、阶段进展和回写记录
- `TODO_01.md / TODO_02.md ...`：维护详细任务清单

#### TODO 任务清单规则

- 每个 `TODO.md` 最多 30 个任务
- 若任务超过 30 个，必须继续拆成：
  - `v1.0_TODO_01.md`
  - `v1.0_TODO_02.md`
  - `v1.0_TODO_03.md`
- 任务必须显式编号，例如：
  - `TODO-001`
  - `TODO-002`
  - `TODO-003`
- 任务必须按前后顺序排列
- 任务依赖只能依赖更早编号的任务，禁止交叉依赖、循环依赖和未来依赖
- 每条任务必须形成最小闭环，能够被 Agent 独立执行与验收

### 阶段4：开发执行

开发前必须完成：

- 读取来源文档
- 确认受影响模块
- 确认是否命中 `CommonCapabilities`
- 高风险任务确认是否命中 `ProblemSolutions`
- 读取当前版本执行跟踪文档与当前 TODO 分片

执行时必须遵守：

- 从当前未完成的最小编号任务开始执行
- 完成 `TODO-001` 后再推进 `TODO-002`
- 当前 `TODO_01.md` 完成后，再进入 `TODO_02.md`
- 不允许跳过前置任务直接实现后续任务
- 每完成一条任务，都要同步更新任务状态和执行跟踪文档中的当前指针

编码完成后必须：

- 更新模块技术文档
- 追加修订历史
- 更新版本执行跟踪文档
- 必要时沉淀到 `CommonCapabilities` 或 `ProblemSolutions`

## 模式2：Brownfield

### 阶段0：读取现有文档

必须先读取：

- `Basic` 中的定位、流程、边界
- 相关模块需求文档
- 相关模块技术文档
- 当前版本执行跟踪文档
- 必要时 `CommonCapabilities / ProblemSolutions`

### 阶段0.5：产品定位审计摘要

在正式提问前，必须先输出：

```text
当前产品定位（基于现有文档）
- 当前产品核心目标：
- 当前主要用户群体：
- 当前核心场景：
- 当前版本边界：
- 当前相关模块：
- 当前已知约束：

本次新需求的初步理解
- 你新提的需求是：
- 我判断它更像：
  - 定位延伸
  - 定位变更
  - 单模块增强
  - 跨模块变更

潜在冲突点
- 与现有定位一致的地方：
- 与现有定位可能冲突的地方：
- 需要你确认是否变化的地方：
```

用户必须先确认：

- 现有定位是否仍成立
- 这次需求是扩展还是定位变化
- 哪些旧边界本次要打破

### 阶段1：增量需求沟通

同样采用 4 轮协议，但聚焦增量：

1. 定位变化确认
2. 增量目标 / 边界 / 验收访谈
3. 增量场景循环访谈
4. 增量流程澄清

#### 放行门禁

只有以下内容清楚后，才允许更新主文档：

- 当前定位已审计
- 用户已确认定位是否变化
- 本次变更范围清楚
- 受影响边界清楚
- 受影响场景清楚
- 受影响流程清楚
- 本次验收标准清楚

### 阶段2：增量设计与回写

按双文档模型更新受影响模块：

- 更新模块需求文档中的业务场景 / 业务流程 / 业务 ASCII / 验收标准
- 更新模块技术文档中的需求映射 / 架构 / 数据 / Contract / 实施现状 / 代码同步说明

如有需要，补充：

- `Framework/CommonCapabilities/`
- `Framework/ProblemSolutions/`

### 阶段3：版本执行跟踪与 TODO 更新

在当前版本执行跟踪文档中追加：

- 新增任务
- 变更范围
- 风险与阻塞
- 文档回写记录

并同时生成或更新当前版本的 TODO 分片：

- `Documentation/DevLogs/v2.0_TODO_01.md`
- 如超过 30 个任务，继续拆为 `v2.0_TODO_02.md`、`v2.0_TODO_03.md`

要求：

- 所有任务必须按先后顺序编号
- 所有依赖必须指向更早任务
- 禁止把一个任务写成“依赖多个未完成大任务”的交叉结构
- 优先拆成 Agent 可连续执行的线性闭环

### 阶段4：开发执行

与 Greenfield 相同，但必须先完成定位审计和差异确认。

## 模块双文档模型

### 模块需求文档

必须至少包含：

1. 模块概览卡
2. 业务背景
3. 目标用户与产品定位
4. 业务场景
5. 业务场景流程（Mermaid）
6. 功能需求
7. 业务规则
8. 业务 ASCII 交互稿
9. 验收标准
10. 边界与待确认项

### 模块技术文档

必须至少包含：

1. 模块说明书 (Module Manual)
2. 需求映射
3. 系统架构
4. 数据 / 状态模型
5. Contract / API / 事件
6. 技术流程设计
7. 异常与补偿
8. 实施现状
9. 测试设计
10. FAQ / 检查清单 / 代码同步说明 / 附录

## 轻量交叉验证

只保留 3 条核心对照链：

1. 模块需求文档 -> 模块技术文档
2. 模块需求文档 -> 版本 TODO 清单
3. 模块技术文档 -> 修订历史 / 代码同步说明

## 轻量 Evaluation

每阶段结束都要输出：

- 是否可放行
- 当前歧义等级
- 当前风险等级
- 进入下一阶段前必须解决的问题

评估维度：

1. 完整性
2. 清晰度
3. 可落地性
4. 可验证性

放行结论：

- `pass`
- `conditional`
- `fail`

## 轻量 Correction

偏差出现后至少要：

1. 判断是需求偏差 / 设计偏差 / 实现偏差
2. 更新对应文档
3. 追加修订历史
4. 更新对应版本执行跟踪文档
5. 更新对应版本 TODO 清单
6. 必要时沉淀到 `ProblemSolutions` 或 `CommonCapabilities`

## 关键脚本

- `scripts/detect_project_mode.py`：检测 Greenfield / Brownfield
- `scripts/init_project_structure.py`：初始化 v3 文档骨架
- `scripts/read_existing_docs.py`：读取现有文档
- `scripts/generate_context_report.py`：生成上下文报告
- `scripts/query_doc_context.py`：查询项目 / 模块 / 能力 / 问题方案上下文
- `scripts/suggest_doc_updates.py`：代码变更后的文档回写建议
- `scripts/generate_revision_history_draft.py`：生成修订历史草案
- `scripts/validate_doc_completeness.py`：验证 v3 文档完整性

## 参考资料

- `references/greenfield/stage1-requirement-comm.md`
- `references/greenfield/stage2-design.md`
- `references/brownfield/stage1-incremental-requirement.md`
- `references/brownfield/stage0-read-existing-docs.md`
- `references/advanced-practices.md`

## 实施顺序

1. 需求沟通规则升级
2. 模块双文档模型落地
3. ASCII 职责迁移
4. 执行跟踪收敛为版本化单文档
5. 交叉验证收敛为 3 条链
6. Evaluation 与 Correction 轻量闭环落地
