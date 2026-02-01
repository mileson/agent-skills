---
name: ios-mvvm-refactor
description: 重构混乱或过于庞大的代码文件，按照 MVVM 架构模式拆分职责，将 UI、业务逻辑和数据处理分离到 View、ViewModel、Model 和 Service 层，提升代码质量和可维护性
---

# MVVM 架构重构助手

## When to Use

Use this skill when you need to:
- 发现代码文件职责混乱、"上帝对象"反模式
- View 文件中包含大量业务逻辑
- 代码文件过于庞大（>500行）
- 业务逻辑和 UI 代码混合在一起
- 数据处理逻辑直接写在 View 中
- 代码可测试性差、难以维护
- 需要标准化架构重构流程

## Prerequisites

确保熟悉以下概念：
- **MVVM 架构模式**：Model-View-ViewModel 的职责分离
- **SwiftUI**：声明式 UI 框架
- **Combine / async-await**：响应式编程和异步处理
- **Protocol-Oriented Programming**：面向协议编程

## Instructions

### 步骤 1: 分析当前文件的职责分布

识别代码混乱的特征：

#### 职责混合的反模式

**❌ 糟糕的例子：所有代码混在一个 View 中**

```swift
struct UserProfileView: View {
    @State private var user: User?
    @State private var isLoading = false
    @State private var errorMessage: String?
    
    var body: some View {
        VStack {
            if isLoading {
                ProgressView()
            } else if let user = user {
                // UI 代码 + 业务逻辑混在一起
                VStack {
                    AsyncImage(url: URL(string: user.avatarURL)) { image in
                        image.resizable()
                    } placeholder: {
                        Color.gray
                    }
                    .frame(width: 100, height: 100)
                    .clipShape(Circle())
                    
                    Text(user.name)
                        .font(.title)
                    
                    // 直接在 View 中处理数据验证
                    if user.email.contains("@") {
                        Text(user.email)
                            .foregroundColor(.blue)
                    }
                    
                    // 直接在 View 中做网络请求
                    Button("Update Profile") {
                        isLoading = true
                        Task {
                            do {
                                let url = URL(string: "https://api.example.com/users/\(user.id)")!
                                var request = URLRequest(url: url)
                                request.httpMethod = "PUT"
                                request.addValue("Bearer \(UserDefaults.standard.string(forKey: "token") ?? "")", forHTTPHeaderField: "Authorization")
                                // ... 大量网络请求代码
                                isLoading = false
                            } catch {
                                errorMessage = error.localizedDescription
                                isLoading = false
                            }
                        }
                    }
                }
            }
        }
        .onAppear {
            // 直接在 View 中加载数据
            loadUserProfile()
        }
    }
    
    // 200+ 行业务逻辑代码混在 View 中...
    private func loadUserProfile() {
        // ...
    }
}
```

**识别职责混合的信号**：
1. ✅ View 中包含 `@State` 管理复杂状态
2. ✅ View 中直接调用 `URLSession` 或网络库
3. ✅ View 中包含数据验证逻辑（如 email 格式检查）
4. ✅ View 中使用 `UserDefaults` 或其他持久化存储
5. ✅ View 中包含复杂的业务逻辑计算
6. ✅ 文件超过 300 行代码

### 步骤 2: 按照 MVVM 模式拆分职责

将识别出的代码按照以下规则重构：

#### 职责划分原则

| 层级 | 职责 | 允许的代码 | 禁止的代码 |
|------|------|------------|------------|
| **View** | UI 展示和用户交互 | SwiftUI 声明式语法、UI 布局、用户手势、导航 | 业务逻辑、网络请求、数据验证、复杂计算 |
| **ViewModel** | 业务逻辑和数据绑定 | 状态管理 (`@Published`)、业务逻辑、调用 Service、数据转换 | UI 代码、直接网络请求、数据持久化 |
| **Model** | 数据结构 | 数据模型定义、`Codable` 实现、简单计算属性 | 业务逻辑、网络请求、UI 相关代码 |
| **Service** | 数据获取和处理 | 网络请求、数据库操作、文件读写、认证管理 | UI 代码、业务逻辑 |

### 步骤 3: 实施重构 - 完整示例

#### 3.1 创建 Model (数据模型)

位置: `Features/[模块名]/Models/User.swift`

```swift
import Foundation

// MARK: - 数据模型
struct User: Identifiable, Codable, Equatable {
    let id: String
    let name: String
    let email: String
    let avatarURL: String
    let createdAt: Date
    
    // 简单的计算属性允许放在 Model
    var isValidEmail: Bool {
        email.contains("@") && email.contains(".")
    }
    
    var displayName: String {
        name.isEmpty ? "未命名用户" : name
    }
}

// MARK: - API 请求模型
struct UpdateUserRequest: Codable {
    let name: String
    let email: String
}

// MARK: - API 响应模型
struct UserResponse: Codable {
    let user: User
    let message: String
}
```

#### 3.2 创建 Service (API 服务层)

位置: `Features/[模块名]/Services/UserAPIService.swift`

```swift
import Foundation

/// 用户 API 服务
actor UserAPIService {
    // MARK: - Singleton
    static let shared = UserAPIService()
    
    private let session: URLSession
    private let baseURL: String
    
    private init() {
        self.session = URLSession.shared
        self.baseURL = AppConfig.apiBaseURL
    }
    
    // MARK: - API Methods
    
    /// 获取用户信息
    func fetchUser(userId: String) async throws -> User {
        let endpoint = "\(baseURL)/users/\(userId)"
        guard let url = URL(string: endpoint) else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // 添加认证
        if let token = await AuthManager.shared.getAccessToken() {
            request.addValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        print("[UserAPI] GET \(url.absoluteString)")
        
        do {
            let (data, response) = try await session.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.networkError
            }
            
            switch httpResponse.statusCode {
            case 200...299:
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .iso8601
                return try decoder.decode(User.self, from: data)
            case 401:
                throw APIError.unauthorized
            case 404:
                throw APIError.notFound
            default:
                throw APIError.serverError(httpResponse.statusCode)
            }
        } catch let error as APIError {
            throw error
        } catch {
            print("[UserAPI] Error: \(error.localizedDescription)")
            throw APIError.networkError
        }
    }
    
    /// 更新用户信息
    func updateUser(userId: String, request: UpdateUserRequest) async throws -> User {
        let endpoint = "\(baseURL)/users/\(userId)"
        guard let url = URL(string: endpoint) else {
            throw APIError.invalidURL
        }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "PUT"
        urlRequest.addValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // 添加认证
        if let token = await AuthManager.shared.getAccessToken() {
            urlRequest.addValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        // 编码请求体
        let encoder = JSONEncoder()
        urlRequest.httpBody = try encoder.encode(request)
        
        print("[UserAPI] PUT \(url.absoluteString)")
        
        let (data, response) = try await session.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.serverError(0)
        }
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let userResponse = try decoder.decode(UserResponse.self, from: data)
        return userResponse.user
    }
}

// MARK: - API Error
enum APIError: Error, LocalizedError {
    case invalidURL
    case networkError
    case unauthorized
    case notFound
    case serverError(Int)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "无效的 URL"
        case .networkError:
            return "网络错误"
        case .unauthorized:
            return "未授权，请重新登录"
        case .notFound:
            return "用户不存在"
        case .serverError(let code):
            return "服务器错误 (\(code))"
        }
    }
}
```

#### 3.3 创建 ViewModel (视图模型)

位置: `Features/[模块名]/ViewModels/UserProfileViewModel.swift`

```swift
import Foundation
import Combine

/// 用户资料视图模型
@MainActor
class UserProfileViewModel: ObservableObject {
    // MARK: - Published Properties
    @Published private(set) var user: User?
    @Published private(set) var isLoading = false
    @Published private(set) var errorMessage: String?
    
    // MARK: - Private Properties
    private let userAPIService: UserAPIService
    private let userId: String
    
    // MARK: - Initialization
    init(userId: String, userAPIService: UserAPIService = .shared) {
        self.userId = userId
        self.userAPIService = userAPIService
    }
    
    // MARK: - Public Methods
    
    /// 加载用户资料
    func loadUserProfile() async {
        isLoading = true
        errorMessage = nil
        
        do {
            let fetchedUser = try await userAPIService.fetchUser(userId: userId)
            self.user = fetchedUser
            print("[UserProfileVM] 用户加载成功: \(fetchedUser.name)")
        } catch {
            self.errorMessage = error.localizedDescription
            print("[UserProfileVM] 加载失败: \(error)")
        }
        
        isLoading = false
    }
    
    /// 更新用户资料
    func updateProfile(name: String, email: String) async {
        guard !name.isEmpty, !email.isEmpty else {
            errorMessage = "名称和邮箱不能为空"
            return
        }
        
        guard email.contains("@") else {
            errorMessage = "邮箱格式不正确"
            return
        }
        
        isLoading = true
        errorMessage = nil
        
        do {
            let request = UpdateUserRequest(name: name, email: email)
            let updatedUser = try await userAPIService.updateUser(
                userId: userId,
                request: request
            )
            self.user = updatedUser
            print("[UserProfileVM] 用户更新成功")
        } catch {
            self.errorMessage = error.localizedDescription
            print("[UserProfileVM] 更新失败: \(error)")
        }
        
        isLoading = false
    }
    
    /// 清除错误
    func clearError() {
        errorMessage = nil
    }
}
```

#### 3.4 创建 View (界面)

位置: `Features/[模块名]/Views/UserProfileView.swift`

```swift
import SwiftUI

/// 用户资料界面
struct UserProfileView: View {
    // MARK: - Properties
    @StateObject private var viewModel: UserProfileViewModel
    @State private var isEditingProfile = false
    
    // MARK: - Initialization
    init(userId: String) {
        _viewModel = StateObject(wrappedValue: UserProfileViewModel(userId: userId))
    }
    
    // MARK: - Body
    var body: some View {
        ZStack {
            if viewModel.isLoading {
                loadingView
            } else if let user = viewModel.user {
                profileContent(user: user)
            } else if let errorMessage = viewModel.errorMessage {
                errorView(message: errorMessage)
            }
        }
        .navigationTitle("用户资料")
        .task {
            await viewModel.loadUserProfile()
        }
        .alert("错误", isPresented: .constant(viewModel.errorMessage != nil)) {
            Button("确定") {
                viewModel.clearError()
            }
        } message: {
            if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
            }
        }
        .sheet(isPresented: $isEditingProfile) {
            if let user = viewModel.user {
                EditProfileView(
                    user: user,
                    onSave: { name, email in
                        Task {
                            await viewModel.updateProfile(name: name, email: email)
                        }
                    }
                )
            }
        }
    }
    
    // MARK: - View Components
    
    private var loadingView: some View {
        VStack {
            ProgressView()
            Text("加载中...")
                .foregroundColor(.secondary)
        }
    }
    
    private func profileContent(user: User) -> some View {
        ScrollView {
            VStack(spacing: 20) {
                // 头像
                AsyncImage(url: URL(string: user.avatarURL)) { image in
                    image
                        .resizable()
                        .scaledToFill()
                } placeholder: {
                    Color.gray.opacity(0.3)
                        .overlay(
                            Image(systemName: "person.fill")
                                .foregroundColor(.white)
                        )
                }
                .frame(width: 100, height: 100)
                .clipShape(Circle())
                
                // 用户信息
                VStack(spacing: 8) {
                    Text(user.displayName)
                        .font(.title)
                        .fontWeight(.bold)
                    
                    if user.isValidEmail {
                        Text(user.email)
                            .foregroundColor(Color(ColorTheme.primaryColor))
                    }
                }
                
                // 编辑按钮
                Button {
                    isEditingProfile = true
                } label: {
                    Text("编辑资料")
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color(ColorTheme.primaryColor))
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
                .padding(.horizontal)
            }
            .padding()
        }
    }
    
    private func errorView(message: String) -> some View {
        VStack(spacing: 20) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 50))
                .foregroundColor(.red)
            
            Text(message)
                .multilineTextAlignment(.center)
            
            Button("重试") {
                Task {
                    await viewModel.loadUserProfile()
                }
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }
}

// MARK: - Edit Profile View
struct EditProfileView: View {
    let user: User
    let onSave: (String, String) -> Void
    
    @State private var name: String
    @State private var email: String
    @Environment(\.dismiss) private var dismiss
    
    init(user: User, onSave: @escaping (String, String) -> Void) {
        self.user = user
        self.onSave = onSave
        _name = State(initialValue: user.name)
        _email = State(initialValue: user.email)
    }
    
    var body: some View {
        NavigationView {
            Form {
                Section("基本信息") {
                    TextField("名称", text: $name)
                    TextField("邮箱", text: $email)
                        .keyboardType(.emailAddress)
                        .autocapitalization(.none)
                }
            }
            .navigationTitle("编辑资料")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("取消") {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("保存") {
                        onSave(name, email)
                        dismiss()
                    }
                    .disabled(name.isEmpty || email.isEmpty)
                }
            }
        }
    }
}
```

### 步骤 4: 更新相关文档

重构完成后，更新以下文档：

#### 4.1 更新文件结构文档

在 `Documentation/File-structure.md` 中更新：

```markdown
Features/
├── UserProfile/             # 用户资料模块（重构后）
│   ├── Models/
│   │   └── User.swift      # 用户数据模型
│   ├── Views/
│   │   └── UserProfileView.swift  # 用户资料界面
│   ├── ViewModels/
│   │   └── UserProfileViewModel.swift  # 视图模型
│   └── Services/
│       └── UserAPIService.swift  # API 服务
```

#### 4.2 创建模块 README

创建 `Features/UserProfile/UserProfile_README.md`：

```markdown
# UserProfile 模块说明书

## 核心功能
用户资料模块，支持查看和编辑用户个人信息，包括头像、名称、邮箱等。

## 输入
- 用户ID（从认证管理器获取）
- 后端 API 返回的用户数据

## 输出
- 用户资料界面
- 用户信息更新结果

## 定位
业务功能模块，位于 Features/ 目录，遵循 MVVM 架构。

## 依赖
- ColorTheme.swift - 颜色主题
- AuthManager.swift - 认证管理
- AppConfig.swift - 应用配置

## 维护规则
1. 严格遵循 MVVM 架构分层
2. View 不包含业务逻辑
3. 所有颜色引用 ColorTheme
4. API 调用统一在 Service 层
5. 状态管理使用 @Published
```

## Quality Checklist

重构完成后，检查以下项目：

### 架构合规性
- ✅ View 只包含 UI 代码和用户交互
- ✅ ViewModel 包含业务逻辑和状态管理
- ✅ Model 只包含数据结构定义
- ✅ Service 负责网络请求和数据获取
- ✅ 没有跨层直接调用（如 View 直接调用 Service）

### 代码质量
- ✅ 每个文件不超过 300 行
- ✅ 函数职责单一，不超过 50 行
- ✅ 没有重复代码
- ✅ 所有颜色引用 ColorTheme
- ✅ 变量和函数命名清晰

### 可测试性
- ✅ ViewModel 可以独立测试
- ✅ Service 可以 Mock
- ✅ 业务逻辑与 UI 完全解耦

### 文档更新
- ✅ 文件结构文档已更新
- ✅ 模块 README 已创建
- ✅ 代码注释完整

## Common Issues

### 问题 1: View 和 ViewModel 循环依赖
**解决方案**: 使用 `@StateObject` 在 View 中创建 ViewModel，避免双向引用

### 问题 2: Service 层过于庞大
**解决方案**: 拆分为多个 Service（如 UserAPIService、AuthAPIService）

### 问题 3: ViewModel 包含 UI 代码
**解决方案**: 将所有 SwiftUI View 代码移到 View 层，ViewModel 只处理数据和状态

## Best Practices

1. **依赖注入**: ViewModel 接收 Service 作为参数，方便测试
2. **错误处理**: 统一在 ViewModel 处理，暴露 errorMessage 给 View
3. **加载状态**: 使用 isLoading 统一管理加载状态
4. **异步处理**: 使用 async/await 替代 Combine 复杂的链式调用
5. **单一职责**: 每个类只负责一件事

## Output Checklist

- ✅ 代码已按 MVVM 分层重构
- ✅ View 纯 UI，无业务逻辑
- ✅ ViewModel 管理状态和业务逻辑
- ✅ Service 负责数据获取
- ✅ Model 定义数据结构
- ✅ 文档已更新
- ✅ 模块 README 已创建
