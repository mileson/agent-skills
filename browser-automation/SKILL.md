---
name: browser-automation
description: |
  AI 驱动的浏览器自动化。当需要执行以下任务时使用此 skill：
  - 打开网页并提取信息（网页抓取、数据收集）
  - 在网站上执行操作（表单填写、按钮点击、登录）
  - 网页截图或生成 PDF
  - 跨页面导航和多步骤网页任务
  - 下载文件或上传文件
  - 测试网页功能或验证 UI

  触发场景：用户请求涉及"打开网页"、"访问网站"、"浏览器操作"、"网页自动化"、"点击按钮"、"填写表单"、"爬取数据"等任务。

user-invocable: false
allowed-tools:
  - Bash
  - Read
---

# Browser Automation

基于 browser-use Cloud API 的浏览器自动化 Skill。通过 AI Agent 控制浏览器执行复杂网页任务。

## 快速开始

**执行任务**（推荐方式）:

```bash
# 创建任务并等待完成
python scripts/browser_use.py run "访问 https://example.com 并提取页面标题"

# 简单任务（一步完成）
python scripts/browser_use.py run "在 Google 搜索 AI news 并返回前3条结果"
```

## 核心命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `run` | 创建任务并等待完成 | `python browser_use.py run "任务描述"` |
| `create` | 仅创建任务（返回 task_id） | `python browser_use.py create "任务描述"` |
| `status` | 查询任务状态 | `python browser_use.py status <task_id>` |
| `list` | 列出历史任务 | `python browser_use.py list` |
| `stop` | 停止/暂停任务 | `python browser_use.py stop <task_id>` |
| `download` | 获取文件下载链接 | `python browser_use.py download <task_id> <file_id>` |

## 任务状态

| 状态 | 说明 |
|------|------|
| `started` | 执行中 |
| `paused` | 已暂停 |
| `finished` | 已完成 |
| `stopped` | 已停止 |

## 高级选项

```bash
# 限制可访问的域名（安全控制）
python scripts/browser_use.py run "登录 GitHub" --allowed-domains "github.com,*.github.com"

# 启用视觉能力（处理图片/CAPTCHA）
python scripts/browser_use.py run "识别验证码并登录" --vision

# 快速模式（跳过思考步骤，适合简单任务）
python scripts/browser_use.py run "打开网页截图" --flash-mode

# 限制最大步骤数
python scripts/browser_use.py run "复杂任务" --max-steps 50
```

## 工作流程

```
1. 构建任务描述 → 2. 调用 run 命令 → 3. 解析返回的 JSON 结果
```

**任务描述最佳实践**:
- 清晰描述目标："访问 X 网站，点击 Y 按钮，提取 Z 信息"
- 指定输出格式："返回 JSON 格式的结果"
- 提供必要上下文："使用用户名 foo 密码 bar 登录"

## 结果解析

`run` 命令返回 JSON 格式：

```json
{
  "id": "task-uuid",
  "status": "finished",
  "isSuccess": true,
  "output": "任务执行结果（文本）",
  "outputFiles": [
    {"id": "file-uuid", "fileName": "screenshot.png"}
  ],
  "steps": [...]
}
```

- `output`: 任务文本输出
- `outputFiles`: 生成的文件列表（截图、下载文件等）
- `isSuccess`: 任务是否成功完成

## 下载文件

如果任务生成了文件（截图、下载），使用 `download` 命令获取下载链接：

```bash
python scripts/browser_use.py download <task_id> <file_id>
# 返回: {"url": "https://presigned-url..."}
```

## 常见用例

**网页数据提取**:
```bash
python scripts/browser_use.py run "访问 Hacker News 首页，提取前5条新闻的标题和链接"
```

**表单填写**:
```bash
python scripts/browser_use.py run "打开 example.com/form，填写姓名为张三，邮箱为test@example.com，提交表单"
```

**截图**:
```bash
python scripts/browser_use.py run "打开 apple.com，截取首页完整截图"
```

**登录操作**:
```bash
python scripts/browser_use.py run "登录 GitHub，用户名 xxx，密码 yyy，确认登录成功" \
  --allowed-domains "github.com,*.github.com"
```

## 错误处理

常见错误：
- `401`: API Key 无效
- `402`: 余额不足
- `429`: 请求过多（自动重试）
- `5xx`: 服务器错误（自动重试）

脚本内置指数退避重试机制，无需手动处理。
