---
name: ios-feature-scaffolder
description: 快速生成 iOS 功能模块的脚手架代码，基于项目现有的组件模式（如 PhotoSelector、Skeleton、CustomTabView），创建可复用的组件或业务模块
---

# iOS 功能模块脚手架生成器

## When to Use

Use this skill when you need to:
- 创建新的可复用 UI 组件（类似 PhotoSelector、CascadingPicker）
- 搭建新的业务功能模块（类似 AIAlbum、Gallery）
- 快速原型开发和 MVP 验证
- 保持项目组件设计的一致性
- 基于项目已有的成熟组件模式，快速搭建新功能模块的完整脚手架

## Component Patterns Reference

项目中已有的优秀组件模式：

### 1. **配置驱动模式** (Config-Driven Pattern)
**参考**: `PhotoSelector`, `CascadingPicker`, `CustomTabView`

**特点**：
- 通过 Config 结构体配置组件行为
- 闭包回调处理用户交互
- 高度解耦，易于测试和复用

### 2. **本地化组件模式** (Localized Component Pattern)
**参考**: `RevenueCat`, `Shortcuts`, `CascadingPicker`

**特点**：
- 组件内置本地化资源 `Resources/Localization/`
- 独立的本地化帮助类
- 支持中英文等多语言

### 3. **主题适配模式** (Theme Adaptation Pattern)
**参考**: 所有 View 组件

**特点**：
- 使用 `ColorTheme.swift` 统一配色
- 自动适配深色/浅色模式
- 禁止硬编码颜色

## Instructions

### 步骤 1: 确定组件类型和模式选择

**A. 可复用 UI 组件**
- 位置：`Components/[组件名]/`
- 参考模式：PhotoSelector、Skeleton、CascadingPicker
- 特征：高度可配置、完全解耦、带本地化

**B. 业务功能模块**
- 位置：`Features/[模块名]/`
- 参考模式：AIAlbum、Gallery、Templates
- 特征：MVVM 架构、完整的业务逻辑

### 步骤 2: 生成组件目录结构

#### 可复用组件结构 (Components/)
```
Components/[组件名]/
├── Core/                        # 核心逻辑（可选）
│   ├── [组件名]Configuration.swift
│   └── [组件名]Manager.swift
├── Models/
│   ├── [组件名]Config.swift     # 配置模型
│   └── [组件名]Item.swift        # 数据项模型
├── Views/
│   ├── [组件名]View.swift        # 主视图
│   └── Components/               # 子组件（可选）
├── Extensions/
│   └── View+[组件名].swift       # View 扩展
├── Resources/
│   └── Localization/             # 本地化资源
│       ├── en.lproj/
│       │   └── [组件名].strings
│       └── zh-Hans.lproj/
│           └── [组件名].strings
└── [组件名]_README.md            # 组件文档
```

#### 业务模块结构 (Features/)
```
Features/[模块名]/
├── Models/
│   ├── [模块名]Model.swift
│   └── [模块名]APIModels.swift  # API 数据模型（如需）
├── Views/
│   ├── [模块名]View.swift
│   └── Components/              # 专用组件
├── ViewModels/
│   └── [模块名]ViewModel.swift
├── Services/
│   └── [模块名]Service.swift    # 业务服务（如需）
└── [模块名]_README.md
```

### 步骤 3: 生成配置驱动的组件代码

#### Config 模型 (参考 PhotoSelectorConfig)
```swift
import Foundation
import SwiftUI

/// [组件名]配置
struct [组件名]Config {
    // MARK: - Configuration Properties
    var option1: Bool = true
    var option2: Int = 10
    var maxCount: Int?
    
    // MARK: - Callbacks
    var onComplete: ([DataType]) -> Void
    var onCancel: (() -> Void)?
    
    // MARK: - Theme (可选)
    var theme: [组件名]Theme = .default
    
    // MARK: - Initialization
    init(
        option1: Bool = true,
        option2: Int = 10,
        maxCount: Int? = nil,
        onComplete: @escaping ([DataType]) -> Void,
        onCancel: (() -> Void)? = nil
    ) {
        self.option1 = option1
        self.option2 = option2
        self.maxCount = maxCount
        self.onComplete = onComplete
        self.onCancel = onCancel
    }
    
    // MARK: - Presets
    static let `default` = [组件名]Config(
        onComplete: { _ in }
    )
}
```

#### 主视图 (参考 PhotoSelectorView)
```swift
import SwiftUI

/// [组件名]主视图
struct [组件名]View: View {
    // MARK: - Properties
    let config: [组件名]Config
    @StateObject private var viewModel: [组件名]ViewModel
    @Environment(\.colorScheme) var colorScheme
    
    // MARK: - Initialization
    init(config: [组件名]Config) {
        self.config = config
        _viewModel = StateObject(wrappedValue: [组件名]ViewModel(config: config))
    }
    
    // MARK: - Body
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                contentView
            }
            .navigationTitle(localizedString("title"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                toolbarContent
            }
        }
        .background(ColorTheme.background)
    }
    
    // MARK: - Subviews
    private var contentView: some View {
        Text("TODO: Content")
    }
    
    @ToolbarContentBuilder
    private var toolbarContent: some ToolbarContent {
        ToolbarItem(placement: .navigationBarLeading) {
            Button(localizedString("cancel")) {
                config.onCancel?()
            }
            .foregroundColor(ColorTheme.primaryText)
        }
        
        ToolbarItem(placement: .navigationBarTrailing) {
            Button(localizedString("done")) {
                config.onComplete(viewModel.selectedItems)
            }
            .foregroundColor(ColorTheme.accent)
            .disabled(viewModel.selectedItems.isEmpty)
        }
    }
    
    // MARK: - Helper Methods
    private func localizedString(_ key: String) -> String {
        [组件名]Localization.string(for: key)
    }
}

// MARK: - Preview
struct [组件名]View_Previews: PreviewProvider {
    static var previews: some View {
        [组件名]View(config: [组件名]Config.default)
    }
}
```

#### ViewModel
```swift
import SwiftUI
import Combine

/// [组件名]视图模型
@MainActor
class [组件名]ViewModel: ObservableObject {
    // MARK: - Published Properties
    @Published var selectedItems: [DataType] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    // MARK: - Private Properties
    private let config: [组件名]Config
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    init(config: [组件名]Config) {
        self.config = config
        setupBindings()
    }
    
    // MARK: - Public Methods
    func toggleSelection(_ item: DataType) {
        if selectedItems.contains(where: { $0.id == item.id }) {
            selectedItems.removeAll { $0.id == item.id }
        } else {
            // 检查最大数量限制
            if let maxCount = config.maxCount, selectedItems.count >= maxCount {
                errorMessage = "最多选择 \(maxCount) 个"
                return
            }
            selectedItems.append(item)
        }
    }
    
    // MARK: - Private Methods
    private func setupBindings() {
        // TODO: 设置数据绑定
    }
}
```

### 步骤 4: 添加本地化支持

#### 创建本地化帮助类
```swift
import Foundation

/// [组件名]本地化工具
enum [组件名]Localization {
    private static let bundle = Bundle.main
    private static let tableName = "[组件名]"
    
    static func string(for key: String) -> String {
        NSLocalizedString(
            key,
            tableName: tableName,
            bundle: bundle,
            comment: ""
        )
    }
}
```

#### 创建本地化文件
**en.lproj/[组件名].strings**:
```
"title" = "[Component Title]";
"cancel" = "Cancel";
"done" = "Done";
"empty_state" = "No items available";
```

**zh-Hans.lproj/[组件名].strings**:
```
"title" = "[组件标题]";
"cancel" = "取消";
"done" = "完成";
"empty_state" = "暂无内容";
```

### 步骤 5: 添加 View 扩展 (便捷调用)

```swift
import SwiftUI

extension View {
    /// 展示 [组件名]
    func [组件名Camel]Sheet(
        isPresented: Binding<Bool>,
        config: [组件名]Config
    ) -> some View {
        self.sheet(isPresented: isPresented) {
            [组件名]View(config: config)
        }
    }
}
```

### 步骤 6: 创建组件 README 文档

参考 `PhotoSelector_README.md` 格式：

```markdown
# [组件名] 组件

## 功能概述
[一句话描述组件的核心功能]

## 主要特性
- ✅ 配置驱动设计
- ✅ 支持中英文本地化
- ✅ 深色/浅色模式自动适配
- ✅ 使用 ColorTheme 统一配色
- ✅ 完全解耦，易于复用

## 使用示例

### 基础用法
\`\`\`swift
[组件名]View(config: [组件名]Config(
    option1: true,
    onComplete: { items in
        print("完成: \(items)")
    }
))
\`\`\`

## 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `option1` | `Bool` | `true` | [选项1说明] |
| `option2` | `Int` | `10` | [选项2说明] |
| `maxCount` | `Int?` | `nil` | 最大数量限制 |

## 依赖
- SwiftUI
- Combine
- ColorTheme.swift

## 更新日志
- v1.0.0 (2026-01-10) - 初始版本
```

### 步骤 7: 配置 ColorTheme 颜色引用

确保所有颜色使用来自 `ColorTheme.swift`：

```swift
// ✅ 正确示例
.foregroundColor(ColorTheme.primaryText)
.background(ColorTheme.background)
.tint(ColorTheme.accent)
```

### 步骤 8: 适配 iOS 15+ 兼容性

```swift
// iOS 版本适配
if #available(iOS 16.0, *) {
    // iOS 16+ 特性
    view.presentationDetents([.medium, .large])
} else {
    // iOS 15 降级方案
    view
}
```

## Best Practices

1. **配置优先**: 所有可变行为通过 Config 配置
2. **完全解耦**: 不依赖全局状态
3. **主题一致**: 必须使用 ColorTheme
4. **本地化支持**: 所有用户可见文本支持本地化

## Output Checklist

完成后确认：
- ✅ 标准目录结构已创建
- ✅ Config 模型已定义
- ✅ 主视图和 ViewModel 已实现
- ✅ 本地化文件已创建（中英文）
- ✅ View 扩展已添加
- ✅ README 文档已生成
- ✅ ColorTheme 引用正确
- ✅ iOS 15+ 兼容性已验证
