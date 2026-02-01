---
name: content-creator
description: AI内容创作自动化工作流。基于80/20记忆策略，从素材提取→选题策划→标题大纲→写作剧本→初稿生成→质量评分→多平台适配，全流程自动化内容创作，支持小红书、微信公众号、知乎等9大平台。
---

# AI内容创作自动化工作流

## When to Use

当你需要以下功能时使用此 skill：
- 📝 创建专业的内容文章（技术教程、产品评测、经验分享等）
- 🎯 基于个人风格（80%）和标杆技巧（20%）的智能内容生成
- 📱 一键适配多个发布平台（小红书、微信公众号、知乎等）
- 🔄 完整的工作流管理（从素材到发布）
- ⭐ 自动化的内容质量评分和优化建议
- 📊 工作区感知的文件管理（自动创建Output目录结构）

**典型场景**：
- "帮我创建一篇关于AI编程的文章，发布到小红书和微信公众号"
- "基于Materials/文件夹的素材，生成一篇技术教程"
- "对比选题方案，给我推荐最佳的标题和大纲"

## Prerequisites

### 📦 Skill 完全自包含（零配置开箱即用）✨

本 Skill 已打包所有必需的文件和资源，**无需任何外部配置**：

```
~/.cursor/skills/content-creator/
├── templates/                          # 静态工作流模板
│   ├── platform_styles_lib.json       # 9大平台样式规则
│   ├── article_creation.md            # 文章创作工作流模板
│   └── article_elements_extraction.md # 素材提取工作流模板
└── memories/                           # 核心记忆系统（已打包）⭐
    ├── memory_indexing.json            # 80/20记忆策略配置（118KB）
    ├── knowledge_dict.json             # 认知校正词典（1.6KB）
    ├── contents/                       # 自有内容库（own_works）
    │   └── wechat/                     # 4篇精选自有作品
    │       ├── 0 基础保姆教程，免费领取 AI 大模型资格证明.md
    │       ├── 万字长文深度解读：AI编程的工程化与技术突破.md
    │       ├── 别整天学 Cursor Rules 了，这个才是普通人强化 AI 的万能方法！.md
    │       └── 我花1天时间，用 AI 开发出了一款排行榜第107名的产品.md
    └── examples/                       # 标杆案例库（reference_examples）
        └── wechat/                     # 45篇行业标杆作品
            ├── AI产品黄叔/（11篇）
            ├── 数字生命卡兹克/（23篇）
            └── 花叔/（11篇）
```

**✅ 完全自包含的优势**：
- 🚀 **开箱即用**：下载即可使用，无需额外配置
- 📦 **便携性强**：单一文件夹，可轻松分享和迁移
- 🎯 **版本一致**：所有资源版本同步，避免不匹配
- 💡 **零门槛**：新用户无需理解复杂的目录结构

**📊 Skill 大小**：
- 总大小：~840KB（包含所有模板和49篇参考文章）
- 内存占用：仅在使用时按需加载
- Git 友好：所有文件均为文本格式，便于版本控制

---

### 🔍 自动资源检查（启动时验证）

Skill 启动时会自动验证所有内置资源：

```bash
# 检查静态模板
✓ templates/platform_styles_lib.json
✓ templates/article_creation.md
✓ templates/article_elements_extraction.md

# 检查核心配置
✓ memories/memory_indexing.json（118KB，2714行）
✓ memories/knowledge_dict.json（1.6KB，认知校正词典）

# 检查内容库
✓ memories/contents/wechat/（4篇自有作品）
✓ memories/examples/wechat/（45篇标杆案例）
```

**如果资源损坏或缺失，Skill 会提示：**
```
❌ 错误：Skill 资源文件损坏

缺少必需文件：
- ~/.cursor/skills/content-creator/memories/memory_indexing.json

解决方案：
1. 重新安装 Skill（推荐）
2. 从备份恢复 memories/ 目录
3. 联系维护者获取完整版本
```

### 工作区目录结构（自动创建）

每个文章创建在独立的工作区文件夹：

```
[文章工作区]/                   # 用户打开的工作区文件夹
├── Materials/                  # 输入：原始素材（用户提供）
│   ├── origin.md              # 主素材文件
│   ├── research-notes.md      # 调研笔记（可选）
│   └── references.txt         # 参考链接（可选）
├── Medias/                    # 输入：媒体资源（可选）
│   ├── images/
│   │   ├── cover.jpg
│   │   └── diagram-*.png
│   ├── videos/
│   └── audio/
└── Output/                    # 输出：所有生成内容（自动创建）
    ├── _drafts/               # 中间产物
    │   ├── 00_extracted_meta.json
    │   ├── 01_topic_proposals.md
    │   ├── 02_titles_and_outline.md
    │   ├── 03_writing_plan.md
    │   ├── 04_draft.md
    │   ├── 05_quality_score_v1.md
    │   ├── 05_draft_optimized_v2.md（如需优化）
    │   ├── 05_quality_score_v2.md（如需优化）
    │   └── 05_optimization_history.json
    ├── xhs/                   # 小红书版本（自动适配）
    │   ├── article.md
    │   ├── metadata.json
    │   ├── images/
    │   └── publish-checklist.md
    ├── wechat/                # 微信公众号版本
    │   ├── article.md
    │   ├── article.html
    │   ├── metadata.json
    │   ├── images/
    │   └── publish-checklist.md
    ├── zhihu/                 # 知乎版本（如需）
    ├── _reports/              # 质量报告
    │   ├── seo-analysis.json
    │   ├── readability-score.json
    │   └── platform-compliance.json
    └── README.md              # 工作区总览
```

## Instructions

### 🚀 快速开始（用户视角）

**步骤 1：准备工作区**
```bash
# 1. 创建文章工作区文件夹
mkdir "我的文章标题"
cd "我的文章标题"

# 2. 准备素材
mkdir Materials Medias/images
echo "原始内容..." > Materials/origin.md
cp ~/cover.jpg Medias/images/

# 3. 在 Cursor 中打开工作区
# （在 Cursor 中 File -> Open Folder）
```

**步骤 2：执行 Skill**
```
@content-creator 帮我创建一篇关于[主题]的文章，发布到[平台1]和[平台2]
```

**步骤 3：配合确认**
- 阶段1：确认选题方向（3个方案选1）
- 阶段2：确认标题+大纲（5个标题选1）
- 阶段3：确认写作剧本
- 阶段4：自动生成初稿
- 阶段5：自动评分，如需优化则再次确认
- 阶段6：自动生成多平台版本

**步骤 4：查看成果**
```
Output/
├── xhs/article.md          # 小红书版本
├── wechat/article.md       # 微信公众号版本
└── _drafts/                # 所有中间产物
```

---

## 📋 完整工作流（6个阶段）

### 阶段0：素材提取与认知校正

**目标**：从原始素材中提取结构化元数据

**输入**：
- `Materials/*.md`（原始素材）
- `Medias/`（媒体资源，可选）
- `~/Memories/knowledge_dict.json`（认知校正词典）

**执行步骤**：

1. **工作区结构检测**：
   ```
   检查 Materials/ 是否存在
   ├─ 不存在 → 提示："请创建Materials/文件夹并放入原始素材"
   └─ 存在 → 继续
   
   检查 Medias/ 是否存在
   ├─ 不存在 → 记录：无媒体资源
   └─ 存在 → 扫描内容
   
   检查 Output/ 是否存在
   ├─ 不存在 → 创建完整目录结构
   └─ 存在 → 询问是否归档旧内容到 _archive/
   ```

2. **平台确认**（前置检查）：
   ```
   检查用户初始请求中是否明确了目标平台
   ├─ 已明确（如"发布到小红书和微信公众号"） → 记录平台列表
   └─ 未明确 → 暂停，询问用户："请明确您计划发布的平台"
   ```

3. **素材扫描与预处理**：
   ```
   读取所有 Materials/*.md 文件
   统计总字数、文件数量
   识别主要素材文件（最大的 .md 文件）
   ```

4. **认知校正**：
   ```
   使用 ~/Memories/knowledge_dict.json 进行校正
   示例校正：
   - "超级风" → "超级峰"
   - "知识相机" → "芝士相机"
   - 其他专有名词、产品名称
   ```

5. **元数据提取**：
   ```
   生成 extracted_meta.json，包含：
   - trending_topics（热点话题）
   - audience（目标受众）
   - purpose（创作目的）
   - brand_voice（品牌语调）
   - writing_style（写作风格）
   - structure（文章结构模型）
   - key_points（核心要点）
   - humanization（人性化策略）
   - seo（SEO设置）
   - quality_targets（质量目标）
   - assets（资源需求）
   - publish_platforms（目标平台，来自步骤2）
   - output_constraints（输出约束）
   ```

6. **生成工作区配置**：
   ```json
   // workspace.config.json
   {
     "workspace": {
       "name": "文章工作区名称",
       "created_at": "2025-01-24T10:00:00Z"
     },
     "materials": {
       "primary_source": "Materials/origin.md",
       "total_word_count": 5000
     },
     "medias": {
       "images": {"count": 8, "total_size": "2.5MB"}
     },
     "target_platforms": ["xhs", "wechat"],
     "generation_status": "extraction_completed"
   }
   ```

**输出**：
- `Output/_drafts/00_extracted_meta.json`
- `workspace.config.json`

**用户确认**：将 `extracted_meta.json` 全文展示给用户，等待回复"继续"

---

### 阶段1：选题策划（新增）

**目标**：生成3个不同角度的选题方案，供用户选择

**输入**：
- `00_extracted_meta.json`（元数据）
- `~/Memories/memory_indexing.json`（记忆库）

**执行步骤**：

1. **80/20 记忆校准（选题维度）**：
   ```
   从 memory_indexing.json 检索：
   
   【80%权重 - 自有内容】own_works
   ├─ 基于 target_audience、technical_stack、primary_keywords
   ├─ 筛选 Top 2 高质量内容（quality_score）
   └─ 提取成功的选题角度、叙事模式
   
   【20%权重 - 标杆案例】reference_examples
   ├─ 基于 content_type、tone 相似度
   ├─ 筛选 Top 1-2 标杆案例
   └─ 提取爆款选题技巧、标题钩子
   ```

2. **竞品热点分析**：
   ```
   使用 WebSearch 工具：
   - 搜索相关热点话题
   - 分析竞品文章的选题角度
   - 识别内容空白区
   ```

3. **生成3个选题方案**：
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

4. **推荐选题**：
   ```
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

### 阶段2：标题+大纲生成（拆分优化）

**目标**：基于选定的选题，生成5个标题备选和详细大纲

**输入**：
- 用户选择的选题方向（来自阶段1）
- `00_extracted_meta.json`
- `~/Memories/memory_indexing.json`

**执行步骤**：

1. **80/20 记忆校准（标题+大纲维度）**：
   ```
   基于选定选题，深度检索：
   
   【80%权重 - 自有风格】
   ├─ 提取 tone、perspective、writing_style
   ├─ 分析个人特色的标题模式
   └─ 确立主导风格基准
   
   【20%权重 - 标杆技巧】
   ├─ 提取 title_hooks、structural_patterns
   ├─ 分析高吸引力的标题公式
   └─ 确立技巧增强元素
   ```

2. **生成5个标题备选**：
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

3. **生成详细大纲（基于推荐标题）**：
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

4. **大纲统计**：
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

### 阶段3：写作剧本生成

**目标**：将大纲转化为详细的、可执行的写作指令

**输入**：
- 用户确认的标题+大纲（`02_titles_and_outline.md`）
- `00_extracted_meta.json`
- 80/20记忆校准结果

**执行步骤**：

1. **生成分章节写作指令**：
   ```markdown
   # 任务事项：文章正式写作与多平台分发
   
   ## 执行规则
   1. 严格遵循待办事项从上到下执行
   2. 状态实时更新为 [✅]
   3. 忠于 article_structure.md 和 extracted_meta.json
   4. 必须写在同一个 article_draft.md 文档内
   
   ## 核心写作指令
   - **视角指令**：第一人称（"我"、"我们"、"我的"）
   - **故事描述指令**：避免具体人名，使用"我有个朋友"
   - **主要指令**：遵循 extracted_meta.json 的 writing_style
   - **80/20 风格校准指令**：
     - 主导风格（80%）：融入自有内容的表达习惯
     - 技巧增强（20%）：借鉴标杆案例的钩子技巧
     - 融合原则：自然统一，避免突兀
   - **分层素材复用指令**：
     - 核心素材优先（golden_sentences、core_workflows）
     - 技巧素材辅助（钩子模式、开篇技巧）
     - 智能组合（自然流畅）
   - **图片引用规范指令**（⭐ 重要）：
     - 所有图片必须使用标准 Markdown 格式：`![图片说明](Medias/images/文件名.jpg)`
     - 图片说明必填，描述图片内容（用于图床上传后生成 alt 文本）
     - 图片路径固定为相对路径：`Medias/images/`
     - 每张图片下方添加小字说明（用于微信公众号图注）
     - 示例格式：
       ```
       ![MacOS Finder 工具栏配置界面](Medias/images/01-toolbar-setup.png)
       
       *▲ 在 Finder 工具栏中拖拽添加应用图标*
       ```
   
   ## 写作待办事项
   
   - [ ] **阶段一：初稿撰写**
       - [ ] 1.1 撰写文章标题（参考技巧增强20%+主导风格80%）
       - [ ] 1.2 撰写章节一：[标题]
           - **指令**（第一人称）：[详细写作要求]
       - [ ] 1.3 撰写章节二：[标题]
           - **指令**（第一人称）：[详细写作要求]
       - [ ] ... （为每个章节生成一个任务项）
   
   - [ ] **阶段二：质量检查与润色**
       - [ ] 2.1 执行全局质量检查
       - [ ] 2.2 执行人味润色（humanization规则）
   ```

**输出**：
- `Output/_drafts/03_writing_plan.md`

**用户确认**：将写作剧本全文展示，等待确认

---

### 阶段4：写作执行（生成初稿）

**目标**：严格按照写作剧本，生成完整初稿

**输入**：
- `03_writing_plan.md`（写作剧本）
- 80/20记忆校准的素材库

**执行步骤**：

1. **逐章节写作**：
   ```
   按照 writing_plan.md 的待办事项：
   - 读取每个章节的写作指令
   - 调用记忆库中的核心素材（80%）
   - 融入标杆技巧（20%）
   - 生成该章节内容
   - 标记该任务为 [✅]
   ```

2. **全局质量检查**：
   ```
   检查项：
   - ✅ 是否全文保持第一人称？
   - ✅ 逻辑是否连贯？
   - ✅ 风格是否统一？
   - ✅ 是否忠于大纲？
   ```

3. **人味润色**：
   ```
   根据 extracted_meta.json 的 humanization 规则：
   - 允许适量错别字（微信≤3个，小红书每200字≥1个）
   - 去除"首先"、"其次"等正式连接词
   - 增加口语化表达
   - 不要破折号、冒号、双引号
   - 不要过度分行，采用自然段
   ```

**输出**：
- `Output/_drafts/04_draft.md`（通用初稿）

**无需用户确认**，直接进入阶段5

---

### 阶段5：爆款潜力评分与优化（新增）

**目标**：自动评估初稿质量，如低于8分则自动优化

**输入**：
- `04_draft.md`（初稿）

**执行步骤**：

#### 步骤 5.1：首次评分

使用**爆款内容多维度分析模型 v2.0**进行评分：

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

**评分报告包含**：
```markdown
# 爆款潜力评分报告 v1

## 📊 总体评分
**总分**: 6.8/10
**评级**: 有效创新（5-6分区间）
**建议**: ⚠️ 需要优化后再发布

## 🔍 详细评分
[详细的每项评分和分析]

## 🎯 核心问题诊断
### 问题1：新鲜感不足（5分）⚠️ 高优先级
**问题描述**：...
**具体表现**：...
**改进建议**（可执行）：
1. 更换开场角度
2. 增加意外元素
3. 差异化案例
**预期提升**：5分 → 7-8分

### 问题2-N：...

## 💡 快速优化检查清单
**必须优化的项目**（<6分）：
- [ ] 新鲜感（5分）→ 更换开场角度
- [ ] 金钱收获（4分）→ 量化收益

**建议优化的项目**（6-7分）：
- [ ] 颠覆性（6分）→ 增加颠覆性观点

## 📊 优化后预期总分
**当前总分**: 6.8/10
**优化后预期**: 8.2-8.5/10
```

**输出**：
- `Output/_drafts/05_quality_score_v1.md`

#### 步骤 5.2：评分决策点

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

#### 步骤 5.3：二次优化（当总分<8.0时）

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

**示例优化**：
```markdown
【问题】：新鲜感不足（5分）
【当前开场】："45天前的我，连代码都不会写"
【优化后开场】："就在昨天，我拒绝了一家公司20万的App外包订单。
不是我清高，而是我发现：这个需求，我用Cursor一天就能搞定..."

【理由】：制造反差（拒绝20万 vs 1天搞定），更有冲击力
【预期提升】：5分 → 7分
```

**输出**：
- `Output/_drafts/05_draft_optimized_v2.md`
- `Output/_drafts/05_optimization_history.json`

#### 步骤 5.4：二次评分

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

### 阶段6：多平台适配

**目标**：基于最终稿，生成各平台的专属版本

**输入**：
- 最终稿（`04_draft.md` 或 `05_draft_optimized_v2.md`）
- `~/Templates/platform_styles_lib.json`（平台规则）
- 用户确认的目标平台列表

**执行步骤**：

1. **确定输入文件**：
   ```
   检查 Output/_drafts/ 目录：
   ├─ 存在 05_draft_optimized_v2.md？
   │   ├─ 是 → 使用该文件
   │   └─ 否 → 使用 04_draft.md
   ```

2. **读取平台规则**：
   ```
   从 platform_styles_lib.json 读取每个目标平台的规则：
   - audience（受众）
   - tone（语调）
   - length（字数）
   - format_rules（格式规则）
   - humanization（人性化策略）
   ```

3. **媒体资源处理**（⭐ 与 markdown-image-uploader 集成）：
   ```
   对每个平台：
   - 读取平台规则中的图片尺寸要求
   - 检查文章中的图片路径格式（![说明](Medias/images/xxx.png)）
   - **关键步骤**：在生成平台版本前，保留原始 Medias/ 路径
     （为后续 markdown-to-wechat 的图床上传做准备）
   - 将 Medias/images/ 的图片复制到 Output/[platform]/images/
   - 在平台版本的 article.md 中，更新图片引用为：
     - 小红书：./images/xxx.png（本地相对路径）
     - 微信公众号：保持 Medias/images/xxx.png（待图床上传）
     - 其他平台：根据平台规则调整
   ```
   
   **重要说明**：
   - 对于**微信公众号平台**，在 `Output/wechat/article.md` 中：
     - **保持原始的 `Medias/images/` 路径**（不要替换为 CDN URL）
     - 这样在后续执行 `/markdown-to-wechat` 时，可以：
       1. 检测到 `Medias/images/` 路径的图片
       2. 自动调用 `markdown-image-uploader` skill
       3. 上传图片到阿里云 OSS
       4. 替换为 CDN URL
       5. 再生成最终 HTML

4. **平台内容生成**：
   ```
   对每个目标平台：
   
   读取通用稿 → 应用平台规则 → 生成平台版本
   
   示例（小红书）：
   - 字数：800字（从2500字精简）
   - 语调：第一人称 + Emoji
   - 格式：钩子开头、3-5行分段、#话题标签
   - 人性化：每200字≥1错别字
   
   示例（微信公众号）：
   - 字数：2500字（完整版）
   - 语调：正式、可信、适量故事化
   - 格式：段落3-5行、首段引痛点、结尾行动号召
   - 人性化：错别字≤3，保留专业术语
   ```

5. **生成配套文件**：
   ```
   对每个平台生成：
   
   1. article.md（平台版本文章）
   
   2. metadata.json（平台元数据）
   {
     "platform": {"id": "xhs", "display_name": "小红书"},
     "article": {"title": "...", "word_count": 650},
     "seo": {"keywords": [...], "hashtags": [...]},
     "medias": {"cover": {...}, "inline_images": [...]},
     "platform_specific": {...},
     "generation": {...},
     "quality_checks": {...},
     "publish_status": {"ready_to_publish": true}
   }
   
   3. publish-checklist.md（发布检查清单）
   # 小红书发布检查清单
   ## 📋 内容检查
   - [ ] 标题吸引力强
   - [ ] 字数在300-800字
   - [ ] Emoji使用恰当
   ...
   
   4. images/（处理后的图片）
   ```

6. **HTML导出（微信专用）**：
   ```
   如果平台 == wechat：
   - 将 article.md 转换为 HTML
   - 应用微信公众号样式
   - 保存为 article.html
   ```

7. **生成质量报告**：
   ```
   Output/_reports/
   ├── seo-analysis.json（SEO分析）
   ├── readability-score.json（可读性评分）
   └── platform-compliance.json（平台合规性检查）
   ```

8. **生成工作区总览**：
   ```markdown
   # 文章工作区总览
   
   ## 📊 生成统计
   - 原始素材字数：5000字
   - 通用初稿字数：2500字
   - 优化后字数：3200字
   - 质量评分：8.3/10（显著创新）
   
   ## 📱 平台版本
   ### 小红书版本
   - 文件：Output/xhs/article.md
   - 字数：650字
   - 配图：5张（1:1比例）
   - 状态：✅ 可发布
   
   ### 微信公众号版本
   - 文件：Output/wechat/article.md
   - 字数：3200字
   - 配图：5张（2.35:1比例）
   - 状态：✅ 可发布
   
   ## 📄 中间产物
   - 00_extracted_meta.json - 元数据提取
   - 01_topic_proposals.md - 选题方案（选择方案A）
   - 02_titles_and_outline.md - 标题+大纲（选择标题2）
   - 03_writing_plan.md - 写作剧本
   - 04_draft.md - 通用初稿
   - 05_quality_score_v1.md - 首次评分（6.8分）
   - 05_draft_optimized_v2.md - 优化版（8.3分）
   - 05_quality_score_v2.md - 二次评分
   
   ## ✅ 下一步建议
   1. 检查各平台版本的 publish-checklist.md
   2. 根据清单完成最后检查
   3. 发布到对应平台
   ```

**输出**：
- `Output/xhs/`（小红书完整输出）
- `Output/wechat/`（微信公众号完整输出）
- `Output/[其他平台]/`（如需）
- `Output/_reports/`（质量报告）
- `Output/README.md`（工作区总览）

**完成提示**：
```
✅ 内容创作完成！

已生成平台版本：
- 小红书：Output/xhs/article.md
- 微信公众号：Output/wechat/article.md

质量评分：8.3/10（显著创新）

下一步：
1. 查看 Output/README.md 了解完整情况
2. 检查各平台的 publish-checklist.md
3. 根据清单完成发布前检查
```

---

## 🎯 核心配置文件说明

### 1. memory_indexing.json（80/20记忆策略）

**位置**：`~/Memories/memory_indexing.json`

**核心结构**：
```json
{
  "own_works": [
    {
      "id": "article-001",
      "title": "我用Cursor1小时开发的App上了榜单",
      "quality_score": 8.5,
      "tone": ["友好", "数据驱动", "鼓励性"],
      "reusable_elements": {
        "golden_sentences": ["..."],
        "core_workflows": ["..."],
        "success_factors": ["..."]
      }
    }
  ],
  "reference_examples": {
    "wechat": {
      "AI产品黄叔": [...],
      "数字生命卡兹克": [...],
      "花叔": [...]
    }
  },
  "search_index": {...},
  "semantic_graph": {...}
}
```

**使用方式**：
- 阶段1-2：检索 `own_works`（80%）和 `reference_examples`（20%）
- 基于 `target_audience`、`technical_stack`、`quality_score` 筛选
- 提取 `reusable_elements` 用于写作

### 2. knowledge_dict.json（认知校正）

**位置**：`~/Memories/knowledge_dict.json`

**核心结构**：
```json
{
  "names": [
    {"name": "超级峰", "description": "作者本人，独立开发者..."}
  ],
  "web_products": [
    {"name": "熊猫灵码", "description": "AI编程效率辅助工具"}
  ],
  "app_products": [
    {"name": "芝士相机", "description": "帮助男朋友给女朋友拍照的App"}
  ]
}
```

**使用方式**：
- 阶段0：校正原始素材中的错误名称
- 防止AI将"超级风"误写为"超级峰"

### 3. platform_styles_lib.json（平台规则）

**位置**：`~/Templates/platform_styles_lib.json`

**支持的平台**：
- wechat（微信公众号）
- xhs（小红书）
- zhihu（知乎）
- jike（即刻）
- twitter（Twitter/X）
- linkedin（LinkedIn）
- douyin（抖音）
- bilibili（哔哩哔哩）
- instagram（Instagram）

**核心结构**：
```json
{
  "platforms": [
    {
      "id": "xhs",
      "display_name": "小红书",
      "audience": "18-35岁年轻女性...",
      "tone": "第一人称 + Emoji",
      "length": "300-800字",
      "format_rules": ["钩子开头", "3-5行分段", "#话题标签"],
      "humanization": "每200字≥1错别字..."
    }
  ]
}
```

### 4. 爆款内容多维度分析模型 v2.0（评分标准）

**评分体系**（总分150分，转换为10分制）：

| 类别 | 权重 | 满分 | 包含维度 |
|------|------|------|----------|
| 观感分析法 | 33% | 50分 | 好奇心、颠覆性、技术力、新鲜感、沉浸感 |
| 视角分析法 | 20% | 30分 | 初级开发者、产品经理、行业人 |
| 场景分析法 | 20% | 30分 | 可比性、社交动机、用户思考 |
| 本质分析法 | 27% | 40分 | 节约时间、节约金钱、心理收获、金钱收获 |

**评级标准**：
- 9-10分：革命性创新
- 7-8分：显著创新
- 5-6分：有效创新
- 3-4分：微小创新
- 0-2分：缺乏创新

**阈值**：
- excellent：8.0+（直接发布）
- good：6.0+（建议优化）
- acceptable：4.0+（必须优化）

---

## Best Practices

### 1. 工作区管理

✅ **推荐做法**：
- 每个文章创建独立的工作区文件夹
- 工作区名称清晰（如"AI编程实战经验分享"）
- Materials/只放原始素材，Output/只放生成内容
- 使用 `workspace.config.json` 追踪工作区状态

❌ **避免做法**：
- 不要在同一工作区混合多篇文章
- 不要手动修改 Output/_drafts/ 的编号前缀
- 不要删除中间产物（便于复盘和调试）

### 2. 素材准备

✅ **推荐做法**：
- Materials/origin.md 作为主素材（5000字+）
- 包含具体案例、数据、故事
- 提前收集相关图片到 Medias/images/
- 素材越详细，生成质量越高

❌ **避免做法**：
- 不要只提供大纲或简短描述
- 不要混合多个完全不相关的主题
- 不要使用低质量或侵权图片

### 3. 用户确认策略

✅ **推荐做法**：
- 阶段1：认真对比3个选题方案，选择最适合的
- 阶段2：从5个标题中选择最吸引人的
- 阶段3：检查写作剧本的指令是否清晰
- 阶段5：如果评分<8，建议执行优化

❌ **避免做法**：
- 不要盲目选择推荐项（推荐基于算法，可能不符合你的需求）
- 不要跳过评分优化环节（优化可提升2-3倍传播效果）

### 4. 平台适配

✅ **推荐做法**：
- 根据平台特性选择发布渠道（小红书+微信是黄金组合）
- 检查每个平台的 `publish-checklist.md`
- 使用平台提供的 `metadata.json` 优化SEO
- 根据平台数据反馈调整策略

❌ **避免做法**：
- 不要将同一版本发布到所有平台（风格不匹配）
- 不要忽略平台的 `humanization` 规则（会被识别为AI生成）
- 不要在小红书用微信公众号的正式语调

### 5. 质量优化

✅ **推荐做法**：
- 重点优化低于6分的维度（高优先级）
- 参考评分报告的具体改进建议
- 保持原有风格，针对性改进
- 记录优化历史（`optimization_history.json`）

❌ **避免做法**：
- 不要为了提分而全盘重写（失去个人风格）
- 不要忽略"保持优势"的项目（已有8分+）
- 不要在优化时改变核心观点

---

## Important Notes

### 1. 依赖检查

**在执行 Skill 前，必须确认**：
- [ ] `~/Memories/memory_indexing.json` 已配置
- [ ] `~/Memories/knowledge_dict.json` 已配置
- [ ] `~/Memories/Contents/` 有自有内容（至少5篇）
- [ ] `~/Memories/Examples/` 有标杆案例（至少10篇）
- [ ] `~/Templates/platform_styles_lib.json` 已配置

**如果缺少，Skill 会提示错误并终止。**

### 2. 工作区要求

**用户必须提供**：
- [ ] Materials/origin.md（主素材，建议5000字+）
- [ ] 目标发布平台（在初始请求中明确）

**可选但推荐**：
- [ ] Medias/images/（配图）
- [ ] Materials/research-notes.md（调研资料）
- [ ] Materials/references.txt（参考链接）

### 3. 平台限制

**当前支持的平台**：
- wechat, xhs, zhihu, jike, twitter, linkedin, douyin, bilibili, instagram

**如果用户请求不支持的平台**：
- 提示："抱歉，当前不支持[平台名]，支持的平台有：[列表]"
- 建议用户选择相近的平台（如：公众号→微信公众号）

### 4. 质量控制

**自动检查项**：
- 素材完整性（字数、格式）
- 平台规则遵循（字数、格式、humanization）
- 颜色/样式规范（图片尺寸、分辨率）
- SEO优化（关键词密度、meta描述）

**人工审核建议**：
- 事实准确性（AI可能产生幻觉）
- 敏感词汇（政治、宗教、暴力等）
- 版权合规（图片、引用来源）
- 品牌一致性（tone、价值观）

### 5. 性能优化

**执行时间预估**：
- 阶段0（素材提取）：1-2分钟
- 阶段1（选题策划）：2-3分钟
- 阶段2（标题+大纲）：2-3分钟
- 阶段3（写作剧本）：1-2分钟
- 阶段4（写作执行）：5-10分钟
- 阶段5（评分+优化）：3-8分钟（如需优化）
- 阶段6（多平台适配）：2-5分钟

**总耗时**：约15-35分钟（取决于是否优化）

**优化建议**：
- 并行处理：多平台适配可以并行
- 缓存复用：同一素材生成多篇文章时，复用记忆校准结果
- 增量生成：如果只需要新增平台，无需重新生成整个流程

---

## Output Checklist

完成后确认：

### 阶段0：素材提取
- [ ] ✅ `Output/_drafts/00_extracted_meta.json` 已生成
- [ ] ✅ `workspace.config.json` 已生成
- [ ] ✅ 用户已确认元数据

### 阶段1：选题策划
- [ ] ✅ `Output/_drafts/01_topic_proposals.md` 已生成
- [ ] ✅ 包含3个选题方案和推荐理由
- [ ] ✅ 用户已选择选题方向

### 阶段2：标题+大纲
- [ ] ✅ `Output/_drafts/02_titles_and_outline.md` 已生成
- [ ] ✅ 包含5个标题备选和详细大纲
- [ ] ✅ 用户已确认标题和大纲

### 阶段3：写作剧本
- [ ] ✅ `Output/_drafts/03_writing_plan.md` 已生成
- [ ] ✅ 包含分章节写作指令
- [ ] ✅ 用户已确认写作剧本

### 阶段4：写作执行
- [ ] ✅ `Output/_drafts/04_draft.md` 已生成
- [ ] ✅ 全文第一人称视角
- [ ] ✅ 逻辑连贯、风格统一

### 阶段5：评分+优化
- [ ] ✅ `Output/_drafts/05_quality_score_v1.md` 已生成
- [ ] ✅ 如总分<8，已执行优化
- [ ] ✅ 如已优化，`05_draft_optimized_v2.md` 和 `05_quality_score_v2.md` 已生成
- [ ] ✅ `05_optimization_history.json` 已记录

### 阶段6：多平台适配
- [ ] ✅ 各平台文件夹已创建（xhs/, wechat/, ...）
- [ ] ✅ 每个平台包含：
  - [ ] article.md
  - [ ] metadata.json
  - [ ] publish-checklist.md
  - [ ] images/（处理后的图片）
- [ ] ✅ 微信公众号包含 article.html（如需）
- [ ] ✅ `Output/_reports/` 质量报告已生成
- [ ] ✅ `Output/README.md` 工作区总览已生成

### 最终检查
- [ ] ✅ 所有中间产物可追溯
- [ ] ✅ workspace.config.json 状态为 "completed"
- [ ] ✅ 向用户展示完成总结和下一步建议

---

## Troubleshooting

### 问题1：提示"Memories目录不存在"

**原因**：Skill 内置资源损坏或缺失

**解决方案**：
```bash
# 检查 Skill 资源完整性
ls ~/.cursor/skills/content-creator/memories/

# 验证核心文件
ls -lh ~/.cursor/skills/content-creator/memories/memory_indexing.json
ls -lh ~/.cursor/skills/content-creator/memories/knowledge_dict.json

# 如果文件缺失，重新安装 Skill
# 或从备份恢复 memories/ 目录
```

### 问题2：评分一直低于8分

**原因**：素材质量不足或选题角度问题

**解决方案**：
1. 检查评分报告的核心问题诊断
2. 重点查看<6分的维度
3. 考虑回到阶段1重新选择选题
4. 补充更多具体案例、数据、故事到素材

### 问题3：平台适配后风格不对

**原因**：平台规则未正确应用

**解决方案**：
1. 检查 `platform_styles_lib.json` 配置
2. 确认 `humanization` 规则是否执行
3. 手动微调 `Output/[platform]/article.md`
4. 参考该平台的 Examples/ 标杆案例

### 问题4：图片处理失败

**原因**：图片格式不支持或尺寸问题

**解决方案**：
1. 确保图片格式为 jpg、png、webp
2. 原图尺寸建议 >=1080px
3. 手动使用图片编辑工具处理
4. 更新 Medias/images/ 后重新执行阶段6

### 问题5：工作流中断如何恢复

**原因**：AI会话断开或错误

**解决方案**：
```
检查 workspace.config.json 的 generation_status：
- "extraction_completed" → 从阶段1开始
- "topic_selected" → 从阶段2开始
- "outline_confirmed" → 从阶段3开始
- "draft_completed" → 从阶段5开始
- "scoring_completed" → 从阶段6开始

重新调用 Skill，说明："继续完成[工作区名称]的内容创作，从[阶段X]开始"
```

---

## Version History

- **v1.0.0** (2025-01-24)
  - 初始版本
  - 支持6阶段完整工作流
  - 支持9大发布平台
  - 集成80/20记忆策略
  - 集成爆款潜力评分系统
  - 工作区感知的文件管理

---

## 相关资源

本 Skill 是完全自包含的，所有必需资源已内置：
- ✅ 工作流模板：`~/.cursor/skills/content-creator/templates/`
- ✅ 记忆系统：`~/.cursor/skills/content-creator/memories/`
- ✅ 自有内容库：`~/.cursor/skills/content-creator/memories/contents/`
- ✅ 标杆案例库：`~/.cursor/skills/content-creator/memories/examples/`

**扩展和自定义**（可选）：
- 添加更多自有作品到 `memories/contents/wechat/`
- 添加更多标杆案例到 `memories/examples/wechat/`
- 更新 `memories/memory_indexing.json` 以索引新内容
- 修改 `templates/platform_styles_lib.json` 自定义平台规则

---

**Made with ❤️ by 超级峰 | Powered by Cursor AI**
