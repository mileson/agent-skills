---
name: folder-manual
description: 为文件夹生成标准化的"文件夹说明书" README 文档，包含核心功能、输入、输出、定位、依赖和维护规则。当用户请求以下任务时触发：(1) 创建新的模块文件夹或目录结构，(2) 修改某个文件夹内的代码结构需要更新文档，(3) 为文件夹创建或更新 README 说明文档，(4) 明确要求生成"文件夹说明书"。默认命名格式：[模块名]_[文件夹名]_README.md。存在同名冲突时自动添加父文件夹前缀。维护规则包含反向更新机制，自动检查并提示需要同步的全局文档变更。使用脚本检测命名冲突。
argument-hint: "[文件夹路径] [模块名]"
context: fork
---

# 文件夹说明书生成器

## 核心规范（必须遵循）

1. **命名规范**：默认格式 `{模块名}_{文件夹名}_README.md`
2. **冲突处理**：存在同名时自动添加父文件夹前缀
3. **格式严格**：必须包含 6 个章节：核心功能、输入、输出、定位、依赖、维护规则
4. **反向更新**：架构变更时必须反向更新 `Documentation/Basic/` 下的全局文档

## 使用流程

1. **识别目标文件夹**：确定要创建/更新 README 的文件夹路径和模块名称
2. **检查命名冲突**（CRITICAL）：
   ```bash
   python3 $SKILL_DIR/scripts/check_naming_conflict.py <project_root> <module_name> <folder_name>
   ```
   - 脚本返回唯一文件名
   - 默认格式：`{模块名}_{文件夹名}_README.md`
   - 冲突时自动添加父文件夹前缀
3. **生成文档内容**：使用 `template.md` 模板结构生成 README
4. **写入文件**：使用脚本返回的文件名写入目标文件夹

## 命名冲突处理

### 冲突场景示例

```
project/
├── Views/
│   └── Common_README.md       # 已存在
└── Services/
    └── Common/                # 需要创建 README
```

运行脚本检测：
```bash
python3 $SKILL_DIR/scripts/check_naming_conflict.py /path/to/project Core Common
```

**输出**：`Views_Core_Common_README.md`（自动添加父文件夹前缀）

### 脚本参数说明

| 参数 | 说明 | 示例 |
|-----|------|------|
| `project_root` | 项目根目录 | `/Users/user/project` |
| `module_name` | 功能模块名 | `Feature` / `Core` / `Services` |
| `folder_name` | 文件夹名称 | `Components` / `Utils` |

## 模板和示例

- **模板**: 使用根目录的 `template.md` 作为基础结构
- **完整示例**: 查看 `examples/folder-manual-template.md` 了解详细格式和示例

## 反向更新清单

当文件夹 README 的架构定位、核心功能或文件结构发生变更时，需要检查并更新以下全局文档：

| 全局文档 | 路径 | 触发条件 |
|---------|------|---------|
| 项目文件结构 | `Documentation/Basic/File-structure.md` | 文件结构变更 |
| 产品流程说明 | `Documentation/Basic/App-flow.md` | 流程变更 |
| 产品逻辑说明 | `Documentation/Basic/PRD.md` | 功能变更 |
| 前端开发规范 | `Documentation/Basic/Frontend-guidelines.md` | 前端架构变更 |
| 后端架构设计 | `Documentation/Basic/Backend-structure.md` | 后端架构变更 |
| 项目技术栈 | `Documentation/Basic/Tech-stack.md` | 技术栈变更 |
