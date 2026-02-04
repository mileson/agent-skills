# 阶段3: 任务拆解（Greenfield）

## 目标

将架构设计拆解为可执行的开发任务，生成 feature_list.json，按 Phase 组织任务。

## 任务拆解原则

### 粒度适中

**单个任务完成时间**: 1-3 天

**任务过大的信号**:
- 描述超过 10 个步骤
- 涉及多个模块（跨用户模块、订单模块等）
- 依赖关系复杂

**任务过小的信号**:
- 只有 1-2 个步骤
- 完成时间少于 4 小时
- 没有独立的测试价值

### 明确依赖关系

**依赖类型**:
1. **技术依赖**: 数据库表必须先创建，才能实现 CRUD API
2. **业务依赖**: 用户注册完成后，才能实现用户登录
3. **测试依赖**: 单元测试完成后，才能进行集成测试

**依赖标记**:
```json
{
  "featureId": "TASK-015",
  "description": "实现用户登录功能",
  "dependencies": ["TASK-001", "TASK-014"]
}
```

### 按 Phase 组织

**Phase 划分原则**:
- Phase 01: 基础环境搭建（项目初始化、数据库创建、CI/CD 配置）
- Phase 02: 核心功能开发（用户模块、核心业务模块）
- Phase 03: 扩展功能开发（通知、搜索、报表）
- Phase 04: 测试和优化（集成测试、性能测试、安全测试）
- Phase 05: 上线准备（文档完善、部署脚本、监控配置）

## 任务分类

### functional（功能型任务）

**特征**: 实现具体的业务功能

**示例**:
- 用户注册功能
- 商品列表页
- 订单创建功能

**测试要求**: 单元测试 + 端到端测试

### infrastructure（基础设施任务）

**特征**: 搭建开发和部署环境

**示例**:
- 初始化项目结构
- 配置数据库连接
- 配置 CI/CD 流水线

**测试要求**: 基础测试（如数据库连接测试）

### integration（集成任务）

**特征**: 集成第三方服务

**示例**:
- 集成 Stripe 支付
- 集成 SendGrid 邮件服务
- 集成 Redis 缓存

**测试要求**: 集成测试

### optimization（优化任务）

**特征**: 性能优化、代码重构

**示例**:
- 优化数据库查询
- 优化前端加载速度
- 重构代码结构

**测试要求**: 性能测试 + 回归测试

## 生成 feature_list.json

### 文件结构

使用模板：`templates/greenfield/feature_list_template.json`

```json
{
  "project": {
    "name": "项目名称",
    "version": "1.0.0",
    "createdAt": "2026-02-04T10:00:00Z"
  },
  "phases": [
    {
      "phaseId": "phase-01",
      "phaseName": "Phase 01: 基础环境搭建",
      "priority": 1,
      "status": "pending",
      "features": [
        {
          "featureId": "TASK-001",
          "category": "infrastructure",
          "description": "初始化项目结构",
          "steps": [
            "创建前端项目目录（React + Vite）",
            "创建后端项目目录（FastAPI）",
            "配置 ESLint 和 Prettier",
            "初始化 git 仓库"
          ],
          "status": "pending",
          "assignedAgent": "initializer",
          "dependencies": [],
          "estimatedEffort": "0.5 day",
          "checkpoint": null
        },
        {
          "featureId": "TASK-002",
          "category": "infrastructure",
          "description": "配置数据库",
          "steps": [
            "创建 PostgreSQL 数据库",
            "创建数据库用户和权限",
            "运行建表 SQL 脚本",
            "创建数据库迁移脚本"
          ],
          "status": "pending",
          "assignedAgent": "initializer",
          "dependencies": ["TASK-001"],
          "estimatedEffort": "0.5 day",
          "checkpoint": null
        }
      ]
    },
    {
      "phaseId": "phase-02",
      "phaseName": "Phase 02: 核心功能开发",
      "priority": 2,
      "status": "pending",
      "features": [
        {
          "featureId": "TASK-014",
          "category": "functional",
          "description": "实现用户注册功能",
          "steps": [
            "创建用户注册 API 端点",
            "实现邮箱格式验证",
            "实现密码强度检查",
            "实现密码哈希存储",
            "编写单元测试",
            "端到端测试"
          ],
          "status": "pending",
          "assignedAgent": "coding",
          "dependencies": ["TASK-002"],
          "estimatedEffort": "2 days",
          "checkpoint": null
        }
      ]
    }
  ],
  "metadata": {
    "totalFeatures": 50,
    "completedFeatures": 0,
    "progressPercentage": 0.0,
    "lastUpdated": "2026-02-04T10:00:00Z"
  }
}
```

### 关键字段说明

| 字段 | 说明 |
|------|------|
| `featureId` | 任务唯一标识，格式：`TASK-{编号}` |
| `category` | 任务分类：functional / infrastructure / integration / optimization |
| `description` | 任务简短描述（1句话） |
| `steps` | 任务详细步骤（3-10 个步骤） |
| `status` | 任务状态：pending / in_progress / completed / cancelled |
| `assignedAgent` | 负责的 Agent：initializer / coding |
| `dependencies` | 依赖的任务 ID 列表 |
| `estimatedEffort` | 预估工作量（如 "2 days"） |
| `checkpoint` | 检查点信息（任务完成后自动填充） |

## 任务拆解示例

### 示例：电商平台

**Phase 01: 基础环境搭建**（4个任务）
- TASK-001: 初始化项目结构
- TASK-002: 配置数据库
- TASK-003: 配置 CI/CD 流水线
- TASK-004: 基础端到端测试

**Phase 02: 核心功能开发**（20个任务）
- TASK-005 ~ TASK-010: 用户模块（注册、登录、信息管理、权限控制）
- TASK-011 ~ TASK-018: 商品模块（列表、详情、搜索、分类）
- TASK-019 ~ TASK-024: 订单模块（购物车、下单、订单管理）

**Phase 03: 扩展功能开发**（15个任务）
- TASK-025 ~ TASK-030: 支付模块（支付、退款、对账）
- TASK-031 ~ TASK-035: 通知模块（邮件、短信、站内通知）
- TASK-036 ~ TASK-039: 报表模块（销售报表、用户报表）

**Phase 04: 测试和优化**（8个任务）
- TASK-040 ~ TASK-042: 集成测试
- TASK-043 ~ TASK-045: 性能优化
- TASK-046 ~ TASK-047: 安全测试

**Phase 05: 上线准备**（3个任务）
- TASK-048: 文档完善
- TASK-049: 部署脚本
- TASK-050: 监控配置

## 用户确认

生成 feature_list.json 后，向用户展示：
1. 总任务数量是否合理？
2. Phase 划分是否清晰？
3. 依赖关系是否正确？
4. 任务粒度是否适中？

允许用户调整任务优先级、合并或拆分任务。

## 运行脚本

使用脚本生成 feature_list.json：

```bash
python3 scripts/generate_feature_list.py \
  --project-name "电商平台" \
  --prd-path doc/01_PRD \
  --arch-path doc/02_arch \
  --output doc/06_dev-logs/feature_list.json
```

脚本会自动分析 PRD 和架构文档，生成任务清单。

## 完成标准

feature_list.json 生成并通过用户确认后，阶段3 完成，进入阶段4。

## 输出清单

- ✅ `doc/06_dev-logs/feature_list.json`
