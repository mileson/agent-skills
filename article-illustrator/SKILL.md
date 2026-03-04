---
name: article-illustrator
description: 文章配图助手。扫描 Markdown 文件中的图片占位符，结合上下文提炼视觉细节并应用预设风格模板，通过 APIMart Gemini API 生成高质量配图并精准存入占位符指定路径。当用户要求“配图”、“为文章生成插图”、“处理图片占位符”时触发。
---

# Article Illustrator (文章配图助手)

## 定位

当与 `content-creator` 配合时，`article-illustrator` 是**唯一的 AI 图片执行入口**：
- 统一处理 `AI封面图`
- 统一处理正文 `[AI生图]`
- 严格跳过 `[待截图]`
- 默认对已存在输出文件执行 `skip existing`，只有显式传入 `--force` 才允许重新生成
- 推荐优先使用单入口脚本 `run_illustration_pipeline.py`，一次完成扫描、生图与占位回写

## 核心工作流：占位符驱动配图

当用户请求为某篇文章生成配图时，Agent 必须遵循以下流程：

### 1. 扫描与读取
- 使用 `Read` 或 `Shell` 工具读取用户指定的 Markdown 文章。
- 如果输入来自 `content-creator` 工作区，不要盲扫任意文件，必须先按平台 `workflow_route` 解析“最终图片主文件”：

```text
long_form
  -> 扫描 Output/{platform}/article.md

short_form
  -> 扫描 Output/{platform}/article.md

visual_first
  -> 扫描 Output/{platform}/image_plan.md
```

- **⚠️ 边界规则**：`工作区目录 + 平台` 模式只面向最终正文产物，不用于 `_drafts` 里的草稿。
- 如果你要对草稿做扫描或生图验证，只能使用“直接传具体 Markdown 文件”的模式。

- 扫描文件中的图片占位符和头部封面占位注释。
- **⚠️ 核心过滤规则（极其重要）**：
  - **处理正文生图**：带有 `[AI生图]` 标记的占位符，例如：`![[AI生图][数据安全隧道][16:9] 数据在安全隧道中传输，发光粒子，科技氛围，无文字](Materials/Medias/images/concept.png)`。
  - **处理平台封面图**：带有 `AI封面图` 标记的头部封面占位，支持以下两种格式：
    - Markdown 头图占位：`![[AI封面图][wechat][21:9][AI 工作流通道] 电影感编辑风封面，发光的 AI 工作流通道，科技媒体质感，无文字](Materials/Medias/images/cover-wechat.jpg)`
    - 注释块头图占位：
      ```html
      <!-- AI封面图
      platform: twitter
      aspect_ratio: 4:5
      caption: AI 工作流通道
      prompt: 电影感编辑风封面，发光的 AI 工作流通道，科技媒体质感，无文字
      output: Materials/Medias/images/cover-twitter.jpg
      -->
      ```
  - **严格跳过/忽略** 带有 `[待截图]` 标记的占位符（例如：`![[待截图] 用户登录页面](...)`）以及没有任何标记的普通图片，这些是留给人类作者手动提供的真实系统截图，千万不能用 AI 假图覆盖！

### 2. 智能匹配风格与品牌 (Smart Styling & Brand Selection)
针对每一个待处理的占位，执行以下操作：
- 读取占位符前后各约 300 字的上下文。
- 提取描述：
  - 正文 `[AI生图]`：显式拆分 `caption`、`aspect_ratio` 与 `prompt`。
  - `AI封面图`：显式拆分 `platform`、`aspect_ratio`、`caption` 与 `prompt`。
- 图注规则：
  - `caption` 只给读者看，最终会写入普通图片的 alt / figcaption
  - `prompt` 只给生图模型，不得出现在最终正文或 HTML 图注里
  - `caption` 推荐 4-10 个字，最长不超过 12 个字，应是图片场景的精简概述
  - 若未提供合格的 `caption`，允许继续生图，但最终回写时不得用 prompt 顶替图注
- 遵循 `references/prompt-enhancement-guide.md` 中的规范，提炼核心实体、隐喻和画面氛围。
- 查阅 `templates/styles.yaml`，选择最适合当前场景的风格：
  - 正文流程图、架构图、数据流转等结构化图解，优先 `corporate_diagram`
  - 正文概念图，优先 `brand_concept` 或 `metaphorical_scene`
  - `AI封面图`，优先 `brand_concept` 或 `metaphorical_scene`，避免使用过度图解化风格
- **品牌动态注入**：
  - 如果选用的风格包含 `requires_brand: true`（如上述两个）：
    - 检查用户是否在全局要求了特定品牌（如 Anthropic），如果是，读取 `references/brands/anthropic.md`。
    - 如果未指定，读取默认高品质商业配置 `references/brands/default_corporate.md`。
  - 提取规范中的 **"Prompt Injection Template"**（包含具体色值和品牌调性）。
- **重要：Agent 必须自己将提取到的品牌色彩描述拼接到最终传给 `--prompt` 的中文文本中**，脚本无法自动解析 `{brand_guidelines}` 变量。如果是普通风格（无品牌要求），则正常只传画面描述。

### 2.5 封面图特殊规则（AI封面图）⭐

当识别到 `AI封面图` 时，必须额外遵守：
- 封面图只能出现在文章头部，不得把它当作正文插图处理。
- 优先使用占位里已经声明的 `aspect_ratio`，不要自行改成通用 `16:9`。
- 微信公众号封面默认执行比例统一使用 `21:9`；这是对历史 `2.35:1` 头图比例的最近似映射。
- 优先使用占位里已经声明的 `output` 路径，必须严格落盘到对应封面文件。
- 默认要求纯画面，**不要在封面图中生成任何文字、数字、logo、水印**。
- 如果文章同时包含正文 `[AI生图]` 和 `AI封面图`，要分别按各自比例生成，不得强行合并成单一比例批次。

### 3. 生图与落盘
提取所有占位符后，按 **`style + aspect_ratio`** 分组并发提交生成请求，并确保严格按照占位符的路径保存。

**⚠️ 关键要求**：
- 如果所有任务比例相同，可以一次性并发提交。
- 如果同时存在 `21:9` 封面和 `16:9` 正文插图，必须拆成不同批次，或者对脚本传入一一对应的 `--aspect_ratio` 列表。
- 封面图输出路径通常类似：
  - `Materials/Medias/images/cover-wechat.jpg`
  - `Materials/Medias/images/cover-jike.jpg`
  - `Materials/Medias/images/cover-twitter.jpg`

### 3.2 生图完成后必须消费占位 ⭐

为了避免后续再次扫描时把已经完成的图片任务重复识别成待执行任务，生图成功后必须立即把占位回写成普通图片引用。

**规则**：
- `AI封面图` 与 `[AI生图]`：如果目标图片已存在，必须回写成普通 Markdown 图片引用
- `[待截图]`：始终保持不动
- 已存在文件被 `skip existing` 跳过时，也必须执行回写

**直接文件模式**：
```bash
python3 ~/.cursor/skills/article-illustrator/scripts/consume_generated_placeholders.py \
  /绝对路径/article.md
```

**工作区模式**：
```bash
python3 ~/.cursor/skills/article-illustrator/scripts/consume_generated_placeholders.py \
  /绝对路径/文章工作区 \
  --platform xhs
```

**效果**：
- `![[AI生图][发光的数据管道][16:9] 发光的数据管道，深色科技背景，无文字](images/01.png)` → `![发光的数据管道](images/01.png)`
- `![[AI封面图][wechat][21:9][科技封面图] 电影感编辑风封面，发光的 AI 工作流通道，科技媒体质感，无文字](images/cover.jpg)` → `![科技封面图](images/cover.jpg)`
- `<!-- AI封面图 ... -->` → `![封面图](images/cover.jpg)`

### 3.5 本地 Dry-Run（不扣费）⭐

在真正调用生图前，如果需要验证占位识别是否正确，可先运行本地扫描脚本：

```bash
# 直接扫描单个 Markdown 文件
python3 ~/.cursor/skills/article-illustrator/scripts/scan_placeholders.py \
  /绝对路径/article.md \
  --format markdown

# 扫描 content-creator 工作区，自动按 workflow_route 选择主文件
python3 ~/.cursor/skills/article-illustrator/scripts/scan_placeholders.py \
  /绝对路径/文章工作区 \
  --platform xhs \
  --format markdown
```

用途：
- 验证能否识别 `AI封面图`
- 验证能否区分 `[AI生图]` 与 `[待截图]`
- 验证每个任务的 `aspect_ratio`、输出路径和平台信息
- 验证是否正确按三链路选中了图片主文件
- **不会调用任何生图 API，不会扣费**

### 3.6 单入口推荐用法（扫描 + 生图 + 占位回写）⭐

默认推荐使用单入口脚本：

```bash
# 直接处理单个 Markdown 文件
python3 ~/.cursor/skills/article-illustrator/scripts/run_illustration_pipeline.py \
  /绝对路径/article.md

# 处理 content-creator 工作区
python3 ~/.cursor/skills/article-illustrator/scripts/run_illustration_pipeline.py \
  /绝对路径/文章工作区 \
  --platform xhs
```

可选参数：
- `--dry-run`：只输出执行计划，不实际生图
- `--force`：忽略已存在文件，强制重生
- `--style-cover` / `--style-diagram` / `--style-scene`：覆盖默认风格选择

默认风格路由：
- `AI封面图` → `brand_concept`
- 含流程 / 架构 / 工作流 / 面板 / dashboard 等关键词的正文图 → `corporate_diagram`
- 其他正文概念图 → `metaphorical_scene`

**使用示例：**
```bash
python3 ~/.cursor/skills/article-illustrator/scripts/generate_image.py \
  --prompt "A user interacting with a login and registration flow..." "Another prompt for second image..." \
  --style "3d_isometric" \
  --output "/绝对路径/login.png" "/绝对路径/second.png" \
  --provider "auto" \
  --aspect_ratio "16:9" "21:9" \
  --resolution "1K"
```

**参数说明：**
- `--prompt`: 提炼后的纯画面中文描述。**支持传入多个提示词（用空格分隔的多个字符串）以实现并发生成**。
- `--style`: `styles.yaml` 中的键名（如 `flat_concept`, `3d_isometric`, `minimalist_ui`, `metaphorical_scene`）。
- `--output`: 图片必须保存的确切本地路径，**必须**与 Markdown 占位符指向的相对路径对齐并保持绝对一致！**注意：传入的路径数量必须与 `--prompt` 数量完全一致！**
- `--provider`: 生图通道。默认 `auto`，会优先走 APIMart，只有在 APIMart 提交前失败时才切 OpenRouter。
- `--aspect_ratio`: 比例，如 `16:9`, `1:1`, `4:3`, `21:9`。可以只传 1 个值给全部任务，也可以按任务逐个传入。`--size` 仍作为兼容别名保留。
- `--resolution`: 分辨率，默认为 `1K`。除非用户明确要求，否则固定使用 `1K`。
- `--force`: (可选) 强制重新生成，忽略本地缓存的任务凭证和已存在输出文件。

### 3.7 三链路兼容规则（content-creator 集成）⭐

当配合 `content-creator` 使用时，必须遵守：

- `long_form` / `short_form`：工作区模式只扫描 `Output/{platform}/article.md`
- `visual_first`：工作区模式只扫描 `Output/{platform}/image_plan.md`
- `_drafts` 中的草稿文件不属于工作区模式扫描范围
- 如果要扫描 `_drafts`，必须显式传入具体文件路径
- 三条链路统一识别：
  - `AI封面图`
  - `[AI生图]`
  - `[待截图]`
- `AI封面图` 与 `[AI生图]` 的提示词统一按**中文**处理
- `visual_first` 平台不要只扫正文，必须优先扫 `image_plan`
- 对于已存在的目标输出文件，默认直接跳过；仅当用户明确要求重生或传入 `--force` 时，才允许重新生成

### 4. 循环与完成
所有目标配图生成完毕后，必须先执行一次占位消费回写，再向用户汇报最终生成的图片列表和落盘路径。

## 🛡️ 资金保护与重试规则 (Fund Protection Rules)

生图 API 调用会消耗真实资金。你必须严格遵守以下规则：
1. **绝不自动重试**：如果脚本执行失败（例如网络超时、524 错误、轮询超时等），你**绝对不能**擅自重新执行生图命令。
2. **强制汇报拦截**：遇到错误时，必须立即中止当前工作流，向用户汇报报错信息以及已获取到的 `task_id`（如果有）。
3. **把决定权交给用户**：询问用户是选择“使用相同命令继续轮询（脚本会自动读取本地缓存的 task_id）”、“放弃当前图”还是“使用 `--force` 参数强制重新扣费生成”。
4. **自动回退边界**：仅当 APIMart 在**提交前**失败、且未拿到 `task_id` 时，才允许 `provider=auto` 自动切到 OpenRouter；一旦 APIMart 已返回 `task_id`，后续失败禁止自动切换。

## 依赖说明
- **API 通道**：默认通道为 APIMart 图像生成接口，备用通道为 OpenRouter 图像生成接口。
- **凭证管理**：依赖 `secrets-vault` 技能，通过 `apimart_image` 与 `openrouter_image` 命名空间获取鉴权信息。
