# 核心配置文件说明

> 本文档详细说明 content-creator skill 使用的核心配置文件

---

## 1. 内容记忆系统（80/20 策略）

通过 **content-creator-memory** skill 提供：

- **自有内容检索（80%）**: 保持个人风格和表达习惯
- **标杆案例检索（20%）**: 借鉴爆款技巧和结构模式

### 使用方式

- **阶段 1-2**：基于 `target_audience`、`technical_stack`、`quality_score` 筛选
- 提取可复用元素用于写作

### 配置位置

由 content-creator-memory skill 管理：
```
~/.cursor/skills/content-creator-memory/
├── memories/                           
│   ├── knowledge_dict.json             # 认知校正词典
│   ├── contents/wechat/                # 自有内容（34 篇）
│   └── examples/wechat/                # 标杆案例（70 篇）
└── data/                               
    ├── own_works.json                  # 自有内容索引
    ├── reference_examples.json         # 标杆案例索引
    └── search_index.json               # 搜索索引
```

---

## 2. 认知校正词典

通过 content-creator-memory skill 提供，用于：

- **阶段 0**：校正原始素材中的错误名称
- 防止 AI 将专有名词误写

### 示例校正

```json
{
  "超级风": "超级峰",
  "知识相机": "芝士相机",
  "GPT4o": "GPT-4o",
  "Claude3": "Claude 3"
}
```

---

## 3. platform_styles_lib.json（平台规则）

### 文件位置

`templates/platform_styles_lib.json`

### 支持的平台

- `wechat`（微信公众号）
- `xhs`（小红书）
- `zhihu`（知乎）
- `jike`（即刻）
- `twitter`（Twitter/X）
- `linkedin`（LinkedIn）
- `douyin`（抖音）
- `bilibili`（哔哩哔哩）
- `instagram`（Instagram）

### 核心结构

```json
{
  "platforms": [
    {
      "id": "xhs",
      "display_name": "小红书",
      "audience": "18-35岁年轻女性为主，关注生活方式、美妆、时尚、科技等领域",
      "tone": "第一人称 + Emoji + 口语化 + 强互动感",
      "length": "300-800字",
      "format_rules": [
        "钩子开头（制造悬念/反差）",
        "3-5行分段（短句为主）",
        "#话题标签（3-5个）",
        "结尾互动引导"
      ],
      "humanization": "每200字≥1错别字，避免过度正式，多用叹号和问号"
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 平台唯一标识，用于文件命名 |
| `display_name` | string | 平台显示名称 |
| `audience` | string | 目标受众描述 |
| `tone` | string | 语调风格 |
| `length` | string | 字数范围 |
| `format_rules` | array | 格式规则列表 |
| `humanization` | string | 人性化策略 |

---

## 4. 爆款内容多维度分析模型 v2.0（评分标准）

详见 [templates/quality-scoring-model.md](../templates/quality-scoring-model.md)

### 评分体系概览

**总分150分，转换为10分制**：

| 类别 | 权重 | 满分 | 包含维度 |
|------|------|------|----------|
| 观感分析法 | 33% | 50分 | 好奇心、颠覆性、技术力、新鲜感、沉浸感 |
| 视角分析法 | 20% | 30分 | 初级开发者、产品经理、行业人 |
| 场景分析法 | 20% | 30分 | 可比性、社交动机、用户思考 |
| 本质分析法 | 27% | 40分 | 节约时间、节约金钱、心理收获、金钱收获 |

### 评级标准

- **9-10分**：革命性创新
- **7-8分**：显著创新
- **5-6分**：有效创新
- **3-4分**：微小创新
- **0-2分**：缺乏创新

### 阈值

- **excellent**：8.0+（直接发布）
- **good**：6.0+（建议优化）
- **acceptable**：4.0+（必须优化）

---

## 5. workspace.config.yaml（工作区配置）

### 自动生成位置

在工作区根目录自动生成

### 结构示例

```yaml
# 工作区基本信息
workspace:
  name: AI编程实战经验分享
  created_at: 2026-02-04T10:00:00Z

# 素材信息
materials:
  primary_source: Materials/origin.md
  total_word_count: 5000
  files:
    - origin.md
    - research-notes.md

# 媒体资源
medias:
  images:
    count: 8
    total_size: 2.5MB
    files:
      - cover.jpg
      - diagram-01.png
      - diagram-02.png

# 目标平台
target_platforms:
  - xhs        # 小红书
  - wechat     # 微信公众号

# 生成状态
# 可能值：extraction_completed, draft_completed, completed
generation_status: completed

# 执行历史
history:
  - stage: extraction
    completed_at: 2026-02-04T10:05:00Z
  
  - stage: topic_selection
    selected: 方案A
    completed_at: 2026-02-04T10:10:00Z
```

### 字段说明

| 字段 | 说明 |
|------|------|
| `workspace.name` | 工作区名称 |
| `materials.*` | 素材信息 |
| `medias.*` | 媒体资源信息 |
| `target_platforms` | 目标平台列表 |
| `generation_status` | 生成状态（extraction_completed/topic_selected/outline_confirmed/draft_completed/scoring_completed/completed） |
| `history` | 执行历史记录 |

---

## 6. 敏感词库配置

详见 [sensitive-words/README.md](sensitive-words/README.md)

### 文件位置

```
references/sensitive-words/
├── README.md（使用说明）
├── xhs.md（小红书敏感词库）
├── wechat.md（微信公众号敏感词库）
└── template.md（新平台模板）
```

### 平台ID映射

| 平台名称 | platform_id | 敏感词库文件 |
|---------|-------------|-------------|
| 小红书 | `xhs` | `xhs.md` |
| 微信公众号 | `wechat` | `wechat.md` |
| 知乎 | `zhihu` | `zhihu.md` |

---

## 配置文件维护

### 更新 platform_styles_lib.json

1. 编辑 `templates/platform_styles_lib.json`
2. 添加/修改平台规则
3. 确保 `id` 唯一
4. 测试生成效果

### 添加敏感词库

1. 复制 `references/sensitive-words/template.md`
2. 重命名为 `{platform_id}.md`
3. 填写敏感词和替代建议
4. 更新 `references/sensitive-words/README.md`

### 更新认知校正词典

通过 content-creator-memory skill 管理：
```bash
# 编辑词典
vi ~/.cursor/skills/content-creator-memory/memories/knowledge_dict.json

# 重建索引
@content-creator-memory 重建索引
```
