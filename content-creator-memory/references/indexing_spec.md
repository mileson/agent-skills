# 索引规范文档 - Indexing Specification

本文档详细定义了 content-creator-memory skill 的索引数据结构和字段规范。

---

## 索引文件结构

```
data/
├── own_works.json              # 自有内容索引
├── reference_examples.json     # 标杆案例索引
├── search_index.json           # 搜索引擎索引
└── metadata.json               # 索引元数据
```

---

## 1. own_works.json（自有内容索引）

### 字段定义

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `id` | String | ✓ | 唯一标识符（小写、连字符分隔） |
| `file_path` | String | ✓ | 文件相对路径（相对于 HOME） |
| `title` | String | ✓ | 文章标题 |
| `summary` | String | ✓ | 文章摘要（200字以内） |
| `word_count` | Integer | ✓ | 字数统计 |
| `quality_score` | Float | ✓ | 质量评分（1.0-10.0） |
| `keywords` | List[String] | ✓ | 关键词列表 |
| `content_type` | String | ✓ | 内容类型 |
| `target_audience` | List[String] | - | 目标受众 |
| `technical_stack` | List[String] | - | 技术栈 |
| `reusable_elements` | Object | - | 可复用元素 |

### 示例

```json
{
  "id": "ai-app-in-1-day-case-study",
  "file_path": ".cursor/skills/content-creator-memory/memories/contents/wechat/我花1天时间用AI开发出了一款排行榜第107名的产品.md",
  "title": "我花1天时间，用 AI 开发出了一款排行榜第107名的产品",
  "summary": "以第一人称视角，详细复盘了如何在一天内，利用 AI 工具从构思、开发到上线一款 App...",
  "word_count": 4200,
  "quality_score": 9.2,
  "keywords": ["ai编程", "独立开发", "cursor", "app开发", "实战经验"],
  "content_type": "Case Study",
  "target_audience": ["独立开发者", "产品经理", "AI编程初学者"],
  "technical_stack": ["Cursor", "iOS开发", "ChatGPT"],
  "reusable_elements": {
    "golden_sentences": [
      "关键不是技术的深度，而是完成的速度。"
    ],
    "core_workflows": [
      "AI产品命名流程",
      "AI编程调试三步法"
    ]
  }
}
```

### 质量评分标准

| 分数 | 等级 | 说明 |
|------|------|------|
| 9.0-10.0 | 优秀 | 高质量、系统性强、可复用性高 |
| 7.0-8.9 | 良好 | 内容扎实、结构清晰、有参考价值 |
| 5.0-6.9 | 中等 | 基本完整、有一定参考价值 |
| < 5.0 | 待改进 | 内容不足或质量较低 |

**当前实现**: 简单基于字数评分（5.0 + word_count/500），未来可接入 AI 评分。

---

## 2. reference_examples.json（标杆案例索引）

### 字段定义

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `id` | String | ✓ | 唯一标识符 |
| `file_path` | String | ✓ | 文件相对路径 |
| `title` | String | ✓ | 文章标题 |
| `author` | String | ✓ | 作者名称 |
| `platform` | String | ✓ | 发布平台（wechat/xhs/...） |
| `keywords` | List[String] | ✓ | 关键词列表 |
| `title_hooks` | List[String] | - | 标题钩子技巧 |
| `structural_patterns` | List[String] | - | 结构模式 |
| `expression_techniques` | List[String] | - | 表达技巧 |

### 示例

```json
{
  "id": "ai产品黄叔-ai编程10小时2个产品",
  "file_path": ".cursor/skills/content-creator-memory/memories/examples/wechat/AI产品黄叔/AI编程10小时2个产品.md",
  "title": "AI编程10小时2个产品：从Claude Sonnet到Cursor...",
  "author": "AI产品黄叔",
  "platform": "wechat",
  "keywords": ["ai编程", "claude", "cursor", "产品开发"],
  "title_hooks": ["数字钩子", "对比冲击"],
  "structural_patterns": ["钩子开场", "问题-解决方案", "案例串联"],
  "expression_techniques": ["第一人称", "数据支撑", "情绪渲染"]
}
```

### 标题钩子类型

| 类型 | 说明 | 示例 |
|------|------|------|
| 数字钩子 | 使用具体数字增强可信度 | "10小时2个产品" |
| 情绪词汇 | 引发情绪共鸣的词汇 | "惊艳"、"震撼"、"爆款" |
| 问句/感叹 | 使用问号或感叹号 | "你还在...吗？" |
| 对比冲击 | 强烈的前后对比 | "从小白到专家" |
| 身份认同 | 让读者产生代入感 | "普通人也能..." |

---

## 3. search_index.json（搜索引擎索引）

### 字段定义

| 字段 | 类型 | 说明 |
|------|------|------|
| `inverted_index` | Object | 倒排索引（关键词 → 文档ID列表） |
| `tfidf_scores` | Object | TF-IDF 分数（文档ID → {关键词: 分数}） |

### 示例

```json
{
  "inverted_index": {
    "ai编程": ["ai-app-in-1-day-case-study", "ai-programming-deep-dive", ...],
    "cursor": ["ai-app-in-1-day-case-study", ...],
    "独立开发": ["ai-app-in-1-day-case-study", ...]
  },
  "tfidf_scores": {
    "ai-app-in-1-day-case-study": {
      "ai编程": 0.4521,
      "cursor": 0.3214,
      "独立开发": 0.2876
    }
  }
}
```

### TF-IDF 计算公式

```
TF (Term Frequency) = 关键词在文档中的出现次数 / 文档总关键词数
IDF (Inverse Document Frequency) = log(总文档数 / 包含该关键词的文档数)
TF-IDF = TF × IDF
```

---

## 4. metadata.json（索引元数据）

### 字段定义

| 字段 | 类型 | 说明 |
|------|------|------|
| `version` | String | 索引版本号 |
| `created_at` | String | 创建时间（ISO 8601） |
| `last_updated` | String | 最后更新时间 |
| `total_own_works` | Integer | 自有内容总数 |
| `total_reference_examples` | Integer | 标杆案例总数 |
| `total_keywords` | Integer | 关键词总数 |

### 示例

```json
{
  "version": "1.0",
  "created_at": "2026-02-04T07:00:00Z",
  "last_updated": "2026-02-04T07:00:00Z",
  "total_own_works": 34,
  "total_reference_examples": 45,
  "total_keywords": 1234
}
```

---

## 字段提取逻辑

### 自动提取字段

| 字段 | 提取方法 |
|------|----------|
| `title` | 提取 Markdown 一级标题 |
| `summary` | 提取前3段文字，限制200字 |
| `word_count` | 统计中文字符+英文单词 |
| `keywords` | 提取高频词（2-4字中文词+3+字英文词） |
| `quality_score` | 基于字数的简单评分（5.0 + word_count/500） |

### 手动标注字段（未来可 AI 辅助）

| 字段 | 说明 |
|------|------|
| `target_audience` | 目标受众（需人工标注或 AI 分析） |
| `technical_stack` | 技术栈（需人工标注或 AI 分析） |
| `reusable_elements` | 可复用元素（需人工标注或 AI 分析） |
| `structural_patterns` | 结构模式（需人工标注或 AI 分析） |
| `expression_techniques` | 表达技巧（需人工标注或 AI 分析） |

---

## 维护建议

### 初始化索引

```bash
# 首次创建索引
python3 rebuild_index.py \
  --contents-dir ~/.cursor/skills/content-creator-memory/memories/contents/wechat \
  --examples-dir ~/.cursor/skills/content-creator-memory/memories/examples/wechat \
  --output-dir ~/.cursor/skills/content-creator-memory/data
```

### 增量更新

```bash
# 添加单篇新内容
python3 add_content.py \
  --file ~/.cursor/skills/content-creator-memory/memories/contents/wechat/新文章.md \
  --auto-extract
```

### 定期维护

- **每周**: 检查新增内容，执行增量更新
- **每月**: 检查索引质量，补充手动标注字段
- **季度**: 执行全量重建，优化索引结构
