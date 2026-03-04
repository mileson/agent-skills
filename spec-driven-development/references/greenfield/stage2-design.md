# 阶段2: 架构设计（Greenfield）

## 目标

基于阶段1已经确认的产品定位、模块需求和业务流程，生成可落地的技术方案，并把模块级业务文档与技术文档正式成型。

本阶段不再把模块页面级 ASCII 集中放到 `Basic/UI`，而是按职责拆分：

- 全局信息架构 / 全局导航 / 全局交互规范：放 `Basic/UI`
- 模块级业务 ASCII：放模块需求文档
- 模块级技术流程 / 状态 / 关系图：放模块技术文档

## 输出目标

### Basic 层

- `Documentation/Basic/Architecture/1_技术选型.md`
- `Documentation/Basic/Architecture/2_系统架构.md`
- `Documentation/Basic/Architecture/3_交互时序图.md`
- `Documentation/Basic/UI/1_信息架构总览.md`

### Modules 层

对每个核心业务模块，完成双文档：

- `Documentation/Modules/<模块名>/<模块名>_需求文档.md`
- `Documentation/Modules/<模块名>/<模块名>_技术文档.md`

## 设计步骤

### 1. 技术选型

输出到：
- `Documentation/Basic/Architecture/1_技术选型.md`

需要明确：
- 运行时 / 主要语言
- 核心框架
- 数据与存储方案
- 集成方式
- 交付与部署方式

### 2. 系统架构

输出到：
- `Documentation/Basic/Architecture/2_系统架构.md`

需要明确：
- 系统分层
- 模块边界
- 关键依赖
- 架构图（Mermaid）

### 3. 关键交互时序

输出到：
- `Documentation/Basic/Architecture/3_交互时序图.md`

需要明确：
- 核心场景时序图（Mermaid）
- 跨模块交互与关键依赖

### 4. 全局信息架构

输出到：
- `Documentation/Basic/UI/1_信息架构总览.md`

只保留全局级内容：
- 产品级信息架构
- 全局导航
- 全局页面地图
- 全局交互规范

禁止把模块页面级线框塞进这里。

### 5. 模块需求文档成型

每个核心模块都要写入：
- 业务场景
- 业务场景流程（Mermaid）
- 功能需求
- 业务规则
- 业务 ASCII 交互稿
- 验收标准

### 6. 模块技术文档成型

每个核心模块都要写入：
- 模块说明书
- 需求映射
- 系统架构
- 数据 / 状态模型
- Contract / API / 事件
- 技术流程设计
- 异常与补偿
- 实施现状
- 测试设计

## Mermaid / ASCII 规则

### Mermaid

以下内容优先使用 Mermaid：
- 业务场景流程
- 架构图
- 时序图
- 状态流转

### ASCII

偏业务的 ASCII 放在模块需求文档，例如：
- 页面入口关系
- 业务流转页面
- 主要状态视图
- 用户可见交互框架

偏技术的流程 / 关系图放在模块技术文档。

## Framework 同步要求

本阶段还必须同步：

- `Framework/Standards/业务模块技术文档规范.md`
- `Framework/Standards/架构模式规范.md`
- `Framework/Standards/测试框架规范.md`
- `Framework/CommonCapabilities/通用能力文档模板.md`
- `Framework/ProblemSolutions/问题解决方案模板.md`

## 审查要点

本阶段结束前，至少检查：

1. 全局信息架构是否只保留全局内容
2. 模块级业务 ASCII 是否已经下沉到模块需求文档
3. 模块技术文档是否完整映射需求文档
4. Mermaid 是否覆盖关键业务流程
5. 是否已识别需要沉淀的通用能力或问题方案

## 完成标准

- ✅ Basic/Architecture 已形成完整技术方案
- ✅ Basic/UI 已形成全局信息架构文档
- ✅ 每个核心模块已建立需求文档 + 技术文档
- ✅ Mermaid / ASCII 职责已按新模型落位
- ✅ Framework 规范与模板已同步
