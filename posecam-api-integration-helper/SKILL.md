---
name: posecam-api-integration-helper
description: 快速接入新的后端 API 端点，自动生成数据模型、API Service、错误处理、认证集成和单元测试，标准化 API 接入流程
---

# PoseCam API 集成助手

## When to Use

Use this skill when you need to:
- 接入新的后端 API 端点
- 为现有功能添加网络请求能力
- 标准化 API 调用流程
- 实现认证和错误处理
- 生成 API 相关的测试用例
- 对接后端 OpenAPI 规范

## Prerequisites

确保项目中存在以下基础设施：
- `AuthManager.swift` - 认证管理器（提供 access token）
- `AppConfig.swift` - 应用配置（API base URL）
- `ColorTheme.swift` - 颜色主题
- 后端 API 文档或 OpenAPI 规范

## Instructions

### 步骤 1: 分析后端 API 文档

收集以下信息：

#### API 端点信息
```
端点: POST /api/v1/templates
描述: 创建新的姿势模板
请求体:
  - image: string (base64)
  - category_id: string
  - is_private: boolean
响应:
  - id: string
  - image_url: string
  - created_at: datetime
认证: Bearer Token
错误码:
  - 400: 参数错误
  - 401: 未授权
  - 413: 图片过大
  - 429: 请求过于频繁
```

### 步骤 2: 生成数据模型

在 `Features/[模块名]/Models/` 目录创建数据模型：

```swift
import Foundation

// MARK: - 请求模型
struct CreateTemplateRequest: Codable {
    let image: String           // base64 编码的图片
    let categoryId: String
    let isPrivate: Bool
    
    enum CodingKeys: String, CodingKey {
        case image
        case categoryId = "category_id"
        case isPrivate = "is_private"
    }
}

// MARK: - 响应模型
struct TemplateResponse: Codable {
    let id: String
    let imageURL: String
    let createdAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id
        case imageURL = "image_url"
        case createdAt = "created_at"
    }
}

// MARK: - 领域模型
struct Template: Identifiable, Codable, Equatable {
    let id: String
    let imageURL: String
    let categoryId: String
    let isPrivate: Bool
    let createdAt: Date
    
    /// 从 API 响应创建
    static func from(response: TemplateResponse, request: CreateTemplateRequest) -> Template {
        Template(
            id: response.id,
            imageURL: response.imageURL,
            categoryId: request.categoryId,
            isPrivate: request.isPrivate,
            createdAt: response.createdAt
        )
    }
}
```

**命名规范**：
- **请求模型**: `[操作][资源]Request` (如 `CreateTemplateRequest`)
- **响应模型**: `[资源]Response` (如 `TemplateResponse`)
- **领域模型**: 直接使用资源名 (如 `Template`)

### 步骤 3: 创建 API Service

在 `Features/[模块名]/Services/` 目录创建 API 服务类：

```swift
import Foundation

/// 模板 API 服务
actor TemplateAPIService {
    // MARK: - Singleton
    static let shared = TemplateAPIService()
    
    // MARK: - Properties
    private let session: URLSession
    private let apiPrefix = "/api/v1"
    
    // 重试配置
    private let maxRetryAttempts = 3
    private let retryDelay: TimeInterval = 2.0
    
    // MARK: - Initialization
    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30.0
        config.timeoutIntervalForResource = 60.0
        self.session = URLSession(configuration: config)
    }
    
    // MARK: - Public Methods
    
    /// 创建模板
    func createTemplate(
        image: String,
        categoryId: String,
        isPrivate: Bool
    ) async throws -> Template {
        let request = CreateTemplateRequest(
            image: image,
            categoryId: categoryId,
            isPrivate: isPrivate
        )
        
        let response: TemplateResponse = try await performRequest(
            endpoint: "/templates",
            method: "POST",
            body: request
        )
        
        return Template.from(response: response, request: request)
    }
    
    /// 获取模板列表
    func fetchTemplates(
        page: Int = 1,
        pageSize: Int = 20,
        categoryId: String? = nil
    ) async throws -> [Template] {
        var queryItems = [
            URLQueryItem(name: "page", value: "\(page)"),
            URLQueryItem(name: "page_size", value: "\(pageSize)")
        ]
        
        if let categoryId = categoryId {
            queryItems.append(URLQueryItem(name: "category_id", value: categoryId))
        }
        
        let response: TemplateListResponse = try await performRequest(
            endpoint: "/templates",
            method: "GET",
            queryItems: queryItems
        )
        
        return response.items
    }
    
    /// 删除模板
    func deleteTemplate(id: String) async throws {
        let _: EmptyResponse = try await performRequest(
            endpoint: "/templates/\(id)",
            method: "DELETE"
        )
    }
    
    // MARK: - Private Methods
    
    /// 执行请求（通用方法）
    private func performRequest<RequestBody: Encodable, Response: Decodable>(
        endpoint: String,
        method: String,
        body: RequestBody? = nil,
        queryItems: [URLQueryItem]? = nil,
        attempt: Int = 1
    ) async throws -> Response {
        // 1. 构建 URL
        guard var urlComponents = URLComponents(string: AppConfig.apiBaseURL + apiPrefix + endpoint) else {
            throw TemplateAPIError.invalidURL
        }
        
        if let queryItems = queryItems {
            urlComponents.queryItems = queryItems
        }
        
        guard let url = urlComponents.url else {
            throw TemplateAPIError.invalidURL
        }
        
        // 2. 创建请求
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = method
        urlRequest.addValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.addValue("application/json", forHTTPHeaderField: "Accept")
        
        // 3. 添加认证
        if let token = await AuthManager.shared.getAccessToken() {
            urlRequest.addValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        } else {
            throw TemplateAPIError.unauthorized
        }
        
        // 4. 编码请求体
        if let body = body {
            let encoder = JSONEncoder()
            encoder.keyEncodingStrategy = .convertToSnakeCase
            urlRequest.httpBody = try encoder.encode(body)
        }
        
        print("[TemplateAPI] \(method) \(url.absoluteString)")
        
        do {
            // 5. 发送请求
            let (data, response) = try await session.data(for: urlRequest)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw TemplateAPIError.networkError
            }
            
            print("[TemplateAPI] Response status: \(httpResponse.statusCode)")
            
            // 6. 处理响应
            switch httpResponse.statusCode {
            case 200...299:
                // 成功响应
                if Response.self == EmptyResponse.self {
                    return EmptyResponse() as! Response
                }
                let decoder = JSONDecoder()
                decoder.keyDecodingStrategy = .convertFromSnakeCase
                decoder.dateDecodingStrategy = .iso8601
                return try decoder.decode(Response.self, from: data)
                
            case 400:
                // 参数错误
                throw handleBadRequest(data)
                
            case 401:
                // 未授权
                throw TemplateAPIError.unauthorized
                
            case 404:
                // 资源不存在
                throw TemplateAPIError.notFound
                
            case 413:
                // 图片过大
                throw TemplateAPIError.imageTooLarge
                
            case 429:
                // 请求过于频繁
                throw handleRateLimited(httpResponse, data)
                
            case 500...599:
                // 服务器错误，支持重试
                if attempt < maxRetryAttempts {
                    print("[TemplateAPI] Server error, retrying... (attempt \(attempt)/\(maxRetryAttempts))")
                    try await Task.sleep(nanoseconds: UInt64(retryDelay * 1_000_000_000))
                    return try await performRequest(
                        endpoint: endpoint,
                        method: method,
                        body: body,
                        queryItems: queryItems,
                        attempt: attempt + 1
                    )
                }
                throw TemplateAPIError.serverError
                
            default:
                throw handleGenericError(data)
            }
            
        } catch let error as TemplateAPIError {
            throw error
        } catch {
            // 网络错误，支持重试
            if attempt < maxRetryAttempts {
                print("[TemplateAPI] Network error, retrying... (attempt \(attempt)/\(maxRetryAttempts))")
                try await Task.sleep(nanoseconds: UInt64(retryDelay * 1_000_000_000))
                return try await performRequest(
                    endpoint: endpoint,
                    method: method,
                    body: body,
                    queryItems: queryItems,
                    attempt: attempt + 1
                )
            }
            print("[TemplateAPI] Network error: \(error.localizedDescription)")
            throw TemplateAPIError.networkError
        }
    }
    
    // MARK: - Error Handling
    
    private func handleBadRequest(_ data: Data) -> TemplateAPIError {
        if let errorResponse = try? JSONDecoder().decode(APIErrorResponse.self, from: data) {
            return .badRequest(errorResponse.message)
        }
        return .badRequest("参数错误")
    }
    
    private func handleRateLimited(_ response: HTTPURLResponse, _ data: Data) -> TemplateAPIError {
        if let retryAfter = response.value(forHTTPHeaderField: "Retry-After"),
           let seconds = Int(retryAfter) {
            return .rateLimited(retryAfter: seconds)
        }
        return .rateLimited(retryAfter: 60)
    }
    
    private func handleGenericError(_ data: Data) -> TemplateAPIError {
        if let errorResponse = try? JSONDecoder().decode(APIErrorResponse.self, from: data) {
            return .unknown(errorResponse.message)
        }
        return .unknown("未知错误")
    }
}

// MARK: - Supporting Types

/// 空响应（用于删除等操作）
struct EmptyResponse: Codable {}

/// 列表响应
struct TemplateListResponse: Codable {
    let items: [Template]
    let total: Int
    let page: Int
    let pageSize: Int
    
    enum CodingKeys: String, CodingKey {
        case items
        case total
        case page
        case pageSize = "page_size"
    }
}

/// API 错误响应
struct APIErrorResponse: Codable {
    let message: String
    let code: String?
}

// MARK: - Error Types

enum TemplateAPIError: Error, LocalizedError {
    case invalidURL
    case networkError
    case unauthorized
    case notFound
    case badRequest(String)
    case imageTooLarge
    case rateLimited(retryAfter: Int)
    case serverError
    case unknown(String)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "无效的 URL"
        case .networkError:
            return "网络连接失败，请检查网络设置"
        case .unauthorized:
            return "未授权，请重新登录"
        case .notFound:
            return "资源不存在"
        case .badRequest(let message):
            return message
        case .imageTooLarge:
            return "图片过大，请选择小于 10MB 的图片"
        case .rateLimited(let seconds):
            return "请求过于频繁，请在 \(seconds) 秒后重试"
        case .serverError:
            return "服务器错误，请稍后重试"
        case .unknown(let message):
            return message
        }
    }
    
    var recoverySuggestion: String? {
        switch self {
        case .networkError:
            return "请检查网络连接后重试"
        case .unauthorized:
            return "请重新登录"
        case .imageTooLarge:
            return "请压缩图片后重试"
        case .rateLimited:
            return "请稍后再试"
        case .serverError:
            return "问题可能是临时的，请稍后重试"
        default:
            return nil
        }
    }
}
```

### 步骤 4: 集成到 ViewModel

在 ViewModel 中使用新的 API Service：

```swift
@MainActor
class TemplateViewModel: ObservableObject {
    @Published var templates: [Template] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiService: TemplateAPIService
    
    init(apiService: TemplateAPIService = .shared) {
        self.apiService = apiService
    }
    
    func loadTemplates(categoryId: String? = nil) async {
        isLoading = true
        errorMessage = nil
        
        do {
            templates = try await apiService.fetchTemplates(categoryId: categoryId)
        } catch let error as TemplateAPIError {
            errorMessage = error.errorDescription
        } catch {
            errorMessage = "加载失败"
        }
        
        isLoading = false
    }
    
    func createTemplate(image: String, categoryId: String) async {
        isLoading = true
        errorMessage = nil
        
        do {
            let newTemplate = try await apiService.createTemplate(
                image: image,
                categoryId: categoryId,
                isPrivate: false
            )
            templates.insert(newTemplate, at: 0)
        } catch let error as TemplateAPIError {
            errorMessage = error.errorDescription
        } catch {
            errorMessage = "创建失败"
        }
        
        isLoading = false
    }
}
```

### 步骤 5: 生成单元测试

在 `tests/` 目录创建测试脚本：

```swift
import XCTest
@testable import PoseCam

@MainActor
class TemplateAPIServiceTests: XCTestCase {
    var service: TemplateAPIService!
    var mockSession: MockURLSession!
    
    override func setUp() async throws {
        try await super.setUp()
        mockSession = MockURLSession()
        // 注入 mock session（需要调整 service 支持依赖注入）
    }
    
    override func tearDown() async throws {
        service = nil
        mockSession = nil
        try await super.tearDown()
    }
    
    func testCreateTemplate_Success() async throws {
        // Given
        let mockResponse = TemplateResponse(
            id: "123",
            imageURL: "https://example.com/image.jpg",
            createdAt: Date()
        )
        mockSession.mockData = try JSONEncoder().encode(mockResponse)
        mockSession.mockStatusCode = 201
        
        // When
        let template = try await service.createTemplate(
            image: "base64...",
            categoryId: "cat1",
            isPrivate: false
        )
        
        // Then
        XCTAssertEqual(template.id, "123")
        XCTAssertEqual(template.categoryId, "cat1")
        XCTAssertFalse(template.isPrivate)
    }
    
    func testCreateTemplate_Unauthorized() async {
        // Given
        mockSession.mockStatusCode = 401
        
        // When & Then
        do {
            _ = try await service.createTemplate(
                image: "base64...",
                categoryId: "cat1",
                isPrivate: false
            )
            XCTFail("Should throw unauthorized error")
        } catch let error as TemplateAPIError {
            XCTAssertEqual(error, .unauthorized)
        } catch {
            XCTFail("Unexpected error type")
        }
    }
    
    func testCreateTemplate_ImageTooLarge() async {
        // Given
        mockSession.mockStatusCode = 413
        
        // When & Then
        do {
            _ = try await service.createTemplate(
                image: "base64...",
                categoryId: "cat1",
                isPrivate: false
            )
            XCTFail("Should throw imageTooLarge error")
        } catch let error as TemplateAPIError {
            XCTAssertEqual(error, .imageTooLarge)
        } catch {
            XCTFail("Unexpected error type")
        }
    }
}
```

### 步骤 6: 更新文档

#### 更新 Backend-structure.md

在 `Documentation/Backend-structure.md` 中添加：

```markdown
## API 端点

### 模板管理

#### POST /api/v1/templates
创建新的姿势模板

**请求体**:
```json
{
  "image": "base64...",
  "category_id": "cat1",
  "is_private": false
}
```

**响应**:
```json
{
  "id": "123",
  "image_url": "https://...",
  "created_at": "2026-01-10T10:00:00Z"
}
```

**客户端实现**: `TemplateAPIService.createTemplate()`
```

## API Integration Patterns

### 认证模式

所有 API Service 都应遵循以下认证模式：

```swift
// 1. 从 AuthManager 获取 token
if let token = await AuthManager.shared.getAccessToken() {
    request.addValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
} else {
    throw APIError.unauthorized
}
```

### 错误处理模式

标准错误处理流程：

```swift
switch httpResponse.statusCode {
case 200...299:
    // 成功
case 400:
    // 参数错误 - 解析错误信息
case 401:
    // 未授权 - 提示重新登录
case 404:
    // 资源不存在
case 429:
    // 限流 - 提取 Retry-After
case 500...599:
    // 服务器错误 - 支持重试
default:
    // 未知错误
}
```

### 重试策略

对于网络错误和服务器错误(5xx)，实施指数退避重试：

```swift
private let maxRetryAttempts = 3
private let retryDelay: TimeInterval = 2.0

// 在 catch 块中
if attempt < maxRetryAttempts {
    try await Task.sleep(nanoseconds: UInt64(retryDelay * 1_000_000_000))
    return try await performRequest(..., attempt: attempt + 1)
}
```

### JSON 编解码策略

统一使用以下策略：

```swift
// 编码
let encoder = JSONEncoder()
encoder.keyEncodingStrategy = .convertToSnakeCase  // camelCase -> snake_case
encoder.dateEncodingStrategy = .iso8601

// 解码
let decoder = JSONDecoder()
decoder.keyDecodingStrategy = .convertFromSnakeCase  // snake_case -> camelCase
decoder.dateDecodingStrategy = .iso8601
```

## Best Practices

1. **Actor 隔离**: 所有 API Service 使用 `actor` 保证线程安全
2. **单例模式**: 使用 `.shared` 单例，但支持依赖注入以便测试
3. **类型安全**: 使用泛型方法 `performRequest<RequestBody, Response>`
4. **错误细化**: 定义专门的 Error enum，提供本地化错误信息
5. **日志记录**: 关键操作打印日志，便于调试
6. **超时配置**: 设置合理的请求超时时间
7. **空响应处理**: 对于 DELETE 等操作，使用 `EmptyResponse`

## Output Checklist

- ✅ 数据模型已创建（Request/Response/Domain）
- ✅ API Service 已实现
- ✅ 认证集成完成
- ✅ 错误处理完整（400/401/404/429/5xx）
- ✅ 重试机制已配置
- ✅ ViewModel 集成完成
- ✅ 单元测试已生成
- ✅ 文档已更新（Backend-structure.md）
