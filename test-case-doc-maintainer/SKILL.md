---
name: test-case-doc-maintainer
description: 自动化测试用例文档维护工具，基于代码分析生成和更新测试用例文档，支持版本追踪、模拟执行和性能指标监控，适用于 iOS (XCTest) 和 Python (pytest) 项目
---

# 测试用例文档维护器 (Test Case Documentation Maintainer)

## When to Use

Use this skill when you need to:
- 为现有测试代码生成标准化的测试用例文档
- 在代码变更后更新测试文档并保留历史版本
- 生成包含性能指标和日志分析的测试报告
- 维护"始终最新（Always Green）"的测试文档
- 为 iOS (Swift/XCTest) 或 Python (pytest) 项目创建测试文档

## Skill Workflow Overview

```
用户触发 → 询问目标模块 → 分析测试代码 → 生成/更新文档 → 模拟执行 → 生成报告
    ↓            ↓                ↓               ↓              ↓           ↓
手动触发   明确范围        提取用例逻辑     增量版本追踪    静态分析    Markdown + HTML
```

## Prerequisites

### 项目结构要求

#### iOS 项目
- 测试代码位于 `[ProjectName]Tests/` 或 `[ProjectName]UITests/`
- 使用 XCTest 框架
- 测试方法命名符合规范：`test[功能]_[场景]_[期望结果]()`

#### Python 项目
- 测试代码位于 `tests/` 目录
- 使用 pytest 框架
- 测试函数命名符合规范：`test_[功能]_[场景]()`

### 文档存储位置
- iOS 文档：`/tests/docs/iOS/TEST-<ModuleName>.md`
- Python 文档：`/tests/docs/Python/TEST-<ModuleName>.md`
- 测试报告：`/tests/reports/<YYYY-MM-DD>/`

## Instructions

### Phase 1: 用户交互 - 明确目标模块

#### 步骤 1.1: 询问用户意图

当用户触发此 Skill 时，首先询问：

```
👋 您好！我将帮您生成或更新测试用例文档。

请告诉我以下信息：

1. **项目类型**：
   - [ ] iOS 项目（Swift/XCTest）
   - [ ] Python 后端项目（pytest）

2. **操作类型**：
   - [ ] 生成新的测试文档
   - [ ] 更新现有测试文档

3. **目标模块/功能**：
   请描述要生成文档的模块或功能，例如：
   - "用户认证模块"
   - "支付流程"
   - "AI 优化功能"

4. **测试文件路径**（可选）：
   如果知道具体测试文件，请提供，例如：
   - iOS: `PoseCamTests/Features/Auth/LoginViewModelTests.swift`
   - Python: `tests/api/test_auth.py`
```

#### 步骤 1.2: 验证信息完整性

确保获得：
- ✅ 项目类型明确
- ✅ 操作类型明确
- ✅ 模块名称清晰
- ✅ （可选）测试文件路径

如果信息不完整，继续追问直到清晰为止。

#### 步骤 1.3: 确认并展示执行计划

```
📋 确认信息：

- 项目类型：iOS (Swift/XCTest)
- 操作类型：生成新文档
- 目标模块：用户认证模块
- 测试文件：PoseCamTests/Features/Auth/LoginViewModelTests.swift

🎯 执行计划：

1. 分析测试代码文件（约 30 秒）
2. 提取测试用例和断言逻辑
3. 生成测试文档（包含 YAML 配置）
4. 模拟执行测试并生成报告
5. 生成 HTML 可视化报告

预计耗时：2-3 分钟

是否继续？(Y/n)
```

等待用户确认后再进入 Phase 2。

---

### Phase 2: 代码分析与用例提取

#### 步骤 2.1: 读取测试代码文件

根据用户提供的路径或通过搜索找到测试文件：

**iOS 项目搜索策略**：
```bash
# 搜索测试文件
find [ProjectName]Tests/ -name "*Tests.swift" | grep -i [ModuleName]
```

**Python 项目搜索策略**：
```bash
# 搜索测试文件
find tests/ -name "test_*.py" | grep -i [module_name]
```

#### 步骤 2.2: 解析测试代码结构

提取以下信息：

**iOS (Swift/XCTest)**：
```swift
// 识别元素
class LoginViewModelTests: XCTestCase {
    // ✅ 提取：测试类名称
    // ✅ 提取：Setup/TearDown 方法
    // ✅ 提取：所有 test* 方法
    
    func testLoginWithValidCredentials_Success() async {
        // ✅ 提取：方法名称 → 用例标题
        // ✅ 提取：Given 部分 → 前置条件
        // ✅ 提取：When 部分 → 测试步骤
        // ✅ 提取：Then 部分（断言）→ 预期结果
    }
}
```

**提取模板（iOS）**：
```
测试类：LoginViewModelTests
测试用例：testLoginWithValidCredentials_Success

前置条件（从代码推断）：
- mockService 已配置
- viewModel 已初始化
- 测试用户数据已准备

测试步骤（从代码提取）：
1. 设置 mockService.mockUser = User(id: "1", name: "Test")
2. 调用 await viewModel.login(email: "test@example.com", password: "Pass123!")
3. 等待异步操作完成

预期结果（从断言提取）：
- XCTAssertTrue(viewModel.isAuthenticated) → isAuthenticated = true
- XCTAssertNotNil(viewModel.user) → user 对象存在
- XCTAssertNil(viewModel.errorMessage) → errorMessage = nil
```

**Python (pytest)**：
```python
# 识别元素
@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient, db: AsyncSession):
    """测试成功创建用户"""  # ✅ 提取：Docstring → 用例描述
    
    # Given
    admin_user = await create_test_user(db, is_admin=True)  # ✅ 提取：前置条件
    
    # When
    response = await client.post("/api/v1/users/", ...)  # ✅ 提取：测试步骤
    
    # Then
    assert response.status_code == 201  # ✅ 提取：断言 → 预期结果
    assert data["name"] == user_data["name"]
```

**提取模板（Python）**：
```
测试函数：test_create_user_success
测试场景：测试成功创建用户（来自 docstring）

前置条件（从代码推断）：
- 管理员用户已创建
- 数据库会话已准备
- HTTP 客户端已配置

测试步骤（从代码提取）：
1. 创建管理员用户：create_test_user(db, is_admin=True)
2. 准备用户数据：{"name": "Test User", "email": "test@example.com"}
3. 发送 POST 请求到 /api/v1/users/
4. 携带认证头：headers = get_auth_headers(admin_user)

预期结果（从断言提取）：
- response.status_code == 201 → HTTP 状态码 201
- data["name"] == user_data["name"] → 用户名匹配
- "id" in data → 响应包含 ID
- "password" not in data → 响应不包含密码（安全检查）
```

#### 步骤 2.3: 性能指标提取（新增功能）

**iOS 项目 - 识别性能测试**：
```swift
// 识别 measure 块
func testSortingPerformance() {
    measure {  // ✅ 检测到性能测试
        _ = array.sorted()
    }
}

// 或识别 measure(metrics:) 块
measure(metrics: [XCTClockMetric(), XCTMemoryMetric()]) {
    // ✅ 提取：测量指标类型
    // ✅ 提取：预期基线（如有）
}
```

**提取性能指标信息**：
```yaml
performance_metrics:
  enabled: true
  metrics_type: ["execution_time", "memory"]
  baseline:
    execution_time: "0.5s"  # 从 Xcode baseline 提取
    memory: "10MB"
  tolerance: 10%  # 允许的偏差范围
```

**Python 项目 - 识别性能装饰器**：
```python
# 识别 pytest-benchmark 或自定义计时
@pytest.mark.benchmark
def test_api_performance(benchmark):
    result = benchmark(some_function)
    # ✅ 提取：性能测试标记
```

#### 步骤 2.4: 日志注入点识别（新增功能）

分析代码中的日志语句：

**iOS**：
```swift
// 识别日志语句
print("LoginViewModel: User authenticated successfully")  // ✅ 提取关键日志
os_log("Login failed: %@", log: .default, type: .error, error.localizedDescription)
```

**Python**：
```python
# 识别日志语句
logger.info("User created successfully with ID: %s", user.id)  # ✅ 提取关键日志
logger.error("Failed to create user: %s", str(e))
```

**提取日志信息**：
```yaml
key_logs:
  - level: "info"
    message: "LoginViewModel: User authenticated successfully with ID: {user_id}"
    trigger: "成功登录后"
  - level: "error"
    message: "LoginViewModel: Authentication failed - {error_reason}"
    trigger: "登录失败时"
```

---

### Phase 3: 文档生成与版本管理

#### 步骤 3.1: 检查文档是否已存在

```bash
# 检查文档路径
if [ -f "/tests/docs/iOS/TEST-Auth.md" ]; then
    echo "文档已存在，执行增量更新"
    MODE="UPDATE"
else
    echo "文档不存在，创建新文档"
    MODE="CREATE"
fi
```

#### 步骤 3.2: Git 版本信息提取

```bash
# 提取 Git 信息
LAST_COMMIT=$(git rev-parse --short HEAD)
COMMIT_MESSAGE=$(git log -1 --pretty=%B)
COMMIT_AUTHOR=$(git log -1 --pretty=%an)
COMMIT_DATE=$(git log -1 --pretty=%ai)

# 如果是更新模式，对比变更
if [ "$MODE" = "UPDATE" ]; then
    git diff HEAD~1:tests/docs/iOS/TEST-Auth.md HEAD:tests/docs/iOS/TEST-Auth.md
fi
```

#### 步骤 3.3: 版本号自动递增逻辑

```
当前版本：v1.2.3

变更类型判断：
1. 新增测试方法 → Minor 版本递增 → v1.3.0
2. 修改现有测试逻辑 → Patch 版本递增 → v1.2.4
3. 重构测试模块 → Major 版本递增 → v2.0.0
4. 仅修改文档内容 → Patch 版本递增 → v1.2.4

规则：
- Major (x.0.0): 测试模块重构，大量用例变更（>50%）
- Minor (0.x.0): 新增用例（新增测试方法）
- Patch (0.0.x): 修正用例细节、更新断言、文档修正
```

#### 步骤 3.4: 生成文档内容（完整格式）

基于 Phase 2 提取的信息，生成完整的 Markdown 文档：

**文档头部（YAML Frontmatter）**：
```yaml
---
# ========================================
# 测试用例文档配置 (Document Configuration)
# ========================================
config:
  test_case_style: "Structured Markdown"
  platform: "iOS"  # 或 "Python"
  framework: "XCTest"  # 或 "pytest"
  
  # 版本追踪配置
  version_tracking:
    enabled: true
    strategy: "incremental"
    git_integration: true
    
  # 报告输出配置
  report_output:
    enabled: true
    path: "/tests/reports/"
    filename_pattern: "{YYYY-MM-DD}_test_execution_report.md"
    html_enabled: true
    html_template_path: ".cursor/skills/test-case-doc-maintainer/html-report-template.md"
    
  # 执行行为
  execution_behavior:
    mode: "static_analysis"
    trigger: "在生成/更新测试用例后，必须单独输出一份测试报告"
  
  # 性能监控配置（新增）
  performance_monitoring:
    enabled: true
    metrics:
      - "execution_time"
      - "memory_usage"
      - "cpu_usage"
    baseline_comparison: true
    alert_threshold: 20  # 性能下降超过 20% 时警告

  # 日志配置（新增）
  logging:
    enabled: true
    log_level: "INFO"
    capture_key_logs: true
    include_in_report: true

# ========================================
# 文档元数据 (Document Metadata)
# ========================================
metadata:
  document_id: "TEST-Auth-20260122"
  module_name: "用户认证模块"
  created_date: "2026-01-10"
  last_updated: "2026-01-22"
  updated_by: "AI Agent"
  version: "v1.2.0"
  
  # Git 追踪信息
  git_tracking:
    last_commit: "abc1234"
    last_commit_message: "Add password validation test cases"
    last_commit_author: "John Doe"
    last_commit_date: "2026-01-22 14:30:00"
    branch: "feature/auth-tests"
    
  # 覆盖率统计
  coverage:
    total_test_cases: 15
    success_scenarios: 8
    failure_scenarios: 5
    edge_cases: 2
    performance_tests: 2  # 新增
    
  # 性能基线（新增）
  performance_baseline:
    last_updated: "2026-01-22"
    execution_time_avg: "0.45s"
    memory_peak: "8.5MB"
    cpu_usage_avg: "15%"
---
```

**文档主体（Markdown 内容）**：
```markdown
# 模块：用户认证模块 (User Authentication Module)

## 1. 测试套件概述 (Test Suite Overview)

**测试范围**：用户登录、注册、密码找回功能  
**覆盖文件**：
- iOS: `PoseCamTests/Features/Auth/LoginViewModelTests.swift`
- Python: `tests/api/test_auth.py`

**依赖项**：
- Mock: UserAPIService (iOS) / UserRepository (Python)
- 测试数据: fixtures/auth_test_data.json

**性能要求**（新增）：
- 登录响应时间：< 500ms
- 内存占用：< 10MB
- CPU 使用率：< 20%

---

## 2. 测试用例清单 (Test Case List)

### 2.1 登录功能测试 (Login Feature Tests)

#### 2.1.1 成功登录 - 有效凭证

**测试场景**: 用户使用正确的邮箱和密码登录  
**前置条件**:
- 用户账户已存在于数据库
- 账户状态为激活状态
- 网络连接正常

**测试步骤** (iOS):
1. 设置 Mock 数据：`mockService.mockUser = User(id: "1", name: "Test")`
2. 调用登录方法：`await viewModel.login(email: "test@example.com", password: "SecurePass123!")`
3. 等待异步操作完成（await）
4. 检查 `viewModel.isAuthenticated` 状态

**预期结果**:
- `isAuthenticated = true`
- `errorMessage = nil`
- `user != nil`，且 `user.id = "1"`
- **关键日志**（新增）：`"LoginViewModel: User authenticated successfully with ID: 1"`
- **性能指标**（新增）：执行时间 < 500ms，内存占用 < 5MB

**实际结果** (模拟):
- ✅ Pass - 所有断言通过
- **执行时间**（新增）：0.35s
- **内存占用**（新增）：3.2MB
- **CPU 使用率**（新增）：12%
- **关键日志**（新增）：
  ```
  [INFO] LoginViewModel: Starting authentication
  [INFO] MockService: Fetching user data
  [INFO] LoginViewModel: User authenticated successfully with ID: 1
  ```

**版本历史**:
| 版本 | 日期 | 修改说明 | Git Commit |
|------|------|----------|------------|
| v1.0.0 | 2026-01-10 | 初始创建 | `def4567` |
| v1.1.0 | 2026-01-15 | 增加 Token 过期时间验证 | `ghi8901` |
| v1.2.0 | 2026-01-22 | 更新为 async/await 语法，增加性能指标 | `abc1234` |

---

#### 2.1.2 登录失败 - 无效密码

**测试场景**: 用户使用正确的邮箱但错误的密码登录  
**前置条件**:
- 用户账户已存在于数据库
- 输入的密码与数据库中的密码不匹配

**测试步骤** (iOS):
1. 设置 Mock 失败状态：`mockService.shouldFail = true`
2. 调用登录方法：`await viewModel.login(email: "test@example.com", password: "WrongPassword")`
3. 等待异步操作完成
4. 检查错误消息

**预期结果**:
- `isAuthenticated = false`
- `errorMessage = "密码错误，请重试"`
- `user = nil`
- **关键日志**（新增）：`"LoginViewModel: Authentication failed - Invalid password"`
- **失败次数记录**：+1（5 次失败后锁定账户）

**实际结果** (模拟):
- ✅ Pass - 错误处理逻辑正确
- **执行时间**（新增）：0.15s（失败路径更快）
- **关键日志**（新增）：
  ```
  [INFO] LoginViewModel: Starting authentication
  [ERROR] MockService: Invalid password provided
  [ERROR] LoginViewModel: Authentication failed - Invalid password
  [INFO] LoginViewModel: Failed login attempts: 1/5
  ```

**版本历史**:
| 版本 | 日期 | 修改说明 | Git Commit |
|------|------|----------|------------|
| v1.0.0 | 2026-01-10 | 初始创建 | `def4567` |
| v1.1.0 | 2026-01-18 | 增加账户锁定机制验证 | `jkl2345` |

---

### 2.2 性能测试 (Performance Tests)（新增章节）

#### 2.2.1 登录性能基准测试

**测试场景**: 测量登录流程的性能指标  
**前置条件**:
- 使用真实网络环境（非 Mock）
- 测试数据已准备

**性能目标**:
- 执行时间：< 500ms (p95)
- 内存占用：< 10MB
- CPU 使用率：< 20%

**测试代码** (iOS):
```swift
func testLoginPerformance() {
    measure(metrics: [XCTClockMetric(), XCTMemoryMetric(), XCTCPUMetric()]) {
        await viewModel.login(email: "test@example.com", password: "Pass123!")
    }
}
```

**实际结果** (模拟):
- ✅ Pass - 性能符合预期
- **平均执行时间**：0.42s (基线: 0.45s, 改善 6.7%)
- **峰值内存**：7.8MB (基线: 8.5MB, 改善 8.2%)
- **平均 CPU**：13% (基线: 15%, 改善 13.3%)

**性能趋势**（新增）：
```
版本      执行时间    内存占用    CPU 使用
v1.0.0    0.58s      9.2MB       18%
v1.1.0    0.50s      8.5MB       15%
v1.2.0    0.42s      7.8MB       13%  ← 当前版本
```

---

## 3. 测试覆盖率矩阵 (Test Coverage Matrix)

| 功能模块 | 成功场景 | 失败场景 | 边界场景 | 性能测试 | 覆盖率 |
|---------|---------|---------|---------|---------|--------|
| 用户登录 | 2 | 3 | 1 | 1 | 95% |
| 密码验证 | 1 | 2 | 2 | 0 | 90% |
| 注册流程 | 3 | 4 | 1 | 0 | 88% |
| 密码找回 | 2 | 2 | 1 | 0 | 85% |

---

## 4. 关键日志索引 (Key Logs Index)（新增章节）

### 4.1 成功路径日志

| 日志级别 | 日志消息 | 触发条件 | 包含信息 |
|---------|---------|---------|---------|
| INFO | `LoginViewModel: User authenticated successfully with ID: {user_id}` | 登录成功 | 用户 ID |
| INFO | `TokenManager: Access token generated, expires in: {seconds}s` | Token 生成 | 过期时间 |
| INFO | `UserSession: Session created for user: {user_email}` | 会话创建 | 用户邮箱 |

### 4.2 失败路径日志

| 日志级别 | 日志消息 | 触发条件 | 包含信息 |
|---------|---------|---------|---------|
| ERROR | `LoginViewModel: Authentication failed - {error_reason}` | 登录失败 | 失败原因 |
| WARN | `LoginViewModel: Failed login attempts: {count}/5` | 失败尝试 | 失败次数 |
| ERROR | `NetworkManager: Request timeout after {duration}s` | 网络超时 | 超时时长 |

### 4.3 性能相关日志

| 日志级别 | 日志消息 | 触发条件 | 包含信息 |
|---------|---------|---------|---------|
| DEBUG | `PerformanceMonitor: Login completed in {duration}ms` | 操作完成 | 执行时间 |
| WARN | `PerformanceMonitor: Memory usage high: {memory}MB` | 内存告警 | 内存占用 |
| WARN | `PerformanceMonitor: CPU usage spike: {cpu}%` | CPU 告警 | CPU 使用率 |

---

## 5. 性能监控配置 (Performance Monitoring Config)（新增章节）

### 5.1 监控指标定义

```yaml
metrics:
  execution_time:
    unit: "seconds"
    baseline: 0.45
    threshold_warning: 0.54  # +20%
    threshold_critical: 0.63  # +40%
    
  memory_usage:
    unit: "MB"
    baseline: 8.5
    threshold_warning: 10.2  # +20%
    threshold_critical: 11.9  # +40%
    
  cpu_usage:
    unit: "percent"
    baseline: 15
    threshold_warning: 18  # +20%
    threshold_critical: 21  # +40%
```

### 5.2 性能告警规则

```yaml
alert_rules:
  - name: "Slow Login Detection"
    condition: "execution_time > threshold_warning"
    action: "Log warning, notify team"
    
  - name: "Memory Leak Detection"
    condition: "memory_usage increases over 5 consecutive runs"
    action: "Log critical, trigger investigation"
    
  - name: "CPU Spike Detection"
    condition: "cpu_usage > threshold_critical"
    action: "Log critical, check background tasks"
```

---

## 6. 待办事项 (TODO)

- [ ] 补充双因素认证测试用例
- [ ] 增加并发登录场景测试
- [ ] 优化 Mock 数据生成逻辑
- [ ] 建立性能回归测试基线
- [ ] 集成日志分析工具（如 ELK）

---

## 7. 附录 (Appendix)

### 7.1 测试数据示例

```json
{
  "valid_user": {
    "email": "test@example.com",
    "password": "SecurePass123!",
    "expected_user_id": "12345"
  },
  "invalid_user": {
    "email": "test@example.com",
    "password": "WrongPassword"
  }
}
```

### 7.2 关键配置参数

| 参数名 | 值 | 说明 |
|--------|---|------|
| `TOKEN_EXPIRY` | 3600s | Access Token 过期时间 |
| `MAX_LOGIN_ATTEMPTS` | 5 | 账户锁定前的最大失败次数 |
| `MIN_PASSWORD_LENGTH` | 8 | 密码最小长度 |
| `PERFORMANCE_BASELINE_DATE` | 2026-01-22 | 性能基线建立日期 |

### 7.3 性能基线变更历史

| 版本 | 日期 | 执行时间 | 内存占用 | CPU 使用 | 备注 |
|------|------|---------|---------|---------|------|
| v1.0.0 | 2026-01-10 | 0.58s | 9.2MB | 18% | 初始基线 |
| v1.1.0 | 2026-01-15 | 0.50s | 8.5MB | 15% | 优化网络请求 |
| v1.2.0 | 2026-01-22 | 0.42s | 7.8MB | 13% | 改用 async/await |
```

---

### Phase 4: 模拟测试执行

#### 步骤 4.1: 静态分析执行

基于提取的断言逻辑，模拟测试执行结果：

**分析逻辑**：
```
对于每个测试用例：
1. 检查断言类型：
   - XCTAssertTrue/assert True → 预期通过
   - XCTAssertEqual/assert == → 检查值是否合理
   - XCTAssertNil/assert is None → 检查空值处理
   
2. 检查错误处理：
   - 是否有 try-catch / do-catch
   - 是否有错误路径测试
   
3. 推断结果：
   - 断言合理 + 错误处理完善 → ✅ Pass
   - 断言可疑 + 无错误处理 → ⚠️ Warning
   - 逻辑矛盾 → ❌ Fail (Predicted)
```

**示例分析**：
```swift
// 用例：testLoginWithValidCredentials_Success
func testLoginWithValidCredentials_Success() async {
    // Given
    mockService.mockUser = User(id: "1", name: "Test")  // ✅ 数据准备合理
    
    // When
    await viewModel.login(email: "test@example.com", password: "Pass123!")
    
    // Then
    XCTAssertTrue(viewModel.isAuthenticated)  // ✅ 断言明确
    XCTAssertNotNil(viewModel.user)  // ✅ 断言明确
    XCTAssertNil(viewModel.errorMessage)  // ✅ 断言明确
}

分析结果：
- 数据准备：完整 ✅
- 断言覆盖：全面（3 个断言）✅
- 错误处理：隐式（通过 Mock）✅
- 推断结果：✅ Pass (高置信度)
```

#### 步骤 4.2: 性能指标模拟（新增）

基于历史数据和代码复杂度，模拟性能指标：

**模拟算法**：
```
执行时间估算：
1. 基础时间：0.1s（网络请求）
2. 数据处理：0.05s * 数据量级
3. UI 更新：0.02s（如有）
4. 总计：基础 + 数据 + UI

内存占用估算：
1. 基础内存：2MB（ViewModel）
2. 数据内存：1MB * 对象数量
3. Mock 数据：0.5MB
4. 总计：基础 + 数据 + Mock

CPU 使用率估算：
1. 轻量操作（简单赋值）：5%
2. 中等操作（数据转换）：10-15%
3. 重度操作（加密、图像处理）：20-30%
```

**示例模拟**：
```yaml
testLoginWithValidCredentials_Success:
  execution_time:
    estimated: "0.35s"
    breakdown:
      - network_mock: "0.10s"
      - data_processing: "0.15s"
      - state_update: "0.08s"
      - assertion: "0.02s"
    compared_to_baseline: "-22%"  # 比基线快
    
  memory_usage:
    estimated: "3.2MB"
    breakdown:
      - viewmodel: "2.0MB"
      - mock_service: "0.5MB"
      - test_data: "0.7MB"
    compared_to_baseline: "-62%"  # 比基线少
    
  cpu_usage:
    estimated: "12%"
    peak: "18%"
    average: "12%"
    compared_to_baseline: "-20%"  # 比基线低
```

#### 步骤 4.3: 日志分析（新增）

从代码中提取的日志语句，模拟执行时的日志输出：

**日志生成规则**：
```
1. 按代码执行顺序排列日志
2. 根据条件分支决定输出哪些日志
3. 为动态值（如 ID）生成占位符
4. 标注日志级别（INFO/WARN/ERROR）
```

**示例日志输出**：
```
成功场景（testLoginWithValidCredentials_Success）：
---------------------------------------------------
[2026-01-22 14:30:00.123] [INFO] LoginViewModel: Starting authentication
[2026-01-22 14:30:00.234] [DEBUG] MockService: Fetching user data for email: test@example.com
[2026-01-22 14:30:00.345] [INFO] MockService: User found with ID: 1
[2026-01-22 14:30:00.456] [INFO] TokenManager: Generating access token
[2026-01-22 14:30:00.567] [INFO] TokenManager: Access token generated, expires in: 3600s
[2026-01-22 14:30:00.678] [INFO] LoginViewModel: User authenticated successfully with ID: 1
[2026-01-22 14:30:00.789] [INFO] UserSession: Session created for user: test@example.com
[2026-01-22 14:30:00.890] [DEBUG] PerformanceMonitor: Login completed in 350ms

失败场景（testLoginWithInvalidPassword_Failure）：
---------------------------------------------------
[2026-01-22 14:31:00.123] [INFO] LoginViewModel: Starting authentication
[2026-01-22 14:31:00.234] [DEBUG] MockService: Fetching user data for email: test@example.com
[2026-01-22 14:31:00.345] [ERROR] MockService: Invalid password provided
[2026-01-22 14:31:00.456] [ERROR] LoginViewModel: Authentication failed - Invalid password
[2026-01-22 14:31:00.567] [INFO] LoginViewModel: Failed login attempts: 1/5
[2026-01-22 14:31:00.678] [DEBUG] PerformanceMonitor: Login completed in 150ms
```

---

### Phase 5: 报告生成

#### 步骤 5.1: 生成 Markdown 报告

基于模拟执行结果，生成测试报告：

**报告路径**：`/tests/reports/2026-01-22/TEST-Auth-execution-report.md`

**报告内容**：
```markdown
# [2026-01-22] 用户认证模块 - 测试执行报告

## 1. 概览 (Summary)

| 指标 | 结果 |
|------|------|
| **执行时间** | 2026-01-22 14:30:00 |
| **覆盖模块** | 用户认证模块 |
| **总用例数** | 15 |
| **通过** | 13 (87%) |
| **失败** | 2 (13%) |
| **跳过** | 0 |
| **性能测试** | 2 |
| **测试结果** | ⚠️ 部分失败 |

### 性能摘要（新增）

| 指标 | 平均值 | 基线 | 变化 | 状态 |
|------|--------|------|------|------|
| **执行时间** | 0.42s | 0.45s | -6.7% | ✅ 改善 |
| **内存占用** | 7.8MB | 8.5MB | -8.2% | ✅ 改善 |
| **CPU 使用** | 13% | 15% | -13.3% | ✅ 改善 |

---

## 2. 详细结果 (Details)

| ID | 用例标题 | 状态 | 执行时间 | 内存 | 关键日志/根因分析 |
|----|---------|------|---------|------|-------------------|
| 2.1.1 | 成功登录 - 有效凭证 | ✅ Pass | 0.35s | 3.2MB | 断言通过，Token 生成正常 |
| 2.1.2 | 登录失败 - 无效密码 | ✅ Pass | 0.15s | 2.5MB | 错误处理符合预期 |
| 2.2.1 | 密码强度检查 - 弱密码 | ❌ Fail | 0.08s | 1.8MB | 预期抛出异常，实际返回 None |
| 2.2.2 | 登录性能基准测试 | ✅ Pass | 0.42s | 7.8MB | 性能改善 6.7%，符合目标 |

---

## 3. 失败用例分析 (Failure Analysis)

### 2.2.1 密码强度检查 - 弱密码

**失败原因**：密码验证逻辑未正确抛出异常  
**代码位置**：`backend/app/utils/validators.py:45`  
**预期行为**：当密码长度不足时，应抛出 `ValidationError`  
**实际行为**：返回 `None`

**关键日志**：
```
[ERROR] PasswordValidator: Validation failed but no exception raised
[WARN] PasswordValidator: Length check returned None instead of raising error
```

**建议修复**：
```python
# 当前代码（错误）
if len(password) < MIN_LENGTH:
    return None  # ❌ 不应返回 None

# 建议修改（正确）
if len(password) < MIN_LENGTH:
    raise ValidationError(f"密码长度不足，至少需要 {MIN_LENGTH} 位")  # ✅ 抛出异常
```

**影响范围**：
- 影响用例数：1
- 影响功能：密码验证
- 严重程度：中等（功能可用但错误处理不当）

---

## 4. 性能趋势分析（新增章节）

### 4.1 执行时间趋势

```
执行时间（秒）
0.60 ┤
0.55 ┤ ●
0.50 ┤   ●
0.45 ┤     ●
0.40 ┤       ● ← 当前版本
0.35 ┤
0.30 ┤
     └─────────────────────
     v1.0  v1.1  v1.2
```

**分析**：
- v1.0 → v1.1: 优化网络请求，提升 13.8%
- v1.1 → v1.2: 改用 async/await，提升 16.0%
- 总体提升：27.6%（相比 v1.0）

### 4.2 内存占用趋势

```
内存占用（MB）
10.0 ┤
 9.0 ┤ ●
 8.5 ┤   ●
 8.0 ┤     ● ← 当前版本
 7.5 ┤
 7.0 ┤
     └─────────────────────
     v1.0  v1.1  v1.2
```

**分析**：
- 内存占用持续优化
- v1.2 相比 v1.0 减少 15.2%
- 建议：继续监控，确保无内存泄漏

### 4.3 性能告警

| 告警级别 | 告警内容 | 触发条件 | 当前状态 |
|---------|---------|---------|---------|
| 🟢 正常 | 执行时间 | < 0.54s | 0.42s ✅ |
| 🟢 正常 | 内存占用 | < 10.2MB | 7.8MB ✅ |
| 🟢 正常 | CPU 使用 | < 18% | 13% ✅ |

**结论**：所有性能指标均在健康范围内，无告警。

---

## 5. 关键日志统计（新增章节）

### 5.1 日志级别分布

| 级别 | 数量 | 占比 |
|------|------|------|
| INFO | 45 | 60% |
| DEBUG | 18 | 24% |
| WARN | 8 | 11% |
| ERROR | 4 | 5% |
| **总计** | **75** | **100%** |

### 5.2 高频日志 Top 5

| 排名 | 日志消息 | 出现次数 | 平均间隔 |
|------|---------|---------|---------|
| 1 | `LoginViewModel: Starting authentication` | 15 | 每个测试 |
| 2 | `PerformanceMonitor: Login completed in {X}ms` | 15 | 每个测试 |
| 3 | `LoginViewModel: User authenticated successfully` | 13 | 成功场景 |
| 4 | `LoginViewModel: Authentication failed` | 2 | 失败场景 |
| 5 | `TokenManager: Access token generated` | 13 | Token 生成 |

### 5.3 错误日志详情

| 时间 | 级别 | 消息 | 用例 |
|------|------|------|------|
| 14:31:00.345 | ERROR | `MockService: Invalid password provided` | 2.1.2 |
| 14:32:15.678 | ERROR | `PasswordValidator: Validation failed but no exception raised` | 2.2.1 |
| 14:33:22.123 | WARN | `PerformanceMonitor: Memory usage spike detected: 9.5MB` | 2.3.1 |

---

## 6. 版本变更追踪 (Version Changelog)

### 本次新增用例 (v1.2.0)
- [+] 2.2.2 登录性能基准测试（新增性能测试）

### 本次修改用例
- [~] 2.1.1 成功登录 - 更新为 async/await 语法
- [~] 2.1.2 登录失败 - 增加失败次数记录验证

### 本次删除用例
无

### 性能基线更新（新增）
- 执行时间基线：0.45s → 0.42s (-6.7%)
- 内存基线：8.5MB → 7.8MB (-8.2%)
- CPU 基线：15% → 13% (-13.3%)

---

## 7. 行动建议 (Action Items)

### 立即修复（高优先级）
1. 🔴 **修复 2.2.1 失败用例**（预计 10 分钟）
   - 位置：`backend/app/utils/validators.py:45`
   - 任务：将 `return None` 改为 `raise ValidationError(...)`
   - 负责人：待分配

### 近期优化（中优先级）
2. 🟡 **补充双因素认证测试用例**（预计 1 小时）
   - 覆盖 2FA 登录流程
   - 包含性能测试

3. 🟡 **优化测试数据生成逻辑**（预计 30 分钟）
   - 使用 Factory Pattern 生成 Mock 数据
   - 减少重复代码

### 长期改进（低优先级）
4. 🟢 **建立性能回归测试基线**（预计 2 小时）
   - 集成到 CI/CD 流程
   - 自动检测性能退化

5. 🟢 **集成日志分析工具**（预计 4 小时）
   - 集成 ELK Stack 或类似工具
   - 实现实时日志监控

---

## 8. 附录 (Appendix)

### 8.1 完整日志输出

<details>
<summary>展开查看完整日志（75 行）</summary>

```
[2026-01-22 14:30:00.123] [INFO] LoginViewModel: Starting authentication
[2026-01-22 14:30:00.234] [DEBUG] MockService: Fetching user data for email: test@example.com
...
（完整日志内容）
```

</details>

### 8.2 性能原始数据

<details>
<summary>展开查看性能数据详情</summary>

```json
{
  "test_cases": [
    {
      "id": "2.1.1",
      "execution_time": 0.35,
      "memory_peak": 3.2,
      "cpu_avg": 12,
      "iterations": 10
    },
    ...
  ]
}
```

</details>

---

**报告生成时间**：2026-01-22 14:35:00  
**文档版本**：v1.2.0  
**Git Commit**：abc1234
```

#### 步骤 5.2: 生成 HTML 报告

调用 HTML 模板提示词生成可视化报告。

**操作流程**：
1. 读取 HTML 模板提示词文件：`.cursor/skills/test-case-doc-maintainer/html-report-template.md`
2. 将 Markdown 报告作为输入传递给模板提示词
3. 执行提示词，生成 HTML 文件
4. 保存到：`/tests/reports/2026-01-22/TEST-Auth-execution-report.html`

**提示词调用示例**：
```
请根据以下 Markdown 测试报告，生成 HTML 可视化报告：

[此处插入完整的 Markdown 报告内容]

要求：
1. 按照 html-report-template.md 中定义的样式和结构
2. 包含交互功能（筛选、搜索、折叠）
3. 生成单个 HTML 文件（内联 CSS/JS）
4. 文件大小 < 500KB
```

---

## Output Checklist

完成后确认：
- ✅ 用户意图已明确（Phase 1）
- ✅ 测试代码已分析（Phase 2）
- ✅ 文档已生成/更新（Phase 3）
- ✅ 版本号已自动递增
- ✅ Git 信息已记录
- ✅ 模拟执行已完成（Phase 4）
- ✅ 性能指标已模拟
- ✅ 关键日志已提取
- ✅ Markdown 报告已生成（Phase 5）
- ✅ HTML 报告已生成
- ✅ 文档路径符合规范

## Best Practices

### 文档维护原则
1. **增量更新，保留历史**：每次更新都记录在版本历史表中
2. **版本号语义化**：遵循 Semantic Versioning
3. **Git 集成**：每次更新记录 Git 信息
4. **性能基线管理**：定期更新性能基线，追踪趋势

### 性能监控原则（新增）
1. **建立基线**：首次运行时建立性能基线
2. **持续监控**：每次更新都对比基线
3. **告警机制**：性能下降超过 20% 时触发告警
4. **趋势分析**：保留历史数据，分析性能趋势

### 日志管理原则（新增）
1. **分级记录**：INFO（正常流程）、WARN（警告）、ERROR（错误）
2. **结构化日志**：包含时间戳、级别、模块、消息
3. **关键日志索引**：为常见日志建立索引，便于查找
4. **日志统计**：分析日志分布，发现异常模式

### 代码分析原则
1. **静态分析优先**：不实际运行测试，基于代码推断
2. **断言驱动**：从断言逻辑推断预期结果
3. **日志追踪**：提取代码中的日志语句，模拟执行流
4. **性能估算**：基于代码复杂度估算性能指标

## Troubleshooting

### 问题 1：无法找到测试文件

**症状**：提示"未找到测试文件"

**解决方案**：
```
1. 检查文件路径是否正确
2. 检查文件命名是否符合规范：
   - iOS: *Tests.swift
   - Python: test_*.py
3. 使用搜索功能定位文件：
   - find [ProjectName]Tests/ -name "*.swift"
   - find tests/ -name "test_*.py"
```

### 问题 2：Git 信息提取失败

**症状**：文档中 Git 信息显示为空

**解决方案**：
```
1. 检查是否在 Git 仓库中：git status
2. 检查是否有提交记录：git log
3. 如果是新仓库，先进行一次提交
```

### 问题 3：性能指标异常（新增）

**症状**：模拟的性能指标明显不合理

**解决方案**：
```
1. 检查历史基线是否存在
2. 如果是首次运行，使用默认值
3. 手动调整基线：
   编辑文档的 YAML Frontmatter 中的 performance_baseline
```

### 问题 4：HTML 报告生成失败（新增）

**症状**：Markdown 报告正常，但 HTML 报告未生成

**解决方案**：
```
1. 检查 html-report-template.md 文件是否存在
2. 检查 Markdown 报告格式是否正确
3. 手动调用模板提示词进行调试
4. 检查生成的 HTML 文件大小是否超过限制
```

## Advanced Features

### 功能 1：批量更新多个模块

```
如果用户需要同时更新多个模块的测试文档：

1. 询问模块列表：
   "请列出要更新的模块，用逗号分隔，例如：
    用户认证模块, 支付流程, AI 优化功能"

2. 依次处理每个模块：
   for module in modules:
       execute_skill(module)

3. 生成汇总报告：
   合并所有模块的报告，生成项目级测试报告
```

### 功能 2：性能回归检测（新增）

```
自动检测性能退化：

1. 对比当前性能与基线
2. 如果任何指标下降 > 20%，触发告警
3. 生成性能回归报告：
   - 列出退化的用例
   - 分析可能的原因
   - 提供优化建议
```

### 功能 3：日志异常检测（新增）

```
分析日志模式，检测异常：

1. 统计日志级别分布
2. 检测异常模式：
   - ERROR 日志突然增加
   - WARN 日志频繁出现
   - 日志缺失（预期有但实际没有）
3. 生成异常报告
```

### 功能 4：测试用例推荐

```
基于现有用例，推荐缺失的测试场景：

1. 分析现有用例覆盖的场景
2. 识别缺失的边界场景：
   - 空值处理
   - 并发场景
   - 异常情况
3. 生成推荐清单
```

## Integration with Other Skills

### 与 `ios-test-script-generator` 集成
- `ios-test-script-generator` 生成测试脚本
- `test-case-doc-maintainer` 为测试脚本生成文档
- 配合使用：先生成脚本，再生成文档

### 与 `doc-auto-sync-checker` 集成
- `doc-auto-sync-checker` 检查文档同步状态
- `test-case-doc-maintainer` 负责更新测试文档
- 配合使用：检查器发现需要更新时，调用维护器

### 与 CI/CD 流程集成（未来扩展）
- 在 PR 提交时自动检查测试文档是否更新
- 在测试运行后自动生成报告
- 性能退化时自动触发告警

## Example Usage

### 示例 1：为新模块生成测试文档

```
用户：请帮我生成用户认证模块的测试文档

AI：
👋 您好！我将帮您生成测试用例文档。

请确认以下信息：
1. 项目类型：iOS 项目（Swift/XCTest）✅
2. 操作类型：生成新的测试文档 ✅
3. 目标模块：用户认证模块 ✅
4. 测试文件路径：需要您提供

请提供测试文件路径，或告诉我模块在哪个目录下，我来帮您搜索。

用户：在 PoseCamTests/Features/Auth/

AI：
好的，我找到了以下测试文件：
- PoseCamTests/Features/Auth/LoginViewModelTests.swift
- PoseCamTests/Features/Auth/RegisterViewModelTests.swift

请问要为哪个文件生成文档，还是全部生成？

用户：LoginViewModelTests.swift

AI：
📋 确认信息：
- 项目类型：iOS (Swift/XCTest)
- 操作类型：生成新文档
- 目标模块：用户认证模块 - 登录功能
- 测试文件：PoseCamTests/Features/Auth/LoginViewModelTests.swift

🎯 执行计划：
1. 分析测试代码文件（约 30 秒）
2. 提取测试用例和断言逻辑
3. 生成测试文档（包含 YAML 配置）
4. 模拟执行测试并生成报告
5. 生成 HTML 可视化报告

预计耗时：2-3 分钟

是否继续？(Y/n)

用户：Y

AI：
✅ 开始执行...

[Phase 1] 正在读取测试代码文件...
[Phase 2] 正在分析代码结构，提取测试用例...
  - 发现 8 个测试方法
  - 发现 2 个性能测试
  - 提取 15 个关键日志点
[Phase 3] 正在生成测试文档...
  - 文档版本：v1.0.0（首次创建）
  - 文档路径：/tests/docs/iOS/TEST-Auth-Login.md
[Phase 4] 正在模拟测试执行...
  - 模拟完成，8 个用例全部通过 ✅
  - 性能指标已估算
  - 日志输出已生成
[Phase 5] 正在生成报告...
  - Markdown 报告：/tests/reports/2026-01-22/TEST-Auth-Login-report.md ✅
  - HTML 报告：/tests/reports/2026-01-22/TEST-Auth-Login-report.html ✅

🎉 完成！

已生成以下文件：
1. 测试文档：/tests/docs/iOS/TEST-Auth-Login.md
2. Markdown 报告：/tests/reports/2026-01-22/TEST-Auth-Login-report.md
3. HTML 报告：/tests/reports/2026-01-22/TEST-Auth-Login-report.html

📊 摘要：
- 总用例数：8
- 通过率：100%
- 性能测试：2
- 平均执行时间：0.42s
- 平均内存占用：7.8MB

💡 建议：
- 建议补充边界场景测试（空值处理、并发场景）
- 建议建立性能回归测试基线
```

### 示例 2：更新现有测试文档

```
用户：代码有变更，请更新用户认证模块的测试文档

AI：
👋 检测到您要更新现有文档。

正在检查 Git 变更...
发现以下变更：
- 修改：PoseCamTests/Features/Auth/LoginViewModelTests.swift
- 新增方法：testLoginWithBiometrics_Success()
- 修改方法：testLoginWithValidCredentials_Success()（改用 async/await）

📋 确认信息：
- 项目类型：iOS (Swift/XCTest)
- 操作类型：更新现有文档
- 目标模块：用户认证模块 - 登录功能
- 当前版本：v1.1.0
- 新版本：v1.2.0（Minor 递增，因为新增了用例）

是否继续更新？(Y/n)

用户：Y

AI：
✅ 开始更新...

[Phase 2] 正在分析代码变更...
  - 识别到 1 个新增测试方法
  - 识别到 1 个修改的测试方法
[Phase 3] 正在更新文档...
  - 追加新用例：2.1.3 生物识别登录 - 成功
  - 更新现有用例：2.1.1 成功登录（语法更新）
  - 版本号：v1.1.0 → v1.2.0
  - Git Commit：abc1234
[Phase 4] 正在模拟测试执行...
  - 9 个用例全部通过 ✅
  - 性能对比基线：执行时间改善 6.7%
[Phase 5] 正在生成报告...

🎉 更新完成！

变更摘要：
- 新增用例：1
- 修改用例：1
- 删除用例：0
- 版本号：v1.1.0 → v1.2.0

性能变化：
- 执行时间：0.45s → 0.42s (-6.7%) ✅
- 内存占用：8.5MB → 7.8MB (-8.2%) ✅
- CPU 使用：15% → 13% (-13.3%) ✅

📄 已更新文件：
1. 测试文档：/tests/docs/iOS/TEST-Auth-Login.md
2. Markdown 报告：/tests/reports/2026-01-22/TEST-Auth-Login-report.md
3. HTML 报告：/tests/reports/2026-01-22/TEST-Auth-Login-report.html
```

## Limitations

1. **静态分析限制**：
   - 只能模拟测试结果，无法发现实际运行时的问题
   - 性能指标为估算值，与实际可能有偏差

2. **代码理解限制**：
   - 对于复杂的逻辑（如复杂的条件分支），可能无法准确提取
   - Mock 对象的行为需要从代码推断

3. **语言支持限制**：
   - 当前仅支持 Swift/XCTest 和 Python/pytest
   - 其他语言/框架需要扩展

4. **性能监控限制**（新增）：
   - 性能指标为模拟值，不是实际测量值
   - 无法检测内存泄漏等运行时问题
   - 建议配合实际性能测试工具使用

5. **日志分析限制**（新增）：
   - 只能提取代码中的日志语句，无法获取实际运行时日志
   - 动态日志（如条件日志）可能无法准确模拟

## Future Enhancements

1. **实际测试执行**：
   - 集成 XCTest / pytest 运行器
   - 支持真实测试执行和结果收集

2. **更多语言支持**：
   - JavaScript (Jest/Mocha)
   - Java (JUnit)
   - Go (testing)

3. **AI 辅助分析**：
   - 使用 LLM 分析测试逻辑
   - 生成更智能的测试建议

4. **可视化增强**：
   - 交互式测试覆盖率地图
   - 性能趋势图表
   - 依赖关系图

5. **CI/CD 集成**（新增）：
   - GitHub Actions workflow 模板
   - GitLab CI 集成
   - Jenkins 插件

6. **实时性能监控**（新增）：
   - 集成 Instruments（iOS）
   - 集成 pytest-monitor（Python）
   - 生成性能火焰图

7. **日志聚合分析**（新增）：
   - 集成 ELK Stack
   - 实时日志监控
   - 异常模式识别

## Notes

- 此 Skill 是文档维护工具，专注于生成和更新测试文档
- 不替代实际测试执行，建议配合 CI/CD 使用
- 性能指标和日志为模拟值，仅供参考
- 建议定期更新性能基线，确保准确性
- HTML 报告模板可根据项目需求定制

---

**Skill Version**: v1.0.0  
**Last Updated**: 2026-01-22  
**Maintainer**: AI Agent
