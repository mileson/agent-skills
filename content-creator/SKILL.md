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
- 📱 一键适配多个发布平台（小红书、微信公众号、知乎等）
- 🔄 完整的工作流管理（从素材到发布）
- ⭐ 自动化的内容质量评分和优化建议
- 🔍 **平台敏感词检查**（新增⭐）：自动检测并提供替代建议
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

### 📦 Skill 目录结构

```
~/.cursor/skills/content-creator/
├── templates/                          # 静态工作流模板
│   ├── platform_styles_lib.json       # 9大平台样式规则
│   └── quality-scoring-model.md       # 爆款内容评分模型
└── references/                         # 详细文档
    ├── workflow-stages.md              # 6阶段详细说明 ⭐
    ├── configurations.md               # 配置文件说明 ⭐
    ├── best-practices.md               # 最佳实践 ⭐
    ├── troubleshooting.md              # 故障排查 ⭐
    └── sensitive-words/                # 敏感词检查模块 ⭐
        ├── README.md                   # 使用说明
        ├── xhs.md                      # 小红书敏感词库
        └── template.md                 # 新平台模板
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
    │   ├── 02_titles_and_outline.md
    │   ├── 03_writing_plan.md
    │   ├── 04_draft.md
    │   ├── 05_quality_score_v1.md
    │   └── 05_draft_optimized_v2.md（如需优化）
    ├── xhs/                   # 小红书版本
    │   ├── article.md
    │   ├── metadata.yaml ⭐
    │   ├── compliance-report.json ⭐
    │   └── images/
    ├── wechat/                # 微信公众号版本
    │   ├── article.md
    │   ├── metadata.yaml ⭐
    │   └── images/
    └── _reports/              # 质量报告（可选）
```

---

## 📋 完整工作流（6个阶段）

| 阶段 | 名称 | 目标 | 输出 | 用户确认 | 详细说明 |
|:---:|:-----|:-----|:-----|:-------:|:--------|
| **0** | 素材提取 | 提取结构化元数据 | `00_extracted_meta.yaml` | ✅ 需要 | [workflow-stages.md#阶段0](references/workflow-stages.md#阶段0素材提取与认知校正) |
| **1** | 选题策划 | 生成3个选题方案 | `01_topic_proposals.md` | ✅ 需要 | [workflow-stages.md#阶段1](references/workflow-stages.md#阶段1选题策划) |
| **2** | 标题大纲 | 5个标题+详细大纲 | `02_titles_and_outline.md` | ✅ 需要 | [workflow-stages.md#阶段2](references/workflow-stages.md#阶段2标题大纲生成) |
| **3** | 写作剧本 | 可执行写作指令 | `03_writing_plan.md` | ✅ 需要 | [workflow-stages.md#阶段3](references/workflow-stages.md#阶段3写作剧本生成) |
| **4** | 写作执行 | 生成完整初稿 | `04_draft.md` | ❌ 自动 | [workflow-stages.md#阶段4](references/workflow-stages.md#阶段4写作执行) |
| **5** | 评分优化 | 评分+优化（如<8分） | `05_quality_score_v1.md` | ❌ 自动 | [workflow-stages.md#阶段5](references/workflow-stages.md#阶段5爆款潜力评分与优化) |
| **6** | 多平台适配 | 各平台版本+敏感词检查⭐ | `xhs/`, `wechat/` | ⚠️ 敏感词 | [workflow-stages.md#阶段6](references/workflow-stages.md#阶段6多平台适配) |

### 核心特性

- **80/20 记忆策略**：80% 自有内容风格 + 20% 标杆技巧
- **质量自动优化**：<8 分自动触发优化
- **敏感词检查**：自动检测并提供替代建议（阶段6）
- **多平台一键适配**：支持 9 大平台（wechat, xhs, zhihu, jike, twitter, linkedin, douyin, bilibili, instagram）

📖 **完整执行步骤**: [references/workflow-stages.md](references/workflow-stages.md)

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

---

## 🚀 快速开始

### 步骤 1：准备工作区
```bash
mkdir "我的文章标题" && cd "我的文章标题"
mkdir -p Materials/Medias/images
echo "原始内容..." > Materials/origin.md
# 将图片文件放到 Materials/Medias/images/ 目录
```

### 步骤 2：执行 Skill
```
@content-creator 帮我创建一篇关于[主题]的文章，发布到[平台1]和[平台2]
```

### 步骤 3：配合确认
- 阶段0-3：确认元数据、选题、标题、剧本
- 阶段4-5：自动生成初稿并评分优化
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

### 2. 敏感词库
- **位置**：`references/sensitive-words/`
- **当前支持**：小红书（xhs.md）
- **功能**：自动检测、替代建议、生成报告
- 📖 [详细说明](references/sensitive-words/README.md)

### 3. 评分模型
- **位置**：`templates/quality-scoring-model.md`
- **体系**：观感(50分) + 视角(30分) + 场景(30分) + 本质(40分) = 150分 → 10分制
- **阈值**：≥8分通过，<8分自动优化
- 📖 [详细说明](templates/quality-scoring-model.md)

### 4. 内容记忆系统
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
| [troubleshooting.md](references/troubleshooting.md) | 常见问题解决方案 |
| [sensitive-words/README.md](references/sensitive-words/README.md) | 敏感词检测使用说明 |

---

## ⚠️ Important Notes

### 依赖检查（必需）
- [ ] content-creator-memory skill 已安装
- [ ] 内容记忆系统有自有内容（至少 5 篇）
- [ ] 内容记忆系统有标杆案例（至少 10 篇）

### 工作区要求（必需）
- [ ] Materials/origin.md（主素材，建议5000字+）
- [ ] 目标发布平台（在初始请求中明确）

### 平台限制
- **支持的平台**：wechat, xhs, zhihu, jike, twitter, linkedin, douyin, bilibili, instagram
- **敏感词检查**：当前仅支持小红书（xhs），其他平台跳过检查

---

## ✅ Output Checklist

完成后确认以下文件已生成：

### 中间产物（_drafts/）
- [ ] 00_extracted_meta.yaml、01_topic_proposals.md、02_titles_and_outline.md
- [ ] 03_writing_plan.md、04_draft.md
- [ ] 05_quality_score_v1.md（如需优化则有 v2 版本）

### 平台版本（各平台文件夹）
- [ ] article.md（平台适配版本）
- [ ] metadata.yaml ⭐（元数据，YAML 格式）
- [ ] compliance-report.json（敏感词检测报告，仅小红书等平台）
- [ ] images/（处理后的图片）

### 工作区文件
- [ ] workspace.config.yaml（状态为 "completed"）

---

## 🔗 相关资源

- ✅ 工作流模板：`content-creator/templates/`
- ✅ 参考文档：`content-creator/references/`
- ✅ 敏感词库：`content-creator/references/sensitive-words/`
- ✅ 记忆系统：`content-creator-memory`（配套 skill）

**扩展和自定义**（可选）：
- 添加更多自有作品/标杆案例到 content-creator-memory
- 使用 content-creator-memory 的管理工具重建索引
- 修改 `templates/platform_styles_lib.json` 自定义平台规则
- 添加新平台敏感词库到 `references/sensitive-words/{platform_id}.md`
