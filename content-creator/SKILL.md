---
name: content-creator
description: |
  AI内容创作自动化工作流，全流程支持从素材提取到多平台发布。
  
  适用场景：
  - 创建专业内容文章（技术教程、产品评测、经验分享等）
  - 基于个人风格（80%）和标杆技巧（20%）生成内容
  - 一键适配多个平台（小红书、微信公众号、知乎等）
  - 管理完整工作流（从素材到发布）
  - 自动质量评分和优化建议
  - 平台敏感词检查和替代建议
  
  触发词："创建文章"、"生成内容"、"写一篇关于X的文章"、"发布到小红书/微信/知乎"
  
  **配套 Skill**: 使用 content-creator-memory 提供内容索引和智能检索功能。

argument-hint: "[主题/素材路径]"
allowed-tools: ["Read", "Write", "StrReplace", "Glob", "Shell"]

hooks:
  PostToolUse:
    - matcher: "Write"
      hooks:
        # YAML 格式验证
        - type: command
          command: |
            if [[ "$file_path" == *.yaml ]]; then
              python3 "$CLAUDE_PROJECT_DIR/scripts/yaml_utils.py" validate "$file_path" 2>&1 || true
            fi
          timeout: 10
          once: false
---

# AI内容创作自动化工作流

## When to Use

当你需要以下功能时使用此 skill：
- 📝 创建专业的内容文章（技术教程、产品评测、经验分享等）
- 🎯 基于个人风格（80%）和标杆技巧（20%）的智能内容生成
- 🖼️ **大纲思辨与配图共创**（阶段2优化⭐）：强制提供结构方案，区分 `[AI生图]`、`[待截图]` 和平台级 `AI封面图` 占位符，支持与 `@article-illustrator` 联动
- 📱 一键适配多个发布平台（小红书、微信公众号、知乎等）
- 🔄 完整的工作流管理（从素材到发布）
- ⭐ 自动化的内容质量评分和优化建议
- 🔍 **平台敏感词检查**：自动检测并提供替代建议
- 📊 工作区感知的文件管理（自动创建Output目录结构）

**典型场景**：
- "帮我创建一篇关于AI编程的文章，发布到小红书和微信公众号"
- "基于Materials/文件夹的素材，生成一篇技术教程"
- "对比选题方案，给我推荐最佳的标题和大纲"

---

## Prerequisites

### 🔗 配套 Skills

本 skill 依赖以下配套组件：

- **content-creator-memory** (必需): 内容记忆索引系统
  - 用途: 提供自有内容和标杆案例的智能检索
  - 使用: 在需要检索历史作品或标杆案例时自动调用

- **secrets-vault** (封面图 AI 生成时必需): 敏感信息保险库
  - 用途: 存储 AI 图像生成 API 凭证（`apimart_image` 命名空间）
  - 配置: `api_url`, `api_token`, `model`, `task_status_url`
  - 使用: 阶段6检测到缺少封面图且用户选择 AI 生成时自动调用

### 📦 Skill 目录结构

```
~/.cursor/skills/content-creator/
├── scripts/                            # 工具脚本
│   ├── scan_images.py                 # 图片扫描工具
│   ├── init_workspace.py             # 工作区自动初始化工具 ⭐ 新增
│   ├── sanitize_output_markdown.py   # 最终发布稿清洗工具 ⭐ 新增
│   └── stage6_delivery_pipeline.py   # Stage 6 单入口交付管道 ⭐ 新增
├── templates/                          # 静态工作流模板
│   ├── platform_styles_lib.json       # 9大平台样式规则
│   └── quality-scoring-model.md       # 爆款内容评分模型
└── references/                         # 详细文档
    ├── workflow-stages.md              # 6阶段详细说明 ⭐
    ├── configurations.md               # 配置文件说明 ⭐
    ├── best-practices.md               # 最佳实践 ⭐
    ├── interview-clarification.md      # 采访式澄清规则 ⭐ 新增
    ├── troubleshooting.md              # 故障排查 ⭐
    ├── route-templates/               # 三条链路模板 ⭐ 新增
    │   ├── 02l-titles-and-outline.template.md
    │   ├── 02s-hook-and-angle.template.md
    │   ├── 02v-cover-and-storyboard.template.md
    │   ├── 03-image-plan.template.md
    │   └── 04v-visual-draft.template.md
    ├── subagent-templates/            # 候选草稿 subagent 模板 ⭐ 新增
    │   ├── variant-writer-a.md        # 技术专家候选写手
    │   ├── variant-writer-b.md        # 故事描述候选写手
    │   └── variant-writer-c.md        # 幽默犀利候选写手
    ├── style-libraries/               # 草稿风格库 ⭐ 新增
    │   ├── README.md                  # 风格库使用说明
    │   └── core/
    │       ├── technical-expert.md    # 技术专家
    │       ├── storytelling.md        # 故事描述
    │       └── sharp-humor.md         # 幽默犀利
    ├── sensitive-words/                # 敏感词检查模块 ⭐
    │   ├── README.md                   # 使用说明
    │   ├── xhs.md                      # 小红书敏感词库
    │   └── template.md                 # 新平台模板
    └── xhs-image-templates/            # 小红书配图模板库 ⭐ 新增
        ├── README.md                   # 模板索引与选择指南
        ├── template-a-product-launch.md  # 产品首发推广型
        ├── template-b-tutorial.md        # 功能教程型
        ├── template-c-update.md          # 版本更新型
        ├── template-d-poll.md            # 互动投票型
        └── template-e-story.md           # 故事话题型
```

### 📝 记忆系统

记忆数据已完全迁移到 **content-creator-memory** skill，详见该 skill 的说明文档。

---

## 工作区目录结构（自动创建）

每个文章创建在独立的工作区文件夹：

```
[文章工作区]/                   # 用户打开的工作区文件夹
├── Materials/                  # 输入：原始素材（用户提供）
│   ├── origin.md              # 主素材文件
│   └── Medias/                # 媒体资源（可选）
│       └── images/            # 图片文件目录
└── Output/                    # 输出：所有生成内容（自动创建）
    ├── _drafts/               # 中间产物
    │   ├── 00_extracted_meta.yaml
    │   ├── 01_topic_proposals.md
    │   ├── 02_titles_and_outline.md             # long_form
    │   ├── 02S_hook_and_angle.[platform].md     # short_form ⭐ 新增
    │   ├── 02V_cover_and_storyboard.[platform].md # visual_first ⭐ 新增
    │   ├── 03_writing_plan.md                   # long_form
    │   ├── 03_image_plan.[platform].md          # visual_first 图片主文件 ⭐ 新增
    │   ├── 04_variants/          # 单平台三风格候选稿 ⭐ 新增
    │   │   └── [platform]/
    │   │       ├── candidate_technical_expert.md
    │   │       ├── candidate_storytelling.md
    │   │       └── candidate_sharp_humor.md
    │   ├── 04_draft.[platform].[style].md
    │   ├── 05_quality_score.[platform].[style].md
    │   └── 05_draft_optimized_v2.[platform].[style].md（如需优化）
    ├── xhs/                   # 小红书版本
    │   ├── article.md
    │   ├── metadata.yaml ⭐
    │   ├── compliance-report.json ⭐
    │   ├── image_plan.md ⭐     # 由 03_image_plan.[platform].md 同步生成
    │   └── images/
    ├── wechat/                # 微信公众号版本
    │   ├── article.md
    │   ├── metadata.yaml ⭐
    │   └── images/
    └── _reports/              # 质量报告（可选）
```

---

## 📋 完整工作流（6个主阶段 + 1个强制澄清环节）

| 阶段 | 名称 | 目标 | 输出 | 用户确认 | 详细说明 |
|:---:|:-----|:-----|:-----|:-------:|:--------|
| **0** | 素材提取 | 提取结构化元数据 | `00_extracted_meta.yaml` | ✅ 需要 | [workflow-stages.md#阶段0](references/workflow-stages.md#阶段0素材提取与认知校正) |
| **1** | 选题策划 | 生成3个选题方案 | `01_topic_proposals.md` | ✅ 需要 | [workflow-stages.md#阶段1](references/workflow-stages.md#阶段1选题策划) |
| **1.5** | 采访式澄清 | 用 1~3 轮轻量访谈补齐方向、证据、平台语境与风格偏好 | 无强制独立文件（按对话完成） | ✅ 强制 | [workflow-stages.md#阶段15](references/workflow-stages.md#阶段15采访式澄清强制门禁) |
| **2** | 路线化前置规划 | 按平台路由生成标题大纲 / 核心判断卡 / 封面叙事板 | `02_titles_and_outline.md`(long) `02S_hook_and_angle.[platform].md`(short) `02V_cover_and_storyboard.[platform].md`(visual) | ✅ 需要 | [workflow-stages.md#阶段2](references/workflow-stages.md#阶段2路线化创作前置规划) |
| **3** | 创作规划 | long_form 生成写作剧本；visual_first 生成图片主文件；short_form 直接进入候选稿 | `03_writing_plan.md`(long) `03_image_plan.[platform].md`(visual) | ✅ 需要 | [workflow-stages.md#阶段3](references/workflow-stages.md#阶段3路线化创作规划) |
| **4** | 候选草稿+正文展开 | 并行生成 3 种风格候选稿并展开选中版本 | `04_variants/` `04_draft.[platform].[style].md` | ✅ 需要 | [workflow-stages.md#阶段4](references/workflow-stages.md#阶段4多风格候选草稿与正文展开) |
| **5** | 评分优化 | 对选中风格正文评分+优化（如<8分） | `05_quality_score.[platform].[style].md` | ❌ 自动 | [workflow-stages.md#阶段5](references/workflow-stages.md#阶段5爆款潜力评分与优化) |
| **6** | 多平台适配 | 各平台版本+敏感词检查⭐ | `xhs/`, `wechat/` | ⚠️ 敏感词 | [workflow-stages.md#阶段6](references/workflow-stages.md#阶段6多平台适配) |

### 核心特性

- **80/20 记忆策略**：80% 自有内容风格 + 20% 标杆技巧
- **质量自动优化**：<8 分自动触发优化
- **敏感词检查**：自动检测并提供替代建议（阶段6）
- **平台级封面图智能处理**：按平台生成头部封面占位，当前优先支持 wechat / jike / twitter，内置平台比例策略
- **多平台一键适配**：支持 9 大平台（wechat, xhs, zhihu, jike, twitter, linkedin, douyin, bilibili, instagram）
- **三条创作链路路由**：`long_form`、`short_form`、`visual_first` 按平台内容形态自动切换
- **采访式澄清门禁**：阶段1后必须进行 `1~3` 轮轻量采访式澄清，先补齐目标、证据、平台语境和风格偏好，再进入 route-specific 规划
- **单平台三风格候选草稿**：阶段4A 固定并行生成 `技术专家`、`故事描述`、`幽默犀利` 3 篇候选草稿，用户选中后再展开正式正文
- **结构化选稿指标**：候选稿对比采用固定表格与推荐指数 rubric，避免纯主观判断
- **统一图片标识协议**：三条链路统一使用 `AI封面图`、`[AI生图]`、`[待截图]`，仅图片主文件因链路不同而变化
- **中文 AI 生图提示词**：`AI封面图` 与 `[AI生图]` 的提示词统一使用中文，便于后续统一生图链路
- **图注与提示词分离**：所有 AI 图片占位必须同时包含 `caption` 与 `prompt`；`caption` 只写给读者看的精简场景概述，`prompt` 只给模型，禁止把提示词直接暴露为图片图注
- **比例显式声明**：所有 `AI封面图` 与正文 `[AI生图]` 都必须显式声明 `aspect_ratio`；只能从当前接口支持的比例集合中选择，微信公众号封面默认使用 `21:9`
- **视觉优先正文去 PPT 化**：`visual_first` 的 `04_draft.[platform].[style].md` 必须是有故事感的图文正文，图片可以呼应文案，但不要求每一页文字都逐图讲解，禁止写成“图1/图2/图3”式 PPT 解说词
- **插画助手统一执行**：阶段 6 生成文章后，所有 AI 图片任务统一交由 `@article-illustrator` 执行，包括 `AI封面图` 与正文 `[AI生图]`；其中视觉优先平台优先扫描 `03_image_plan.[platform].md`
- **单入口配图执行**：优先通过 `run_illustration_pipeline.py` 一次完成“扫描 + 生图 + 占位消费回写”，避免遗漏中间步骤
- **占位自动消费**：`article-illustrator` 生图完成或命中 `skip existing` 后，会立即把 `AI封面图` 与 `[AI生图]` 回写成普通图片引用，避免后续再次被识别成待执行任务
- **阶段6 发布稿确定性清洗**：生成 `Output/{platform}/article.md` 时，必须优先调用 `sanitize_output_markdown.py` 清理固定作者辅助标记（如 `> 💡 **截图指引**：...`），禁止默认依赖 Agent 手工删除；仅在脚本缺失或执行失败时，才允许 fallback 到手工处理并显式说明
- **封面图职责收口**：`content-creator` 负责产出封面占位与触发时机，但不再直接执行封面生图；封面图与正文 AI 图统一由 `article-illustrator` 执行
- **平台级交付自动化配置**：通过 `workspace.config.yaml > delivery.platforms.{platform}.mode` 控制每个平台默认执行 `auto_format` 或 `auto_format_and_publish`
- **创作模式配置**：通过 `workspace.config.yaml > creation.mode` 控制 `collaborative`（人机协同）或 `autonomous`（自动创作）；自动模式下 warning 默认继续执行并写入 `Output/_reports/autonomous-run-report.md`
- **Stage 6 单入口交付管道**：通过 `stage6_delivery_pipeline.py` 一次完成复制素材、清洗正文、统一配图、微信 HTML 格式化和按配置自动发布

📖 **完整执行步骤**: [references/workflow-stages.md](references/workflow-stages.md)
📖 **采访式澄清模板**: [references/interview-clarification.md](references/interview-clarification.md)

---

## 🛠️ 核心工具

### 图片扫描工具（scan_images.py）⭐

**用途**：自动扫描工作区的 `Materials/Medias/images/` 目录，列出所有图片文件

**位置**：`~/.cursor/skills/content-creator/scripts/scan_images.py`

**使用方法**：

```bash
# 在工作区根目录执行
python3 ~/.cursor/skills/content-creator/scripts/scan_images.py [工作区路径] markdown

# 输出示例：
## 图片扫描结果
- 工作区: `/Users/xxx/my-article`
- 图片目录: `/Users/xxx/my-article/Materials/Medias/images`
- 目录存在: ✅ 是
- 图片总数: **5** 张

### 图片清单
1. `Medias/images/01-preview.png` (序号: 01) [关键词: preview]
2. `Medias/images/02-workflow.png` (序号: 02) [关键词: workflow]
...
```

**⚠️ 重要**：在阶段3（写作剧本生成）时，Agent 必须先运行此工具，才能生成包含图片的写作指令

### AI 图片执行入口（统一使用 article-illustrator）⭐

**用途**：在阶段6统一执行所有 AI 图片任务，包括：
- `AI封面图`
- 正文 `[AI生图]`

**⚠️ 默认不单独调用**：正常情况下应通过 `stage6_delivery_pipeline.py` 触发；本节仅说明其内部职责与调试用法。

**执行原则**：
- 所有 AI 图片统一交给 `@article-illustrator`
- 若输出文件已存在，`article-illustrator` 默认跳过；仅显式 `--force` 时才允许重生

**工作区模式推荐调用**：

```text
long_form / short_form:
  -> 调用 run_illustration_pipeline.py 处理 Output/{platform}/article.md

visual_first:
  -> 调用 run_illustration_pipeline.py 处理 Output/{platform}/image_plan.md
```

**命令模板**：

```bash
python3 ~/.cursor/skills/article-illustrator/scripts/run_illustration_pipeline.py \
  [工作区路径] \
  --platform [platform]
```

### 最终发布稿清洗工具（sanitize_output_markdown.py）⭐ 新增

**用途**：在阶段6生成最终 `article.md` 时，确定性清理作者辅助标记，避免把截图指引这类固定提示混入发布稿

**⚠️ 默认不单独调用**：正常情况下应通过 `stage6_delivery_pipeline.py` 触发；本节仅说明其内部职责与调试用法。

**位置**：`~/.cursor/skills/content-creator/scripts/sanitize_output_markdown.py`

**使用原则**：
- 生成 `Output/{platform}/article.md` 时必须优先调用
- 不应默认依赖 Agent 手工删除 `> 💡 **截图指引**：...`
- `visual_first` 的 `image_plan.md` 不使用该脚本删除截图指引，因为它本来就是图片执行文件
- Stage 6 实际执行顺序固定为：`复制图片资源 -> 调用 sanitize_output_markdown.py 生成 article.md -> 调用 run_illustration_pipeline.py 统一执行配图 -> 再继续平台适配与合规检查`

**示例**：

```bash
# long_form 图文混排平台：删除截图指引 + 改写图片路径
python3 ~/.cursor/skills/content-creator/scripts/sanitize_output_markdown.py \
  --input Output/_drafts/05_draft_optimized_v2.wechat.storytelling.md \
  --output Output/wechat/article.md \
  --strip-screenshot-guides \
  --rewrite-image-paths

# short_form / visual_first 的 article.md：删除截图指引 + 删除正文图片占位
python3 ~/.cursor/skills/content-creator/scripts/sanitize_output_markdown.py \
  --input Output/_drafts/04_draft.jike.storytelling.md \
  --output Output/jike/article.md \
  --strip-screenshot-guides \
  --strip-image-placeholders
```

### Stage 6 单入口交付管道（stage6_delivery_pipeline.py）⭐ 新增

**用途**：读取 `workspace.config.yaml > delivery.platforms.{platform}.mode`，统一完成 Stage 6 的实际执行。

**位置**：`~/.cursor/skills/content-creator/scripts/stage6_delivery_pipeline.py`

**执行内容**：
- 复制 `Materials/Medias/images/` 到 `Output/{platform}/images/`
- 调用 `sanitize_output_markdown.py` 生成最终 `article.md`
- 对 visual_first 同步 `Output/{platform}/image_plan.md`
- 调用 `run_illustration_pipeline.py` 统一执行 AI 图片
- 若平台为 `wechat`，自动执行 `markdown-to-wechat` 生成 `article.html`
- 若平台配置为 `auto_format_and_publish`，继续调用 `content-publisher`
- 若进入自动发布阶段，平台发布所需敏感信息统一由 `content-publisher` 通过 [`/secrets-vault` Skill](/Users/mileson/.cursor/skills/secrets-vault/SKILL.md) 获取，`content-creator` 不直接读取发布凭证
- 若 `creation.mode = autonomous`，遇到 warning 默认继续执行，并汇总写入 `Output/_reports/autonomous-run-report.md`
- 每次真实执行后，会把本次 Stage 6 结果回写到 `Output/{platform}/metadata.yaml` 的 `last_delivery` 和 `delivery_records`
- 每次真实执行后，还会把本次跨平台结果汇总回写到 `Output/_reports/delivery-summary.yaml`

**默认执行提示**：

```text
Stage 6 默认直接调用 stage6_delivery_pipeline.py。
除非用户明确要求逐步调试某个子流程，否则不要再拆成“先清洗、再配图、再 markdown-to-wechat、再发布”的人工多步执行。

### Stage 6 收尾回复模板

Stage 6 完成后，默认按 `workspace.config.yaml > delivery.platforms.{platform}.mode` 选择收尾话术：

- `auto_format`
  - 汇报：`article.md`、`images/`、`metadata.yaml`
  - `wechat` 额外汇报：`article.html`
  - 状态统一写为：`已完成本地交付包`
  - 不再提示用户手动调用任何 Skill

- `auto_format_and_publish`
  - 先汇报本地交付包
  - 再汇报平台发布结果
  - `wechat`：草稿创建结果
  - `jike`：真实发布结果
  - 不再提示用户手动执行发布
```

**示例**：

```bash
# 处理工作区内全部目标平台
python3 ~/.cursor/skills/content-creator/scripts/stage6_delivery_pipeline.py \
  [工作区路径]

# 只处理单个平台
python3 ~/.cursor/skills/content-creator/scripts/stage6_delivery_pipeline.py \
  [工作区路径] \
  --platform wechat

# dry-run 预览执行计划
python3 ~/.cursor/skills/content-creator/scripts/stage6_delivery_pipeline.py \
  [工作区路径] \
  --dry-run
```

---

## 🚀 快速开始

### 启动模式 A：已有工作区
```bash
mkdir "我的文章标题" && cd "我的文章标题"
mkdir -p Materials/Medias/images
echo "原始内容..." > Materials/origin.md
# 将图片文件放到 Materials/Medias/images/ 目录
```

### 启动模式 B：任意目录启动（推荐）
先沟通确认选题，再在当前目录自动创建本次内容创作工作区：

```bash
python3 ~/.cursor/skills/content-creator/scripts/init_workspace.py \
  --base-dir "$(pwd)" \
  --topic "AI 内容工作流重构复盘" \
  --platforms "jike,wechat" \
  --seed-text "围绕这次工作流重构，写一篇兼顾即刻和公众号的内容"
```

初始化后会自动生成：
- 选题目录
- `Materials/origin.md`
- `Output/` 标准目录结构
- `workspace.config.yaml`

默认交付配置：
- 默认创作模式为 `collaborative`（人机协同）
- 所有目标平台初始化为 `auto_format`
- 后续如需指定平台自动继续调用 `content-publisher`，可将该平台改为 `auto_format_and_publish`

### 步骤 2：执行 Skill
```
@content-creator 帮我创建一篇关于[主题]的文章，发布到[平台1]和[平台2]
```

### 步骤 3：配合确认
- 阶段0-3：确认元数据、选题、标题、剧本
- 阶段4：查看 3 篇不同风格候选稿的表格化对比，选中一个风格
- 阶段4-5：展开选中风格正文并评分优化
- 阶段6：自动生成多平台版本（如有敏感词需确认）

### 步骤 4：查看成果
```
Output/
├── xhs/article.md          # 小红书版本
├── wechat/article.md       # 微信公众号版本
└── _drafts/                # 所有中间产物
```

---

## 🎯 核心配置

### 1. 平台规则库
- **位置**：`templates/platform_styles_lib.json`
- **支持**：wechat, xhs, zhihu, jike, twitter, linkedin, douyin, bilibili, instagram
- 📖 [详细说明](references/configurations.md#2-平台规则库)

### 1.5 草稿风格库 ⭐ 新增
- **位置**：`references/style-libraries/core/`
- **当前固定风格**：`technical-expert`、`storytelling`、`sharp-humor`
- **用途**：阶段4A 并行生成 3 种候选草稿
- **说明**：风格库只负责“怎么写”，不替代 `content-creator-memory` 的内容检索能力

### 1.6 候选稿 subagent 模板 ⭐ 新增
- **位置**：`references/subagent-templates/`
- **用途**：安装到工作区 `.claude/agents/` 后并行生成三风格候选稿
- **当前固定角色**：
  - `variant-writer-a` → 技术专家
  - `variant-writer-b` → 故事描述
  - `variant-writer-c` → 幽默犀利

### 2. 敏感词库
- **位置**：`references/sensitive-words/`
- **当前支持**：小红书（xhs.md）
- **功能**：自动检测、替代建议、生成报告
- 📖 [详细说明](references/sensitive-words/README.md)

### 3. 小红书配图模板库 ⭐ 新增
- **位置**：`references/xhs-image-templates/`
- **模板**：5 种固定模板（产品首发、功能教程、版本更新、互动投票、故事话题）
- **功能**：自动匹配笔记类型 → 生成逐图设计规范 + AI 生图提示词
- **触发**：阶段3（写作剧本）目标平台包含 xhs 时自动加载
- **输出**：`Output/xhs/image_plan.md`（含可直接复制使用的 AI 提示词）
- **扩展**：新增模板按 `template-{id}-{name}.md` 格式添加到目录并更新 README.md 索引
- 📖 [详细说明](references/xhs-image-templates/README.md)

### 4. 评分模型
- **位置**：`templates/quality-scoring-model.md`
- **体系**：观感(50分) + 视角(30分) + 场景(30分) + 本质(40分) = 150分 → 10分制
- **阈值**：≥8分通过，<8分自动优化
- 📖 [详细说明](templates/quality-scoring-model.md)

### 5. 内容记忆系统
- **管理**：通过 content-creator-memory skill
- **策略**：80% 自有内容 + 20% 标杆案例
- 📖 [详细说明](references/configurations.md#1-内容记忆系统)

---

## 📚 扩展文档

| 文档 | 用途 |
|:-----|:-----|
| [workflow-stages.md](references/workflow-stages.md) | 6阶段详细执行步骤 |
| [configurations.md](references/configurations.md) | 平台规则、评分模型、记忆系统 |
| [best-practices.md](references/best-practices.md) | 提升使用效果的技巧 |
| [style-libraries/README.md](references/style-libraries/README.md) | 草稿风格库维护与扩展说明 |
| [troubleshooting.md](references/troubleshooting.md) | 常见问题解决方案 |
| [sensitive-words/README.md](references/sensitive-words/README.md) | 敏感词检测使用说明 |
| [xhs-image-templates/README.md](references/xhs-image-templates/README.md) | 小红书配图模板库索引 |

---

## ⚠️ Important Notes

### 依赖检查（必需）
- [ ] content-creator-memory skill 已安装
- [ ] 内容记忆系统有自有内容（至少 5 篇）
- [ ] 内容记忆系统有标杆案例（至少 10 篇）

### 工作区要求（必需）
- [ ] Materials/origin.md（主素材，建议5000字+；可通过 `init_workspace.py` 自动生成种子文件）
- [ ] 目标发布平台（在初始请求中明确）

### 平台限制
- **支持的平台**：wechat, xhs, zhihu, jike, twitter, linkedin, douyin, bilibili, instagram
- **敏感词检查**：当前仅支持小红书（xhs），其他平台跳过检查
- **多风格候选模式**：当前按**单个平台**执行；如果用户一次请求多个平台，先确认当前优先生成哪个平台的三风格候选稿

---

## ✅ Output Checklist

完成后确认以下文件已生成：

### 中间产物（_drafts/）
- [ ] 00_extracted_meta.yaml、01_topic_proposals.md、02_titles_and_outline.md
- [ ] long_form：03_writing_plan.md
- [ ] visual_first：03_image_plan.[platform].md
- [ ] 04_variants/[platform]/candidate_technical_expert.md
- [ ] 04_variants/[platform]/candidate_storytelling.md
- [ ] 04_variants/[platform]/candidate_sharp_humor.md
- [ ] 04_draft.[platform].[style].md
- [ ] visual_first：03_image_plan.[platform].md（视觉优先图片主文件）
- [ ] 05_quality_score.[platform].[style].md（如需优化则有 v2 版本）

### 平台版本（各平台文件夹）
- [ ] article.md（平台适配版本）
- [ ] metadata.yaml ⭐（元数据，YAML 格式）
- [ ] compliance-report.json（敏感词检测报告，仅小红书等平台）
- [ ] image_plan.md（配图策划文档，仅小红书，含 AI 生图提示词）⭐
- [ ] images/（处理后的图片）

### 工作区文件
- [ ] workspace.config.yaml（状态为 "completed"）

---

## 🔗 相关资源

- ✅ 工作流模板：`content-creator/templates/`
- ✅ 参考文档：`content-creator/references/`
- ✅ 敏感词库：`content-creator/references/sensitive-words/`
- ✅ 小红书配图模板：`content-creator/references/xhs-image-templates/`
- ✅ 草稿风格库：`content-creator/references/style-libraries/`
- ✅ subagent 模板：`content-creator/references/subagent-templates/`
- ✅ 记忆系统：`content-creator-memory`（配套 skill）

**扩展和自定义**（可选）：
- 添加更多自有作品/标杆案例到 content-creator-memory
- 使用 content-creator-memory 的管理工具重建索引
- 修改 `templates/platform_styles_lib.json` 自定义平台规则
- 添加新平台敏感词库到 `references/sensitive-words/{platform_id}.md`
- 添加新的小红书配图模板到 `references/xhs-image-templates/template-{id}-{name}.md`
