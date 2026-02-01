# 文件夹说明书模板 (Folder Manual Template)

## 文件命名规则

默认格式：`[模块名]_[文件夹名]_README.md`

冲突时格式：`[父文件夹名]_[模块名]_[文件夹名]_README.md`

---

## 模板内容

```markdown
# [文件夹名称] 说明书 (Folder Manual)

## 核心功能 (Core Function)
[简述该文件夹/模块包含的一组功能及其核心目标]

## 输入 (Input)
[描述进入该模块的数据流、参数或上游依赖的信号]

## 输出 (Output)
[描述该模块对外暴露的接口、视图、数据或服务能力]

## 定位 (Position)
[描述该模块在整个项目架构中的层级（如：UI组件层、业务逻辑层、数据持久层）]

## 依赖 (Dependency)
[列出该模块运行所必须的外部模块或第三方库]

## 维护规则 (Maintenance Rules)
1. 内部同步：当本文件夹内的代码文件（.swift, .kt, .ts 等）增加、删除或功能变更时，必须检查并更新上述的【核心功能】、【输入】、【输出】等信息，确保文档与代码一致
2. 反向更新 (Reverse Update)：一旦本 README 的内容发生实质性变更（尤其是架构定位、核心功能或文件结构改变时），必须检查并同步更新 `Documentation/Basic/` 目录下的以下全局文档，确保信息一致：
    * `Documentation/Basic/File-structure.md` 项目文件结构
    * `Documentation/Basic/App-flow.md` 产品流程说明
    * `Documentation/Basic/PRD.md` 产品逻辑说明（含用户故事）
    * `Documentation/Basic/Frontend-guidelines.md` 前端开发规范说明
    * `Documentation/Basic/Backend-structure.md` 后端架构设计说明
    * `Documentation/Basic/Tech-stack.md` 项目技术栈说明
```

---

## 示例

### 示例 1：UI 组件层

```markdown
# Components 说明书 (Folder Manual)

## 核心功能 (Core Function)
包含项目中所有可复用的 UI 组件，提供基础交互能力和视觉样式

## 输入 (Input)
- 来自父组件的 props 参数
- 来自全局状态管理的数据

## 输出 (Output)
- 提供 Button、Input、Modal 等通用组件
- 提供组件的事件回调接口

## 定位 (Position)
属于 UI 组件层，为上层页面提供可复用的基础组件

## 依赖 (Dependency)
- React: 框架依赖
- TailwindCSS: 样式系统
- @/lib/utils: 工具函数

## 维护规则 (Maintenance Rules)
1. 新增组件时更新本 README 的【核心功能】和【输出】章节
2. 组件 API 变更时同步更新相关页面文档
3. 架构变更时反向更新 Documentation/Basic/Frontend-guidelines.md
```

### 示例 2：业务逻辑层

```markdown
# Services 说明书 (Folder Manual)

## 核心功能 (Core Function)
处理所有业务逻辑，包括数据获取、转换、缓存和状态管理

## 输入 (Input)
- 来自 API 的原始数据
- 来自 ViewModel 的业务请求

## 输出 (Output)
- 提供处理后的业务数据
- 提供状态变更通知

## 定位 (Position)
属于业务逻辑层，连接 UI 层和数据层

## 依赖 (Dependency)
- APIClient: 网络请求
- CacheManager: 本地缓存
- 数据模型: Model 层

## 维护规则 (Maintenance Rules)
1. 新增服务时更新本 README
2. 服务接口变更时同步更新调用方文档
3. 架构变更时反向更新 Documentation/Basic/Backend-structure.md
```
