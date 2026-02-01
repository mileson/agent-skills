# 文件说明书模板 (File Manual Template)

## 模板结构

```text
# 文件说明书 (File Manual)
## 核心功能 (Core Function)
[一句话描述该文件的核心功能，需反映最新的代码逻辑]

## 输入 (Input)
[编写当前文件上游的数据来源与关键规则]

## 输出 (Output)
[编写当前文件对外提供的服务与能力]

## 定位 (Position)
[编写当前文件在局部文件夹内的定位与充当的作用]

## 依赖 (Dependency)
[编写当前文件涉及到的所有依赖的核心文件名称与作用，从关键依赖到次要依赖，分点使用"- XXX"罗列]
- [示例：依赖 ContentView.swift 提供 UI 结构]

## 维护规则 (Maintenance Rules)
1. 每次修改代码逻辑后，必须检查并更新上述的【核心功能】、【输入】、【输出】等信息，确保文档与代码一致。
2. 禁止修改或删除本【维护规则】章节的内容。
3. 修改完成后，必须扫描当前文件所在的文件夹目录，找到对应的 [当前文件夹名称]_README.md 文档，并同步更新该 README 中关于本文件的描述信息。
```

---

## 不同语言的注释格式

### Swift / Kotlin / Java / TypeScript / JavaScript
```swift
// # 文件说明书 (File Manual)
// ## 核心功能 (Core Function)
// [功能描述]
//
// ## 输入 (Input)
// [输入描述]
//
// ...
```

### Python / Shell / Bash
```python
# # 文件说明书 (File Manual)
# ## 核心功能 (Core Function)
# [功能描述]
#
# ## 输入 (Input)
# [输入描述]
#
# ...
```

### HTML / CSS
```css
/*
 * # 文件说明书 (File Manual)
 * ## 核心功能 (Core Function)
 * [功能描述]
 *
 * ## 输入 (Input)
 * [输入描述]
 *
 * ...
 */
```

---

## 维护联动清单

代码变更后需要检查的联动文档：

| 文档类型 | 路径 | 触发条件 |
|---------|------|---------|
| 文件夹 README | `[模块]_[文件夹名]_README.md` | 每次代码变更后 |
| 项目文件结构 | `Documentation/Basic/File-structure.md` | 新增/删除文件时 |
| 产品流程说明 | `Documentation/Basic/App-flow.md` | 流程变更时 |
| 前端/后端架构 | `Documentation/Basic/*-structure.md` | 架构变更时 |
