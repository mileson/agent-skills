# 阶段4: 开发执行（Greenfield）

## 目标

基于 feature_list.json，使用 Initializer Agent + Coding Agent 循环实现所有功能。

## Agent 分工

### Initializer Agent

**职责**: 初始化开发环境，设置基线

**主要任务**:
1. 创建 `init.sh` 脚本（环境设置、依赖安装）
2. Git 基线提交（初始代码、配置文件）
3. 基础端到端测试（确保环境可用）

**完成标准**:
- `init.sh` 脚本可成功运行
- Git 仓库已初始化，有初始提交
- 基础端到端测试通过（如访问首页、健康检查）

### Coding Agent

**职责**: 循环实现功能，直到所有任务完成

**工作流程**:
1. **读取进度**: 读取 `doc/06_dev-logs/PROGRESS.md`
2. **选择任务**: 从 feature_list.json 中选择 `status: "pending"` 的任务
3. **实现功能**: 实现单个功能（编写代码、单元测试）
4. **端到端测试**: 运行端到端测试，确保功能可用
5. **更新状态**: 更新 feature_list.json 中的 `status: "completed"`
6. **Git 提交**: 提交代码到 Git
7. **更新进度**: 更新 PROGRESS.md
8. **保存检查点**: 使用 checkpoint_manager.py 保存检查点
9. **循环**: 如果还有 pending 任务，回到步骤 2

## PROGRESS.md 格式

使用模板：`templates/greenfield/claude-progress_template.txt`

```
========================================
项目: 项目名称
最后更新: 2026-02-04 14:00:00
总进度: 26% (13/50 功能完成)
========================================

## 2026-02-04 14:00 - 完成用户注册API端点
执行的Agent: coding-agent-session-5
完成的功能: TASK-014
变更摘要:
- 创建了 /backend/api/auth/register.py
- 实现了邮箱格式验证
- 添加了密码强度检查
- 通过了单元测试 test_register_valid_user
Git Commit: a3b2c1d feat: add user registration endpoint
测试结果: ✅ 通过 (5/5 测试用例)
下一步计划: 实现登录功能 (TASK-015)

## 2026-02-04 10:30 - 初始化项目结构
执行的Agent: initializer-agent
完成的功能: TASK-001
变更摘要:
- 创建前端项目目录（React + Vite）
- 创建后端项目目录（FastAPI）
- 初始化 git 仓库
Git Commit: b4c5d6e chore: initial project structure
下一步计划: 配置开发环境 (TASK-002)

========================================
错误记录（最近3次）
========================================

## 2026-02-04 13:45 - 邮箱验证逻辑错误
错误类型: 业务逻辑错误
功能: TASK-014
错误描述: 正则表达式未正确匹配国际域名
解决方案: 更新正则表达式为 RFC 5322 标准
耗时: 15分钟

========================================
```

## 端到端测试

### 测试工具

**推荐工具**:
- 前端：Playwright / Cypress
- 后端：pytest / Supertest
- 浏览器自动化：Puppeteer MCP（如可用）

### 测试流程

**每个功能完成后，必须运行端到端测试**:

```bash
# 前端测试
npm run test:e2e

# 后端测试
pytest tests/e2e/

# 浏览器自动化测试（如使用 Puppeteer MCP）
# 使用 MCP 工具启动浏览器，访问功能页面，验证行为
```

### 测试通过标准

**必须满足**:
1. 所有断言通过
2. 无 JavaScript 错误
3. 无 HTTP 5xx 错误
4. 关键业务流程完整（如注册 → 登录 → 操作）

**如果测试失败**:
- 使用 `scripts/handle_agent_error.py` 生成错误日志
- 分析错误原因
- 修复代码
- 重新测试

## Git 提交规范

### Commit Message 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建工具、依赖更新

**示例**:
```
feat(auth): add user registration endpoint

- Implement email format validation
- Implement password strength check
- Add unit tests

Closes TASK-014
```

## 错误处理

### 使用 handle_agent_error.py

**任何错误都必须记录**:

```bash
python3 scripts/handle_agent_error.py \
  --project-name "项目名称" \
  --feature-id "TASK-014" \
  --error-message "邮箱验证逻辑错误" \
  --agent-session "coding-agent-session-5" \
  --stack-trace "$(cat error_trace.txt)"
```

**生成的错误日志**:
```json
{
  "ProjectName": "项目名称",
  "FeatureId": "TASK-014",
  "FailedAt": "2026-02-04T13:45:00Z",
  "ErrorMessage": "邮箱验证逻辑错误",
  "AgentSession": "coding-agent-session-5",
  "StackTrace": "...",
  "ContextState": {
    "lastCommand": "pytest tests/test_register.py",
    "workingDirectory": "/backend",
    "openFiles": ["api/auth/register.py"]
  }
}
```

**保存路径**: `doc/06_dev-logs/errors/error_20260204_134500.json`

## 检查点管理

### 使用 checkpoint_manager.py

**每个功能完成后，保存检查点**:

```bash
python3 scripts/checkpoint_manager.py save \
  --feature-id "TASK-014" \
  --checkpoint-id "ckpt-014" \
  --state '{"createdFiles": ["/backend/api/auth/register.py"], "lastCommand": "git commit"}'
```

**检查点文件**:
```json
{
  "checkpointId": "ckpt-014",
  "featureId": "TASK-014",
  "timestamp": "2026-02-04T14:00:00Z",
  "state": {
    "createdFiles": ["/backend/api/auth/register.py"],
    "lastCommand": "git commit",
    "gitCommit": "a3b2c1d"
  }
}
```

**保存路径**: `doc/06_dev-logs/checkpoint_ckpt-014.json`

### 从检查点恢复

**如果 Agent 中断，可以从检查点恢复**:

```bash
python3 scripts/checkpoint_manager.py restore \
  --checkpoint-id "ckpt-014"
```

**恢复操作**:
1. 读取检查点文件
2. 恢复到对应的 Git commit
3. 更新 feature_list.json 状态
4. 继续执行下一个任务

## 完成标准

所有功能实现并测试通过后，阶段4 完成：
1. feature_list.json 中所有任务 `status: "completed"`
2. 所有端到端测试通过
3. Git 仓库有完整的提交历史
4. PROGRESS.md 记录完整

## 输出清单

- ✅ `init.sh` - 初始化脚本
- ✅ `doc/06_dev-logs/PROGRESS.md` - 进度文件
- ✅ `doc/06_dev-logs/feature_list.json` - 功能清单（状态已更新）
- ✅ `doc/06_dev-logs/checkpoint_*.json` - 检查点文件
- ✅ `doc/06_dev-logs/errors/error_*.json` - 错误日志（如有）
- ✅ 完整的代码仓库（Git 提交历史）
