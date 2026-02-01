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
1. **内部同步**：当本文件夹内的代码文件（.swift, .kt, .ts 等）增加、删除或功能变更时，必须检查并更新上述的【核心功能】、【输入】、【输出】等信息，确保文档与代码一致。
2. **反向更新 (Reverse Update)**：一旦本 README 的内容发生实质性变更（尤其是架构定位、核心功能或文件结构改变时），必须检查并同步更新 `Documentation/Basic/` 目录下的以下全局文档，确保信息一致：
    * `Documentation/Basic/File-structure.md` 项目文件结构
    * `Documentation/Basic/App-flow.md` 产品流程说明
    * `Documentation/Basic/PRD.md` 产品逻辑说明（含用户故事）
    * `Documentation/Basic/Frontend-guidelines.md` 前端开发规范说明
    * `Documentation/Basic/Backend-structure.md` 后端架构设计说明
    * `Documentation/Basic/Tech-stack.md` 项目技术栈说明
