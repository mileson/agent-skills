---
name: ios-test-script-generator
description: 为 iOS 和 Python 项目自动生成标准化的测试脚本，包括单元测试、集成测试和 API 测试，遵循项目的测试规范
---

# 测试脚本生成器

## When to Use

Use this skill when you need to:
- 为新功能或现有代码快速生成标准化的测试脚本
- 提升测试覆盖率和代码质量
- 新功能开发后生成测试用例
- 重构代码后补充测试
- 实施 TDD（测试驱动开发）流程

## Test Types Supported

### iOS 项目测试
- **单元测试**: XCTest，测试 ViewModel、Service、Manager
- **UI 测试**: XCUITest，测试用户交互流程
- **集成测试**: 测试模块间协作

### 后端项目测试
- **API 测试**: pytest，测试 API 端点
- **功能测试**: 测试业务逻辑
- **数据库测试**: 测试数据持久化

## Instructions

### iOS 单元测试

#### 步骤 1: 分析目标代码

识别需要测试的元素：

```swift
// 分析 ViewModel
class UserProfileViewModel: ObservableObject {
    @Published var user: User?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    func loadUserProfile() async { }
    func updateProfile(name: String) async { }
}

// 识别：
// - 3个状态属性需要测试
// - 2个异步方法需要测试
// - 需要测试成功和失败场景
```

#### 步骤 2: 生成单元测试模板

在 `[ProjectName]Tests/` 创建测试文件：

```swift
import XCTest
@testable import PoseCam

@MainActor
class UserProfileViewModelTests: XCTestCase {
    // MARK: - Properties
    var viewModel: UserProfileViewModel!
    var mockService: MockUserAPIService!
    
    // MARK: - Setup & Teardown
    override func setUp() async throws {
        try await super.setUp()
        mockService = MockUserAPIService()
        viewModel = UserProfileViewModel(service: mockService)
    }
    
    override func tearDown() async throws {
        viewModel = nil
        mockService = nil
        try await super.tearDown()
    }
    
    // MARK: - Initial State Tests
    func testInitialState() {
        XCTAssertNil(viewModel.user)
        XCTAssertFalse(viewModel.isLoading)
        XCTAssertNil(viewModel.errorMessage)
    }
    
    // MARK: - Load Profile Tests
    func testLoadUserProfile_Success() async {
        // Given
        let expectedUser = User(id: "1", name: "Test User")
        mockService.mockUser = expectedUser
        
        // When
        await viewModel.loadUserProfile()
        
        // Then
        XCTAssertEqual(viewModel.user?.id, expectedUser.id)
        XCTAssertEqual(viewModel.user?.name, expectedUser.name)
        XCTAssertFalse(viewModel.isLoading)
        XCTAssertNil(viewModel.errorMessage)
    }
    
    func testLoadUserProfile_Failure() async {
        // Given
        mockService.shouldFail = true
        
        // When
        await viewModel.loadUserProfile()
        
        // Then
        XCTAssertNil(viewModel.user)
        XCTAssertFalse(viewModel.isLoading)
        XCTAssertNotNil(viewModel.errorMessage)
    }
    
    func testLoadUserProfile_LoadingState() async {
        // Given
        mockService.shouldDelay = true
        
        // When
        Task {
            await viewModel.loadUserProfile()
        }
        
        // Then (检查加载状态)
        try? await Task.sleep(nanoseconds: 100_000_000) // 100ms
        XCTAssertTrue(viewModel.isLoading)
    }
    
    // MARK: - Update Profile Tests
    func testUpdateProfile_Success() async {
        // Given
        let newName = "Updated Name"
        mockService.mockUser = User(id: "1", name: "Old Name")
        
        // When
        await viewModel.updateProfile(name: newName)
        
        // Then
        XCTAssertEqual(viewModel.user?.name, newName)
        XCTAssertNil(viewModel.errorMessage)
    }
    
    func testUpdateProfile_EmptyName() async {
        // Given
        let emptyName = ""
        
        // When
        await viewModel.updateProfile(name: emptyName)
        
        // Then
        XCTAssertNotNil(viewModel.errorMessage)
        XCTAssertTrue(viewModel.errorMessage?.contains("名称不能为空") == true)
    }
}

// MARK: - Mock Service
class MockUserAPIService: UserAPIServiceProtocol {
    var mockUser: User?
    var shouldFail = false
    var shouldDelay = false
    
    func fetchUser() async throws -> User {
        if shouldDelay {
            try? await Task.sleep(nanoseconds: 500_000_000) // 500ms
        }
        
        if shouldFail {
            throw NSError(domain: "Test", code: -1)
        }
        
        guard let user = mockUser else {
            throw NSError(domain: "Test", code: -2)
        }
        
        return user
    }
    
    func updateUser(name: String) async throws -> User {
        if name.isEmpty {
            throw NSError(domain: "Test", code: -3, userInfo: [
                NSLocalizedDescriptionKey: "名称不能为空"
            ])
        }
        
        var user = mockUser ?? User(id: "1", name: name)
        user.name = name
        mockUser = user
        return user
    }
}
```

#### 步骤 3: 生成 UI 测试模板

在 `[ProjectName]UITests/` 创建 UI 测试：

```swift
import XCTest

class UserProfileUITests: XCTestCase {
    var app: XCUIApplication!
    
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments = ["UI-Testing"]
        app.launch()
    }
    
    override func tearDown() {
        app = nil
        super.tearDown()
    }
    
    func testNavigateToProfile() {
        // 点击设置 Tab
        let settingsTab = app.buttons["设置"]
        XCTAssertTrue(settingsTab.exists)
        settingsTab.tap()
        
        // 点击用户资料
        let profileButton = app.buttons["用户资料"]
        XCTAssertTrue(profileButton.waitForExistence(timeout: 2))
        profileButton.tap()
        
        // 验证进入资料页面
        let profileTitle = app.navigationBars["用户资料"]
        XCTAssertTrue(profileTitle.waitForExistence(timeout: 2))
    }
    
    func testEditProfile() {
        // 进入编辑页面
        navigateToProfile()
        
        // 点击编辑按钮
        let editButton = app.buttons["编辑"]
        XCTAssertTrue(editButton.exists)
        editButton.tap()
        
        // 修改名称
        let nameField = app.textFields["名称"]
        XCTAssertTrue(nameField.exists)
        nameField.tap()
        nameField.typeText("New Name")
        
        // 保存
        let saveButton = app.buttons["保存"]
        saveButton.tap()
        
        // 验证保存成功
        let successMessage = app.staticTexts["保存成功"]
        XCTAssertTrue(successMessage.waitForExistence(timeout: 3))
    }
    
    // MARK: - Helper Methods
    private func navigateToProfile() {
        let settingsTab = app.buttons["设置"]
        settingsTab.tap()
        let profileButton = app.buttons["用户资料"]
        profileButton.tap()
    }
}
```

### Python API 测试

#### 步骤 1: 生成 API 测试

在 `tests/api/` 创建测试文件：

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from tests.utils import create_test_user, get_auth_headers

# ============================================
# 创建用户测试
# ============================================

@pytest.mark.asyncio
async def test_create_user_success(
    client: AsyncClient,
    db: AsyncSession
):
    """测试成功创建用户"""
    # Given
    admin_user = await create_test_user(db, is_admin=True)
    headers = get_auth_headers(admin_user)
    
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "SecurePass123!"
    }
    
    # When
    response = await client.post(
        "/api/v1/users/",
        headers=headers,
        json=user_data
    )
    
    # Then
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "password" not in data  # 密码不应返回


@pytest.mark.asyncio
async def test_create_user_duplicate_email(
    client: AsyncClient,
    db: AsyncSession
):
    """测试创建重复邮箱的用户"""
    # Given
    existing_user = await create_test_user(db)
    admin_user = await create_test_user(db, is_admin=True)
    headers = get_auth_headers(admin_user)
    
    user_data = {
        "name": "New User",
        "email": existing_user.email,  # 重复邮箱
        "password": "SecurePass123!"
    }
    
    # When
    response = await client.post(
        "/api/v1/users/",
        headers=headers,
        json=user_data
    )
    
    # Then
    assert response.status_code == 409
    assert "已存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_user_invalid_email(
    client: AsyncClient,
    db: AsyncSession
):
    """测试无效邮箱格式"""
    # Given
    admin_user = await create_test_user(db, is_admin=True)
    headers = get_auth_headers(admin_user)
    
    user_data = {
        "name": "Test User",
        "email": "invalid-email",  # 无效格式
        "password": "SecurePass123!"
    }
    
    # When
    response = await client.post(
        "/api/v1/users/",
        headers=headers,
        json=user_data
    )
    
    # Then
    assert response.status_code == 422  # Validation Error


@pytest.mark.asyncio
async def test_create_user_unauthorized(
    client: AsyncClient,
    db: AsyncSession
):
    """测试未授权创建用户"""
    # Given
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "SecurePass123!"
    }
    
    # When (无认证头)
    response = await client.post(
        "/api/v1/users/",
        json=user_data
    )
    
    # Then
    assert response.status_code == 401
```

#### 步骤 2: 创建测试配置文件

在 `tests/conftest.py` 配置 pytest fixtures：

```python
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.config import settings
from app.models.base import Base

# ============================================
# Database Fixtures
# ============================================

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话"""
    # 创建测试数据库引擎
    engine = create_async_engine(
        settings.TEST_DATABASE_URL,
        echo=False
    )
    
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建会话
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    # 清理：删除所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """创建测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

## Test Coverage Scenarios

### 成功场景
- ✅ 正常输入，期望成功
- ✅ 边界值输入
- ✅ 特殊字符处理

### 失败场景
- ❌ 无效输入
- ❌ 缺少必需参数
- ❌ 权限不足
- ❌ 资源不存在
- ❌ 网络错误/超时

### 边界场景
- 🔢 最小值/最大值
- 🔢 空值/Null
- 🔢 并发操作

## Naming Conventions

```
# iOS XCTest
func test[功能]_[场景]_[期望结果]()

示例：
- testLoadUserProfile_Success()
- testLoadUserProfile_Failure()
- testUpdateProfile_EmptyName()

# Python pytest
def test_[功能]_[场景]()

示例：
- test_create_user_success()
- test_create_user_duplicate_email()
- test_list_users_with_pagination()
```

## Output Checklist

完成后确认：
- ✅ 测试文件已创建在正确目录
- ✅ Mock 对象已定义
- ✅ 成功和失败场景都已覆盖
- ✅ 断言逻辑清晰完整
- ✅ 测试命名符合规范
- ✅ Setup/Teardown 已实现
