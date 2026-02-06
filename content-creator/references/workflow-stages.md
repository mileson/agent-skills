# 完整工作流详细说明（6个阶段）

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
- [阶段2：标题+大纲生成](#阶段2标题大纲生成)
- [阶段3：写作剧本生成](#阶段3写作剧本生成)
- [阶段4：写作执行](#阶段4写作执行)
- [阶段5：爆款潜力评分与优化](#阶段5爆款潜力评分与优化)
- [阶段6：多平台适配](#阶段6多平台适配)

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
├─ 不存在 → 提示："请创建Materials/文件夹并放入原始素材"
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

## 阶段2：标题+大纲生成

**目标**：基于选定的选题，生成5个标题备选和详细大纲

**输入**：
- 用户选择的选题方向（来自阶段 1）
- `00_extracted_meta.yaml`
- 内容记忆系统（content-creator-memory）

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

### 步骤2.3：生成详细大纲（基于推荐标题）

格式示例：

```markdown
## 📐 文章大纲（基于标题2）

**结构模型**：故事化PAS（Problem-Agitate-Solution）

### 章节一：钩子开场
**核心要点**：制造反差，设置悬念
**写作指令**（第一人称）：
- 以具体场景开头
- 描述震惊/意外的时刻
- 设置悬念："但X天前..."
**预计字数**：150-200字

### 章节二-N：...
```

### 步骤2.4：大纲统计

```
- 总章节数：6个
- 预计总字数：2050-2900字
- 适配平台：
  - 小红书版本：精简为800字
  - 微信公众号：完整版2500字
- 配图需求：5张
```

**输出**：
- `Output/_drafts/02_titles_and_outline.md`

**用户确认**：
1. 展示5个标题，询问："您选择哪个标题？（推荐标题2）"
2. 展示完整大纲，询问："大纲是否需要调整？"

---

## 阶段3：写作剧本生成

**目标**：将大纲转化为详细的、可执行的写作指令

**输入**：
- 用户确认的标题+大纲（`02_titles_and_outline.md`）
- `00_extracted_meta.yaml`
- 80/20记忆校准结果

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
5. `Medias/images/cover.jpg` [关键词: cover]

### Markdown 引用格式

```markdown
![图注说明，10-20字](Medias/images/01-preview.png)
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

### 步骤3.2：生成分章节写作指令（直接包含图片）⭐

**⚠️ 关键要求**：必须将图片路径直接写入每个章节的写作指令中，不要单独创建"配图方案"章节

生成格式：

```markdown
# 任务事项：文章正式写作与多平台分发

## 执行规则
1. 严格遵循待办事项从上到下执行
2. 状态实时更新为 [✅]
3. 忠于 article_structure.md 和 extracted_meta.json
4. 必须写在同一个 article_draft.md 文档内
5. ⭐ **图片必须嵌入到章节合适位置，禁止放在文章最后**

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
- **图片嵌入规范指令**（⭐⭐⭐ 重要）：
  - 必须使用步骤3.1扫描到的图片路径：`Medias/images/文件名.png`（以实际扫描到的扩展名为准，如 .png/.jpeg/.jpg/.webp）
  - 图片必须嵌入到章节内容的合适位置（描述该内容的段落之后）
  - 禁止将图片集中放在文章最后作为"配图建议"
  - 标准格式：
    ```markdown
    ![图注文字，10-20字](Medias/images/01-preview.png)
    ```
  - alt 文本 = 图注说明：简洁描述图片内容，10-20字（markdown-to-wechat 会自动渲染为 figcaption）
  - ⚠️ **禁止**在图片下方另起一行写 `*▲ ...*` 斜体图注（会与 figcaption 重复显示）

## 写作待办事项

- [ ] **阶段一：初稿撰写**
    - [ ] 1.1 撰写文章标题（参考技巧增强20%+主导风格80%）
    - [ ] 1.2 撰写章节一：[标题]
        - **指令**（第一人称）：[详细写作要求]
        - **配图**：在描述[具体功能/场景]时，嵌入 `Medias/images/01-preview.png`
        - **图片位置**：紧跟描述性段落之后，不要放在章节开头或结尾
    - [ ] 1.3 撰写章节二：[标题]
        - **指令**（第一人称）：[详细写作要求]
        - **配图**：在解释[流程/步骤]时，嵌入 `Medias/images/02-workflow.png`
        - **图片位置**：插入到核心说明段落之后
    - [ ] 1.4 撰写章节三：[标题]
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
- [ ] 1.2 撰写章节一：快速上手指南
    - **指令**：介绍工具的主界面和核心功能
    - **配图**：在描述"主界面布局"时，嵌入 `Medias/images/01-preview.png`
    - **图片位置**：紧跟"界面设计很简洁"这段描述之后
```

**输出**：
- `Output/_drafts/03_writing_plan.md`（每个章节包含明确的图片路径和位置）

**用户确认**：将写作剧本全文展示，等待确认

---

## 阶段4：写作执行

**目标**：严格按照写作剧本，生成完整初稿

**输入**：
- `03_writing_plan.md`（写作剧本）
- 80/20记忆校准的素材库

**执行步骤**：

### 步骤4.1：逐章节写作（严格嵌入图片）⭐⭐⭐

**⚠️ 执行前必读**：图片必须嵌入到章节内对应位置，禁止放在文章最后

```
按照 writing_plan.md 的待办事项：
for each 章节 in 写作待办事项:
  1. 读取该章节的写作指令
  2. ⭐⭐⭐ 检查该章节是否有配图指令（必查！）
  3. 如果有配图：
     - 记录图片路径（如 Medias/images/01-preview.png）
     - 记录图片应该插入的位置说明
  4. 调用记忆库中的核心素材（80%）
  5. 融入标杆技巧（20%）
  6. 生成该章节内容
  7. ⭐⭐⭐ 在生成内容时，在合适位置嵌入图片（必须执行！）
     - 不要在章节结尾一次性插入所有图片
     - 不要把图片留到文章最后统一处理
     - 必须在描述该内容的段落后立即插入
  8. 标记该任务为 [✅]
```

**⚠️ 关键原则**（强制遵守）：

1. **即时嵌入**：写到相关内容时，立即插入图片，不要延后
2. **禁止堆积**：不要把所有图片放在章节最后或文章最后
3. **遍历完整**：必须检查并使用 scan_images.py 扫描到的所有图片
4. **不要遗漏**：每张图片都必须找到合适的位置嵌入

**图片嵌入策略**（⭐ 关键）：

```
如果章节有配图指令（如：配图：Medias/images/01-preview.png）：

执行流程：
┌─────────────────────────────────────┐
│ 1. 写章节开头段落（引入）          │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 2. 写核心描述段落                   │
│    （如：介绍主界面布局）           │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 3. ⭐ 立即嵌入图片                        │
│    ![简洁的主界面设计](Medias/images/01.png)     │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 4. 继续写后续内容                   │
└─────────────────────────────────────┘

图片插入位置决策：
- 预览图/截图 → 插入到功能描述段落之后
- 流程图/架构图 → 插入到流程解释段落之后
- 结果展示图 → 插入到成果描述段落之后
- 配置截图 → 插入到配置步骤说明之后
```

**标准 Markdown 格式**（必须遵守）：

```markdown
![图注文字，10-20字](Medias/images/文件名.png)
```

> ⚠️ 图注只写在 alt 文本中，**不要**另起 `*▲ ...*` 行（markdown-to-wechat 会自动将 alt 渲染为 figcaption，另写会重复）

**完整章节示例**（正确做法）⭐：

```markdown
## 第一章：快速上手指南

在开始使用这个工具之前，我想先带你看看它的界面。整个界面设计得非常简洁，左侧是功能菜单，右侧是主工作区。

![简洁的主界面设计，一目了然](Medias/images/01-preview.png)

看到了吗？这个设计的核心理念就是：让你专注于核心功能，不被复杂的选项干扰。

接下来，我会教你如何配置工具栏。这个功能很实用，可以把常用的应用直接放到工具栏，一键启动。

![拖拽即可添加应用到工具栏](Medias/images/02-toolbar-config.png)

配置完成后，你的工作效率会提升不少...
```

**⚠️ 禁止的做法**（严重错误）：

❌ **错误示例1**：把图片全部放在文章最后
```markdown
## 第一章：快速上手指南
[内容...]

## 第二章：核心功能
[内容...]

## 第三章：实战案例
[内容...]

---
**[图片:配图建议]**  ← ❌ 禁止这样做！
- 第一章：Medias/images/01-preview.png
- 第二章：Medias/images/02-workflow.png
...
```

❌ **错误示例2**：图片堆在章节最后
```markdown
## 第一章：快速上手指南

[所有段落内容...]

然后，这里是相关图片：  ← ❌ 禁止这样做！
![图1](Medias/images/01.png)
![图2](Medias/images/02.png)
```

❌ **错误示例3**：遗漏图片
```markdown
# Agent 只用了 3 张图片，但 scan_images.py 扫描到 5 张
# ← ❌ 禁止遗漏！必须遍历所有图片
```

✅ **正确做法**：图片即时嵌入对应位置

```markdown
## 第一章：快速上手指南

介绍界面的段落...

![主界面设计](Medias/images/01-preview.png)  ← ✅ 紧跟描述段落

继续写配置的段落...

![配置步骤](Medias/images/02-config.png)  ← ✅ 紧跟配置说明

继续后续内容...
```

**质量检查清单**（写完后必须自查）：

- [ ] 所有图片都已嵌入到对应章节？
- [ ] 没有图片被遗漏？
- [ ] 没有图片堆在章节最后或文章最后？
- [ ] 每张图片都紧跟相关描述段落？
- [ ] 图片路径格式正确（`Medias/images/xxx.png`，以实际扫描到的扩展名为准）？
- [ ] 每张图片都有 alt 文本（图注说明，10-20字）？
- [ ] 没有另起 `*▲ ...*` 斜体行（避免与 figcaption 重复）？

### 步骤4.2：全局质量检查

检查项：
- ✅ 是否全文保持第一人称？
- ✅ 逻辑是否连贯？
- ✅ 风格是否统一？
- ✅ 是否忠于大纲？

### 步骤4.3：人味润色

根据 `extracted_meta.yaml` 的 humanization 规则：
- 允许适量错别字（微信≤3个，小红书每200字≥1个）
- 去除"首先"、"其次"等正式连接词
- 增加口语化表达
- 不要破折号、冒号、双引号
- 不要过度分行，采用自然段
- 避免「不是...而是...」「与其说...不如说...」等对立转折句式，这是典型的 AI 写作痕迹，改用更自然的口语化转折（如"换句话说""其实"）

### 步骤4.4：移除元数据信息（⭐ 新增）

**⚠️ 强制规则**：文章中禁止出现以下内容：

❌ **禁止在文章头部出现**：
```markdown
# ❌ 错误示例（禁止）
作者：超级峰 | AI 独立开发者
发布时间：2026-02-05
分类：技术教程
---
```

❌ **禁止在文章结尾出现**：
```markdown
# ❌ 错误示例（禁止）
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

**原因**：
- 这些是给创作者看的技术元数据
- 不应该暴露给最终读者
- 会破坏阅读体验和文章专业性

✅ **正确做法**：
- 文章直接从标题开始
- 结尾自然收尾，无需元数据说明
- 元数据信息记录在 `metadata.yaml` 中

**输出**：
- `Output/_drafts/04_draft.md`（通用初稿，干净无元数据）

**无需用户确认**，直接进入阶段5

---

## 阶段5：爆款潜力评分与优化

**目标**：自动评估初稿质量，如低于8分则自动优化

**输入**：
- `04_draft.md`（初稿）

**执行步骤**：

### 步骤5.1：首次评分

使用**爆款内容多维度分析模型 v2.0**进行评分。

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
- `Output/_drafts/05_quality_score_v1.md`

### 步骤5.2：评分决策点

```
检查总分：
├─ 总分 >= 8.0？
│   ├─ 是 → 标记"通过质量检查"
│   │      将 04_draft.md 标记为最终版本
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
- 04_draft.md（原稿）
- 05_quality_score_v1.md（评分建议）

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
- `Output/_drafts/05_draft_optimized_v2.md`
- `Output/_drafts/05_optimization_history.json`

### 步骤5.4：二次评分

```
读取 05_draft_optimized_v2.md
再次应用爆款内容多维度分析模型
对比首次评分，生成改进报告：
- 哪些维度提升了？
- 提升了多少分？
- 是否达到预期目标（8.0+）？

无论本次评分结果如何，都将继续后续步骤

确定最终版本：
├─ 二次评分>=8.0 → 使用 05_draft_optimized_v2.md
├─ 二次评分>首次评分 → 使用 05_draft_optimized_v2.md
└─ 二次评分<首次评分（异常） → 回退到 04_draft.md
```

**输出**：
- `Output/_drafts/05_quality_score_v2.md`
- 更新 `05_optimization_history.json`

---

## 阶段6：多平台适配

**目标**：基于最终稿，生成各平台的专属版本

**输入**：
- 最终稿（`04_draft.md` 或 `05_draft_optimized_v2.md`）
- `templates/platform_styles_lib.json`（平台规则）
- 用户确认的目标平台列表

**执行步骤**：

### 步骤6.1：确定输入文件

```
检查 Output/_drafts/ 目录：
├─ 存在 05_draft_optimized_v2.md？
│   ├─ 是 → 使用该文件
│   └─ 否 → 使用 04_draft.md
```

### 步骤6.2：读取平台规则

```
从 platform_styles_lib.json 读取每个目标平台的规则：
- audience（受众）
- tone（语调）
- length（字数）
- format_rules（格式规则）
- humanization（人性化策略）
```

### 步骤6.3：媒体资源处理

对每个平台：

```
执行步骤：
1. 读取平台规则中的图片尺寸要求
2. 检查 draft 中的图片路径格式（![说明](Medias/images/xxx.png)）
3. 复制图片文件：
   从：Materials/Medias/images/xxx.png
   到：Output/[platform]/images/xxx.png
4. ⭐ 更新平台版本 article.md 中的图片引用为相对路径：
   将：Medias/images/xxx.png
   替换为：images/xxx.png（相对路径，去掉 Medias/ 前缀）
```

**⚠️ 关键原则**：

```
阶段4（draft.md）：
  引用格式：Medias/images/01.png
  图片位置：Materials/Medias/images/01.png
  
阶段6（article.md）：
  引用格式：images/01.png ⭐ 相对路径
  图片位置：Output/{platform}/images/01.png
```

**⚠️ 图片路径转换规则**（关键）：

阶段6将图片路径从 draft 格式转换为平台相对路径：

```markdown
# draft.md 中（阶段4输出）
![说明](Medias/images/01.png)

# ↓ 转换为 ↓

# article.md 中（阶段6输出）
![说明](images/01.png)  ⭐ 使用相对路径
```

**转换逻辑**：

```
for each 图片引用 in draft.md:
  原路径：Medias/images/subfolder/01.png
  ↓
  1. 复制文件：
     从：Materials/Medias/images/subfolder/01.png
     到：Output/{platform}/images/subfolder/01.png
  
  2. 更新引用：
     将：Medias/images/subfolder/01.png
     替换为：images/subfolder/01.png
     （去掉 Medias/ 前缀，保留子目录结构）
```

**平台统一处理策略**：

| 平台 | 路径格式 | 图片位置 | markdown-to-wechat 支持 |
|-----|---------|---------|----------------------|
| **所有平台** | `images/xxx.png` ⭐ | `Output/{platform}/images/` | ✅ 支持 |

**markdown-to-wechat 工作流**（简化）：

```bash
# 用户在 content-creator 完成后，执行转换
@markdown-to-wechat Output/wechat/article.md

# markdown-to-wechat 自动执行：
# 1. 检测图片路径格式（images/xxx.png）
# 2. 找到本地图片文件（Output/wechat/images/xxx.png）
# 3. 上传到阿里云 OSS
# 4. 替换为 CDN URL：https://cdn.example.com/...
# 5. 转换为微信公众号 HTML 格式
# 6. 输出：Output/wechat/article.html
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

#### 工作流A：markdown-to-wechat 一键处理（推荐）⭐

```bash
# 1. content-creator 生成平台版本（路径：images/xxx.png）
# 2. 图片已复制到 Output/wechat/images/
# 3. 直接调用 markdown-to-wechat
@markdown-to-wechat Output/wechat/article.md

# markdown-to-wechat 自动：
# - 从 Output/wechat/images/ 读取图片
# - 上传到阿里云 OSS
# - 替换为 CDN URL
# - 转换为 HTML
```

**路径格式**：`images/xxx.png`（相对于 `Output/wechat/`）

#### 工作流B：markdown-image-uploader + markdown-to-wechat

```bash
# 1. content-creator 生成平台版本（路径：Materials/Medias/images/xxx.png）⭐
# 2. 从工作区根目录运行图片上传工具
cd "[工作区根目录]"
markdown-image-uploader Output/wechat/article.md -o Output/wechat/article_with_cdn.md

# 3. 再用 markdown-to-wechat 转换 HTML（此时图片已是 CDN URL）
@markdown-to-wechat Output/wechat/article_with_cdn.md
```

**路径格式**：`Materials/Medias/images/xxx.png`（相对于工作区根目录）

---

**⭐ 默认策略**：使用工作流A（路径：`images/xxx.png`）

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

| 平台 | article.md | metadata.yaml | compliance-report.json | images/ | 备注 |
|-----|-----------|--------------|----------------------|---------|------|
| **微信公众号** | ✅ | ✅ | ❌ | ✅ | 无需敏感词检查 |
| **小红书** | ✅ | ✅ | ✅ | ✅ | 需要敏感词检查 |
| **知乎** | ✅ | ✅ | ❌ | ✅ | 无需敏感词检查 |
| **其他平台** | ✅ | ✅ | 根据需要 | ✅ | 按平台规则 |

对每个平台生成：

#### 1. article.md（平台版本文章）

已在步骤6.4生成，可能在步骤6.5被修改

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
# - 命名约定: cover.{ext}，ext 可以是 jpg/jpeg/png/gif/webp/bmp
# - 路径: 相对于当前平台输出目录 Output/{platform}/
# - 来源: content-creator 阶段6 从 Materials/Medias/images/ 中选取或用户提供
# - content-publisher 会读取此路径进行上传，不会自动猜测文件名
medias:
  cover:
    path: "./images/cover.jpg"   # 支持任意图片格式，无需限制为 .png
    size: "1:1"
  inline_images:
    - path: "./images/01.png"
      alt: "图片说明"

platform_specific:
  emoji_usage: moderate
  content_style: conversational

generation:
  source_draft: "04_draft.md"
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
```

**author（作者）字段规则** ⭐：

| 规则 | 说明 |
|---|---|
| 数据来源 | 从 `00_extracted_meta.yaml` 的 `brand_voice.name` 读取 |
| 必填性 | 所有平台均必填 |
| 用途 | content-publisher 发布时用作署名 |

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
| 命名约定 | `cover.{ext}`，ext 支持 jpg/jpeg/png/gif/webp/bmp |
| 路径格式 | 相对路径，相对于 `Output/{platform}/` 目录 |
| 图片来源 | 从 `Materials/Medias/images/` 中选取合适图片复制为 cover |
| 路径示例 | `./images/cover.jpg`、`./images/cover.png` |
| 重要 | content-publisher 仅读取 `medias.cover.path`，不会自动搜索 |

#### 3. 发布提示

**所有平台**：
- ✅ 直接调用对应的转换工具
- ✅ 微信公众号：提示词 `@markdown-to-wechat Output/wechat/article.md`

**小红书等需敏感词检查的平台**：
- ⚠️ 需要生成 `compliance-report.json`
- ⚠️ 如有敏感词，需用户确认处理方式
- ⚠️ 敏感词处理完成后，提示："内容已通过合规检查，可以发布"

#### 4. images/（处理后的图片）⭐ 必需

从 `Materials/Medias/images/` 复制到 `Output/{platform}/images/`

**封面图处理**：
```
1. 如果用户在 Materials/Medias/images/ 中已提供 cover.{ext} 文件：
   → 直接复制到 Output/{platform}/images/cover.{ext}
2. 如果没有命名为 cover 的文件：
   → 选取最合适的一张图片，复制并重命名为 cover.{ext}
   → 选择策略：优先选体现文章主题的图片
3. 在 metadata.yaml 的 medias.cover.path 中记录相对路径
   → 例如: "./images/cover.jpg"
```

### 步骤6.7：微信公众号后续处理提示

**⚠️ 不在此步骤生成 HTML**，而是提示用户选择工作流

```
如果平台 == wechat：
  提示用户选择工作流：
  
  "✅ 微信公众号版本已生成：Output/wechat/article.md
  
  🚀 下一步：请选择图片处理工作流
  
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  【工作流A】一键处理（推荐）⭐
  
  直接使用 markdown-to-wechat：
  @markdown-to-wechat Output/wechat/article.md
  
  ✅ 自动上传图片到 OSS
  ✅ 自动转换为 HTML
  ✅ 最简单快捷
  
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  【工作流B】分步处理（如需自定义图床）
  
  ⚠️ 注意：当前文章使用的是相对路径（images/xxx.png）
  如果要使用 markdown-image-uploader，需要先切换回工作区根目录路径：
  
  1. 修改图片路径（从 images/ 改为 Materials/Medias/images/）
  2. 从工作区根目录运行上传工具
  3. 再使用 markdown-to-wechat 转换 HTML
  
  ⚠️ 建议：如无特殊需求，请使用工作流A
  
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

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
├── seo-analysis.yaml（SEO分析）
├── readability-score.yaml（可读性评分）
└── platform-compliance.yaml（平台合规性检查）
```

**默认行为**：跳过此步骤，不生成质量报告

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

```
✅ 内容创作完成！

📊 质量评分：8.3/10（显著创新）

📱 已生成平台版本：

### 小红书
- 文件：Output/xhs/article.md
- 字数：650字 | 配图：5张
- 敏感词：✅ 通过检查
- 状态：✅ 可发布

### 微信公众号
- 文件：Output/wechat/article.md
- 字数：3200字 | 配图：5张
- 状态：✅ 待转换

🚀 下一步操作：

**微信公众号**：
请使用 markdown-to-wechat 转换为 HTML：
@markdown-to-wechat Output/wechat/article.md

**小红书**：
可直接复制 Output/xhs/article.md 内容发布
```

