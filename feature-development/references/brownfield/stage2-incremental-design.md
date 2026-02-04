# 阶段2: 增量架构设计（Brownfield）

## 目标

基于现有架构，生成增量技术方案，包括兼容性评估、数据库变更 DDL、API 变更设计。

## 兼容性评估

### 评估维度

1. **架构兼容性**：新功能是否与现有架构冲突？
2. **数据库兼容性**：是否需要修改现有表结构？
3. **API 兼容性**：是否影响现有 API？
4. **依赖兼容性**：新增技术栈是否与现有技术兼容？

### 输出：兼容性评估报告

```markdown
## 兼容性评估报告

### 架构层面
- ✅ 新增推荐引擎模块，独立微服务，不影响现有架构
- ⚠️ 需要在商品详情页嵌入推荐位，涉及前端改动

### 数据库层面
- ⚠️ 需要 ALTER TABLE products 新增 recommendation_score 字段
- ✅ 新增 user_profiles 表，不影响现有表

### API 层面
- ✅ 新增 /v2/recommendations 端点，不影响现有 API
- ⚠️ GET /products/:id 返回结构新增 recommendations 字段（向后兼容）

### 依赖层面
- ✅ 新增 TensorFlow Recommenders，与现有技术栈兼容
- ✅ 新增 Redis（已有），复用现有实例
```

## 数据库变更 DDL

### 使用脚本生成

```bash
python3 scripts/generate_database_ddl.py \
  --base-version "v1.5" \
  --new-version "v2.0" \
  --output doc/03_database/2_建表SQL_v2.0_变更DDL.sql
```

### DDL 模板

```sql
-- ==============================
-- 数据库变更 DDL (v2.0)
-- 基于版本: v1.5
-- 变更日期: 2026-02-04
-- ==============================

-- 1. 修改现有表：products 表新增推荐分字段
ALTER TABLE "products" 
ADD COLUMN "recommendation_score" DECIMAL(5,2) DEFAULT 0.0;

COMMENT ON COLUMN "products"."recommendation_score" IS '推荐分（0-100）';

-- 2. 新增表：用户画像表
CREATE TABLE "user_profiles" (
    "id" BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "user_id" BIGINT NOT NULL,
    "profile_data" JSONB NOT NULL,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "fk_user_profiles_user" FOREIGN KEY ("user_id") 
        REFERENCES "users"("id") ON DELETE CASCADE
);

-- 3. 新增索引
CREATE INDEX "idx_user_profiles_user_id" ON "user_profiles"("user_id");
CREATE INDEX "idx_products_recommendation_score" ON "products"("recommendation_score" DESC);

-- ==============================
-- 回滚脚本 (Rollback)
-- ==============================

-- ALTER TABLE "products" DROP COLUMN "recommendation_score";
-- DROP TABLE "user_profiles";
```

## API 变更设计

### 新增 API 端点

```markdown
#### GET /v2/recommendations

**描述**: 获取用户推荐商品

**Request**:
- Headers: Authorization: Bearer {token}
- Query Params:
  - user_id (required): 用户ID
  - limit (optional): 返回数量（默认 10）

**Response** (200 OK):
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "recommendations": [
      {
        "product_id": 123,
        "product_name": "商品A",
        "recommendation_score": 95.5,
        "reason": "基于您的浏览历史"
      }
    ]
  }
}
```

### 修改现有 API（向后兼容）

```markdown
#### GET /products/:id (v2.0)

**变更说明**: 返回结构新增 recommendations 字段（可选）

**Response** (200 OK):
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "product_id": 123,
    "product_name": "商品A",
    "price": 99.99,
    "recommendations": [  // 🆕 新增字段（v2.0）
      {"product_id": 456, "product_name": "商品B"}
    ]
  }
}
```

**向后兼容**: v1.5 客户端可忽略 recommendations 字段。
```

## 完成标准

增量架构设计生成并通过用户审查后，阶段2 完成，进入阶段3。

## 输出清单

- ✅ `doc/02_arch/2_系统架构_v2.0.md`
- ✅ `doc/03_database/2_建表SQL_v2.0_变更DDL.sql`
- ✅ `doc/04_api/1_RESTful_API_v2.0_变更日志.md`
