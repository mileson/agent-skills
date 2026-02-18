---
name: open-source-publish
description: |
  开源发布与提交自动化工作流。两种模式：
  (1) 首次发布：检测 Git 环境 → 扫描敏感信息 → 完善开源资产 → 提交推送 → 仓库公开
  (2) 常规提交：快速敏感扫描 → 功能导向 Commit → Push
  触发场景：用户说"开源发布"、"公开仓库"、"开源检查"、"提交代码"、"commit"等。
disable-model-invocation: true
---

# 开源发布与提交工作流

## 模式自动识别

```
用户触发 /open-source-publish
         │
         ▼
  ┌─ 检测项目状态 ─┐
  │                │
  ▼                ▼
仓库未公开       仓库已公开
或首次发布       且非首次
  │                │
  ▼                ▼
Mode A           Mode B
首次开源发布     常规提交
(7 阶段)         (快速流程)
```

**识别逻辑**：
1. `git remote -v` 有远程 + `gh api repos/{owner}/{repo}` 返回 `private: false` → **Mode B**
2. 用户明确说"开源"、"公开" → **Mode A**
3. 用户明确说"提交"、"commit"、"push" → **Mode B**
4. 其他情况 → 询问用户意图

---

## Mode A: 首次开源发布

完整的 7 阶段工作流，确保项目安全、完整、专业地完成开源发布。

| 阶段 | 名称 | 用户确认 |
|:---:|:-----|:-------:|
| 1 | Git 环境检测 | ⚠️ 非 Git 仓库时 |
| 2 | 远程仓库 & 可见性 | ⚠️ 需配置时 |
| 3 | 当前文件敏感扫描 | ✅ 发现问题时 |
| 4 | Git 历史敏感扫描 | ✅ 发现泄露时 |
| 5 | 开源资产完善 | ✅ 内容确认 |
| 6 | Commit & Push | ❌ 自动 |
| 7 | 发布 & 验证 | ⚠️ 公开仓库时 |

### Stage 1: Git 环境检测

```
git rev-parse --is-inside-work-tree
├── ✅ 是 Git 仓库 → Stage 2
└── ❌ 不是 →
    检测 git config --global user.name / user.email
    ├── 有配置 → "检测到身份：<name> (<email>)，是否用此初始化？"
    │   ├── 确认 → git init → Stage 2
    │   └── 拒绝 → 请用户提供 name/email
    └── 无配置 → "未检测到 Git 身份，请提供 name 和 email"
        → 收到后 git init（使用 git config --local）→ Stage 2
```

**约束**：禁止修改全局 Git 配置，仅用 `git config --local`

### Stage 2: 远程仓库 & 可见性

```
git remote -v
├── 有远程 →
│   gh api repos/{owner}/{repo} --jq '.private'
│   ├── false → ⚠️ "仓库已公开！历史已暴露，继续扫描清理。"
│   ├── true → "仓库为私有，将在 Stage 7 公开。"
│   └── 失败 → 记录状态继续
└── 无远程 →
    "请提供 GitHub 仓库 URL，或需要创建新仓库？"
    ├── 提供 URL → git remote add origin <url>
    └── 创建仓库 → 从 secrets-vault 读取 GitHub 凭证
        python3 ~/.cursor/skills/secrets-vault/scripts/get_secret.py github token
        → gh api 创建仓库（默认 public，开源发布场景无需先私有再公开）
        → git remote add origin
```

### Stage 3: 当前文件敏感扫描

**核心策略**：不使用固定正则，利用 Agent AI 理解力进行多轮扫描。

**三轮扫描**：

| 轮次 | 策略 | 扫描内容 |
|------|------|---------|
| 第一轮 | 经典模式 | API 密钥、数据库连接、Token/JWT、密码、内网地址、云服务 ID、私钥、Webhook、个人信息 |
| 第二轮 | 技术栈推断 | 基于项目依赖自动推断额外检查项（如 Supabase→service_role_key） |
| 第三轮 | 边界场景 | 注释中的密钥、测试报告、嵌套配置、文档真实值、lock 文件私有 registry 等 |

**执行**：`git ls-files` 获取文件列表 → 按文件类型分批读取分析 → 持续扫描直到连续一轮无新发现。

📖 详细扫描模式和示例见 [references/sensitive-scan-guide.md](references/sensitive-scan-guide.md)

**输出**：分级报告（🔴高危 / 🟡中危 / 🟢低危 / ✅安全），呈现给用户确认后处理。

**处理策略**：

| 类型 | 处理 |
|------|------|
| 硬编码密钥 | 替换为 `process.env.XXX`，更新 `.env.example` |
| 真实数据文件 | 加入 `.gitignore`，`git rm --cached` |
| 内网地址 | 替换为 `YOUR_SERVER_IP` 等占位符 |
| 默认密码 | 移除默认值，强制从环境变量读取 |

### Stage 4: Git 历史敏感扫描

基于 Stage 3 发现的敏感字符串在历史中搜索：

```bash
git log -S "<sensitive_string>" --all --oneline        # 搜索敏感字符串
git log --all --diff-filter=D --summary -- "*.env"     # 搜索已删除敏感文件
```

发现泄露 → 生成报告 → 用户确认后用 `git filter-repo` 清理：

```bash
git branch backup-before-cleanup                       # 备份
git filter-repo --invert-paths --path <file>           # 移除文件
git filter-repo --replace-text replacements.txt        # 替换字符串
git remote add origin <url>                            # filter-repo 会移除 remote
# ⚠️ force push 必须用户确认后执行
```

📖 详细命令参考见 [references/sensitive-scan-guide.md](references/sensitive-scan-guide.md#git-历史扫描策略)

### Stage 5: 开源资产完善

检查并完善以下资产：

| 资产 | 不存在时 | 已存在时 |
|------|---------|---------|
| **README.md** | 分析项目 + Web 搜索竞品 + 从用户视角创建 | 评估完善度（≥7/9 标准），必要时补充 |
| **LICENSE** | 询问用户偏好，默认推荐 MIT | 确认年份和作者信息 |
| **.env.example** | 从代码提取 `process.env.*` 引用，生成占位符版 | 对比代码确认无遗漏、无真实值 |
| **.gitignore** | 基于技术栈生成完整版 | 检查是否遗漏敏感文件类型 |

📖 详细模板和检查标准见 [references/open-source-assets.md](references/open-source-assets.md)

### Stage 6: Commit & Push

> 此阶段同时服务于 Mode A 和 Mode B，是 skill 的核心能力。

详见下方 **[Commit 规范](#commit-规范)** 章节。

### Stage 7: 发布 & 验证

```
如果仓库为私有：
1. "所有检查和清理已完成，是否将仓库设为公开？"
2. 确认后 →
   python3 ~/.cursor/skills/secrets-vault/scripts/get_secret.py github token
   gh api -X PATCH repos/{owner}/{repo} -f visibility=public \
     -f description="..." -f homepage="..."
3. 可选：gh api -X PUT repos/{owner}/{repo}/topics -f '{"names":[...]}'

最终验证：
- 通过 GitHub API 抽查关键文件无敏感信息
- README 正常渲染、LICENSE 存在、.env.example 安全
- 输出完成报告
```

---

## Mode B: 常规提交

仓库已公开后的日常提交流程。

```
1. 快速敏感扫描（可选）
   对本次变更的文件（git diff --name-only）进行快速扫描
   仅检查新增/修改内容是否包含敏感信息
   ├── 发现敏感信息 → 报告用户，处理后继续
   └── 无敏感信息 → 继续

2. Commit & Push
   按下方 Commit 规范执行
```

**触发方式**：
```
/open-source-publish              # 自动识别为 Mode B（如果仓库已公开）
"帮我提交代码"
"commit 并 push"
```

---

## Commit 规范

### 核心原则

Commit 信息描述**用户能感知的变化**，而非技术实现细节。

| ✅ 正确 | ❌ 避免 |
|---------|---------|
| 修复,相机界面底部布局偏移问题 | 优化，CameraPreviewView 添加 frame(maxWidth: .infinity) |
| 新增,按钮禁用状态的视觉反馈 | 新增，ColorTheme.createSaveButtonDisabledBackground |
| 精简,多语言配置以提升启动速度 | 优化，Localizable.xcstrings 从 4.1 万行减少到 8000 行 |

### 写作规则

1. **聚焦用户价值**：描述对用户的影响
2. **使用祈使句**：新增/修复/优化/移除/改进/更新/调整/整合/精简
3. **标题 ≤ 20 字符**，条目 ≤ 50 字符
4. **避免技术细节**：不出现文件名、函数名、参数值

### 动作词

| 动作词 | 场景 | 动作词 | 场景 |
|-------|------|-------|------|
| 新增 | 新功能/组件 | 移除 | 废弃功能/冗余代码 |
| 修复 | Bug/兼容性 | 更新 | 数据/配置/文档 |
| 优化 | 性能/体验 | 调整 | 参数/布局 |
| 改进 | 功能改进 | 整合 | 合并/整合 |
| 精简 | 减少体积 | | |

### 格式

```
<精简标题>（≤20字符）

- 动作词,功能描述
- 动作词,功能描述

Co-Authored-By: Claude (可选)
```

### 标题示例

| 条目 | 标题 |
|------|------|
| 清理敏感信息 + 完善开源资产 | 开源发布准备 |
| 修复面板点击 + 优化面板交互 | 面板交互优化 |

### 执行步骤

```
1. git status + git diff [--staged] 查看变更
2. 分析变更，提取用户价值描述
3. 生成 Commit 信息
4. git add . + git commit -m "..."
5. git push（自动执行，无需用户确认）
6. push 失败 → 显示错误，不自动重试
```

**force push 例外**：如有历史清理导致需要 force push，必须告知用户并等待确认。

---

## 参考文档

| 文档 | 内容 |
|------|------|
| [sensitive-scan-guide.md](references/sensitive-scan-guide.md) | 三轮扫描详细模式、技术栈推断表、边界场景清单、历史扫描命令 |
| [open-source-assets.md](references/open-source-assets.md) | README 评估标准/模板、LICENSE 选择、.env.example 生成、.gitignore 清单 |
| [checklist.md](references/checklist.md) | 全阶段检查清单，逐项勾选 |

---

## ⚠️ 重要约束

### 安全红线
- **禁止**修改全局 Git 配置
- **禁止**自动 force push（必须用户确认）
- **禁止**在代码或 Commit 中包含真实密钥
- 敏感信息发现必须**报告用户确认**后再处理

### 破坏性操作提醒
- `git filter-repo`：重写历史，需 force push，协作者需重新 clone
- 仓库一旦公开，历史代码即对外可见，公开前务必确保敏感信息已清理完毕

### 依赖
- `git`：必需
- `gh` CLI：推荐（GitHub API 操作）
- `git-filter-repo`：历史清理时需要（`pip install git-filter-repo`）
- `secrets-vault` skill：仅在需要 GitHub API 操作时读取凭证
