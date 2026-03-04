# 完整工作流详细说明（6个主阶段 + 1个强制澄清环节）

> 本文档包含 content-creator skill 的完整工作流执行步骤
> 
> **关联文档**:
> - 核心流程概览: `../SKILL.md`
> - 配置文件说明: [configurations.md](configurations.md)
> - 最佳实践: [best-practices.md](best-practices.md)
> - 故障排查: [troubleshooting.md](troubleshooting.md)

---

## 📋 目录

- [阶段0：素材提取与认知校正](#阶段0素材提取与认知校正)
- [阶段1：选题策划](#阶段1选题策划)
- [阶段1.5：采访式澄清（强制门禁）](#阶段15采访式澄清强制门禁)
- [阶段2：路线化创作前置规划](#阶段2路线化创作前置规划)
- [阶段3：路线化创作规划](#阶段3路线化创作规划)
- [阶段4：多风格候选草稿与正文展开](#阶段4多风格候选草稿与正文展开)
- [阶段5：爆款潜力评分与优化](#阶段5爆款潜力评分与优化)
- [阶段6：多平台适配](#阶段6多平台适配)

---

## 🧭 三条内容创作链路总览

`content-creator` 先共享阶段0-1，并在进入 route-specific 规划前执行阶段1.5 采访式澄清，再按平台内容形态路由到不同深度的创作链路。

```text
[统一前置层]
阶段0 素材提取
阶段1 选题策划
阶段1.5 采访式澄清
        |
        v
[按平台路由]
        |
        +---------------- long_form ----------------+
        |  阶段2L 标题 + 大纲                       |
        |  阶段3L 写作剧本 + 配图规划               |
        |  阶段4A 三风格候选草稿                    |
        |  阶段4B 展开正式正文                      |
        |  阶段5L 长内容评分优化                    |
        |  阶段6 发布                               |
        |
        +---------------- short_form ---------------+
        |  阶段2S 核心判断 + 开头钩子               |
        |  阶段4A 三风格候选草稿                    |
        |  阶段4B 展开最终短内容                    |
        |  阶段5S 短内容评分优化                    |
        |  阶段6 发布                               |
        |
        +---------------- visual_first -------------+
           阶段2V 封面钩子 + 图片叙事板             |
           阶段3V image plan / storyboard           |
           阶段4A 三风格图文候选稿                  |
           阶段4B 展开最终图文版本                  |
           阶段5V 视觉优先评分优化                  |
           阶段6 发布
```

## 🚪 工作区启动模式

`content-creator` 现在支持两种启动方式：

```text
模式A：已有工作区
  -> 用户已手动创建文章目录
  -> 直接从阶段0开始

模式B：任意目录启动
  -> 先围绕需求做选题沟通
  -> 用户确认选题
  -> 自动创建“选题目录”作为本次工作区
  -> 再进入阶段0
```

### 模式B 推荐流程

```text
用户在任意目录提出内容需求
   |
先做选题沟通
   |
用户确认选题
   |
调用 init_workspace.py
   |
自动创建 [选题目录]/
   ├── Materials/origin.md
   ├── Materials/Medias/images/
   ├── Output/_drafts/
   ├── Output/_reports/
   └── workspace.config.yaml
   |
进入阶段0继续执行
```

### init_workspace.py

```bash
python3 ~/.cursor/skills/content-creator/scripts/init_workspace.py \
  --base-dir "<当前目录>" \
  --topic "<已确认选题>" \
  --platforms "xhs,wechat" \
  --seed-text "<本次需求摘要或已有素材摘要>"
```

规则：
- 工作区目录名默认使用“已确认选题”
- 如目录重名，自动追加 `-2`、`-3`
- 自动生成 `Materials/origin.md` 作为种子素材文件
- 自动生成 `workspace.config.yaml`，状态为 `initialized`

### 图片主文件规则

```text
long_form
  图片主文件 -> 04_draft.[platform].[style].md

short_form
  图片主文件 -> 04_draft.[platform].[style].md

visual_first
  图片主文件 -> 03_image_plan.[platform].md
  正文主文件 -> 04_draft.[platform].[style].md
```

### 全局硬规则

- 三篇候选稿必须保持：**事实一致、目标一致、平台一致，只允许写法角度不同**
- 三条链路统一图片标识：`AI封面图`、`[AI生图]`、`[待截图]`
- `AI封面图` 与 `[AI生图]` 的提示词统一使用**中文**
- 所有 AI 图片占位必须显式区分 `caption` 与 `prompt`：`caption` 是给读者看的简短场景概述，`prompt` 只给模型，不得直接进入最终图注
- 视觉优先平台的图片顺序、来源类型和截图指引必须集中写入 `03_image_plan.[platform].md`
- 阶段1后必须执行 `1~3` 轮采访式澄清；未补齐方向、证据和平台语境前，不允许直接进入阶段2

---

## 阶段0：素材提取与认知校正

**目标**：从原始素材中提取结构化元数据

**输入**：
- `Materials/*.md`（原始素材）
- `Medias/`（媒体资源，可选）
- 认知校正词典（通过 content-creator-memory）

**执行步骤**：

### 步骤0.1：工作区结构检测

```
检查 Materials/ 是否存在
├─ 不存在
│   ├─ 当前属于“已有工作区模式” → 提示："请创建Materials/文件夹并放入原始素材"
│   └─ 当前属于“任意目录启动模式” → 先回到选题确认，调用 init_workspace.py 自动创建工作区
└─ 存在 → 继续

检查配图资源（⚠️ 必须使用 scan_images.py，禁止 Agent 自行判断）
├─ 执行：python3 ~/.cursor/skills/content-creator/scripts/scan_images.py [工作区路径] markdown
├─ 以脚本输出为唯一判断依据：
│   ├─ 脚本报告"目录不存在"或"0张图片"
│   │   → ⚠️ 主动询问用户："是否有配图需要添加？"
│   │   ├─ 用户：有 → 提示放入 Materials/Medias/images/ 后回复"继续"
│   │   │         → 用户确认后重新执行 scan_images.py
│   │   └─ 用户：无 → 标记"本文确认无配图（用户已确认）"
│   └─ 脚本报告有图片
│       → 记录图片数量和清单，纳入元数据
└─ ⚠️ 禁止规则：Agent 不得通过自行检查目录、Glob 搜索等方式
   独立判断配图状态，必须以 scan_images.py 输出为准

检查 Output/ 是否存在
├─ 不存在 → 创建完整目录结构
└─ 存在 → 询问是否归档旧内容到 _archive/
```

### 步骤0.2：平台确认（前置检查）

```
检查用户初始请求中是否明确了目标平台
├─ 已明确（如"发布到小红书和微信公众号"） → 记录平台列表
└─ 未明确 → 暂停，询问用户："请明确您计划发布的平台"
```

### 步骤0.3：素材扫描与预处理

```
读取所有 Materials/*.md 文件
统计总字数、文件数量
识别主要素材文件（最大的 .md 文件）
```

### 步骤0.4：认知校正

```
使用认知校正词典进行校正
示例校正：
- "超级风" → "超级峰"
- "知识相机" → "芝士相机"
- 其他专有名词、产品名称
```

### 步骤0.5：元数据提取

生成 `extracted_meta.yaml`，包含：
- `trending_topics`（热点话题）
- `audience`（目标受众）
- `purpose`（创作目的）
- `brand_voice`（品牌语调）
- `writing_style`（写作风格）
- `structure`（文章结构模型）
- `key_points`（核心要点）
- `humanization`（人性化策略）
- `seo`（SEO设置）
- `quality_targets`（质量目标）
- `assets`（资源需求）
- `publish_platforms`（目标平台，来自步骤0.2）
- `output_constraints`（输出约束）

### 步骤0.6：生成工作区配置

生成 `workspace.config.yaml`:

```yaml
# 工作区基本信息
workspace:
  name: 文章工作区名称
  created_at: 2026-02-04T10:00:00Z

# 素材信息
materials:
  primary_source: Materials/origin.md
  total_word_count: 5000

# 媒体资源
medias:
  images:
    count: 8
    total_size: 2.5MB

# 目标平台
target_platforms:
  - xhs        # 小红书
  - wechat     # 微信公众号

# 创作模式
creation:
  mode: collaborative

# 平台交付自动化配置
delivery:
  platforms:
    xhs:
      mode: auto_format
    wechat:
      mode: auto_format

# 生成状态
generation_status: extraction_completed
```

**输出**：
- `Output/_drafts/00_extracted_meta.yaml`
- `workspace.config.yaml`

**用户确认**：使用 Rich 库美化展示 YAML 元数据

```python
import yaml
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

# 读取 YAML 文件
with open('Output/_drafts/00_extracted_meta.yaml', 'r', encoding='utf-8') as f:
    yaml_content = f.read()

# 使用 Rich 美化展示
console = Console()
syntax = Syntax(yaml_content, "yaml", theme="monokai", line_numbers=True, word_wrap=True)
console.print(Panel(
    syntax,
    title="[bold cyan]📊 元数据预览[/bold cyan]",
    subtitle="阶段 0：素材提取",
    border_style="cyan"
))
console.print("\n[dim]💡 提示: 输入 'continue' 继续，或提出修改意见[/dim]\n")
```

---

## 阶段1：选题策划

**目标**：生成3个不同角度的选题方案，供用户选择

**输入**：
- `00_extracted_meta.yaml`（元数据）
- 内容记忆系统（content-creator-memory）

**执行步骤**：

### 步骤1.1：80/20 记忆校准（选题维度）

通过 content-creator-memory 检索：

```
【80% 权重 - 自有内容】
├─ 基于 target_audience、technical_stack、primary_keywords
├─ 筛选 Top 2 高质量内容（quality_score）
└─ 提取成功的选题角度、叙事模式

【20% 权重 - 标杆案例】
├─ 基于 content_type、tone 相似度
├─ 筛选 Top 1-2 标杆案例
└─ 提取爆款选题技巧、标题钩子
```

### 步骤1.2：竞品热点分析

使用 WebSearch 工具：
- 搜索相关热点话题
- 分析竞品文章的选题角度
- 识别内容空白区

### 步骤1.3：生成3个选题方案

格式示例：

```markdown
## 方案A：[类型，如"新手成长故事型"]
**选题角度**：[一句话描述]
**核心叙事**：开头→过程→结果
**适用平台**：✅ 小红书、✅ 微信公众号
**预期效果**：
- 标题吸引力：⭐⭐⭐⭐⭐
- 传播潜力：⭐⭐⭐⭐⭐
- 转化能力：⭐⭐⭐⭐
**标题方向预测**：3个标题示例

## 方案B：[工具测评对比型]
...

## 方案C：[方法论拆解型]
...
```

### 步骤1.4：推荐选题

```markdown
## 💡 推荐选择
**最佳选题**：方案A
**理由**：
1. ✅ 强共鸣
2. ✅ 真实可信
3. ✅ 多平台适配
4. ✅ 传播潜力大
5. ✅ 素材充足
```

**输出**：
- `Output/_drafts/01_topic_proposals.md`

**用户确认**：展示3个方案，等待用户选择（"我选择方案A" 或 "方案B更好"）

---

## 阶段1.5：采访式澄清（强制门禁）

**目标**：在进入 route-specific 创作前，用 `1~3` 轮轻量访谈补齐真正影响内容质量的缺口，避免直接进入标题、大纲、钩子或 storyboard 生成。

**定位**：
- 不是独立的长文档产出阶段
- 是阶段1到阶段2之间的强制门禁
- 结果主要体现在对话中，不强制新增独立文件

### 需要补齐的 6 类信息

1. 写作目标：解释、说服、分享、引发讨论、促进收藏或转发
2. 目标读者：给谁看，对方已知什么、缺什么
3. 平台语境：目标平台上读者期待的表达形态
4. 证据边界：哪些事实、案例、截图、数据必须保留，哪些不能编造
5. 风格偏好：更偏 `技术专家`、`故事描述`、`幽默犀利`，还是先看三种候选
6. 成稿约束：是否要封面、多图、截图、CTA、敏感表达规避

### 轮次规则

#### Round 1：共性澄清

所有链路必做，优先补齐目标、读者、证据边界、成稿约束。

#### Round 2：路由定向澄清

默认需要：

- `long_form`：标题承诺、结构骨架、必须展开的论点和案例深度
- `short_form`：核心判断、开头钩子、讨论点、长度约束
- `visual_first`：封面钩子、图片顺序、AI生图/待截图分配、每页角色

#### Round 3：高歧义补问

仅在以下情况触发：
- 事实边界不清
- 平台不清
- 用户目标冲突
- 视觉素材责任不清
- 前两轮后仍不足以稳定进入阶段2

### 每轮固定输出格式

每轮面向用户的输出必须遵守：

1. 当前理解摘要
2. 已确认内容
3. 仍需确认的关键缺口
4. 本轮问题清单

问题清单必须放在消息最后，并使用代码块包裹；每轮最多 `5` 个问题，推荐 `3` 个问题。

### 放行门禁

只有以下信息清楚后，才允许进入阶段2：

- 目标平台清楚
- 目标读者清楚
- 内容目标清楚
- 必须保留的事实或案例清楚
- 当前路由的关键缺口已补齐

### 路由问题模板

#### Round 1：共性问题包

```text
1. 这篇内容最想让读者带走的一句话是什么？
2. 这篇内容主要是给谁看的？对方现在最缺什么信息？
3. 有没有必须保留的事实、案例、截图或数据？
4. 你最不希望它写成什么样？
5. 这次更看重专业可信、代入感，还是传播性？
```

#### Round 2L：长内容

```text
1. 标题更偏“结论型”还是“故事型”？
2. 哪 2~3 个论点必须展开？
3. 有没有必须讲透的案例、反例或步骤？
```

#### Round 2S：短内容

```text
1. 这条内容最核心的一句话判断是什么？
2. 你更想让读者评论、转发，还是单纯记住这个观点？
3. 开头更想要稳、故事感，还是锋利一点？
```

#### Round 2V：视觉优先

```text
1. 封面最想让人停下来的点是什么？
2. 这组内容计划做几张图？
3. 哪些页必须截图，哪些页可以 AI 生图？
4. 整组图更像“问题 -> 解法 -> 结果”还是“对比 -> 流程 -> 总结”？
```

---

## 阶段2：路线化创作前置规划

**目标**：按平台路由生成最适合的前置规划产物，而不是所有平台都走同一套“标题+大纲”重流程。

**输入**：
- 用户选择的选题方向（来自阶段 1）
- `00_extracted_meta.yaml`
- 内容记忆系统（content-creator-memory）

### 三条子路径

```text
long_form
  -> 02_titles_and_outline.md

short_form
  -> 02S_hook_and_angle.[platform].md

visual_first
  -> 02V_cover_and_storyboard.[platform].md
```

### 标题字段统一规则

三条链路的规划文档统一使用：

```markdown
### [标题]
**标题思路**：标签1、标签2、标签3
```

解释：
- `long_form`：这里的 `标题` 是未来正文小标题
- `short_form`：这里的 `标题` 是表达推进点，默认不直接输出为正文小标题
- `visual_first`：这里的 `标题` 是页面标题，是否显示取决于页面需要

**硬规则**：
- `标题思路` 只用于用户审查和后续生成约束
- `标题思路` 禁止进入任何最终正文
- 禁止把 `章节一 / 章节二 / 认知误区 / 破局点 / 总结与升华` 这类内部提纲语言写进最终正文

### 阶段2L：长内容平台

适用：`wechat`、`zhihu`、`linkedin`、`bilibili`

**执行步骤**：

### 步骤2.1：80/20 记忆校准（标题+大纲维度）

基于选定选题，深度检索：

```
【80%权重 - 自有风格】
├─ 提取 tone、perspective、writing_style
├─ 分析个人特色的标题模式
└─ 确立主导风格基准

【20%权重 - 标杆技巧】
├─ 提取 title_hooks、structural_patterns
├─ 分析高吸引力的标题公式
└─ 确立技巧增强元素
```

### 步骤2.2：生成5个标题备选

格式示例：

```markdown
## 标题1：数字钩子型 【推荐⭐⭐⭐⭐⭐】
**45天从代码小白到App开发者，我只做对了这3件事**

- **吸引力分析**：
  - ✅ 具体数字（45天、3件事）
  - ✅ 强烈对比（小白→开发者）
  - ✅ 承诺明确（只需做对3件事）
- **平台适配**：
  - 小红书：⭐⭐⭐⭐⭐
  - 微信公众号：⭐⭐⭐⭐

## 标题2：情绪冲击型 【推荐⭐⭐⭐⭐⭐】
...

## 标题3-5：...
```

**用户确认**：展示 5 个标题，等待用户选择。

### 步骤2.3：核心主旨与结构骨架提议（⭐ 互动思辨）

在用户选定标题后，**不要直接生成详细大纲**。Agent 必须主动提炼核心主旨，并提供 2 种宏观结构方案供用户选择。

**Agent 互动示例**：

> 针对《XXX》这个标题，我为您提炼的核心主旨是：[一句话核心]。
> 为了更好地呈现这个主旨，我建议以下两种文章结构：
> 
> **方案A：痛点-激化-解决（PAS）模型**（适合引发共鸣）
> - 模块1：描述[痛点场景]
> - 模块2：揭示导致这个痛点的深层原因
> - 模块3：给出我们的解决方案
> 
> **方案B：What-Why-How 模型**（适合干货科普）
> - 模块1：什么是[核心概念]
> - 模块2：为什么现在必须了解它
> - 模块3：实操步骤拆解
> 
> 💡 **建议：**基于您的受众群体，我更推荐**方案A**。您选择方案A、方案B，还是有其他补充？

**用户确认**：等待用户选择或补充结构骨架。

### 步骤2.4：模块化深度思辨与配图共创（⭐ 核心互动）

在结构骨架敲定后，Agent 需要逐个模块与用户确认“核心表达思路”和“配图方案”。

**配图双轨制原则**：
Agent 必须提醒用户一篇文章建议至少 3 张以上配图，并在每个模块提供明确的配图选项：
1. **[AI生图]**：适合概念插画、氛围图。后续可通过 `@article-illustrator` 自动生成。
2. **[待截图]**：适合软件界面、实操步骤、真实数据报表。需由用户手动提供。

**Agent 互动示例**（逐个模块提问）：

> 关于**【模块一：开篇痛点引入】**，为了吸引读者：
> 
> **1. 核心表达思路建议：**
> - 选项A：用一个真实的失败案例引入。
> - 选项B：直接抛出扎心的数据对比。
> 💡推荐选项A，更有代入感。
> 
> **2. 模块配图建议：**
> 我建议在此处安排 **1 张配图**：
> - **选A（AI生图）**：一张表现"深夜加班写代码抓狂"的插图。*(后续可通过 article-illustrator 自动生成)*
> - **选B（实操截图）**：一张您系统里真实的"复杂报错日志"截图。*(需由您手动提供)*
> 
> 👉 **请问：表达思路您选A还是B？配图您倾向于 AI 生图还是手动截图？**（如有自备图片，请直接提供文件名）

*Agent 需记录用户的选项，直至所有主要模块思辨完毕。*

### 步骤2.5：生成最终详细大纲与配图清单

结合 2.3 和 2.4 的讨论结果，生成最终详细大纲。**配图必须严格使用以下标准占位符格式**：

**【格式规范：AI 生图】**
```markdown
![[AI生图][<图片场景概述>][<横纵比>] <这里写纯画面的中文提示词描述>](Materials/Medias/images/<语义化英文命名>.png)
```
*(注：`caption` 只写给读者看的精简图注，`prompt` 才是生图提示词；提示词统一使用中文。)*

**横纵比选择规则**：
- `aspect_ratio` 必填，只能从当前接口支持的比例中选择：`1:1 / 1:4 / 1:8 / 2:3 / 3:2 / 3:4 / 4:1 / 4:3 / 4:5 / 5:4 / 8:1 / 9:16 / 16:9 / 21:9`
- 横向概念图、流程图、头图优先：`16:9` 或 `21:9`
- 竖向人物 / 卡片感强的图片优先：`4:5` 或 `3:4`
- 微信公众号封面默认使用 `21:9`，正文 AI 图默认优先考虑 `16:9`

**【格式规范：用户待截图】**
```markdown
![[待截图] <中文描述>](Materials/Medias/images/<语义化英文命名>.png)
> 💡 **截图指引**：<这里写详细的截图要求，如“打开设置页面，圈出版本号”>
```

**【格式规范：平台级 AI 封面图占位】** ⭐ 新增

在生成最终大纲时，Agent 还必须检查目标平台的 `cover_policy`。如果平台启用了封面策略，则在文章头部提前生成平台专属封面占位，供阶段6后续 AI 生图使用。`@article-illustrator` 现已支持识别这类 `AI封面图` 占位。

```
当前第一批启用平台：
├─ wechat  → inline_markdown（正文头部可见占位）
├─ jike    → header_comment（正文头部注释占位，不污染正文）
└─ twitter → header_comment（正文头部注释占位，不污染正文）

未来预留：
├─ xhs     → image_plan_cover_slot
└─ zhihu   → inline_markdown
```

**微信公众号（inline_markdown）**：
```markdown
![[AI封面图][wechat][21:9][<封面场景概述>] <纯画面的中文提示词描述>](Materials/Medias/images/cover-wechat.jpg)
```

**即刻 / Twitter（header_comment）**：
```markdown
<!-- AI封面图
platform: twitter
aspect_ratio: 4:5
prompt: <纯画面的中文提示词描述>
caption: <封面场景概述>
output: Materials/Medias/images/cover-twitter.jpg
-->
```

**⚠️ 关键规则**：
1. `AI封面图` 与正文里的 `[AI生图]` 不是同一种占位，不能混用。
2. 封面图只允许出现在文章头部，不允许插入到章节正文中。
3. 图文分离型平台虽然正文不能嵌图片，但允许在文章头部写 `header_comment` 形式的封面占位。
4. `output` 文件名必须使用平台专属命名：`cover-wechat.jpg`、`cover-jike.jpg`、`cover-twitter.jpg`。

**输出格式示例**（`02_titles_and_outline.md`）：

```markdown
## 📐 最终文章大纲

![[AI封面图][wechat][21:9][AI 工作流通道] 电影感编辑风封面，发光的 AI 工作流通道，科技媒体质感，无文字](Materials/Medias/images/cover-wechat.jpg)

**结构模型**：故事化PAS（Problem-Agitate-Solution）

### 一天烧掉一亿 Token 之后，我先看清了一个事实
**标题思路**：热点切入、真实数据、反常识开场

**核心表达思路**：用真实的失败案例引入（基于选项A）
**预计字数**：150-200字
**配图方案**：
![[AI生图][深夜报错现场][16:9] 深夜程序员坐在昏暗房间里，被多块显示复杂报错日志的发光屏幕照亮，赛博朋克氛围，无文字](Materials/Medias/images/frustrated_programmer.png)

### 你以为卡在 Prompt，其实卡在流程
**标题思路**：反差、判断句、认知扭转

**配图方案**：
![[待截图] 数据库连接配置页面](Materials/Medias/images/db_config_screenshot.png)
> 💡 **截图指引**：请在此处替换一张系统设置 -> 数据库连接页面的完整截图，重点用红框圈出“连接字符串”所在位置。

---
## 🖼️ 核心配图执行清单
- [ ] `frustrated_programmer.png` (交由 AI 生图)
- [ ] `db_config_screenshot.png` (需您手动准备)
```

**输出**：
- `Output/_drafts/02_titles_and_outline.md`

**用户确认**：展示最终大纲与配图清单，确认无误后进入阶段3。

---

### 阶段2S：短内容平台

适用：`jike`、`twitter`

**目标**：提炼单条内容真正要表达的判断和开头抓手，不再强制走重标题/重大纲流程。

**输出文件**：
- `Output/_drafts/02S_hook_and_angle.[platform].md`

**内容结构**：
- 核心判断：一句话说清这条内容到底想表达什么
- 反差点 / 冲突点：为什么值得继续看
- 开头钩子候选：至少 3 个
- 表达推进点：使用 `### [标题]` + `**标题思路**` 标注 2~3 个推进点
- 必须提到的事实：哪些信息不能丢
- 禁止写法：哪些表达一出现就会写歪

### 阶段2V：视觉优先平台

适用：`xhs`、`instagram`、`douyin`

**目标**：先明确封面承诺和图序叙事，再让文案为视觉服务。

**输出文件**：
- `Output/_drafts/02V_cover_and_storyboard.[platform].md`

**内容结构**：
- 封面钩子：最想让用户停下来的点
- 图片叙事板：每张图讲什么、承担什么角色
- 页面标题规划：使用 `### [标题]` + `**标题思路**` 标注 3~5 个页面标题
- 视觉统一要求：配色、构图、节奏、禁区
- 与正文关系：文案必须服务于图序推进，不反客为主；但不要求最终正文逐图逐页机械讲解

---

## 阶段3：路线化创作规划

**目标**：根据不同链路，生成真正能驱动候选稿与成稿的规划文件。

**输入**：
- 阶段2已确认产物
- `00_extracted_meta.yaml`
- 80/20记忆校准结果

### 三条子路径

```text
long_form
  -> 03_writing_plan.md

short_form
  -> 无强制独立文件，阶段4A 直接读取阶段0-2已确认产物

visual_first
  -> 03_image_plan.[platform].md
```

**执行步骤**：

### 步骤3.1：扫描图片资源（🆕 必须执行）⭐⭐⭐

**⚠️ 关键步骤**：在生成写作剧本前，必须先运行图片扫描工具

```bash
# 运行图片扫描工具（必须执行）
python3 ~/.cursor/skills/content-creator/scripts/scan_images.py [工作区路径] markdown
```

**工具输出示例**：

```markdown
## 图片扫描结果

- 工作区: `/Users/xxx/my-article`
- 图片目录: `/Users/xxx/my-article/Materials/Medias/images`
- 目录存在: ✅ 是
- 图片总数: **5** 张

### 图片清单

1. `Medias/images/01-preview.png` (序号: 01) [关键词: preview]
2. `Medias/images/02-workflow.png` (序号: 02) [关键词: workflow]
3. `Medias/images/03-result.png` (序号: 03) [关键词: result]
4. `Medias/images/04-detail.png` (序号: 04) [关键词: detail]
5. `Medias/images/cover-wechat.jpg` [关键词: cover-wechat]

### Markdown 引用格式

```markdown
![精简场景概述](Medias/images/01-preview.png)
```
```

**⚠️ 重要规则**：

1. **必须遍历所有图片**：不要遗漏任何一张图片
2. **记录完整路径**：使用工具输出的 `Medias/images/` 格式
3. **分析图片语义**：
   - 优先使用序号（01-xxx.png → 第一章节）
   - 提取关键词（workflow → 流程相关章节）
   - 参考文件名含义（cover → 封面/开篇）

**智能匹配策略**：

```
读取大纲的章节列表：
章节1: 快速上手
章节2: 核心功能
章节3: 实战案例
...

遍历扫描到的所有图片：
for each 图片 in 图片清单:
  分析图片语义：
    - 如果有序号（如 01-xxx.png）→ 匹配到第1章节
    - 如果关键词匹配章节标题（如 workflow 与 "核心功能"）→ 匹配到该章节
    - 如果文件名是 cover/intro → 匹配到开篇
    - 如果无法明确匹配 → 根据图片内容和上下文决定位置
  
  决策输出：
    章节1 → 使用 Medias/images/01-preview.png
    章节2 → 使用 Medias/images/02-workflow.png
    章节3 → 使用 Medias/images/03-result.png
    ...
```

**如果目录不存在或无图片**：

```bash
# 工具输出
❌ 错误: 图片目录不存在: /path/to/Materials/Medias/images

# Agent 应该：
- 标记：本文无配图
- 在写作剧本中注明"无配图"
- 继续执行后续步骤（不影响文章生成）
```

---

### 步骤3.1.5：视觉优先平台 image plan / storyboard ⭐⭐⭐

> **触发条件**：目标平台属于 `visual_first`（当前首批：`xhs`、`instagram`、`douyin`）时必须执行，其他平台跳过本步骤。

**目的**：为视觉优先平台制定完整的图片主文件，指导后续图片准备与 AI 生图。

**执行流程**：

```
步骤 A：加载模板索引
  读取 references/xhs-image-templates/README.md
  获取 5 种模板的适用场景和决策流

步骤 B：判断笔记类型
  基于阶段1的选题 + 阶段2的大纲内容：
  ├─ 新产品/工具首次推广？ → 模板A：产品首发推广型
  ├─ 教用户如何使用某功能？ → 模板B：功能教程型
  ├─ 已有产品功能更新？    → 模板C：版本更新型
  ├─ 征集用户意见/投票？   → 模板D：互动投票型
  ├─ 趣味话题/情绪共鸣？   → 模板E：故事话题型
  └─ 不确定？ → 默认模板A，或组合多模板元素

步骤 C：加载对应模板
  读取 references/xhs-image-templates/template-{id}-{name}.md
  获取：
  - 图片序列总览（每张图的角色定位）
  - 逐图详细规范（设计规范、内容定义）
  - AI 生图提示词模板

步骤 D：填充实际内容
  将模板中的占位符替换为文章实际内容：
  - {痛点文案} → 从大纲的 hook 提取
  - {产品名} → 从 extracted_meta.yaml 提取
  - {核心卖点} → 从大纲的核心价值提取
  - {核心功能A/B} → 从大纲的重点章节提取
  - {配色方案} → 根据产品调性从通用设计规范中选择

步骤 E：判断每张图的来源类型
  for each 图片 in 图片序列:
    ├─ 该图需要 App 截图？
    │   → 标记为 📱 screenshot
    │   → 生成截图指引（具体页面、操作状态、标注位置）
    ├─ 该图需要设计/生成？
    │   → 标记为 🎨 design
    │   → 生成完整的 AI 生图提示词（中文）
    ├─ 该图需要拼图/对比？
    │   → 标记为 🧩 composite
    │   → 生成拼图指引（各部分内容、拼合方式）
    └─ 该图需要实拍？
        → 标记为 📷 photo
        → 生成拍摄建议（场景、光线、角度）

步骤 F：生成图片主文件
  输出到 Output/_drafts/03_image_plan.[platform].md
  包含：
  - 模板类型 & 内容类型说明
  - 建议图片总数
  - 逐图详细方案（每张图独立章节）
  - 每张图的统一图片标识（可直接给 article-illustrator 扫描）
```

**输出格式**（`03_image_plan.[platform].md`）：

```markdown
# Image Plan / Storyboard

## 基本信息
- **内容标题**：{标题}
- **使用模板**：模板{ID} - {模板名称}
- **建议图片数**：{X} 张
- **整体风格**：{风格描述}

---

## 图 1 — 封面钩子图 🎨
![[AI封面图][xhs][3:4] {已替换占位符的完整中文提示词}](Materials/Medias/images/cover-xhs.jpg)

### 页面角色
- 封面钩子页

### 设计规范
- 尺寸：1080×1440（3:4）
- 配色：{根据产品选择的具体配色方案}
- 构图：{具体构图说明}

---

## 图 2 — {图片角色} 📱
![[待截图] {具体要展示的界面/功能}](Materials/Medias/images/{语义化文件名}.png)

### 截图指引
> {具体的截图操作步骤}

---

## 图 3 — {图片角色} 📱
...

---

## 执行清单

- [ ] 图1：{封面} — 来源：{🎨 AI生成 / 📱 截图 / 🧩 拼图}
- [ ] 图2：{角色} — 来源：{来源类型}
- [ ] 图3：{角色} — 来源：{来源类型}
- [ ] ...
```

**⚠️ 关键原则**：

1. **AI 提示词必须是中文且即用**：所有占位符必须替换为实际内容，并使用统一图片标识语法
2. **截图指引必须具体**：明确指出打开哪个页面、什么操作状态、标注哪个区域
3. **视觉一致性**：同一篇笔记内所有图片保持统一的配色、字体、风格
4. **封面图最重要**：封面图的设计规范必须最详细，它决定了 80% 的点击率

**用户确认**：将图片主文件方案展示给用户，等待确认后再进入步骤3.2

---

### 步骤3.2：生成分章节写作指令⭐

**⚠️ 关键前置判断：平台内容格式分类**

不同平台对图片的处理方式不同，必须先判断目标平台的内容格式：

```
平台内容格式分类：

【图文混排型】→ 图片内嵌在正文中，与文字混排显示
├─ 微信公众号（wechat）
├─ 知乎（zhihu）
├─ 哔哩哔哩专栏（bilibili）
└─ LinkedIn
→ 规则：图片必须嵌入到章节合适位置（Markdown 图片语法）

【图文分离型】→ 图片作为独立画廊/轮播上传，正文为纯文字
├─ 小红书（xhs）
├─ Instagram
├─ 抖音（douyin）
├─ 微博（weibo）
├─ 即刻（jike）
└─ Twitter/X
→ 规则：正文不嵌入章节图片，图片顺序由 image_plan.md 管理
→ 例外：若平台启用了 `cover_policy.placeholder_mode = header_comment`
         则允许在文章头部插入 `AI封面图` 注释块
```

**⚠️ 关键要求**：
- **图文混排型平台**：必须将图片路径直接写入每个章节的写作指令中，不要单独创建"配图方案"章节
- **图文分离型平台**：写作指令中标注"章节N对应图片X"作为参考，但 draft.md 和 article.md 中**不嵌入图片**，图片排序和使用由 `image_plan.md` 独立管理

生成格式：

```markdown
# 任务事项：文章正式写作与多平台分发

## 执行规则
1. 严格遵循待办事项从上到下执行
2. 状态实时更新为 [✅]
3. 忠于 article_structure.md 和 extracted_meta.json
4. 必须写在同一个 article_draft.md 文档内
5. ⭐ **图文混排型平台**：图片必须嵌入到章节合适位置，禁止放在文章最后
6. ⭐ **图文分离型平台**：正文不嵌入图片语法，保持纯文字（图片由 image_plan.md 管理）

## 核心写作指令
- **视角指令**：第一人称（"我"、"我们"、"我的"）
- **故事描述指令**：避免具体人名，使用"我有个朋友"
- **主要指令**：遵循 extracted_meta.yaml 的 writing_style
- **80/20 风格校准指令**：
  - 主导风格（80%）：融入自有内容的表达习惯
  - 技巧增强（20%）：借鉴标杆案例的钩子技巧
  - 融合原则：自然统一，避免突兀
- **分层素材复用指令**：
  - 核心素材优先（golden_sentences、core_workflows）
  - 技巧素材辅助（钩子模式、开篇技巧）
  - 智能组合（自然流畅）
- **图片处理指令**（⭐⭐⭐ 重要，按平台格式区分）：

  **【图文混排型平台】**（wechat / zhihu / bilibili / linkedin）：
  - 必须使用步骤3.1扫描到的图片路径：`Medias/images/文件名.png`（以实际扫描到的扩展名为准，如 .png/.jpeg/.jpg/.webp）
  - 图片必须嵌入到章节内容的合适位置（描述该内容的段落之后）
  - 禁止将图片集中放在文章最后作为"配图建议"
  - ⚠️ **如果占位符是 `[待截图]`**：在 `draft` 草稿层必须保留该图片占位及其下方的 `> 💡 **截图指引**：...` 引用块，供作者补图与审查使用；但这些截图指引在阶段6生成最终 `article.md` 时必须被清理掉。
  - 标准格式：
    ```markdown
    ![[AI生图][预览概念图][16:9] 中文提示词](Medias/images/01-preview.png)
    或
    ![[待截图] 中文描述](Medias/images/01-screenshot.png)
    > 💡 **截图指引**：...
    ```
  - 最终图片图注 = `caption`：简洁描述图片场景，推荐 4-10 个字（markdown-to-wechat 会自动渲染为 figcaption）
  - `prompt` 只服务 AI 生图，不得直接出现在最终图注中
  - ⚠️ **禁止**在图片下方另起一行写 `*▲ ...*` 斜体图注（会与 figcaption 重复显示）

  **【图文分离型平台】**（xhs / instagram / douyin / weibo / jike / twitter）：
  - ⚠️ **正文中不嵌入图片**（不使用 `![](...)` 语法）
  - 若平台启用头部封面策略（当前 jike / twitter）：
    - 在文章第一行写入 `AI封面图` 注释块
    - 注释块只承载封面生图信息，不算正文配图
  - 正文保持纯文字 + emoji + 话题标签
  - 图片排序和用途由 `image_plan.md` 独立管理
  - 写作指令中仅标注"本章节对应图片X"作为内容对齐参考

## 写作待办事项

- [ ] **阶段一：初稿撰写**
    - [ ] 1.1 撰写文章标题（参考技巧增强20%+主导风格80%）
    - [ ] 1.2 撰写第一部分：[标题]
        - **指令**（第一人称）：[详细写作要求]
        - **配图**：在描述[具体功能/场景]时，嵌入 `Medias/images/01-preview.png`
        - **图片位置**：紧跟描述性段落之后，不要放在章节开头或结尾
    - [ ] 1.3 撰写第二部分：[标题]
        - **指令**（第一人称）：[详细写作要求]
        - **配图**：在解释[流程/步骤]时，嵌入 `Medias/images/02-workflow.png`
        - **图片位置**：插入到核心说明段落之后
    - [ ] 1.4 撰写第三部分：[标题]
        - **指令**（第一人称）：[详细写作要求]
        - **配图**：在展示[结果/案例]时，嵌入 `Medias/images/03-result.png`
        - **图片位置**：跟随成果描述段落
    - [ ] ... （为每个章节生成任务项，包含具体的图片路径和插入位置说明）

- [ ] **阶段二：质量检查与润色**
    - [ ] 2.1 执行全局质量检查
    - [ ] 2.2 检查图片是否已嵌入到合适位置（⭐ 必查）
    - [ ] 2.3 执行人味润色（humanization规则）
```

**⚠️ 禁止的做法**（必须避免）：

❌ **错误示例1**：创建单独的"配图方案"章节
```markdown
## 图片配图方案
1. 章节1 → Medias/images/01.png
2. 章节2 → Medias/images/02.png
...
```

❌ **错误示例2**：在文章最后列出配图建议
```markdown
[文章内容...]

---
**[图片:配图建议]**
- 开篇：预览图
- 第一章：截图
```

✅ **正确做法**：在每个章节的写作指令中直接指定图片路径和位置

```markdown
- [ ] 1.2 撰写第一部分：快速上手指南
    - **指令**：介绍工具的主界面和核心功能
    - **配图**：在描述"主界面布局"时，嵌入 `Medias/images/01-preview.png`
    - **图片位置**：紧跟"界面设计很简洁"这段描述之后
```

**输出**：
- `Output/_drafts/03_writing_plan.md`（每个章节包含明确的图片路径和位置）
- `Output/_drafts/03_image_plan.[platform].md`（visual_first，作为图片主文件）

**用户确认**：将写作剧本全文展示，等待确认

---

## 阶段4：多风格候选草稿与正文展开

**目标**：针对当前单个平台并行生成 3 种固定风格候选稿，由用户选中后再展开为正式正文

**输入**：
- 已确认的阶段0-3产物（按路由不同而不同）
  - `long_form`：`03_writing_plan.md`
  - `short_form`：`02S_hook_and_angle.[platform].md`
  - `visual_first`：`02V_cover_and_storyboard.[platform].md` + `03_image_plan.[platform].md`
- `content-creator-memory` 检索结果（由主线程整合进 subagent prompt，不单独落共享底稿文件）
- 当前目标平台规则
- 三份固定风格文档：
  - `references/style-libraries/core/technical-expert.md`
  - `references/style-libraries/core/storytelling.md`
  - `references/style-libraries/core/sharp-humor.md`

**⚠️ 当前范围限制**：
- 阶段4A 的三风格候选模式按**单个平台**执行
- 如果用户一次请求多个平台，先确认当前优先平台，只为该平台生成三风格候选稿
- 候选稿只用于选稿，不直接进入发布

### 步骤4.1：安装 3 个 writer subagents（首次进入当前工作区时）

将以下模板复制到工作区 `.claude/agents/`：

```text
.claude/agents/
├── variant-writer-a.md   # 技术专家
├── variant-writer-b.md   # 故事描述
└── variant-writer-c.md   # 幽默犀利
```

**规则**：
- subagent 只负责写一篇候选稿
- subagent 统一接收主线程传入的事实、目标、平台约束
- subagent 只改变切入角度、语气、结构，不允许改动事实
- subagent 默认输出“候选稿”，不是最终完整正文

### 步骤4.2：并行生成 3 篇候选稿

**固定风格**：

| 子代理 | 风格文档 | 输出文件 |
|:--|:--|:--|
| `variant-writer-a` | `technical-expert.md` | `Output/_drafts/04_variants/[platform]/candidate_technical_expert.md` |
| `variant-writer-b` | `storytelling.md` | `Output/_drafts/04_variants/[platform]/candidate_storytelling.md` |
| `variant-writer-c` | `sharp-humor.md` | `Output/_drafts/04_variants/[platform]/candidate_sharp_humor.md` |

**额外规则**：
- `visual_first` 平台的三篇候选稿，正文头部必须带“图片顺序总览”表，并与 `03_image_plan.[platform].md` 保持一致
- `visual_first` 平台的候选稿必须是“图文正文候选”，不是逐图说明文；文案允许跨 1~2 张图自然推进
- `visual_first` 候选稿禁止出现 `图1 / 图2 / 第1页 / 第2页` 这类机械式说明，除非用户明确要求做教程分镜脚本
- `short_form` 平台的候选稿应尽量短，不要伪装成长文摘要

**主线程传给 subagent 的 prompt 必须包含**：
- 当前平台
- 已确认的阶段产物路径
- 对应风格文档路径
- 输出文件路径
- 强制规则：
  - 三篇候选稿必须事实一致、目标一致、平台一致，只允许写法角度不同
  - 明显体现对应风格
  - 保持当前平台长度和语气边界
  - 输出候选稿，不要直接写成完整版终稿

### 步骤4.3：候选稿硬门槛检查

每篇候选稿都必须先过 4 个硬门槛：

| 指标 | 说明 | 结论 |
|:--|:--|:--|
| 事实保真 | 是否忠于阶段0-3已确认事实，不捏造案例或数据 | 通过 / 不通过 |
| 平台合规 | 是否符合当前平台长度、语气、格式边界 | 通过 / 不通过 |
| 风格清晰 | 是否能明显看出对应风格，而不是普通稿 | 通过 / 不通过 |
| 可展开性 | 是否能自然扩展成完整正文 | 通过 / 不通过 |

**规则**：
- 任意一项不通过，该候选稿不能作为推荐项
- 如果三稿中有两稿以上不通过，应直接重写本轮候选稿

### 步骤4.4：推荐指数评分（结构化 rubric）

对通过硬门槛的候选稿，再按以下指标评分：

| 指标 | 权重 | 说明 |
|:--|:--:|:--|
| 平台适配度 | 20 | 是否像该平台会自然出现的内容 |
| 开头抓力 | 15 | 前两段是否有继续读下去的动力 |
| 核心价值清晰度 | 15 | 这篇要表达什么是否一眼清楚 |
| 事实保真度 | 15 | 是否稳定建立在阶段0-3已确认事实之上 |
| 可展开性 | 10 | 是否适合扩成正式正文 |
| 人味与可读性 | 10 | 是否像真人写的，不工整僵硬 |
| 风格达成度 | 10 | 是否真正写出对应风格 |
| 差异化贡献 | 5 | 相对另外两篇是否有明确差异 |

**评分规则**：
- 满分 100
- `>= 85` → 强推荐
- `78-84` → 推荐
- `70-77` → 可选，但有明显短板
- `< 70` → 不建议直接展开

### 步骤4.5：主线程在对话中输出表格化对比（不生成 compare.md）

**⚠️ 强制规则**：
- 不生成 `compare.md` 文件
- 候选稿写完后，主线程必须在对话中用固定表格做对比回复
- 推荐结论必须基于 rubric，不能只写主观感受

**固定回复格式**：

```markdown
| 风格 | 平台适配度20 | 开头抓力15 | 核心价值15 | 事实保真15 | 可展开性10 | 人味10 | 风格达成10 | 差异化5 | 推荐指数100 |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 技术专家 | 18 | 13 | 14 | 15 | 9 | 8 | 9 | 4 | 90 |
| 故事描述 | 17 | 15 | 13 | 15 | 9 | 9 | 10 | 4 | 92 |
| 幽默犀利 | 16 | 14 | 12 | 14 | 8 | 9 | 9 | 5 | 87 |
```

表格下方必须再补一段：

```markdown
## 建议
- 我更推荐：`故事描述`
- 推荐依据：开头抓力最强，平台适配稳定，可展开性足够
- 如果你更看重专业可信，选：`技术专家`
- 如果你更看重传播感和讨论感，选：`幽默犀利`
```

### 步骤4.6：等待用户选择风格

用户只需回复以下 3 选 1：

```text
技术专家
故事描述
幽默犀利
```

### 步骤4.7：展开选中风格为正式正文

根据用户选中的候选稿，展开生成正式正文：

**输出文件命名规则**：

```text
Output/_drafts/04_draft.[platform].[style].md
```

示例：
- `04_draft.wechat.technical-expert.md`
- `04_draft.jike.storytelling.md`
- `04_draft.twitter.sharp-humor.md`

**展开规则**：
- 忠于被选中的候选稿角度
- 保留阶段0-3已确认的事实边界
- 再应用当前平台的内容格式规则
- 图文混排型平台继续在正文中保留图片占位
- 图文分离型平台保持纯文字正文，仅允许头部封面注释块
- 视觉优先平台的正文头部必须保留“图片顺序总览”，并与 `03_image_plan.[platform].md` 对齐
- 视觉优先平台的正文主体必须是可阅读的图文内容，而不是逐图说明稿
- 视觉优先平台允许“文案呼应图片”，但不要求每一段都与单独一张图片 1:1 对齐
- 只有在用户明确要求“教程分镜 / 逐页讲解 / 提词卡”时，才允许写成逐页说明风格
- 不要在正文暴露技术元数据

**输出**：
- `Output/_drafts/04_draft.[platform].[style].md`

**用户确认**：
- 阶段4A 完成后需要用户选风格
- 阶段4B 展开正式正文后，无需额外确认，直接进入阶段5

---

## 阶段5：爆款潜力评分与优化

**目标**：按平台路由执行首次评分和优化，如低于阈值则自动优化

**输入**：
- `04_draft.[platform].[style].md`（选中风格的正式稿）

### 路由化评分模型

```text
long_form
  -> 使用完整爆款内容多维度分析模型 v2.0

short_form
  -> 使用短内容评分模型

visual_first
  -> 使用视觉优先评分模型
```

#### short_form 评分指标

| 指标 | 权重 |
|:--|:--:|
| 首屏抓力 | 25 |
| 信息密度 | 20 |
| 平台 native 感 | 20 |
| 核心判断清晰度 | 15 |
| 讨论触发度 | 10 |
| 人味与节奏 | 10 |

#### visual_first 评分指标

| 指标 | 权重 |
|:--|:--:|
| 封面抓力 | 20 |
| 图文一致性 | 20 |
| 图片页序推进感 | 15 |
| 文案信息密度 | 15 |
| 收藏 / 分享价值 | 10 |
| 平台 native 感 | 10 |
| 人味与节奏 | 10 |

**执行步骤**：

### 步骤5.1：首次评分（按 route 选择模型）

根据当前平台的 `workflow_route` 选择评分模型：

- `long_form`：使用**爆款内容多维度分析模型 v2.0**
- `short_form`：使用上方短内容评分指标
- `visual_first`：使用上方视觉优先评分指标

详见 [templates/quality-scoring-model.md](../templates/quality-scoring-model.md)

**评分体系**（总分150分，转换为10分制）：

```
【观感分析法】50分
├─ 好奇心（10分）：认知差距型、悬念型、新奇发现型
├─ 颠覆性（10分）：数据型、观念型、场景型、行业型
├─ 技术力（10分）：技术创新度、实现复杂度、应用价值
├─ 新鲜感（10分）：是否前所未见
└─ 沉浸感（10分）：能否让用户完全投入

【视角分析法】30分
├─ 初级开发者视角（10分）：是否零门槛、易复制
├─ 产品经理视角（10分）：是否定位精准、方案完整
└─ 行业人视角（10分）：是否有深度洞察、商业模式

【场景分析法】30分
├─ 可比性（10分）：是否有形象的类比物
├─ 社交动机（10分）：是否能提升用户形象
└─ 用户思考（10分）：是否能引发深度思考

【本质分析法】40分
├─ 节约时间（10分）
├─ 节约金钱（10分）
├─ 心理收获（10分）
└─ 金钱收获（10分）

总分：150分 → 转换为10分制
```

**输出**：
- `Output/_drafts/05_quality_score.[platform].[style].md`

### 步骤5.2：评分决策点

```
检查总分：
├─ 总分 >= 8.0？
│   ├─ 是 → 标记"通过质量检查"
│   │      将 `04_draft.[platform].[style].md` 标记为最终版本
│   │      跳过步骤5.3和5.4
│   │      直接进入阶段6
│   └─ 否 → 标记"需要优化"
│          向用户说明当前评分和预期提升
│          继续执行步骤5.3
```

### 步骤5.3：二次优化（当总分<8.0时）

**优化策略**：

```
读取：
- `04_draft.[platform].[style].md`（原稿）
- `05_quality_score.[platform].[style].md`（评分建议）

执行优化：
【高优先级问题】<6分 → 必须全部修改
【中优先级问题】6-7分 → 建议修改
【保持优势】>=8分 → 不做改动

优化原则：
- 忠于原有风格和80/20记忆校准基准
- 针对性改进，避免全盘重写
- 确保优化后的内容与原稿逻辑一致
```

**输出**：
- `Output/_drafts/05_draft_optimized_v2.[platform].[style].md`
- `Output/_drafts/05_optimization_history.[platform].[style].json`

### 步骤5.4：二次评分

```
读取 `05_draft_optimized_v2.[platform].[style].md`
再次应用爆款内容多维度分析模型
对比首次评分，生成改进报告：
- 哪些维度提升了？
- 提升了多少分？
- 是否达到预期目标（8.0+）？

无论本次评分结果如何，都将继续后续步骤

确定最终版本：
├─ 二次评分>=8.0 → 使用 `05_draft_optimized_v2.[platform].[style].md`
├─ 二次评分>首次评分 → 使用 `05_draft_optimized_v2.[platform].[style].md`
└─ 二次评分<首次评分（异常） → 回退到 `04_draft.[platform].[style].md`
```

**输出**：
- `Output/_drafts/05_quality_score_v2.[platform].[style].md`
- 更新 `05_optimization_history.[platform].[style].json`

---

## 阶段6：多平台适配

**目标**：基于最终稿，生成各平台的专属版本

**输入**：
- 最终稿（`04_draft.[platform].[style].md` 或 `05_draft_optimized_v2.[platform].[style].md`）
- `templates/platform_styles_lib.json`（平台规则）
- 用户确认的目标平台列表

**执行步骤**：

### 步骤6.1：确定输入文件

```
检查 Output/_drafts/ 目录：
├─ 存在 `05_draft_optimized_v2.[platform].[style].md`？
│   ├─ 是 → 使用该文件
│   └─ 否 → 使用 `04_draft.[platform].[style].md`
```

### 步骤6.2：读取平台规则

```
从 platform_styles_lib.json 读取每个目标平台的规则：
- audience（受众）
- tone（语调）
- length（字数）
- format_rules（格式规则）
- humanization（人性化策略）
- cover_policy（平台级封面图策略）
```

### 步骤6.3：媒体资源处理

对每个平台：

```
执行步骤：
1. 读取平台规则中的图片尺寸要求
2. 复制图片文件：
   从：Materials/Medias/images/xxx.png
   到：Output/[platform]/images/xxx.png
3. 根据平台内容格式处理 article.md 中的图片：

   【图文混排型】（wechat/zhihu/bilibili/linkedin）：
   ├─ 检查 draft 中的图片路径格式（![说明](Medias/images/xxx.png)）
   ├─ 必须优先调用 `sanitize_output_markdown.py`
   │  参数：`--strip-screenshot-guides --rewrite-image-paths`
   ├─ **清理截图指引（⭐固定脚本处理）**：删除所有 `> 💡 **截图指引**：...` 引用块，只保留合法图片占位行，确保正式文章干净整洁
   └─ 图片保留在文章正文中

   【图文分离型】（xhs/instagram/douyin/weibo/jike/twitter）：
   ├─ 生成 `article.md` 时必须优先调用 `sanitize_output_markdown.py`
   │  参数：`--strip-screenshot-guides --strip-image-placeholders`
   ├─ article.md 中不包含正文图片语法（纯文字）
   ├─ 若平台 `cover_policy.placeholder_mode = header_comment`
   │   → 保留文章头部的 `<!-- AI封面图 ... -->` 注释块
   ├─ 图片排序和用途由 image_plan.md 管理
   └─ 图片仅复制到 Output/{platform}/images/ 供发布时上传
```

**⚠️ 关键原则**：

```
【图文混排型平台】：
  阶段4（draft.md）→ 引用格式：Medias/images/01.png
  阶段6（article.md）→ 引用格式：images/01.png ⭐ 相对路径

【图文分离型平台】：
  阶段4（draft.md）→ 纯文字，无图片语法
  阶段6（article.md）→ 纯文字，无章节图片语法；允许头部保留 AI封面图注释块
  图片管理 → image_plan.md（图片顺序、封面选择、发布指引）
```

**图文混排型平台的路径转换规则**：

```markdown
# draft.md 中（阶段4输出，含截图指引）
![[待截图] 面板设置](Medias/images/01.png)
> 💡 **截图指引**：这里是留给作者看的提示...

# ↓ 转换为 ↓

# article.md 中（阶段6输出，脚本清理后）
![[待截图] 面板设置](images/01.png)  ⭐ 相对路径且指引被移除
```

**转换逻辑**（仅图文混排型平台执行，且必须通过脚本完成）：

```
python3 scripts/sanitize_output_markdown.py \
  --input "Output/_drafts/05_draft_optimized_v2.{platform}.{style}.md" \
  --output "Output/{platform}/article.md" \
  --strip-screenshot-guides \
  --rewrite-image-paths
```

**短内容 / 视觉优先平台的 `article.md` 清洗逻辑**：

```bash
python3 scripts/sanitize_output_markdown.py \
  --input "Output/_drafts/04_draft.{platform}.{style}.md" \
  --output "Output/{platform}/article.md" \
  --strip-screenshot-guides \
  --strip-image-placeholders
```

**⚠️ 工具使用硬规则**：

```text
1. 阶段6 生成 article.md 时，必须优先调用 sanitize_output_markdown.py
2. 不允许默认依赖 Agent 手工删除固定截图指引标记
3. 仅在脚本缺失、执行失败或输入异常时，才允许 Agent fallback 手工处理
4. 如果发生 fallback，必须在回复中显式说明
5. visual_first 的 image_plan.md 不使用该脚本删除截图指引，因为它属于图片执行信息
```

**Stage 6 Agent 执行模板（单入口优先）**：

```text
默认应优先调用：

python3 /Users/mileson/.cursor/skills/content-creator/scripts/stage6_delivery_pipeline.py \
  "{workspace_dir}" \
  --platform "{platform}"

它会自动完成：
- 复制图片资源到 Output/{platform}/images/
- 生成最终 article.md
- visual_first 同步 image_plan.md
- 调用 run_illustration_pipeline.py
- wechat 自动 markdown-to-wechat -> article.html
- 按 delivery.platforms.{platform}.mode 决定是否继续调用 content-publisher
- 若继续自动发布，平台发布所需敏感信息统一由 `content-publisher` 通过 [`/secrets-vault` Skill](/Users/mileson/.cursor/skills/secrets-vault/SKILL.md) 获取，`content-creator` 不直接读取任何发布凭证
```

**仅在需要解释内部执行顺序时，按以下步骤理解**：

```text
对每个平台生成最终 article.md 时：

1. 先确定输入文件
   - 优先使用 05_draft_optimized_v2.[platform].[style].md
   - 否则使用 04_draft.[platform].[style].md

2. 先复制图片资源到 Output/{platform}/images/

3. 立即调用 sanitize_output_markdown.py 生成 article.md
   - long_form：
     python3 scripts/sanitize_output_markdown.py \
       --input "<draft_file>" \
       --output "Output/{platform}/article.md" \
       --strip-screenshot-guides \
       --rewrite-image-paths

   - short_form / visual_first：
     python3 scripts/sanitize_output_markdown.py \
       --input "<draft_file>" \
       --output "Output/{platform}/article.md" \
       --strip-screenshot-guides \
       --strip-image-placeholders

4. 统一调用 article-illustrator 单入口执行所有 AI 图片任务
   - 固定命令：
     python3 /Users/mileson/.cursor/skills/article-illustrator/scripts/run_illustration_pipeline.py \
       "<workspace_dir>" \
       --platform "{platform}"
   - 单入口内部会自动完成：
     - long_form / short_form 扫描 Output/{platform}/article.md
     - visual_first 扫描 Output/{platform}/image_plan.md
     - 统一处理 `AI封面图` 与正文 `[AI生图]`
     - 跳过 `[待截图]`
     - 已存在输出默认跳过，仅显式 `--force` 才重生
     - 生图成功或 `skip existing` 后自动把占位回写为普通图片引用

5. 只有在 article-illustrator 单入口执行成功后，才继续后续的：
   - 平台语调适配
   - 敏感词检查
   - metadata 生成
   - 交付模式判断

6. 不允许跳过脚本直接手工编辑 article.md 来删除截图指引

7. 如果脚本执行失败：
   - 明确说明失败原因
   - 才允许 fallback 手工清理
   - 并在回复中显式标注“本次使用了 fallback 手工清理”

8. 读取 `workspace.config.yaml > delivery.platforms.{platform}.mode`
   - 若缺失：默认 `auto_format`
   - `auto_format`：
     - 停在本地发布产物完成
     - `wechat` 由 `stage6_delivery_pipeline.py` 内部自动生成 `Output/wechat/article.html`
   - `auto_format_and_publish`：
     - 先完成 `auto_format`
     - 再自动调用 `content-publisher`
     - 平台发布所需敏感信息统一由 `content-publisher` 通过 `secrets-vault` 获取
     - `wechat` 默认执行“创建草稿”，不直接群发
     - `jike` 默认执行真实发布
     - 固定命令：
       python3 /Users/mileson/.cursor/skills/content-publisher/scripts/publisher.py \
         publish \
         --platform "{platform}" \
         --workspace "{workspace_dir}"

9. 一旦工作区配置显式写入 `auto_format_and_publish`
   - 视为用户已授权该平台自动继续执行发布动作
   - Stage 6 不需要再次追问“是否继续发布”
   - 但仍需在回复中明确回报执行结果（例如 draft_id / publish_id / url）

10. `creation.mode = autonomous` 时的 warning 规则
   - warning 一律不中断执行
   - 所有 warning 统一写入 `Output/_reports/autonomous-run-report.md`
   - 只有 hard blocker 才允许中断 Stage 6（如关键输入文件缺失）
```

**平台统一处理策略**：

| 平台 | 路径格式 | 图片位置 | markdown-to-wechat 支持 |
|-----|---------|---------|----------------------|
| **所有平台** | `images/xxx.png` ⭐ | `Output/{platform}/images/` | ✅ 支持 |

**markdown-to-wechat 工作流**（Stage 6 默认内置，不再单独提示用户执行）：

```bash
# 由 stage6_delivery_pipeline.py 内部自动执行
/Users/mileson/.cursor/skills/markdown-to-wechat/convert.sh \
  Output/wechat/article.md \
  --theme deep-blue \
  -o Output/wechat/article.html

# markdown-to-wechat 自动执行：
# 1. 检测图片路径格式（images/xxx.png）
# 2. 找到本地图片文件（Output/wechat/images/xxx.png）
# 3. 上传到阿里云 OSS
# 4. 替换为 CDN URL：https://cdn.example.com/...
# 5. 转换为微信公众号 HTML 格式
# 6. 输出：Output/wechat/article.html
```

**与交付模式的关系**：

```text
wechat + auto_format
  -> Stage 6 自动执行 markdown-to-wechat
  -> 停在 Output/wechat/article.html

wechat + auto_format_and_publish
  -> Stage 6 自动执行 markdown-to-wechat
  -> 再自动调用 content-publisher 创建公众号草稿
  -> 发布凭证统一由 content-publisher 通过 secrets-vault 获取
```

**优势**：
- ✅ 每个平台目录自包含（article.md + images/）
- ✅ 路径相对化，便于移动和分发
- ✅ 符合 markdown-to-wechat 的相对路径优先原则

---

### ⚠️ 重要：图片路径策略说明

**问题场景**：
用户可能使用不同的图片处理工具，导致路径需求不同。

**两种工作流对比**：

#### 工作流A：Stage 6 单入口自动处理（默认）⭐

```bash
# 1. content-creator 通过 stage6_delivery_pipeline.py 生成平台版本（路径：images/xxx.png）
# 2. 图片已复制到 Output/wechat/images/
# 3. pipeline 内部自动执行 markdown-to-wechat

# markdown-to-wechat 自动：
# - 从 Output/wechat/images/ 读取图片
# - 上传到阿里云 OSS
# - 替换为 CDN URL
# - 转换为 HTML
```

**路径格式**：`images/xxx.png`（相对于 `Output/wechat/`）

#### 工作流B：markdown-image-uploader + markdown-to-wechat

```bash
# 1. 仅在用户明确要求使用外部图片上传工具时，才改走这条手工 override 流程
# 2. content-creator 生成平台版本（路径：Materials/Medias/images/xxx.png）⭐
# 2. 从工作区根目录运行图片上传工具
cd "[工作区根目录]"
markdown-image-uploader Output/wechat/article.md -o Output/wechat/article_with_cdn.md

# 3. 再手工执行 markdown-to-wechat 转换 HTML（此时图片已是 CDN URL）
/Users/mileson/.cursor/skills/markdown-to-wechat/convert.sh \
  Output/wechat/article_with_cdn.md \
  --theme deep-blue \
  -o Output/wechat/article.html
```

**路径格式**：`Materials/Medias/images/xxx.png`（相对于工作区根目录）

---

**⭐ 默认策略**：使用工作流A（路径：`images/xxx.png`），也就是直接运行 `stage6_delivery_pipeline.py`

**切换到工作流B**：
如果用户明确表示要使用 `markdown-image-uploader` 或类似工具，则在步骤6.3的路径转换中保持 `Materials/Medias/images/` 路径，不进行转换。

---

### 步骤6.4：平台内容生成

对每个目标平台：

```
读取通用稿 → 应用平台规则 → 生成平台版本

示例（小红书）：
- 字数：800字（从2500字精简）
- 语调：第一人称 + Emoji
- 格式：钩子开头、3-5行分段、#话题标签
- 人性化：每200字≥1错别字

示例（微信公众号）：
- 字数：2500字（完整版）
- 语调：正式、可信、适量故事化
```

**⚠️ 强制规则**（必须遵守）：

❌ **禁止在文章头部添加**：
```markdown
作者：XXX | 身份描述
发布时间：YYYY-MM-DD
分类：XXX
标签：XXX
---
```

❌ **禁止在文章结尾添加**：
```markdown
---
## 关于本文
- 总字数：约 4800 字
- 预计阅读时间：12 分钟
- 生成时间：2026-02-05
- 版本：微信公众号 v1.0
- 基于：content-creator skill + Anthropic Skill 系统
- 图片数量：11 张
- 原创度：100%
- 推荐阅读时间：工作日早 8:00-9:00
- 适合人群：AI 从业者、独立开发者...
- 转载说明：欢迎转载，请注明出处
```

✅ **正确做法**：
- 文章直接从标题开始，无作者署名
- 结尾自然收尾（可以是行动号召、总结等）
- 所有元数据记录在 `metadata.yaml` 中，不写入文章正文
- 格式：段落3-5行、首段引痛点、结尾行动号召
- 人性化：错别字≤3，保留专业术语
```

### 步骤6.5：平台内容合规检查 ⭐ 新增

**目标**：检测生成的平台内容是否包含敏感词

详见 [sensitive-words/README.md](sensitive-words/README.md)

**执行流程**：

对每个目标平台：

#### 6.5.1 检查敏感词库是否存在

```
读取 references/sensitive-words/{platform_id}.md
├─ 存在 → 继续检测
└─ 不存在 → 跳过检测，记录日志
   提示："ℹ️ {platform}平台暂无敏感词库，跳过合规检查"
```

#### 6.5.2 扫描平台内容

```
读取 Output/{platform}/article.md

检测范围：
├─ 标题
├─ 正文（逐段）
└─ 图片说明文字

检测方法：
遍历敏感词库的所有分类
检测文章中是否包含敏感词
记录敏感词的位置和上下文
```

#### 6.5.3 生成检测报告

生成 `Output/{platform}/compliance-report.json`:

```json
{
  "platform": "xhs",
  "scan_time": "2026-02-04T10:30:00Z",
  "detected_sensitive_words": [
    {
      "word": "第一",
      "category": "极限用语类 > 绝对化表述",
      "position": "标题",
      "line_number": 1,
      "original_text": "第一次用AI写文章",
      "suggestion": "推荐替换为：初次用AI写文章",
      "risk_level": "high"
    },
    {
      "word": "最好",
      "category": "极限用语类 > 最高级表述",
      "position": "正文第3段",
      "line_number": 12,
      "original_text": "这款产品最好用",
      "suggestion": "推荐替换为：这款产品很好用",
      "risk_level": "medium"
    }
  ],
  "total_issues": 2,
  "risk_level": "high",
  "compliance_status": "需要修改"
}
```

**风险等级定义**：
- `critical`：严重（政治敏感、色情低俗、违法内容）
- `high`：高风险（极限用语、医疗用语、虚假宣传）
- `medium`：中风险（点击诱导、刺激消费、引流导流）
- `low`：低风险（拉踩行为、诱导互动）

**合规状态**：
- `通过`：未检测到敏感词
- `警告`：检测到低风险敏感词，建议修改
- `需要修改`：检测到中高风险敏感词，必须修改
- `严重违规`：检测到严重敏感词，禁止发布

#### 6.5.4 用户交互

**场景1：检测到敏感词**

```
⚠️ {平台}版本检测到 {数量} 个敏感词（{风险等级}）：

【标题】
❌ "{原文}" 
   问题：包含{类别}"{敏感词}"
   建议：{替代建议}

【正文】
❌ "{原文}"（第X段）
   问题：包含{类别}"{敏感词}"
   建议：{替代建议}

选项：
1. [Y] 自动替换为建议词汇
2. [N] 我手动修改
3. [S] 跳过检查，继续发布（不推荐）

请选择（Y/N/S）：
```

**场景2：未检测到敏感词**

```
✅ {平台}版本通过合规检查
   未检测到敏感词，可以安全发布

继续生成配套文件...
```

**场景3：平台无敏感词库**

```
ℹ️ {平台}暂无敏感词库
   跳过合规检查，已记录日志

提示：如需检查，请添加 references/sensitive-words/{platform_id}.md

继续生成配套文件...
```

#### 6.5.5 处理用户选择

**选择Y：自动替换**

```
执行自动替换：
- 读取 article.md
- 遍历检测到的敏感词
- 使用替代建议替换
- 保存更新后的 article.md
- 标记 compliance_status: "已修改"
- 继续步骤6.6
```

**选择N：手动修改**

```
等待用户手动修改：
- 提示："请修改 Output/{platform}/article.md"
- 暂停流程
- 用户修改完成后回复"继续"
- 重新执行步骤6.5（再次检测）
- 继续步骤6.6
```

**选择S：跳过检查**

```
跳过检查：
- 在 compliance-report.json 标记 skipped: true
- 在 metadata.yaml 标记 compliance_warning: true
- 继续步骤6.6
```

### 步骤6.6：生成配套文件

**⚠️ 根据平台类型，生成不同的配套文件**：

| 平台 | article.md | metadata.yaml | compliance-report.json | image_plan.md | images/ | 备注 |
|-----|-----------|--------------|----------------------|--------------|---------|------|
| **微信公众号** | ✅ | ✅ | ❌ | ❌ | ✅ | 无需敏感词检查 |
| **小红书** | ✅ | ✅ | ✅ | ✅ ⭐ | ✅ | 需要敏感词检查 + 视觉优先图片主文件 |
| **知乎** | ✅ | ✅ | ❌ | ❌ | ✅ | 无需敏感词检查 |
| **其他平台** | ✅ | ✅ | 根据需要 | 视觉优先平台按需生成 | ✅ | 按平台规则 |

对每个平台生成：

#### 1. article.md（平台版本文章）

已在步骤6.4生成，可能在步骤6.5被修改

#### 1.5. image_plan.md（视觉优先图片主文件）⭐

> **仅当目标平台属于 visual_first 时生成**

**来源**：从阶段3步骤3.1.5生成的 `Output/_drafts/03_image_plan.[platform].md` 提取，并根据最终稿内容进行更新校准。

**输出路径**：`Output/[platform]/image_plan.md`

**校准流程**：

```
读取阶段3生成的 03_image_plan.[platform].md
对比最终稿（`04_draft.[platform].[style].md` 或 `05_draft_optimized_v2.[platform].[style].md`）：
├─ 文章标题是否变化？ → 更新封面图的痛点文案/标题
├─ 核心功能是否调整？ → 更新功能截图的展示内容
├─ 卖点是否优化？    → 更新中文 AI 生图提示词中的卖点描述
└─ 整体风格是否调整？ → 更新配色方案

输出校准后的完整图片主文件到 Output/[platform]/image_plan.md
```

**⚠️ 关键要求**：
- AI 生图提示词中的所有占位符必须替换为实际内容
- 用户可直接复制提示词粘贴给 AI 图像生成工具（如 Midjourney、DALL-E、Gemini）
- 截图指引必须具体到"打开哪个页面 → 什么操作状态 → 标注哪个区域"
- `image_plan.md` 只负责图片执行和顺序，不代替最终图文正文
- 最终正文允许与图片形成情绪和叙事呼应，不要求 100% 一页一段、一图一解释

#### 2. metadata.yaml（平台元数据）

```yaml
platform:
  id: xhs
  display_name: 小红书

# ⭐ 作者信息（从 00_extracted_meta.yaml 的 brand_voice.name 获取）
author:
  name: "超级峰"                # 必填：发布时的署名

article:
  title: "..."
  digest: "..."              # ⭐ 摘要（仅限有 digest_max_chars 配置的平台，如微信≤40字）
  word_count: 650

seo:
  keywords:
    - AI
    - 编程
  hashtags:
    - "#AI编程"
    - "#技术分享"

# ⭐ 封面图规范
# - Materials 命名约定: cover-{platform}.{ext}
# - Output 命名约定: cover.{ext}
# - 路径: 相对于当前平台输出目录 Output/{platform}/
# - 来源优先级:
#   1. 用户已在 Materials/Medias/images/ 提供 cover-{platform}.{ext} → 直接使用
#   2. 未提供 → 询问用户是否 AI 生成（由 @article-illustrator 统一执行 `AI封面图` 占位并保存到 Materials/）
#   3. 用户拒绝 AI 生成 → 从现有图片中选取最合适的一张
# - content-publisher 会读取此路径进行上传，不会自动猜测文件名
# - AI 生成默认中文文字，仅当用户明确要求时才使用英文
medias:
  cover:
    path: "./images/cover.jpg"   # 支持任意图片格式，无需限制为 .png
    source: "ai_placeholder"
    placeholder_mode: "inline_markdown"
    aspect_ratio: "21:9"
    recommended_size: "900x383"
    source_asset: "Materials/Medias/images/cover-wechat.jpg"
  inline_images:
    - path: "./images/01.png"
      alt: "图片说明"

platform_specific:
  emoji_usage: moderate
  content_style: conversational

generation:
  source_draft: "04_draft.jike.storytelling.md"
  adapted_at: "2026-02-04 10:30:00"
  version: "1.0"

quality_checks:
  word_count_match: true
  format_compliance: true

compliance:
  checked: true
  status: "通过"
  sensitive_words_count: 0
  warning: false

publish_status:
  ready_to_publish: true
  notes: ""

last_delivery:
  executed_at: "2026-03-04T10:30:00"
  mode: "auto_format"
  workflow_route: "long_form"
  status: "formatted"
  quality_score: "8.3/10"
  outputs:
    article: "./article.md"
    images_dir: "./images/"
    metadata: "./metadata.yaml"
    html: "./article.html"

delivery_records:
  - executed_at: "2026-03-04T10:30:00"
    mode: "auto_format"
    workflow_route: "long_form"
    status: "formatted"
    quality_score: "8.3/10"
    outputs:
      article: "./article.md"
      images_dir: "./images/"
      metadata: "./metadata.yaml"
      html: "./article.html"
```

**author（作者）字段规则** ⭐：

| 规则 | 说明 |
|---|---|
| 数据来源 | 从 `00_extracted_meta.yaml` 的 `brand_voice.name` 读取 |
| 必填性 | 所有平台均必填 |
| 用途 | content-publisher 发布时用作署名 |

**last_delivery / delivery_records 规则** ⭐：

| 字段 | 说明 |
|---|---|
| `last_delivery` | 记录最近一次 Stage 6 单入口交付结果，便于快速查看当前平台最后一次构建/发布状态 |
| `delivery_records` | 记录 Stage 6 历史交付记录，按时间追加 |
| `mode` | 来自 `workspace.config.yaml > delivery.platforms.{platform}.mode` |
| `workflow_route` | 当前平台链路类型：`long_form / short_form / visual_first` |
| `status` | `formatted`（仅本地交付完成）/ `published`（已发布成功）/ `publish_skipped`（配置了自动发布但该平台尚未接通，已降级为本地交付） |
| `outputs` | 本次交付生成的主要产物路径 |
| `publish` | 仅在 `auto_format_and_publish` 时记录，包含 `status / message / draft_id / publish_id / url` 等平台发布结果 |

**digest（摘要）生成规则** ⭐：

当平台配置了 `digest_max_chars` 时（如微信公众号 = 40），必须生成 `article.digest` 字段：

| 规则 | 说明 |
|---|---|
| 字数 | ≤ 平台 `digest_max_chars`（微信 ≤ 40 字） |
| 内容 | 从正文提炼核心价值，回答「读者为什么要点开」 |
| 语气 | 与文章整体 tone 一致 |
| 禁止 | 不重复标题、不用「本文将…」等模板句式 |
| 来源 | 优先从开篇 hook 或结论精华提炼 |

**cover（封面图）字段规则** ⭐：

| 规则 | 说明 |
|---|---|
| Materials 命名约定 | `cover-{platform}.{ext}`，ext 支持 jpg/jpeg/png/gif/webp/bmp |
| Output 命名约定 | `cover.{ext}`，统一给 content-publisher 读取 |
| 路径格式 | 相对路径，相对于 `Output/{platform}/` 目录 |
| 图片来源 | 优先从 `Materials/Medias/images/cover-{platform}.*` 获取；若不存在，**询问用户**是否 AI 生成 |
| AI 生成 | 统一由 `@article-illustrator` 识别 `AI封面图` 占位并执行，默认保存到 `Materials/Medias/images/cover-{platform}.{ext}` |
| 路径示例 | `./images/cover.jpg`、`./images/cover.png` |
| 重要 | content-publisher 仅读取 `medias.cover.path`，不会自动搜索 |

#### 3. 发布提示

**所有平台**：
- ✅ 默认优先调用 `stage6_delivery_pipeline.py`
- ✅ `wechat` 的 HTML 转换已由 Stage 6 管道内置处理，不再额外提示 `@markdown-to-wechat`

**小红书等需敏感词检查的平台**：
- ⚠️ 需要生成 `compliance-report.json`
- ⚠️ 如有敏感词，需用户确认处理方式
- ⚠️ 敏感词处理完成后，提示："内容已通过合规检查，可以发布"

#### 4. images/（处理后的图片）⭐ 必需

从 `Materials/Medias/images/` 复制到 `Output/{platform}/images/`

**封面图处理** ⭐⭐⭐（关键流程，必须严格执行）：

```
封面图检测与执行流程：

步骤 A：检查是否已有封面图
  扫描 Materials/Medias/images/ 目录：
  ├─ 存在 cover-{platform}.{jpg|jpeg|png|gif|webp|bmp} 文件？
  │   ├─ 是 → 直接使用，跳到步骤 D
  │   └─ 否 → 继续步骤 B

步骤 B：询问用户是否需要 AI 生成封面图 ⭐ 必须询问
  向用户展示以下选项：
  
  "📷 检测到工作区未提供专用封面图（cover-{platform}.jpg/png/...）
  
  是否需要通过 AI 生成一张专用封面图？
  
  1️⃣ 是 - 科技极简风（深色背景 + 主题概念）
  2️⃣ 是 - 概念插画风（场景化插图）
  3️⃣ 是 - 数据可视化风（数据/图表元素）
  4️⃣ 是 - 我来描述风格（用户自定义）
  5️⃣ 不需要 - 从已有图片中选取最合适的一张作为封面"
  
  等待用户选择 → 继续步骤 C

步骤 C：调用单入口配图管道
  根据用户选择：
  - 保留最终主文件中的 `AI封面图` 占位
  - 统一执行命令：
    python3 /Users/mileson/.cursor/skills/article-illustrator/scripts/run_illustration_pipeline.py \
      "<workspace_dir>" \
      --platform "{platform}"
  - 由单入口统一读取占位中的：
    - platform
    - aspect_ratio
    - prompt
    - output

  ⚠️ 默认规则：
  - 封面图与正文 `[AI生图]` 统一由 `article-illustrator` 执行
  - 最终图注只能来自显式 `caption`，不得回退使用 `prompt`
  - 已存在的 `cover-{platform}.{ext}` 默认跳过，只有用户明确要求重生时才允许 `--force`
  - 提示词统一使用中文
  - 封面图中禁止任何文字、数字、logo、水印
  - 当前平台默认比例：
    - wechat = 21:9
    - jike = 1:1
    - twitter = 4:5
    - xhs = 3:4（预留）
    - zhihu = 16:9（预留）

步骤 D：复制封面到平台输出目录
  从：Materials/Medias/images/cover-{platform}.{ext}
  到：Output/{platform}/images/cover.{ext}

步骤 E：更新 metadata.yaml
  在 medias.cover.path 中记录相对路径：
  → "./images/cover.{ext}"
  同时记录：
  → medias.cover.source = "ai_placeholder" / "manual_asset"
  → medias.cover.placeholder_mode = "inline_markdown" / "header_comment"
  → medias.cover.aspect_ratio = 平台默认比例
  → medias.cover.source_asset = "Materials/Medias/images/cover-{platform}.{ext}"
```

**⚠️ 如果用户选择"5️⃣ 不需要生成"**：
```
从 Materials/Medias/images/ 中选取最合适的一张：
→ 选择策略：优先选体现文章主题的图片
→ 先复制为 Materials/Medias/images/cover-{platform}.{ext}
→ 再复制并重命名到 Output/{platform}/images/cover.{ext}
→ 目标位置：Output/{platform}/images/cover.{ext}
```

### 步骤6.7：微信公众号后续处理提示

**默认情况**：Stage 6 已通过 `stage6_delivery_pipeline.py` 自动生成 `Output/wechat/article.html`，不再让用户手动选择工作流。

**仅在以下场景才需要退出单入口、改走手动分步流程**：
- 用户明确要求自定义图床
- 用户明确要求调试 `markdown-to-wechat` 转换问题
- 需要保留非标准图片路径或插入额外 CDN 处理步骤

**路径兼容性说明**：

| 工作流 | 图片路径格式 | 适用工具 | 注意事项 |
|-------|------------|---------|---------|
| **A（默认）** | `images/xxx.png` | markdown-to-wechat | 图片在 Output/wechat/images/ |
| **B（高级）** | `Materials/Medias/images/xxx.png` | markdown-image-uploader | 需从工作区根目录运行 |

**⚠️ 如果用户报告"图片找不到"错误**：
1. 检查当前使用的是哪种路径格式
2. 检查工具运行的工作目录
3. 如果使用外部图片上传工具，需要使用 `Materials/Medias/images/` 路径

### 步骤6.8：生成质量报告（可选）

**⚠️ 质量报告为可选项**，仅在用户明确要求时生成

```
Output/_reports/（如需）
├── delivery-summary.yaml（Stage 6 跨平台交付总览）
├── seo-analysis.yaml（SEO分析）
├── readability-score.yaml（可读性评分）
└── platform-compliance.yaml（平台合规性检查）
```

**默认行为**：跳过此步骤，不生成质量报告

**Stage 6 工作区级交付总览** ⭐：

`stage6_delivery_pipeline.py` 每次真实执行后，会额外回写：

```yaml
last_run:
  executed_at: "2026-03-04T10:30:00"
  mode: "mixed"
  status: "published"
  platforms:
    - platform: wechat
      mode: auto_format_and_publish
      workflow_route: long_form
      quality_score: "8.3/10"
      outputs:
        article: "Output/wechat/article.md"
        images_dir: "Output/wechat/images/"
        metadata: "Output/wechat/metadata.yaml"
        html: "Output/wechat/article.html"
      publish:
        status: "draft_created"
        draft_id: "123456"
    - platform: xhs
      mode: auto_format
      workflow_route: visual_first
      quality_score: "8.6/10"
      outputs:
        article: "Output/xhs/article.md"
        images_dir: "Output/xhs/images/"
        metadata: "Output/xhs/metadata.yaml"
        image_plan: "Output/xhs/image_plan.md"

run_records:
  - ...
```

规则：
- `last_run`：最近一次 Stage 6 跨平台汇总结果
- `run_records`：历史 Stage 6 运行记录，按时间追加
- `mode`：
  - 单平台或所有平台同一模式时，写实际 mode
  - 多平台混合模式时，写 `mixed`
- `status`：
  - 仅本地构建完成时写 `formatted`
  - 只要本次有平台继续自动发布，则写 `published`

### 步骤6.9：完成提示

不生成 `Output/README.md`，直接在终端输出完成信息

**输出**：
- `Output/xhs/`（小红书完整输出）
  - `article.md`、`metadata.yaml`、`compliance-report.json`、`images/`
- `Output/wechat/`（微信公众号完整输出）
  - `article.md`、`metadata.yaml`、`images/`
- `Output/[其他平台]/`（如需）
- `Output/_reports/`（质量报告，可选）

**完成提示**：

统一使用以下两套正式模板，不再混合输出：

#### 模板 A：`auto_format`

```text
✅ 内容创作完成

📊 质量评分：{score}

📦 已完成本地交付包：

### {platform}
- 交付模式：delivery.platforms.{platform}.mode = auto_format
- 正文：Output/{platform}/article.md
- 图片：Output/{platform}/images/
- metadata：Output/{platform}/metadata.yaml
{wechat_html_line}
{optional_extra_lines}
- 状态：✅ 已完成本地交付包

📌 后续状态
- 当前模式只完成本地格式化与交付产物构建
- 不再提示用户手动调用某个 Skill
```

其中：
- `wechat_html_line` 仅在 `platform = wechat` 时输出：
  - `- HTML：Output/wechat/article.html`
- `optional_extra_lines` 仅在该平台存在额外产物时输出：
  - 如 `image_plan.md`、`compliance-report.json`

#### 模板 B：`auto_format_and_publish`

```text
✅ 内容创作完成

📊 质量评分：{score}

📦 已完成本地交付包：

### {platform}
- 交付模式：delivery.platforms.{platform}.mode = auto_format_and_publish
- 正文：Output/{platform}/article.md
- 图片：Output/{platform}/images/
- metadata：Output/{platform}/metadata.yaml
{wechat_html_line}
{optional_extra_lines}
- 状态：✅ 已完成格式化并继续自动发布

🚀 发布结果
- 平台：{platform}
- 执行动作：{publish_action}
- 结果：{publish_result_summary}
{publish_id_line}
{publish_url_line}

📌 后续状态
- 当前模式已自动继续执行 `content-publisher`
- 回复中直接汇报平台结果，不再提示用户手动执行发布
```

其中：
- `publish_action`
  - `wechat`：`创建公众号草稿`
  - `jike`：`发布即刻动态`
- `publish_result_summary`
  - 如：`草稿创建成功`、`动态发布成功`
- `publish_id_line`
  - 有返回 ID 时输出，如：`- 草稿ID：{draft_id}`、`- 发布ID：{publish_id}`
- `publish_url_line`
  - 有返回链接时输出，如：`- 链接：{url}`

📌 回复规则：
- 若某平台是 `auto_format`：严格使用模板 A
- 若某平台是 `auto_format_and_publish`：严格使用模板 B
- 同一次回复中，多平台可按平台分段列出，但每个平台必须使用匹配自己 mode 的模板字段
- 不再使用“接下来请你手动调用某个 Skill”作为默认收尾
