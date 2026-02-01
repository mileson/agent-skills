---
name: folder-readme-generator
description: 自动生成或更新文件夹级别的 README 文档，分析文件夹结构和功能定位，遵循文件夹说明书模板，并触发全局文档的反向更新检查
---

# 文件夹说明书生成器

## When to Use

Use this skill when you need to:
- 创建新的功能模块文件夹
- 文件夹内部文件结构发生变化
- 功能定位或职责调整
- 需要为已有文件夹补充文档
- 模块重构后更新说明
- 确保文档与代码结构同步

## Prerequisites

确保熟悉以下概念：
- **文件夹说明书模板**: 项目定义的标准文档格式
- **反向更新机制**: 文件夹 README 变更后需要同步更新全局文档
- **项目文件结构**: `Documentation/Basic/` 下的全局文档体系

## Instructions

### 步骤 1: 扫描目标文件夹结构

分析文件夹内的文件组成和层级关系：

#### 扫描策略

```bash
# 扫描目标文件夹
target_folder="Features/AIOptimization"

# 列出所有 Swift 文件
find "$target_folder" -name "*.swift" -type f

# 分析子目录结构
tree "$target_folder"
```

**输出示例**：
```
Features/AIOptimization/
├── Models/
│   ├── OptimizationTool.swift
│   └── FilterOption.swift
├── Views/
│   ├── AIOptimizationSheet.swift
│   └── Components/
│       ├── FilterSelectorView.swift
│       └── StickerGridView.swift
├── ViewModels/
│   └── AIOptimizationViewModel.swift
└── Services/
    └── AIOptimizationService.swift
```

### 步骤 2: 分析文件夹功能定位

识别文件夹的核心职责和在项目中的角色：

#### 分析维度

**1. 功能类型识别**

| 目录位置 | 功能类型 | 定位描述 |
|---------|---------|----------|
| `Features/[ModuleName]/` | 业务功能模块 | 独立的业务功能，包含完整的 MVVM 层 |
| `Common/[ComponentName]/` | 通用组件 | 跨模块复用的组件或工具 |
| `Components/[UIName]/` | UI 组件 | 可复用的界面组件 |
| `Managers/[ServiceName]/` | 核心服务 | 全局单例服务（如认证、网络） |
| `Models/` | 数据模型 | 数据结构定义 |
| `Services/` | 业务服务 | 数据获取和处理逻辑 |

**2. 职责范围分析**

通过文件名和代码结构推断：
- **Models/**: 数据模型和业务实体
- **Views/**: 用户界面展示
- **ViewModels/**: 业务逻辑和状态管理
- **Services/**: API 调用、数据持久化
- **Utils/**: 工具函数和扩展

**3. 依赖关系分析**

扫描 `import` 语句，识别核心依赖：
```swift
// 从代码中提取
import SwiftUI          // UI 框架
import Combine          // 响应式编程
import ColorTheme       // 项目内部依赖
import RevenueCat       // 第三方库
```

### 步骤 3: 按照模板生成 README

使用标准的【文件夹说明书模板】生成文档：

#### 模板结构

```markdown
# [文件夹名称] 说明书 (Folder Manual)

## 核心功能 (Core Function)
[一句话描述该文件夹包含的功能及其核心目标，需反映最新的代码逻辑]

## 输入 (Input)
[描述进入该模块的数据流、参数或上游依赖的信号]
- 来源 1: [描述]
- 来源 2: [描述]

## 输出 (Output)
[描述该模块对外暴露的接口、视图、数据或服务能力]
- 输出 1: [描述]
- 输出 2: [描述]

## 定位 (Position)
[描述该模块在整个项目架构中的层级]
- 架构层级: [UI组件层 / 业务逻辑层 / 数据持久层]
- 功能分类: [业务功能 / 通用组件 / 核心服务]

## 文件结构 (File Structure)
```
[文件夹名称]/
├── Models/
│   └── [文件列表及说明]
├── Views/
│   └── [文件列表及说明]
├── ViewModels/
│   └── [文件列表及说明]
└── Services/
    └── [文件列表及说明]
```

## 依赖 (Dependency)
[列出该模块运行所必须的外部模块或第三方库，从关键依赖到次要依赖]
- [依赖项 1]: [作用说明]
- [依赖项 2]: [作用说明]

## 核心文件说明 (Key Files)

### [文件名 1]
- **职责**: [描述]
- **关键类/结构**: [列出]
- **使用场景**: [描述]

### [文件名 2]
- **职责**: [描述]
- **关键类/结构**: [列出]
- **使用场景**: [描述]

## 使用示例 (Usage Examples)

### 示例 1: [场景描述]
```swift
// 代码示例
```

### 示例 2: [场景描述]
```swift
// 代码示例
```

## 维护规则 (Maintenance Rules)

### 1. 内部同步
当本文件夹内的代码文件增加、删除或功能变更时，必须检查并更新上述的【核心功能】、【输入】、【输出】等信息，确保文档与代码一致。

### 2. 反向更新 (Reverse Update)
一旦本 README 的内容发生实质性变更（尤其是架构定位、核心功能或文件结构改变时），必须检查并同步更新 `Documentation/Basic/` 目录下的以下全局文档，确保信息一致：

#### 必须更新的全局文档
- `Documentation/Basic/File-structure.md`
  - **更新时机**: 文件/目录结构变更
  - **更新内容**: 项目文件结构树中关于本文件夹的描述

- `Documentation/Basic/App-flow.md`
  - **更新时机**: 涉及用户流程变更
  - **更新内容**: 产品流程图中相关节点

- `Documentation/Basic/PRD.md`
  - **更新时机**: 涉及需求变更或新增功能
  - **更新内容**: 产品需求文档中的功能描述

- `Documentation/Basic/Frontend-guidelines.md` *(如适用)*
  - **更新时机**: 引入新的设计模式或组件规范
  - **更新内容**: 前端开发规范相关内容

- `Documentation/Basic/Backend-structure.md` *(如适用)*
  - **更新时机**: 涉及后端架构或 API 变更
  - **更新内容**: 后端架构设计相关内容

- `Documentation/Basic/Tech-stack.md` *(如适用)*
  - **更新时机**: 引入了新技术栈或第三方库
  - **更新内容**: 技术栈文档

### 3. 代码规范
- 所有颜色必须引用 `ColorTheme.swift`
- 遵循 MVVM 架构模式
- 文件命名符合项目规范

### 4. 测试要求
- 核心业务逻辑必须有单元测试
- ViewModel 必须可独立测试

## 变更历史 (Change History)

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|----------|------|
| 2026-01-10 | v1.0 | 初始创建 | AI |

---

**最后更新**: [自动生成时间戳]
```

### 步骤 4: 填充具体内容

#### 示例：AIOptimization 模块

```markdown
# AIOptimization 说明书 (Folder Manual)

## 核心功能 (Core Function)
AI相册的姿势优化功能模块，支持用户选择 AI 滤镜（单选）和贴纸元素（多选，最多4个），实时预览选择摘要，并触发云端 AI 生成任务。

## 输入 (Input)
- 用户选择的照片数据（从 CloudAIAlbumView 传入）
- 可选的滤镜列表（从 AIFilterService 获取）
- 可选的贴纸列表（从 AIStickerService 获取）
- 用户交互事件（选择、取消、确认）

## 输出 (Output)
- 优化配置界面（AIOptimizationSheet）
- 选择结果回调（通过闭包传递给父视图）
- AI 生成任务（提交给 AIBackgroundTaskManager）
- 用户操作反馈（Toast 提示、错误弹窗）

## 定位 (Position)
- **架构层级**: 业务逻辑层（Feature Layer）
- **功能分类**: 业务功能模块
- **MVVM 层级**: 完整的 Model-View-ViewModel 架构

本模块位于 AI相册功能流程的中间环节：
```
CloudAIAlbumView → AIOptimizationSheet → AIBackgroundTaskManager
    (选择照片)      (配置优化选项)         (执行生成任务)
```

## 文件结构 (File Structure)
```
AIOptimization/
├── Models/
│   ├── OptimizationTool.swift         # 优化工具基础协议
│   ├── AIFilter.swift                 # AI 滤镜数据模型
│   └── AISticker.swift                # AI 贴纸数据模型
├── Views/
│   ├── AIOptimizationSheet.swift      # 主弹窗视图
│   └── Components/
│       ├── FilterSelectorView.swift   # 滤镜选择器
│       ├── StickerGridView.swift      # 贴纸网格
│       └── SelectionSummaryView.swift # 选择摘要
├── ViewModels/
│   └── AIOptimizationViewModel.swift  # 视图模型（状态管理）
└── Services/
    ├── AIFilterService.swift          # 滤镜 API 服务
    └── AIStickerService.swift         # 贴纸 API 服务
```

## 依赖 (Dependency)

### 核心依赖（必需）
- **ColorTheme.swift**: 提供配色方案，确保视觉一致性
- **AIBackgroundTaskManager.swift**: 管理 AI 生成任务的提交和状态跟踪
- **AuthManager.swift**: 提供 API 认证 Token

### 功能依赖
- **CloudAIAlbumView.swift**: 父视图，触发优化流程
- **ToastManager.swift**: 显示操作反馈提示

### 第三方库
- **SwiftUI**: UI 框架
- **Combine**: 响应式数据绑定

## 核心文件说明 (Key Files)

### AIOptimizationSheet.swift
- **职责**: 主弹窗视图，整合滤镜选择、贴纸选择和摘要显示
- **关键类/结构**: `AIOptimizationSheet` (View)
- **使用场景**: 在 CloudAIAlbumView 中通过 `.sheet(isPresented:)` 展示

### AIOptimizationViewModel.swift
- **职责**: 管理选择状态、调用 API、提交生成任务
- **关键类/结构**: `AIOptimizationViewModel` (ObservableObject)
- **使用场景**: 作为 AIOptimizationSheet 的 `@StateObject`

### OptimizationTool.swift
- **职责**: 定义优化工具的通用协议（滤镜和贴纸都遵循）
- **关键类/结构**: `OptimizationTool` (Protocol)
- **使用场景**: 统一滤镜和贴纸的数据结构

### AIFilterService.swift
- **职责**: 获取可用的 AI 滤镜列表
- **关键类/结构**: `AIFilterService` (Actor)
- **使用场景**: 在 ViewModel 初始化时调用

## 使用示例 (Usage Examples)

### 示例 1: 在 CloudAIAlbumView 中展示优化弹窗
```swift
struct CloudAIAlbumView: View {
    @State private var showOptimization = false
    @State private var selectedPhotos: [Photo] = []
    
    var body: some View {
        // ... 照片展示
        
        Button("优化姿势") {
            showOptimization = true
        }
        .sheet(isPresented: $showOptimization) {
            AIOptimizationSheet(
                photos: selectedPhotos,
                onConfirm: { filter, stickers in
                    // 处理用户确认的优化配置
                    submitOptimizationTask(filter: filter, stickers: stickers)
                },
                onCancel: {
                    showOptimization = false
                }
            )
        }
    }
}
```

### 示例 2: ViewModel 使用
```swift
@MainActor
class MyViewModel: ObservableObject {
    func loadFilters() async {
        do {
            let filters = try await AIFilterService.shared.fetchFilters()
            // 处理滤镜列表
        } catch {
            print("加载滤镜失败: \(error)")
        }
    }
}
```

## 维护规则 (Maintenance Rules)

### 1. 内部同步
当本文件夹内的代码文件增加、删除或功能变更时，必须检查并更新上述的【核心功能】、【输入】、【输出】等信息，确保文档与代码一致。

### 2. 反向更新 (Reverse Update)
一旦本 README 的内容发生实质性变更（尤其是架构定位、核心功能或文件结构改变时），必须检查并同步更新 `Documentation/Basic/` 目录下的以下全局文档，确保信息一致：

#### 必须更新的全局文档
- ✅ `Documentation/Basic/File-structure.md` - 添加 AIOptimization 模块描述
- ✅ `Documentation/Basic/PRD.md` - 添加"AI姿势优化"功能需求
- ⚠️ `Documentation/Basic/App-flow.md` - 更新 AI相册流程图
- ⚠️ `Documentation/Basic/Frontend-guidelines.md` - 添加 Config 驱动弹窗模式示例

### 3. 代码规范
- 所有颜色必须引用 `ColorTheme.swift`
- 遵循 MVVM 架构模式
- API Service 使用 `actor` 保证线程安全
- ViewModel 使用 `@MainActor` 标记

### 4. 测试要求
- AIOptimizationViewModel 必须有单元测试
- API Service 必须有 Mock 测试

## 变更历史 (Change History)

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|----------|------|
| 2026-01-10 | v1.0 | 初始创建，包含滤镜和贴纸选择功能 | AI |

---

**最后更新**: 2026-01-10 16:30:00
```

### 步骤 5: 触发反向更新检查

生成 README 后，自动检查哪些全局文档需要更新：

#### 反向更新检查清单

```
========================================
反向更新检查报告
========================================
文件夹: Features/AIOptimization
README 生成时间: 2026-01-10 16:30:00

📋 需要更新的全局文档
========================================

【高优先级】必须立即更新：

1. Documentation/Basic/File-structure.md
   原因: 新增了功能模块
   建议操作:
   - 在 Features/ 章节添加 AIOptimization/ 目录
   - 添加子目录说明（Models/Views/ViewModels/Services）
   
2. Documentation/Basic/PRD.md
   原因: 新增了"AI姿势优化"功能
   建议操作:
   - 在"核心功能需求"章节添加功能描述
   - 更新功能优先级列表

【中优先级】建议更新：

3. Documentation/Basic/App-flow.md
   原因: AI相册流程增加了新环节
   建议操作:
   - 更新 AI相册流程图
   - 添加"优化配置"节点

4. Documentation/Basic/Frontend-guidelines.md
   原因: 引入了 Config 驱动的弹窗设计模式
   建议操作:
   - 在"设计模式"章节添加示例
   - 说明 AIOptimizationSheet 的配置方式

【低优先级】可选更新：

5. Documentation/Basic/Tech-stack.md
   原因: 无新技术栈引入
   建议: 暂不更新

========================================
```

### 步骤 6: 保存 README 文件

将生成的内容保存为 `[文件夹名称]_README.md`：

```bash
# 文件命名规则
target_folder="Features/AIOptimization"
readme_file="$target_folder/AIOptimization_README.md"

# 保存文件
echo "$readme_content" > "$readme_file"
```

## Generation Strategies

### 策略 1: 新模块创建时自动生成

当执行 `ios-feature-creator` 或 `ios-feature-scaffolder` 时，自动触发本 skill 生成 README。

### 策略 2: 定期批量更新

扫描所有缺少 README 的文件夹，批量生成：

```bash
# 查找缺少 README 的功能模块
find Features/ -type d -maxdepth 1 ! -name ".*" -exec test ! -e "{}/*_README.md" \; -print
```

### 策略 3: Git Commit Hook

在 git commit 前自动检查并提示更新 README：

```bash
#!/bin/bash
# .git/hooks/pre-commit

changed_folders=$(git diff --cached --name-only | xargs dirname | sort -u)

for folder in $changed_folders; do
    if [[ $folder == Features/* ]] && [[ ! -f "$folder/*_README.md" ]]; then
        echo "⚠️  $folder 缺少 README，建议生成"
    fi
done
```

## Quality Checklist

生成 README 后，检查以下项目：

### 内容完整性
- ✅ 核心功能描述清晰
- ✅ 输入输出明确
- ✅ 定位准确
- ✅ 文件结构完整
- ✅ 依赖关系清晰
- ✅ 使用示例实用

### 格式规范
- ✅ 遵循模板结构
- ✅ Markdown 格式正确
- ✅ 代码块语法高亮
- ✅ 表格对齐美观

### 反向更新
- ✅ 已生成更新检查报告
- ✅ 已标记需要更新的全局文档
- ✅ 已提供具体更新建议

## Output Checklist

- ✅ 文件夹结构已扫描
- ✅ 功能定位已分析
- ✅ README 内容已生成
- ✅ 文件已保存为 `[文件夹名称]_README.md`
- ✅ 反向更新检查报告已生成
- ✅ 全局文档更新清单已输出
