---
name: doc-auto-sync-checker
description: 自动检查代码变更后文档是否需要同步更新，根据文件类型和变更内容智能判断需要更新的文档，并生成更新建议
---

# 文档自动同步检查器

## When to Use

Use this skill when you need to:
- 在代码提交前检查文档同步状态
- Pull Request 审查流程中验证文档完整性
- 定期进行文档维护检查
- 重大功能变更后的文档同步
- 避免文档滞后于代码实现

## Prerequisites

项目中存在以下标准文档：
- `Documentation/File-structure.md` - 文件结构文档
- `Documentation/PRD.md` - 产品需求文档
- `Documentation/App-flow.md` - 应用流程文档
- `Documentation/Frontend-guidelines.md` - 前端开发指南
- `Documentation/Backend-structure.md` - 后端架构文档
- `Documentation/Tech-stack.md` - 技术栈文档

## Instructions

### 步骤 1: 分析代码变更类型

支持两种分析模式：

**A. Git Diff 模式**（推荐）
```bash
# 获取最近的变更
git diff HEAD~1 HEAD --name-status

# 或检查未提交的变更
git diff --staged --name-status
```

**B. 手动指定模式**
直接指定变更的文件或目录

### 步骤 2: 识别变更类型和影响范围

根据变更文件的类型和位置，判断需要更新的文档：

#### 变更类型 A：文件结构变更

**触发条件**：
- 新增文件或目录
- 删除文件或目录
- 移动文件到新位置
- 重命名文件或目录

**需要更新的文档**：
- ✅ `Documentation/File-structure.md` - **必须更新**

**更新建议**：
```markdown
需要在 File-structure.md 中：
1. 添加新文件/目录的说明
2. 更新目录树结构图
3. 说明文件的用途和职责

变更详情：
- 新增：Features/NewModule/
- 移动：Utils/Helper.swift → Common/Utils/Helper.swift
```

#### 变更类型 B：功能逻辑变更

**触发条件**：
- 新增功能模块（Features/ 目录）
- 修改业务逻辑（ViewModel、Service 文件）
- 新增/修改 API 端点（backend/app/api/）
- 修改用户流程（View 文件）

**需要更新的文档**：
- ✅ `Documentation/PRD.md` - 如涉及新需求或需求变更
- ✅ `Documentation/App-flow.md` - 如涉及用户流程变更

**更新建议**：
```markdown
PRD.md 需要更新：
- 在"功能需求"章节添加[新功能名]的描述
- 更新功能优先级列表

App-flow.md 需要更新：
- 添加[新功能]的流程图
- 更新现有流程图中的交互节点

变更详情：
- 新增功能：AIOptimization 模块
- 影响流程：AI相册 → 优化姿势 → 确认生成
```

#### 变更类型 C：架构模式变更

**触发条件**：
- 引入新的设计模式（如新的 Adapter、Strategy）
- 修改 MVVM 层级结构
- 新增通用组件（Components/ 目录）
- 修改数据流架构

**需要更新的文档**：
- ✅ `Documentation/Frontend-guidelines.md`（iOS 前端）
- ✅ `Documentation/Backend-structure.md`（后端）

**更新建议**：
```markdown
Frontend-guidelines.md 需要更新：
- 在"设计模式最佳实践"章节添加新模式说明
- 更新组件使用示例
- 添加架构图（如需）

变更详情：
- 新增模式：Strategy Pattern for Filter Selection
- 新增组件：OptimizationSheet
- 影响章节：2. UI组件规范 → 核心组件
```

#### 变更类型 D：技术栈变更

**触发条件**：
- 添加新的第三方库依赖
- 升级主要框架版本
- 引入新技术（如 async/await）
- 修改构建配置

**需要更新的文档**：
- ✅ `Documentation/Tech-stack.md` - **必须更新**

**更新建议**：
```markdown
Tech-stack.md 需要更新：
- 在"第三方依赖"章节添加新库
- 更新版本号信息
- 说明使用场景和原因

变更详情：
- 新增依赖：Alamofire 5.8.0 - 网络请求库
- 升级：SwiftUI (iOS 15 → iOS 16)
- 移除：旧的网络层实现
```

### 步骤 3: 生成文档同步检查报告

输出格式：

```
========================================
文档同步检查报告
========================================
检查时间：2026-01-10 16:00:00
检查范围：最近一次提交 (commit abc1234)

📊 变更统计
-----------------
变更文件数：15
新增文件：5
修改文件：8
删除文件：2
移动文件：0

🔍 文档影响分析
-----------------

【高优先级】需要立即更新的文档：

1. Documentation/File-structure.md
   原因：新增了 5 个文件，删除了 2 个文件
   变更详情：
   - ✚ Features/AIOptimization/Models/OptimizationTool.swift
   - ✚ Features/AIOptimization/Views/AIOptimizationSheet.swift
   - ✚ Features/AIOptimization/ViewModels/AIOptimizationViewModel.swift
   - ✚ Features/AIFilter/Models/AIFilter.swift
   - ✚ Features/AIFilter/Services/AIFilterService.swift
   - ✖ Features/Old/DeprecatedView.swift
   - ✖ Features/Old/DeprecatedModel.swift
   
   建议更新内容：
   在 File-structure.md 的 Features/ 章节添加新模块说明

2. Documentation/PRD.md
   原因：新增了 AIOptimization 功能模块
   变更详情：AI相册新增"优化姿势"功能
   
   建议更新内容：
   在 PRD.md 的"核心功能需求"章节添加功能描述

【中优先级】建议更新的文档：

3. Documentation/Frontend-guidelines.md
   原因：新增了配置驱动的弹窗组件模式
   变更详情：AIOptimizationSheet 采用 Config + Callback 模式

【低优先级】可选更新的文档：

4. Documentation/Tech-stack.md
   原因：无新的技术栈变更
   建议：暂不更新

========================================
🎯 快速行动清单
========================================

请按以下顺序更新文档：

□ 1. 更新 File-structure.md
     - 添加 AIOptimization 和 AIFilter 模块
     - 删除 Old 目录引用
     - 估计耗时：5 分钟

□ 2. 更新 PRD.md
     - 添加"AI姿势优化"功能描述
     - 更新功能列表
     - 估计耗时：10 分钟

□ 3. 更新 Frontend-guidelines.md（可选）
     - 添加 AIOptimizationSheet 组件示例
     - 估计耗时：5 分钟

========================================
```

### 步骤 4: 提取关键信息用于更新

为每个需要更新的文档，提取关键信息：

**信息提取模板**：
```
文档：Documentation/File-structure.md
更新章节：Features/ 目录结构
新增内容：
  - 目录名：AIOptimization/
  - 功能描述：AI相册优化功能，支持滤镜和贴纸选择
  - 子目录：Models/, Views/, ViewModels/
  - 创建时间：V2.x 版本
删除内容：
  - 目录名：Old/
  - 原因：功能废弃
```

### 步骤 5: 验证文档一致性

检查文档之间的交叉引用：

```
检查 File-structure.md 中提到的文件是否确实存在：
✅ Features/AIOptimization/ - 存在
✅ Features/AIFilter/ - 存在
✅ Components/PhotoSelector/ - 存在

检查 PRD.md 中描述的功能是否已实现：
✅ AI姿势优化 - 已在 Features/AIOptimization/ 实现
⚠️ 批量编辑模板 - 未找到对应实现
```

## Smart Filtering Rules

某些变更**不需要**更新文档：

### 排除规则 1：测试文件变更
```
变更文件：Tests/SomeTest.swift
判断：测试文件变更通常不需要更新文档
结果：跳过
```

### 排除规则 2：私有方法修改
```
变更类型：修改 private func 内部实现
判断：内部实现细节变更，不影响外部接口
结果：跳过
```

### 排除规则 3：注释和格式调整
```
变更类型：仅修改注释或代码格式
判断：不影响功能逻辑
结果：跳过
```

### 排除规则 4：Bug 修复
```
变更类型：Bug Fix，不涉及新功能
判断：通常不需要更新需求文档
结果：可能需要更新 Changelog，但不更新 PRD
```

## CI/CD Integration

将验证器集成到持续集成流程：

```yaml
# .github/workflows/doc-check.yml
name: Documentation Sync Check

on: [pull_request]

jobs:
  check-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check Documentation
        run: |
          # 运行检查器，生成报告
      - name: Comment PR
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              body: '📚 文档同步检查报告：\n' + report
            })
```

## Output Checklist

完成后确认：
- ✅ 代码变更已分析
- ✅ 文档影响范围已识别
- ✅ 更新建议已生成
- ✅ 行动清单已列出
- ✅ 更新草稿已准备（如需）
