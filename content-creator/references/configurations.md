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
      "humanization": "每200字≥1错别字，避免过度正式，多用叹号和问号",
      "cover_policy": {
        "enabled": false,
        "phase": "phase_2",
        "placeholder_mode": "image_plan_cover_slot",
        "placement": "image_plan_head",
        "generation_mode": "deferred_ai",
        "default_aspect_ratio": "3:4",
        "recommended_size": "1080x1440",
        "source_filename": "cover-xhs.jpg",
        "output_filename": "cover.jpg"
      }
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
| `cover_policy.enabled` | boolean | 是否启用平台级封面图占位 |
| `cover_policy.phase` | string | 接入阶段，如 `phase_1` / `phase_2` |
| `cover_policy.placeholder_mode` | string | 占位形式，如 `inline_markdown` / `header_comment` / `image_plan_cover_slot` |
| `cover_policy.placement` | string | 封面占位放置位置，如 `article_head` |
| `cover_policy.default_aspect_ratio` | string | 平台默认封面比例 |
| `cover_policy.recommended_size` | string | 推荐像素尺寸 |
| `cover_policy.source_filename` | string | 材料区平台专属封面源文件名 |
| `cover_policy.output_filename` | string | 输出目录中的标准封面文件名 |

### 平台级封面图策略（2026-03 新增）

当前推荐按平台分开管理封面图，不再只使用单一 `cover.jpg`：

| 平台 | 启用状态 | 占位模式 | 推荐比例 | 推荐尺寸 | Materials 源文件 |
|------|----------|----------|----------|----------|------------------|
| `wechat` | 启用 | `inline_markdown` | `21:9` | `900x383` | `cover-wechat.jpg` |
| `jike` | 启用 | `header_comment` | `1:1` | `1080x1080` | `cover-jike.jpg` |
| `twitter` | 启用 | `header_comment` | `4:5` | `1440x1800` | `cover-twitter.jpg` |
| `xhs` | 预留 | `image_plan_cover_slot` | `3:4` | `1080x1440` | `cover-xhs.jpg` |
| `zhihu` | 预留 | `inline_markdown` | `16:9` | `1280x720` | `cover-zhihu.jpg` |

说明：
- `inline_markdown`：在文章头部直接放 Markdown 封面占位，适合图文混排平台。
- `header_comment`：在文章头部写注释型封面占位，不污染正文，适合即刻、Twitter/X 这类图文分离平台。
- `image_plan_cover_slot`：封面需求写入独立配图策划，不直接写进正文。
- 微信历史常用头图尺寸仍可参考 `900x383`，但由于当前生图接口不支持 `2.35:1`，执行时统一使用最接近的 `21:9`。

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
      - cover-wechat.jpg
      - diagram-01.png
      - diagram-02.png

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
| `creation.mode` | 创作模式：`collaborative` / `autonomous` |
| `delivery.platforms.{platform}.mode` | 平台交付模式：`auto_format` / `auto_format_and_publish` |
| `generation_status` | 生成状态（extraction_completed/topic_selected/outline_confirmed/draft_completed/scoring_completed/completed） |
| `history` | 执行历史记录 |

### 创作模式配置（2026-03 新增）

| 模式 | 含义 |
|------|------|
| `collaborative` | 人机协同，关键节点可交互确认 |
| `autonomous` | 自动创作，默认继续执行；出现 warning 写入 `Output/_reports/autonomous-run-report.md` |

规则：
- `creation.mode` 缺失时，默认 `collaborative`
- `autonomous` 下，warning 不中断流程，仅进入自动化运行报告
- 只有 hard blocker（如关键输入缺失）才中断执行

### 平台交付自动化配置（2026-03 新增）

用户侧只保留两档：

| 模式 | 含义 |
|------|------|
| `auto_format` | 只自动完成本地构建与格式化，不调用 `content-publisher` |
| `auto_format_and_publish` | 自动完成本地构建与格式化，再继续调用 `content-publisher` |

平台内映射：

| 平台 | `auto_format_and_publish` 的内部动作 |
|------|--------------------------------------|
| `wechat` | 自动创建公众号草稿（`draft/add`），不直接群发 |
| `jike` | 直接调用即刻发布接口 |
| `xhs` / `zhihu` | 待平台实现后按能力映射 |

规则：
- 若 `delivery.platforms.{platform}.mode` 缺失，默认按 `auto_format` 处理
- 对 `wechat` 而言，`auto_format` 已包含 `markdown-to-wechat` 本地格式化
- 一旦工作区配置显式写入 `auto_format_and_publish`，后续 Stage 6 视为用户已授权该平台自动继续执行发布动作
- 进入 `auto_format_and_publish` 后，平台发布所需敏感信息统一由 `content-publisher` 通过 [`/secrets-vault` Skill](/Users/mileson/.cursor/skills/secrets-vault/SKILL.md) 获取
- 若某平台自动发布能力暂未接通，Stage 6 会降级为本地交付并记录 warning（`status = publish_skipped`）

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
