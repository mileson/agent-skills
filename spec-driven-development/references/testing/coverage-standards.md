# 覆盖率标准

## 最低覆盖率要求

- 总体覆盖率：≥ 70%
- 核心业务逻辑：≥ 90%
- 工具函数：≥ 80%
- UI 组件：≥ 60%

## 测试用例设计

### Handler 测试
- 正常流程
- 异常流程
- 边界情况

### Repository 测试
- CRUD 操作
- 查询条件
- 事务处理

### Core Business Logic 测试
- 业务规则验证
- 数据转换
- 权限检查

## 测试命名规范

```
test_<function_name>_<scenario>_<expected_result>

示例:
test_register_valid_email_success
test_register_invalid_email_returns_error
test_register_duplicate_email_returns_conflict
```
