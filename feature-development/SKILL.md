---
name: feature-development
description: |
  长时间复杂功能开发 Skill，支持两种模式：
  
  **模式1 - 从0到1全新项目开发 (Greenfield)**：
  完整需求沟通（6维度PRD）→ 架构设计 → 数据库设计 → API设计 → 任务拆解 → 开发执行。
  生成完整的文档结构（doc/），包含 PRD、架构、数据库、API、测试设计。
  
  **模式2 - 基于已有系统的迭代优化 (Brownfield)**：
  读取现有文档（PRD/架构/数据库/API）→ 生成现有系统上下文报告 → 增量需求沟通 → 
  增量架构设计（兼容性评估）→ 数据库变更DDL（ALTER TABLE）→ 任务合并 → 开发执行。
  生成增量文档（v2.0），更新文档修订历史。
  
  **长任务可持续性**：
  基于 Anthropic 长任务最佳实践，使用 feature_list.json（含 checkpoint）+ 
  PROGRESS.md + Git history 追踪进度。支持从任意检查点恢复。
  
  **错误处理**：
  生成 JSON 格式错误日志，包含任务上下文和堆栈跟踪。
  
  **测试标准**：
  遵循测试金字塔（80% 单元测试、15% 集成测试、5% E2E 测试），
  强制端到端测试通过。
  
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
            if echo "$tool_input" | grep -q '"path".*"doc/'; then
              python3 "$CLAUDE_PROJECT_DIR/.cursor/skills/feature-development/scripts/check_doc_size.py" \
                --doc-path "$CLAUDE_PROJECT_DIR/doc" \
                --warn 400 \
                --max 500 2>/dev/null || true
            fi
          timeout: 10
---

# Feature Development Skill

长时间复杂功能开发 Skill，支持从0到1全新项目开发和基于已有系统的迭代优化。

## 核心能力

### 双模式智能切换

Skill 自动检测项目模式：
- **模式1 (Greenfield)**：无 `doc/` 目录 → 从0到1全新项目开发
- **模式2 (Brownfield)**：有 `doc/` 目录 → 基于已有系统的迭代优化

### 四个核心阶段

无论哪种模式，开发过程都分为 4 个阶段（模式2 额外增加阶段0）：

1. **阶段1: 需求沟通** - 多维度提问框架，生成详细 PRD
2. **阶段2: 架构设计** - 技术选型、系统架构、数据库、API 设计
3. **阶段3: 任务拆解** - 生成 feature_list.json，按 Phase 组织任务
4. **阶段4: 开发执行** - Initializer Agent + Coding Agent 循环

模式2 额外增加：
- **阶段0: 读取现有文档** - 理解现有系统，生成上下文报告

## 工作流程

### 启动时

1. **运行模式检测**:
   ```bash
   python3 scripts/detect_project_mode.py
   ```
   
2. **根据检测结果选择工作流**:
   - 模式1: 阅读 `references/greenfield/` 下的指南
   - 模式2: 阅读 `references/brownfield/` 下的指南

### 模式1: 从0到1全新项目开发

**阶段1: 需求沟通**
- 参考: `references/greenfield/stage1-requirement-comm.md`
- 使用多维度提问框架（6个维度）
- 生成完整 PRD（产品概述、用户画像、核心流程、边界场景、商业模式、运营模式）
- 每个维度逐一审查确认

**阶段2: 架构设计**
- 参考: `references/greenfield/stage2-design.md`
- 生成技术选型（前后端技术栈、第三方服务、部署平台）
- 生成系统架构（分层架构、模块划分）
- 生成数据库设计（表结构、建表SQL、索引设计）
- 生成 API 设计（RESTful API、错误码定义）
- 逐个审查确认
- **部署询问**: 架构设计确认后，询问部署需求
  - 参考: `references/deployment/platform-options.md`
  - 询问后端部署: Supabase / 自行部署
  - 询问前端部署: Vercel / Netlify / 自行部署
  - 收集部署凭证: 参考 `references/deployment/credentials-checklist.md`
- **集成询问**: 询问第三方服务集成需求
  - 参考: `references/integrations/index.md`
  - OAuth 集成: X/Twitter、GitHub、Google 等
  - 支付集成: Stripe、支付宝、微信支付
  - 通知集成: SendGrid、Twilio 等

**阶段3: 任务拆解**
- 参考: `references/greenfield/stage3-task-decomposition.md`
- 运行 `scripts/generate_feature_list.py`
- 生成 feature_list.json（按 Phase 组织，包含 checkpoint）
- 用户确认任务拆解

**阶段4: 开发执行**
- 参考: `references/greenfield/stage4-coding.md`
- Initializer Agent 初始化环境（init.sh、Git 基线）
- Coding Agent 循环实现功能（读取 progress → 实现 → 测试 → 提交 → 更新 progress）
- 使用 `scripts/checkpoint_manager.py` 管理检查点
- 使用 `scripts/handle_agent_error.py` 处理错误

### 模式2: 基于已有系统的迭代优化

**阶段0: 读取现有文档**
- 参考: `references/brownfield/stage0-read-existing-docs.md`
- 运行 `scripts/detect_project_mode.py` 检测现有文档
- 运行 `scripts/read_existing_docs.py` 智能读取现有文档
- 运行 `scripts/generate_context_report.py` 生成系统上下文报告
- 向用户展示上下文报告，确认理解准确性

**阶段1: 增量需求沟通**
- 参考: `references/brownfield/stage1-incremental-requirement.md`
- 基于现有 PRD 提问（使用增量提问框架）
- 生成增量 PRD v2.x（继承现有内容，只编写新增/变更部分）
- 更新文档修订历史
- 用户审查确认

**阶段2: 增量架构设计**
- 参考: `references/brownfield/stage2-incremental-design.md`
- 兼容性评估（新功能是否与现有架构冲突）
- 生成增量技术方案（新增模块、现有模块变更）
- 运行 `scripts/generate_database_ddl.py` 生成数据库变更 DDL
- 生成 API 变更设计（新增端点、修改现有 API）
- 用户审查确认
- **部署询问**: 如涉及新服务，询问部署需求
  - 参考: `references/deployment/platform-options.md`
- **集成询问**: 如涉及新第三方服务，询问集成需求
  - 参考: `references/integrations/index.md`

**阶段3: 增量任务拆解**
- 参考: `references/brownfield/stage3-merge-tasks.md`
- 运行 `scripts/merge_feature_list.py` 合并任务到 feature_list.json
- 标记新 Phase + 版本号
- 标记依赖关系（baseFeatures）
- 用户确认

**阶段4: 开发执行**
- 与模式1 相同，参考 `references/brownfield/stage4-coding.md`

## 参考资料

### 阶段性指南

- **Greenfield 模式**: `references/greenfield/stage1-4.md`（4 个阶段）
- **Brownfield 模式**: `references/brownfield/stage0-4.md`（5 个阶段，含阶段0）
- **测试标准**: `references/testing/test-pyramid.md`, `coverage-standards.md`

### 深度学习

- **高级实践（测试、异步任务、代码审查）**: `references/advanced-practices.md`
- **文档粒度控制（拆分策略）**: `references/doc-granularity.md`

### 部署与集成

- **部署平台选项**: `references/deployment/platform-options.md`
- **部署凭证清单**: `references/deployment/credentials-checklist.md`
- **第三方集成总览**: `references/integrations/services-overview.md`
- **X/Twitter OAuth**: `references/integrations/x-twitter-oauth.md`

### 示例模板

- **环境变量模板**: `examples/env-template.md`
- **部署指南示例**: `examples/deployment-guide.md`

## 核心脚本

### 模式检测与初始化

- `scripts/detect_project_mode.py` - 检测项目模式（Greenfield/Brownfield）
- `scripts/init_project_structure.py` - 初始化文档结构（模式1）

### 模式2 专用脚本

- `scripts/read_existing_docs.py` - 智能读取现有文档
- `scripts/generate_context_report.py` - 生成系统上下文报告
- `scripts/merge_feature_list.py` - 合并功能清单
- `scripts/generate_database_ddl.py` - 生成数据库变更 DDL

### 通用脚本

- `scripts/generate_feature_list.py` - 生成功能清单（模式1）
- `scripts/validate_doc_completeness.py` - 验证文档完整性
- `scripts/check_doc_size.py` - 检查文档行数（警告/错误/拆分建议）
- `scripts/handle_agent_error.py` - 错误处理（JSON 格式）
- `scripts/checkpoint_manager.py` - 检查点管理

## 模板文件

### 模式1 模板

- `templates/greenfield/feature_list_template.json` - 功能清单模板
- `templates/greenfield/claude-progress_template.txt` - 进度文件模板

### 模式2 模板

- `templates/brownfield/context_report_template.md` - 系统上下文报告模板

## 重要规则

### 用户审查确认

每个阶段完成后，必须向用户展示生成的文档，等待用户审查确认后才能进入下一阶段。

### 文档版本管理

模式2 生成的文档必须包含文档修订历史表格（借鉴 nn-gene）：

```markdown
## 文档修订历史

| 版本 | 日期 | 修订人 | 修订内容 |
|------|------|--------|----------|
| v1.0 | 2025-10-10 | 产品团队 | 初始版本 |
| v2.0 | 2026-02-04 | AI Agent | 新增智能推荐功能 |
```

### 错误处理

任何错误都必须使用 `scripts/handle_agent_error.py` 生成 JSON 格式错误日志。

### 测试标准

遵循测试金字塔（80% 单元测试、15% 集成测试、5% E2E 测试），端到端测试必须通过。

## 使用示例

### 示例1: 从0到1开发新项目

```
用户: "我想做一个电商平台"
Agent: 
1. 检测到无 doc/ 目录，进入模式1
2. 阶段1：需求沟通（6个维度提问）
3. 生成完整 PRD → 用户审查
4. 阶段2：架构设计
5. 生成技术方案 → 用户审查
6. 阶段3：任务拆解
7. 生成 feature_list.json → 用户确认
8. 阶段4：开发执行
```

### 示例2: 基于已有系统迭代

```
用户: "在现有电商平台上新增智能推荐功能"
Agent:
1. 检测到有 doc/ 目录，进入模式2
2. 阶段0：读取现有文档，生成上下文报告 → 用户确认理解
3. 阶段1：增量需求沟通
4. 生成增量 PRD v2.0 → 用户审查
5. 阶段2：增量架构设计
6. 生成数据库变更 DDL、API 变更设计 → 用户审查
7. 阶段3：增量任务拆解
8. 合并到 feature_list.json → 用户确认
9. 阶段4：开发执行
```

### 示例3: 带部署和集成的新项目

```
用户: "我想做一个社交应用，支持 X 登录"
Agent:
1. 检测到无 doc/ 目录，进入模式1
2. 阶段1：需求沟通（6个维度提问）
3. 生成完整 PRD → 用户审查
4. 阶段2：架构设计
5. 生成技术方案 → 用户审查
6. 部署询问：
   - "是否需要部署后端？" → 是 → "选择 Supabase"
   - "是否需要部署前端？" → 是 → "选择 Vercel"
   - 收集 Supabase 凭证和 Vercel Token
7. 集成询问：
   - "需要 X OAuth 登录吗？" → 是
   - 收集 X Client ID、Client Secret、Callback URL
8. 生成环境变量模板 → 参考 examples/env-template.md
9. 阶段3：任务拆解（含部署任务）
10. 阶段4：开发执行
```

## 最佳实践

### 需求沟通阶段

- 使用多维度提问框架，不遗漏关键问题
- 每个维度逐一审查，确保充分理解
- 模式2 需聚焦增量需求，避免重复现有内容

### 架构设计阶段

- 技术选型要考虑团队技术栈和项目复杂度
- 数据库设计要考虑性能和扩展性
- API 设计要保持一致性（模式2 尤其重要）

### 任务拆解阶段

- 任务粒度适中（单个功能 1-3 天完成）
- 明确任务依赖关系
- 按 Phase 组织，便于里程碑管理

### 开发执行阶段

- 端到端测试强制通过
- 每个功能完成后立即提交 Git
- 及时更新 PROGRESS.md
- 遇到错误立即生成错误日志

## 故障排查

### 模式检测失败

如果 `scripts/detect_project_mode.py` 检测失败，检查：
- `doc/` 目录是否存在
- `doc/` 目录是否有权限访问

### 读取现有文档失败（模式2）

如果 `scripts/read_existing_docs.py` 读取失败，检查：
- 文档格式是否符合规范（Markdown）
- 文档是否可读

### 功能清单合并失败（模式2）

如果 `scripts/merge_feature_list.py` 合并失败，检查：
- 现有 feature_list.json 格式是否正确
- 新功能的 Phase 编号是否冲突

## 核心设计原则

### Anthropic 长任务最佳实践

基于 [Anthropic 工程博客](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)，我们实现了以下机制：

1. **Feature List**: `feature_list.json`，包含所有功能清单
   - 每个 feature 有 `status` 字段（pending/in_progress/completed）
   - 支持 Phase 组织，便于里程碑管理
   - 包含依赖关系（dependencies）

2. **Progress File**: `PROGRESS.md`，记录每个 session 的工作
   - 结构化格式（时间戳、完成的功能、Git commit、测试结果）
   - 独立的错误记录章节

3. **Git History**: 强制 Git commit，描述性提交信息
   - 每个功能完成后立即提交
   - 提交信息格式：`feat: 功能描述` 或 `fix: 修复描述`

4. **init.sh/init_project_structure.py**: 快速初始化开发环境
   - 创建完整 doc/ 结构
   - 生成 README.md
   - 生成 00_文档规范.md

5. **增量式工作**: 每次只做一个 feature
   - 避免 agent 试图"一次完成所有功能"
   - 确保每个 session 结束时代码处于干净状态

6. **端到端测试**: 强制测试通过
   - 使用浏览器自动化工具（如 Puppeteer MCP）
   - 测试覆盖率要求（Repository 100% CRUD，Handler ≥85%）

### 文档规范（借鉴 nn-gene）

**8 章节标准结构**:
1. 业务需求：业务背景、场景、核心需求、业务规则
2. 功能需求：功能列表、数据项清单、非功能需求
3. 系统架构：分层架构、技术栈、项目结构
4. 数据库设计：表结构、建表SQL、索引设计、数据字典
5. 接口设计：RESTful API、OData查询、错误码定义
6. 功能模块设计：模块组成、实体类、Repository、Handler
7. 业务流程设计：整体架构流程、核心操作流程
8. 测试设计：测试策略、单元测试、集成测试、覆盖率要求

**文档行数控制**: 单个文档建议 200-500 行，目录总行数 5000-10000 行

**文档拆分工具**: 使用 `scripts/check_doc_size.py` 自动检查文档行数
```bash
python3 scripts/check_doc_size.py --doc-path doc/ --warn 400 --max 500
```

**文档拆分策略**: 当文档超过 500 行时，按维度/模块/表拆分。详见 `references/doc-granularity.md`

**测试金字塔**: 单元测试 80%、集成测试 15%、E2E 测试 5%

### 需求沟通框架（6 维度）

**核心原则**:
1. **循序渐进**: 不要一次性问所有问题，每次提问 3-5 个关键问题
2. **发散思考**: 根据用户回答，继续追问细节，发现隐藏需求
3. **确认理解**: 每个维度完成后，总结用户需求，确认理解无误

**6 个核心维度**:

**维度1: 产品概述** - 核心价值、目标用户、独特优势、核心功能、用户规模

**维度2: 用户画像** - 用户群体、用户特征、使用场景、技术水平、使用频率

**维度3: 核心流程** - 首次使用、核心功能、审批流程、支付流程、通知流程

**维度4: 边界场景** - 未登录场景、权限不足、数据量大、并发量大、第三方故障、误操作

**维度5: 商业模式** - 盈利方式、定价策略、免费试用、会员体系、成本结构

**维度6: 运营模式** - 获取用户、激活用户、提高留存、促进分享、运营后台

**提问技巧**:
- 从宽泛到具体（"电商平台是一个很大的概念，我们先从核心功能开始..."）
- 总结确认（"根据您的描述，我理解的产品概述是..."）
- 发现隐藏需求（"关于用户注册，我有几个问题..."）

### Agent 回调处理模式

用于多阶段任务的回调处理（需求完成 → 设计完成 → 编码完成）：

```python
class IAgentStepHandler:
    def business_type(self) -> str:
        """业务类型标识"""
        pass
    
    def handle_callback(self, context: AgentStepContext) -> None:
        """处理回调"""
        if not context.is_success:
            self._handle_failure(context)
            return
        
        if context.stage == "requirement_complete":
            self._handle_requirement_complete(context)
        elif context.stage == "design_complete":
            self._handle_design_complete(context)
        elif context.stage == "coding_complete":
            self._handle_coding_complete(context)
```

## 深入学习

- **高级实践（测试、异步任务、代码审查）**: `references/advanced-practices.md`
- **文档粒度控制（拆分策略）**: `references/doc-granularity.md`

## 总结

Feature Development Skill 是一个完整的长时间复杂功能开发解决方案，支持从0到1和系统迭代两种模式。通过自动模式检测、多阶段审查确认、长任务可持续性机制、错误处理和测试标准，确保复杂项目的高质量交付。
