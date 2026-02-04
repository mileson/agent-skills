# 阶段0: 读取现有文档（Brownfield）

## 目标

理解现有系统的全貌，生成"现有系统上下文报告"，作为增量开发的基础。

## 执行步骤

### 1. 运行模式检测

```bash
python3 scripts/detect_project_mode.py
```

**输出示例**:
```json
{
  "mode": "brownfield",
  "hasDocStructure": true,
  "existingDocs": {
    "prd": ["1_产品概述.md", "2_用户画像.md"],
    "arch": ["1_技术选型.md", "2_系统架构.md"],
    "database": ["1_数据表设计.md"],
    "api": ["1_RESTful_API.md"]
  },
  "existingFeatureList": "/path/to/doc/06_dev-logs/feature_list.json"
}
```

### 2. 智能读取现有文档

```bash
python3 scripts/read_existing_docs.py --doc-path doc/
```

**读取策略**:
- 避免全量加载：只读取摘要和关键信息
- 提取结构化信息：表名列表、API 端点数量
- 识别最新版本文档：v2.0 > v1.5 > v1.0
- 超长文档只读取前 500 行

**输出**: 现有文档的结构化上下文（JSON格式）

### 3. 生成现有系统上下文报告

```bash
python3 scripts/generate_context_report.py --doc-path doc/ --output doc/06_dev-logs/context_report.md
```

**报告内容**:
1. 产品定位（基于 PRD）
2. 技术架构（基于架构文档）
3. 数据库现状（表数量、核心实体）
4. API 现状（端点数量、认证方式）
5. 功能现状（基于 feature_list.json）
6. 技术债务（扫描代码中的 TODO 注释）

**报告模板**: `templates/brownfield/context_report_template.md`

## 现有系统上下文报告示例

```markdown
# 现有系统上下文报告

**生成时间**: 2026-02-04 14:30:00
**项目名称**: 电商平台
**当前版本**: v1.5

## 产品定位（基于 01_PRD/1_产品概述.md）
- 核心价值：为中小企业提供一站式电商解决方案
- 目标用户：中小型电商商家（月销售额 10万-100万）
- 主要功能：商品管理、订单管理、会员管理、营销工具

## 技术架构（基于 02_arch/2_系统架构.md）
- 前端技术栈：React 18 + TypeScript + Ant Design
- 后端技术栈：FastAPI + PostgreSQL + Redis
- 部署平台：AWS (EC2 + RDS + S3)
- 第三方服务：Stripe（支付）、SendGrid（邮件）

## 数据库现状（基于 03_database/1_数据表设计.md）
- 现有数据表：22 个
- 核心实体：User, Product, Order, Payment, Member
- 索引设计：已优化高频查询

## API 现状（基于 04_api/1_RESTful_API.md）
- 现有端点：45 个
- 认证方式：JWT Token
- 错误码规范：已定义 30+ 错误码

## 功能现状（基于 06_dev-logs/feature_list.json）
- 总功能数：50 个
- 已完成：48 个 (96%)
- 进行中：0 个
- 待开发：2 个
- 当前版本：v1.5
- 当前 Phase：Phase 04（测试和优化）

## 技术债务和优化空间
- [ ] 商品搜索性能优化（TODO in product_search.py）
- [ ] 订单列表分页优化（TODO in order_list.py）
- [ ] 前端代码拆分（TODO in App.tsx）
- [ ] Redis 缓存策略优化（TODO in cache.py）
```

## 向用户展示报告

生成报告后，向用户展示并确认：
1. 对现有系统的理解是否准确？
2. 是否有遗漏的重要信息？
3. 是否有需要补充的背景？

允许用户补充信息。

## 完成标准

现有系统上下文报告生成并通过用户确认后，阶段0 完成，进入阶段1。

## 输出清单

- ✅ `doc/06_dev-logs/context_report_[timestamp].md`
