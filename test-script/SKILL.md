---
name: test-script
description: 自动化测试脚本生成与执行工作流。测试脚本分类到 tests/ 目录：api/ 用于接口测试，feature/ 用于功能测试，unit/ 用于单元测试。当用户请求以下任务时触发：(1) 创建新的测试脚本文件（.py/.js/.ts/.go 等），(2) 编写 API 接口测试或功能测试用例，(3) 创建/更新对接 API 的功能时自动生成对应测试并执行验证，(4) 创建单元测试或集成测试。对于 API 功能变更，自动创建/更新测试脚本，执行测试确保通过后才完成任务。
argument-hint: "[测试类型] [功能名称]"
---

# 测试脚本生成器

## 核心规范（必须遵循）

1. **目录位置**：所有测试脚本必须放置在项目根目录的 `tests/` 文件夹内
2. **分类规则**：按照测试类型自动分类到对应子目录
3. **命名规范**：文件名使用蛇形命名法（snake_case），描述性命名
4. **模板适配**：根据测试类型（API/功能/单元）选择对应模板

## 目录结构

```
tests/
├── api/                    # API 接口测试脚本
│   ├── test_login.py
│   └── test_user_api.py
├── feature/                # 功能测试脚本（按功能分类）
│   ├── upload/
│   │   └── test_image_upload.py
│   └── auth/
│       └── test_otp.py
├── unit/                   # 单元测试（可选）
│   └── test_utils.py
└── __init__.py
```

## API 功能完整工作流

当创建/更新**对接 API 的功能**时，必须执行以下完整流程：

### 步骤 1：识别 API 变更

判断功能是否涉及 API 接口：
- 新增/修改后端路由或端点
- 新增/修改 API 调用代码
- 变更数据模型或接口参数

### 步骤 2：创建/更新 API 测试脚本

使用 `templates/api-test-template.py` 创建或更新对应的测试脚本：
- 脚本路径：`tests/api/test_<endpoint>.py`
- 包含成功场景和失败场景的测试用例
- 验证请求参数、响应格式、错误处理

### 步骤 3：执行测试

在完成功能开发后，自动运行测试验证：

```bash
# Python 项目
cd $CLAUDE_PROJECT_DIR && python -m pytest tests/api/test_<endpoint>.py -v

# 带覆盖率报告
cd $CLAUDE_PROJECT_DIR && python -m pytest tests/api/ --cov=app --cov-report=term-missing
```

### 步骤 4：验证结果

- ✅ **测试通过**：向用户报告测试结果，说明功能已完成并验证
- ❌ **测试失败**：分析失败原因，修复问题后重新执行测试，直到全部通过

### 步骤 5：报告完成

只有在**所有测试通过**后，才向用户确认功能已完成并可以测试验证。

## 测试类型映射

| 测试类型 | 目标目录 | 命名规则 | 模板 |
|---------|---------|---------|------|
| API 接口测试 | `tests/api/` | `test_<endpoint>.py` | `templates/api-test-template.py` |
| 功能测试 | `tests/feature/<name>/` | `test_<feature>.py` | `templates/feature-test-template.py` |
| 单元测试 | `tests/unit/` | `test_<module>.py` | - |

## 模板和示例

- **API 测试模板**: `templates/api-test-template.py`
- **功能测试模板**: `templates/feature-test-template.py`
- **Python API 示例**: `examples/test_login_api.py`
- **功能测试示例**: `examples/test_image_upload.py`

## 测试执行命令

| 语言 | 命令 |
|-----|------|
| Python | `python -m pytest tests/ -v` |
| JavaScript | `npm test` |
| TypeScript | `npm test` 或 `jest tests/` |
| Go | `go test ./...` |
