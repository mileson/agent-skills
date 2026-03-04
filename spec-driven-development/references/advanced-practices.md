# 高级开发实践

## Spec-Driven 通用原则

本文件面向**任意代码类型项目**，不绑定 Web、iOS、Backend 或具体语言。

在 Spec-Driven 模式下，Agent 的执行输入应按优先级读取：

1. `Documentation/Basic/` 中的业务目标、架构、数据、Contract、测试规范
2. `Documentation/Modules/` 中的模块主文档
3. `Documentation/Framework/Standards/` 中的全局规范
4. `Documentation/Framework/CommonCapabilities/` 中的可复用能力文档
5. `Documentation/Framework/ProblemSolutions/` 中的问题方案与反模式约束

只有满足以下条件，任务才允许进入编码：

- 任务已绑定 `sourceDocs`
- 涉及模块实现时已绑定 `targetModules`
- 已绑定 `testSpecs`
- 高风险任务已绑定 `problemSolutionRefs`
- `docStatus = approved`

## 测试框架规范

### 测试分层架构（4 层金字塔）

```
测试金字塔（从下到上）

┌─────────────────────────────────────┐
│   API集成测试 (15%)                   │  ← HTTP层面验证
│   - WebApplicationFactory           │    P1优先级
│   - 真实HTTP请求/响应                 │    每次合并执行
│   - 路由、参数绑定、状态码             │
├─────────────────────────────────────┤
│   数据一致性测试 (10%)                │  ← 业务价值验证
│   - 验证自引用外键设计                │    P0核心测试
│   - 验证数据自动同步                  │    每次提交执行
│   - 解决脏数据问题                    │
├─────────────────────────────────────┤
│   Handler单元测试 (45%)              │  ← 业务逻辑验证
│   - 命令/查询处理器                   │    P0优先级
│   - Mock Repository                 │    每次提交执行
│   - 业务规则验证                      │
├─────────────────────────────────────┤
│   Repository单元测试 (25%)           │  ← 数据访问验证
│   - CRUD操作                        │    P1优先级
│   - 查询方法                         │    每次提交执行
│   - InMemory数据库                   │
└─────────────────────────────────────┘

注: E2E测试(5%)单独分类，使用真实数据库和浏览器自动化
```

### 测试覆盖率要求

| 测试类型 | 比例 | 覆盖率要求 | 执行频率 | 优先级 |
|---------|------|-----------|---------|--------|
| **Repository 单元测试** | 25% | CRUD操作 100% | 每次提交 | P1 |
| **Handler 单元测试** | 45% | 核心业务 ≥85% | 每次提交 | P0 |
| **数据一致性测试** | 10% | 关键规则 100% | 每次提交 | P0 |
| **API 集成测试** | 15% | 核心端点 ≥70% | 每次合并 | P1 |
| **E2E 测试** | 5% | 关键流程 100% | 每日/发布前 | P0 |

### 测试命名规范

**格式**: `{被测对象}_{测试场景}_{预期结果}`

```csharp
// ✅ 好的示例
[TestMethod]
public async Task Repository_AddEntity_ShouldReturnEntityWithId()
{
    // ...
}

[TestMethod]
public async Task Handler_InvalidCommand_ShouldThrowValidationException()
{
    // ...
}

[TestMethod]
public async Task SelfReference_ParentChildRelation_ShouldMaintainIntegrity()
{
    // ...
}

// ❌ 坏的示例
[TestMethod]
public async Task Test1()  // 不描述性
{
    // ...
}

[TestMethod]
public async Task AddTest()  // 太简略
{
    // ...
}
```

---

## 异步任务执行最佳实践

### Fire-and-Forget 模式规范

**核心原则**: 执行器负责线程创建，调用方只触发任务

```csharp
// ✅ 正确实现：执行器内部使用 Task.Run

public class BackgroundTaskExecutor
{
    private readonly IServiceScopeFactory _scopeFactory;
    private readonly ILogger<BackgroundTaskExecutor> _logger;
    
    public async Task ExecuteAsync(int taskId)
    {
        _logger.LogInformation($"提交任务到后台，TaskId={taskId}");
        
        // 执行器负责线程创建
        _ = Task.Run(async () =>
        {
            using var scope = _scopeFactory.CreateScope();
            var service = scope.ServiceProvider.GetRequiredService<TaskService>();
            
            try
            {
                await service.ProcessAsync(taskId);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"任务执行失败，TaskId={taskId}");
            }
        });
        
        await Task.CompletedTask;
    }
}

// ✅ 正确调用：调用方直接await，不再包装Task.Run

public async Task<Result> Handle(MyCommand command)
{
    // 保存任务
    var task = await _repository.AddAsync(new BackgroundTask(...));
    await _context.SaveChangesAsync();
    
    // 触发后台执行 - 不使用Task.Run！
    await _executor.ExecuteAsync(task.Id);
    
    return Result.Success();
}
```

```python
# Python 等价实现

import asyncio
import logging
from typing import Callable

class BackgroundTaskExecutor:
    """后台任务执行器 - Fire-and-Forget 模式"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    async def execute_async(self, task_id: int, task_func: Callable):
        """
        提交任务到后台执行
        
        Args:
            task_id: 任务ID
            task_func: 任务函数
        """
        self.logger.info(f"提交任务到后台，TaskId={task_id}")
        
        # 执行器负责创建后台任务
        asyncio.create_task(self._run_task(task_id, task_func))
    
    async def _run_task(self, task_id: int, task_func: Callable):
        """内部执行任务"""
        try:
            await task_func(task_id)
        except Exception as ex:
            self.logger.error(f"任务执行失败，TaskId={task_id}", exc_info=ex)

# ✅ 正确调用
async def handle_command(command):
    # 保存任务
    task = await repository.add_async(BackgroundTask(...))
    await db.commit()
    
    # 触发后台执行 - 不使用 asyncio.create_task！
    await executor.execute_async(task.id, process_task)
    
    return {"code": 0, "message": "Success"}
```

### 常见错误：双重Task.Run

```csharp
// ❌ 错误示例：双重线程创建

// 调用方代码 - 错误！
if (shouldTrigger)
{
    // 外层Task.Run - ❌ 不应该在这里创建线程！
    _ = Task.Run(async () =>
    {
        try
        {
            await _executor.ExecuteAsync(taskId);  // 内部还有一个Task.Run
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "执行失败");
        }
    }, CancellationToken.None);
}
```

**问题影响**:
1. 性能开销：创建了两层线程，浪费资源
2. 异常丢失：外层的 try-catch 可能捕获不到内层异常
3. 生命周期混乱：任务的真实状态难以追踪

---

## 问题方案文档的使用时机

以下场景应优先读取或新增 `Documentation/Framework/ProblemSolutions/` 文档，而不是仅在模块文档内局部说明：

- 异步、并发、重试、轮询、回调
- 状态一致性、缓存同步、幂等、补偿
- 大文件处理、长任务、批量处理
- 错误归档、异常恢复、回滚
- 跨模块依赖或跨系统集成
- 已经踩过一次以上的历史坑

标准做法：

1. 设计阶段先识别是否命中高风险问题类型
2. 若已有问题方案文档，任务必须绑定 `problemSolutionRefs`
3. 若尚无问题方案文档，先补文档，再进入编码
4. 编码完成后，如形成新的标准解法或反模式，反写到 `ProblemSolutions`

---

## 代码审查检查清单

### 测试完整性检查

- [ ] **Repository 层**
  - [ ] 每个 Repository 方法都有对应的单元测试
  - [ ] CRUD 操作全覆盖（Create, Read, Update, Delete）
  - [ ] 查询方法测试了边界情况（空结果、单条、多条）

- [ ] **Handler 层**
  - [ ] 每个 Command/Query Handler 都有单元测试
  - [ ] 测试了成功场景和失败场景
  - [ ] Mock 了所有外部依赖（Repository, Service）

- [ ] **数据一致性**
  - [ ] 自引用外键的完整性测试
  - [ ] 级联删除/更新的正确性测试
  - [ ] 并发操作的数据一致性测试

- [ ] **API 层**
  - [ ] 核心端点的集成测试
  - [ ] 测试了请求参数绑定
  - [ ] 测试了HTTP状态码和响应格式

- [ ] **E2E 测试**
  - [ ] 关键业务流程的端到端测试
  - [ ] 使用真实数据库（或Docker测试容器）
  - [ ] 使用浏览器自动化工具（Selenium, Puppeteer）

### 异步任务检查

- [ ] **执行器设计**
  - [ ] 执行器内部使用 `Task.Run` 或 `asyncio.create_task`
  - [ ] 执行器提供了日志记录
  - [ ] 执行器处理了异常（不应向调用方抛出）

- [ ] **调用方代码**
  - [ ] 调用方 **不** 使用 `Task.Run` 包装执行器调用
  - [ ] 调用方 `await` 执行器的返回值（即使是 `Task.CompletedTask`）
  - [ ] 调用方不依赖执行器的返回结果（Fire-and-Forget）

- [ ] **生命周期管理**
  - [ ] 使用 `IServiceScopeFactory` 创建独立作用域
  - [ ] 在 `using` 块中正确释放资源
  - [ ] 避免闭包捕获外部作用域的服务

### 文档完整性检查

- [ ] **文档修订历史**
  - [ ] 每个技术文档包含修订历史表格
  - [ ] 记录版本号、日期、修订人、修订内容

- [ ] **章节完整性**
  - [ ] 包含业务需求、功能需求、系统架构
  - [ ] 包含数据库设计、接口设计、功能模块设计
  - [ ] 包含业务流程设计、测试设计

- [ ] **质量标准**
  - [ ] 单个文档不超过 10000 行
  - [ ] Mermaid 图表包含样式头
  - [ ] 表格行之间无空行（保证渲染）

---

## 在开发执行阶段的应用

### 测试验证步骤

在 **Stage 4: Coding（开发执行）** 阶段，Agent 必须执行以下验证：

1. **代码完成后，立即运行测试**
   ```bash
   # Python 项目
   pytest tests/ --cov=app --cov-report=term-missing
   
   # .NET 项目
   dotnet test --collect:"XPlat Code Coverage"
   ```

2. **检查测试覆盖率**
   - Repository 层：100% CRUD 覆盖
   - Handler 层：≥85% 核心业务逻辑
   - API 层：≥70% 核心端点

3. **只有测试通过 + 覆盖率达标，才能提交**
   ```
   ✅ 测试结果：25 passed, 0 failed
   ✅ 覆盖率：Repository 100%, Handler 87%, API 72%
   ✅ 允许 Git commit
   ```

### 异步任务开发规范

如果功能涉及**后台任务**（如文件处理、AI 推理、定时任务），必须：

1. **创建执行器**：`scripts/background_task_executor.py`
2. **执行器内部使用 `asyncio.create_task`**
3. **调用方直接 `await executor.execute_async()`**，不再包装

### 文档自动验证

使用 `scripts/validate_doc_completeness.py` 在每个 session 结束前验证：

```bash
python3 scripts/validate_doc_completeness.py --doc-path Documentation/
```

确保：
- 所有必需目录存在
- 所有必需文件存在
- 文档行数在限制内
- Mermaid 图表包含样式头
