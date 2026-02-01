---
name: ios-file-manual-generator
description: 自动为代码文件生成或更新标准化的文件说明书注释，包含核心功能、输入输出、定位、依赖等信息，并同步更新对应的文件夹 README 文档
---

# iOS 文件说明书生成器

## When to Use

Use this skill when you need to:
- 为新创建的代码文件添加说明书
- 代码逻辑修改后需要更新说明书
- 批量为项目文件补充说明书
- 保持代码文档的一致性和完整性
- 为 Swift 代码文件生成或更新文件说明书注释

## File Manual Template Format

```swift
/*
# 文件说明书 (File Manual)

## 核心功能 (Core Function)
[一句话精确描述该文件的核心功能，需反映最新的代码逻辑]

## 输入 (Input)
[描述该文件接收的数据来源和关键参数]
- 数据来源：[上游模块/网络请求/本地存储等]
- 关键参数：[主要的输入参数说明]

## 输出 (Output)
[描述该文件对外提供的功能和服务]
- 对外接口：[公开的方法、属性、通知等]
- 数据输出：[返回的数据类型和格式]

## 定位 (Position)
[描述该文件在当前文件夹/模块内的定位和作用]

## 依赖 (Dependency)
[列出该文件依赖的核心文件和第三方库，从关键到次要排序]
- [文件名/库名] - [作用说明]
- [文件名/库名] - [作用说明]

## 维护规则 (Maintenance Rules)
1. 每次修改代码逻辑后，必须检查并更新【核心功能】、【输入】、【输出】等章节
2. 禁止修改或删除本【维护规则】章节的内容
3. 修改完成后，必须同步更新所在文件夹的 [文件夹名称]_README.md 文档
*/
```

## Instructions

### 步骤 1: 分析代码文件结构

扫描并识别文件中的关键元素：
- **类型定义**: `class`, `struct`, `enum`, `protocol`, `actor`
- **主要方法**: `public`, `internal` 方法
- **属性**: `@Published`, `@State`, `@ObservedObject` 等
- **依赖导入**: `import` 语句
- **继承和协议**: 继承的父类和遵循的协议

### 步骤 2: 生成核心功能描述

根据代码分析，用一句话精确概括文件的核心功能：

**示例**：
- **ViewModel 文件**: "管理 [功能名] 界面的状态和业务逻辑，处理用户交互和数据更新"
- **View 文件**: "展示 [功能名] 界面，提供用户交互入口"
- **Model 文件**: "定义 [数据名] 数据结构，实现数据序列化和验证逻辑"
- **Service 文件**: "封装 [服务名] API 调用，处理网络请求和响应解析"
- **Manager 文件**: "管理 [资源名] 的生命周期和全局状态"

### 步骤 3: 识别输入数据来源

分析文件的输入来源：
- **初始化参数**: `init` 方法的参数
- **公开方法参数**: `public/internal` 方法的参数
- **通知监听**: `NotificationCenter` 监听的事件
- **环境对象**: `@EnvironmentObject`, `@Environment`
- **依赖注入**: 通过构造器或属性注入的依赖

**输出格式**：
```
## 输入 (Input)
- 数据来源：[上游ViewModel/API响应/本地CoreData/NotificationCenter通知]
- 关键参数：[参数名]: [参数类型] - [参数说明]
```

### 步骤 4: 识别输出和对外服务

分析文件提供的功能和接口：
- **公开属性**: `@Published` 属性供外部观察
- **公开方法**: `public/internal` 方法供外部调用
- **通知发送**: `NotificationCenter.post` 发送的事件
- **返回值**: 方法的返回类型和数据

**输出格式**：
```
## 输出 (Output)
- 对外接口：[方法名]、[属性名]、[通知名称]
- 数据输出：[数据类型] - [数据说明]
```

### 步骤 5: 确定文件定位

根据文件所在目录和代码特征，描述其在模块中的角色：

**常见定位**：
- **Models 目录**: "定义 [模块] 的核心数据模型"
- **Views 目录**: "实现 [模块] 的主界面视图"
- **ViewModels 目录**: "作为 [View] 和 [Model] 的桥梁，管理界面状态"
- **Services 目录**: "提供 [功能] 的服务层接口"
- **Utils 目录**: "提供 [功能] 的通用工具方法"

### 步骤 6: 分析依赖关系

提取并分类依赖：

**系统框架**：
```
- SwiftUI - UI 框架
- Combine - 响应式编程
- Foundation - 基础框架
```

**项目内部依赖**（按重要性排序）：
```
- [ViewModel文件名] - 提供业务逻辑支持
- [Service文件名] - 提供数据服务
- [Model文件名] - 提供数据模型定义
- ColorTheme.swift - 提供统一配色方案
```

**第三方库**（如有）：
```
- Alamofire - 网络请求
- Kingfisher - 图片加载
```

### 步骤 7: 插入说明书注释到文件起始行

将生成的说明书注释块插入到文件的第一行，在 `import` 语句之前：

```swift
/*
# 文件说明书 (File Manual)
...
*/

import SwiftUI
import Combine

// 原有代码...
```

### 步骤 8: 同步更新文件夹 README

找到文件所在目录的 `[文件夹名称]_README.md`，更新该文件的条目：

**示例**：
```markdown
## 文件清单

### ViewModels/
- **UserProfileViewModel.swift**
  - 核心功能：管理用户资料界面的状态和业务逻辑
  - 依赖：UserAPIService, UserModel
  - 更新时间：2026-01-10
```

### 步骤 9: 检查并更新项目文档（如有重大变更）

如果文件变更涉及架构调整，检查是否需要更新：
- `Documentation/File-structure.md` - 文件结构变更
- `Documentation/Frontend-guidelines.md` - 新增架构模式
- `Documentation/Tech-stack.md` - 新增技术依赖

## Special Scenarios

### 场景 1：ViewModel 文件
```swift
/*
## 核心功能 (Core Function)
管理 [功能名] 界面的状态和业务逻辑，处理用户交互并协调 Model 和 View 的数据流

## 输入 (Input)
- 数据来源：[Service]APIService 网络请求、NotificationCenter 事件通知
- 关键参数：无直接外部参数，通过方法调用触发

## 输出 (Output)
- 对外接口：loadData(), refresh(), handle[Action]() 方法
- 数据输出：@Published var items: [Model] - 供 View 观察的数据源

## 定位 (Position)
作为 [View] 和 [Model] 的桥梁，封装业务逻辑，管理界面状态

## 依赖 (Dependency)
- [Service].swift - 提供数据获取服务
- [Model].swift - 定义数据结构
- Combine - 响应式数据绑定
*/
```

### 场景 2：SwiftUI View 文件
```swift
/*
## 核心功能 (Core Function)
展示 [功能名] 界面，提供用户交互入口，响应 ViewModel 的状态变化

## 输入 (Input)
- 数据来源：[ViewModel] 提供的 @Published 状态
- 关键参数：@StateObject viewModel: [ViewModel]

## 输出 (Output)
- 对外接口：SwiftUI View 视图，可作为子视图嵌入其他界面
- 数据输出：通过闭包回调或 NotificationCenter 发送用户操作事件

## 定位 (Position)
实现 [模块] 的主界面，遵循 MVVM 架构的 View 层

## 依赖 (Dependency)
- [ViewModel].swift - 提供业务逻辑和状态管理
- ColorTheme.swift - 提供统一配色方案
- SwiftUI - UI 框架
*/
```

### 场景 3：Service 文件
```swift
/*
## 核心功能 (Core Function)
封装 [功能] API 调用，处理网络请求、响应解析和错误处理

## 输入 (Input)
- 数据来源：外部调用方通过方法传入请求参数
- 关键参数：authToken: String, requestBody: [RequestModel]

## 输出 (Output)
- 对外接口：async/await 异步方法，返回解析后的数据模型
- 数据输出：Result<[ResponseModel], Error> - 包含成功或失败信息

## 定位 (Position)
提供 [模块] 的数据服务层接口，隔离网络层实现细节

## 依赖 (Dependency)
- URLSession - 网络请求
- [ResponseModel].swift - 定义响应数据结构
- AppConfig.swift - 获取 API 基础配置
*/
```

## Quality Checklist

完成说明书生成后，检查以下项目：
- ✅ 注释块位于文件最顶部（import 之前）
- ✅ 核心功能描述清晰且不超过一行
- ✅ 输入和输出描述具体，有实际内容
- ✅ 依赖列表完整，按重要性排序
- ✅ 维护规则章节保持不变
- ✅ 文件夹 README 已同步更新
- ✅ 颜色引用检查（View 文件）
- ✅ iOS 15+ 兼容性检查

## Batch Processing

如需为多个文件批量生成说明书：
1. 优先处理核心业务模块（Features/ 目录）
2. 其次处理通用组件（Components/ 目录）
3. 最后处理工具类（Utils/、Extensions/ 目录）
4. 每处理一个目录，立即更新该目录的 README
5. 所有文件处理完毕后，统一检查项目文档
