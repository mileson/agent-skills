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
psql -d mydb -f Documentation/Basic/Database/5_数据库变更DDL_v2.0.sql

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

### 5. 文档反写要求

Brownfield 不仅要更新受影响模块主文档，还要判断：

- 本次改动是否抽象出了新的通用能力？
- 本次修复是否形成了新的标准解法或反模式约束？

若是，则分别更新：

- `Documentation/Framework/CommonCapabilities/`
- `Documentation/Framework/ProblemSolutions/`

并在受影响文档的 `## 文档修订历史` 中记录“基于实际代码实现同步”。

## 其他步骤与 Greenfield 相同

参考：`references/greenfield/stage4-coding.md`

## 输出清单

- ✅ 与 Greenfield 相同
- ✅ 额外：回归测试报告
- ✅ 额外：数据迁移脚本（如需要）
- ✅ 额外：受影响的 Framework 能力/问题方案文档（如适用）
