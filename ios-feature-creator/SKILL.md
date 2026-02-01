---
name: ios-feature-creator
description: 自动化创建 iOS 功能模块，遵循项目 MVVM 架构规范，生成完整的文件结构、模板代码和配套文档
---

# iOS 功能模块创建器

## When to Use

Use this skill when you need to:
- 创建新的业务功能模块（如用户模块、订单模块、消息模块等）
- 创建可复用的通用组件（如图片选择器、日期选择器等）
- 快速搭建新功能的脚手架
- 保持团队代码结构一致性
- 在 iOS 项目中创建符合架构规范的完整模块结构

## Instructions

### 步骤 1: 确定模块类型和位置

- **业务功能**: 创建在 `[ProjectName]/Features/[功能名]/` 目录
- **通用组件**: 创建在 `[ProjectName]/Common/[组件名]/` 或 `[ProjectName]/Components/[组件名]/` 目录
- 如果目录不存在，自动创建

### 步骤 2: 生成标准目录结构

在模块目录下创建以下子目录：
```
[模块名]/
├── Models/          # 数据结构和业务逻辑
├── Views/           # 界面展示和用户交互
├── ViewModels/      # 界面逻辑和数据绑定
├── Services/        # 通用服务和数据处理（如需）
├── Utils/           # 通用工具和扩展方法（如需）
└── Resources/       # 资源文件（如需本地化）
    └── Localization/
```

### 步骤 3: 生成符合 MVVM 架构的模板代码

#### Models 层 (数据模型)
```swift
import Foundation

/// [模块名]数据模型
struct [模块名]Model: Codable, Identifiable, Equatable {
    let id: String
    // TODO: 添加具体属性
    
    // MARK: - Initialization
    init(id: String = UUID().uuidString) {
        self.id = id
    }
}
```

#### Views 层 (SwiftUI视图)
```swift
import SwiftUI

/// [模块名]主视图
struct [模块名]View: View {
    // MARK: - Properties
    @StateObject private var viewModel = [模块名]ViewModel()
    
    // MARK: - Body
    var body: some View {
        NavigationView {
            VStack(spacing: 16) {
                // TODO: 添加UI组件
                Text("TODO: 实现界面")
            }
            .navigationTitle("[模块显示名称]")
        }
    }
}

// MARK: - Preview
struct [模块名]View_Previews: PreviewProvider {
    static var previews: some View {
        [模块名]View()
    }
}
```

#### ViewModels 层 (视图模型)
```swift
import SwiftUI
import Combine

/// [模块名]视图模型
@MainActor
class [模块名]ViewModel: ObservableObject {
    // MARK: - Published Properties
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    // MARK: - Private Properties
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    init() {
        setupBindings()
    }
    
    // MARK: - Public Methods
    func loadData() {
        isLoading = true
        // TODO: 实现数据加载逻辑
        isLoading = false
    }
    
    // MARK: - Private Methods
    private func setupBindings() {
        // TODO: 设置数据绑定
    }
}
```

#### Services 层 (可选，如需要网络请求)
```swift
import Foundation

/// [模块名]API服务
actor [模块名]APIService {
    // MARK: - Singleton
    static let shared = [模块名]APIService()
    
    private init() {}
    
    // MARK: - API Methods
    func fetch[数据名]() async throws -> [[模块名]Model] {
        // TODO: 实现API调用
        return []
    }
}
```

### 步骤 4: 配置 ColorTheme 颜色引用

在所有 View 文件中，确保颜色使用来自 `ColorTheme.swift`：
```swift
// ✅ 正确使用
.foregroundColor(ColorTheme.primaryText)
.background(ColorTheme.background)

// ❌ 禁止硬编码
.foregroundColor(.black)  // 不要使用
```

### 步骤 5: 创建模块文档

生成 `[模块名]_README.md` 文件：
```markdown
# [模块名] 说明书

## 核心功能
[一句话描述该模块的核心功能]

## 输入
[描述该模块的输入数据来源]

## 输出
[描述该模块对外提供的功能]

## 定位
[描述该模块在项目中的定位]

## 依赖
- [依赖的其他模块或服务]

## 使用示例
\`\`\`swift
// TODO: 添加使用示例
\`\`\`

## 维护规则
1. 修改代码后，必须更新本 README 文档
2. 新增文件需要添加文件说明书注释
3. 遵循 MVVM 架构规范
```

### 步骤 6: 更新项目文档

检查并更新以下文档（如有重大变更）：
- `Documentation/File-structure.md` - 添加新模块的文件结构说明
- `Documentation/PRD.md` - 如涉及新需求，更新产品需求
- `Documentation/App-flow.md` - 如涉及新流程，更新流程图
- `Documentation/Frontend-guidelines.md` - 如有新的架构模式，更新指南

### 步骤 7: 生成单元测试模板（可选）

在 `[ProjectName]Tests/` 目录创建测试文件：
```swift
import XCTest
@testable import [ProjectName]

class [模块名]ViewModelTests: XCTestCase {
    var viewModel: [模块名]ViewModel!
    
    override func setUp() {
        super.setUp()
        viewModel = [模块名]ViewModel()
    }
    
    override func tearDown() {
        viewModel = nil
        super.tearDown()
    }
    
    func testInitialState() {
        XCTAssertFalse(viewModel.isLoading)
        XCTAssertNil(viewModel.errorMessage)
    }
    
    // TODO: 添加更多测试用例
}
```

## Important Notes

1. **iOS 版本兼容**: 确保所有代码支持 iOS 15+
2. **命名规范**: 
   - View 文件以 `View` 结尾
   - ViewModel 文件以 `ViewModel` 结尾
   - Model 文件以 `Model` 结尾
3. **颜色规范**: 必须使用 `ColorTheme.swift` 中的颜色
4. **架构规范**: 严格遵循 MVVM 架构，不要在 View 中写业务逻辑
5. **文档规范**: 每个模块必须有 README 文档和文件说明书注释

## Output Checklist

完成后确认：
- ✅ 标准目录结构已创建
- ✅ 基础代码文件已生成
- ✅ 颜色引用符合规范
- ✅ README 文档已创建
- ✅ 项目文档已更新（如需）
- ✅ 单元测试模板已生成（如需）
