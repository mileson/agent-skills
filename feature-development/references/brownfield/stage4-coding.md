# 阶段4: 开发执行（Brownfield）

## 与 Greenfield 的区别

Brownfield 的开发执行与 Greenfield 基本相同，但有以下额外注意事项：

### 1. 回归测试

**必须运行回归测试**，确保新功能不影响现有功能：

```bash
# 运行所有测试
pytest tests/

# 重点测试受影响的模块
pytest tests/products/  # 商品模块受影响
pytest tests/users/     # 用户模块受影响
```

### 2. 数据迁移

如果有数据库变更，执行迁移脚本：

```bash
# 执行 DDL
psql -d mydb -f doc/03_database/2_建表SQL_v2.0_变更DDL.sql

# 数据迁移（如需要）
python3 scripts/data_migration_v2.0.py
```

### 3. 版本标记

Git commit 和 progress 文件中标记版本号：

```
feat(v2.0): add recommendation engine

Closes TASK-051
```

### 4. 兼容性测试

确保 v1.5 客户端可以正常工作（向后兼容）。

## 其他步骤与 Greenfield 相同

参考：`references/greenfield/stage4-coding.md`

## 输出清单

- ✅ 与 Greenfield 相同
- ✅ 额外：回归测试报告
- ✅ 额外：数据迁移脚本（如需要）
