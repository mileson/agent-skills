# 阶段0: 读取现有文档（Brownfield）

## 目标

理解现有系统的全貌，生成“现有系统上下文报告”，作为增量开发的基础，并识别基础文档、Framework 规范文档、通用能力文档、问题方案文档和模块主文档之间的关系。

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
  "existingFeatureList": "/path/to/Documentation/DevLogs/v2.0_执行跟踪.md"
}
```

### 2. 智能读取现有文档

```bash
python3 scripts/read_existing_docs.py --doc-path Documentation/
```

**读取策略**:
- 避免全量加载：只读取摘要和关键信息
- 提取结构化信息：表名列表、API 端点数量
- 识别最新版本文档：v2.0 > v1.5 > v1.0
- 超长文档只读取前 500 行

**输出**: 现有文档的结构化上下文（JSON格式）

### 3. 生成现有系统上下文报告

```bash
python3 scripts/generate_context_report.py --doc-path Documentation/ --output Documentation/DevLogs/context_report.md
```

**报告内容**:
1. 产品定位（基于 PRD）
2. 技术架构（基于架构文档）
3. 数据库现状（表数量、核心实体）
4. API 现状（端点数量、认证方式）
5. 执行现状（基于版本执行跟踪文档）
6. Framework 现状（Standards / CommonCapabilities / ProblemSolutions）
7. 技术债务（扫描代码中的 TODO 注释）
8. 产品定位审计摘要（供用户确认定位是否变化）

**报告结构**: 由 `generate_context_report.py` 按当前文档现状直接生成

## 现有系统上下文报告示例

```markdown
# 现有系统上下文报告

**生成时间**: 2026-02-04 14:30:00
**项目名称**: 电商平台
**当前版本**: v1.5

## 产品定位（基于 Basic/PRD/1_产品概述.md）
- 核心价值：为中小企业提供一站式电商解决方案
- 目标用户：中小型电商商家（月销售额 10万-100万）
- 主要功能：商品管理、订单管理、会员管理、营销工具

## 技术架构（基于 Basic/Architecture/2_系统架构.md）
- 前端技术栈：React 18 + TypeScript + Ant Design
- 后端技术栈：FastAPI + PostgreSQL + Redis
- 部署平台：AWS (EC2 + RDS + S3)
- 第三方服务：Stripe（支付）、SendGrid（邮件）

## 数据库现状（基于 Basic/Database/1_数据表设计.md）
- 现有数据表：22 个
- 核心实体：User, Product, Order, Payment, Member
- 索引设计：已优化高频查询

## API 现状（基于 Basic/API/1_RESTful_API.md）
- 现有端点：45 个
- 认证方式：JWT Token
- 错误码规范：已定义 30+ 错误码

## Framework 现状
- Standards：3 份
- CommonCapabilities：4 份
- ProblemSolutions：2 份
- 已沉淀的高风险问题：异步竞态、错误归档

## 执行现状（基于 DevLogs/v1.5_执行跟踪.md）
- 当前版本：v1.5
- 已完成任务：48 个
- 待开发任务：2 个
- 当前阶段：测试和优化

## 产品定位审计摘要
- 当前产品核心目标：为中小电商商家提供一站式电商运营系统
- 当前主要用户群体：中小型电商商家
- 当前核心场景：商品管理、订单管理、会员管理、营销活动
- 当前版本边界：暂不支持跨境支付和多租户隔离
- 本次新需求初判：待确认是定位延伸还是定位变化

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
4. 是否存在应该先补 `CommonCapabilities / ProblemSolutions` 再进入设计的内容？
5. 当前产品定位是否仍成立？本次需求是否会改变原定位？

允许用户补充信息。

## 完成标准

现有系统上下文报告生成并通过用户确认后，阶段0 完成，进入阶段1。

## 输出清单

- ✅ `Documentation/DevLogs/context_report_[timestamp].md`
