# content-creator Skill

AI内容创作自动化工作流 Skill，支持从素材到多平台发布的完整流程。

**✨ 完全自包含 | 零配置 | 开箱即用**

## 📁 目录结构

```
content-creator/
├── SKILL.md                          # Skill 主文档（完整说明）
├── README.md                         # 本文件（快速参考）
├── CHANGELOG.md                      # 版本更新日志
├── DEPENDENCIES.md                   # 依赖管理说明
├── templates/                        # 内置工作流模板 ⭐
│   ├── platform_styles_lib.json     # 9大平台样式规则
│   ├── article_creation.md          # 文章创作工作流模板
│   └── article_elements_extraction.md # 素材提取工作流模板
└── memories/                         # 内置记忆系统（核心资源）⭐⭐⭐
    ├── memory_indexing.json          # 80/20记忆策略配置（118KB）
    ├── knowledge_dict.json           # 认知校正词典（1.6KB）
    ├── contents/                     # 自有内容库（4篇精选作品）
    │   └── wechat/
    │       ├── 0 基础保姆教程，免费领取 AI 大模型资格证明.md
    │       ├── 万字长文深度解读：AI编程的工程化与技术突破.md
    │       ├── 别整天学 Cursor Rules 了，这个才是普通人强化 AI 的万能方法！.md
    │       └── 我花1天时间，用 AI 开发出了一款排行榜第107名的产品.md
    └── examples/                     # 标杆案例库（45篇行业精选）
        └── wechat/
            ├── AI产品黄叔/（11篇）
            ├── 数字生命卡兹克/（23篇）
            └── 花叔/（11篇）
```

### 📦 完全自包含（零外部依赖）

**✅ Skill 已打包所有资源**：
- 静态模板：3个工作流模板文件
- 核心配置：memory_indexing.json + knowledge_dict.json
- 自有内容库：4篇精选作品（contents/）
- 标杆案例库：45篇行业精选（examples/）

**🚀 开箱即用的优势**：
- 无需额外配置全局路径
- 无需克隆完整项目仓库
- 无需手动复制文件
- 下载即可使用

**📊 Skill 大小**：~840KB（包含所有资源）

## 🚀 快速开始

### 1. 准备工作区

```bash
mkdir "我的文章标题"
cd "我的文章标题"
mkdir Materials Medias/images
echo "原始内容..." > Materials/origin.md
```

### 2. 执行 Skill

```
@content-creator 帮我创建一篇关于[主题]的文章，发布到[平台1]和[平台2]
```

### 3. 配合确认

- ✅ 阶段1：确认选题方向（3选1）
- ✅ 阶段2：确认标题+大纲（5选1）
- ✅ 阶段3：确认写作剧本
- ✅ 阶段4：自动生成初稿
- ✅ 阶段5：自动评分+优化
- ✅ 阶段6：自动多平台适配

## 📊 工作流程

```
阶段0: 素材提取 → 00_extracted_meta.json
       ↓
阶段1: 选题策划 → 01_topic_proposals.md（3个方案）
       ↓
阶段2: 标题+大纲 → 02_titles_and_outline.md（5个标题）
       ↓
阶段3: 写作剧本 → 03_writing_plan.md
       ↓
阶段4: 写作执行 → 04_draft.md
       ↓
阶段5: 质量评分 → 05_quality_score_v1.md（如<8分自动优化）
       ↓
阶段6: 多平台适配 → Output/xhs/, Output/wechat/, ...
```

## 🎯 支持的平台

- ✅ 微信公众号（wechat）
- ✅ 小红书（xhs）
- ✅ 知乎（zhihu）
- ✅ 即刻（jike）
- ✅ Twitter/X（twitter）
- ✅ LinkedIn（linkedin）
- ✅ 抖音（douyin）
- ✅ 哔哩哔哩（bilibili）
- ✅ Instagram（instagram）

## 📦 完全自包含（无需外部配置）

本 Skill 已打包所有必需资源，**无需配置全局路径或克隆项目仓库**：

```
✅ 所有资源已内置到 Skill：
└── ~/.cursor/skills/content-creator/
    ├── templates/          # 静态工作流模板
    └── memories/           # 完整的记忆系统
        ├── memory_indexing.json（118KB）
        ├── knowledge_dict.json（1.6KB）
        ├── contents/wechat/（4篇自有作品）
        └── examples/wechat/（45篇标杆案例）
```

**扩展和自定义**（可选）：
- 添加更多自有作品：`memories/contents/wechat/`
- 添加更多标杆案例：`memories/examples/wechat/`
- 更新索引：编辑 `memories/memory_indexing.json`
- 自定义平台规则：编辑 `templates/platform_styles_lib.json`

## 🔧 核心特性

### 1. 80/20记忆策略
- 80%挖掘自有内容风格
- 20%借鉴标杆案例技巧
- 智能检索和风格融合

### 2. 爆款潜力评分系统
- 观感分析法（好奇心、颠覆性、技术力、新鲜感、沉浸感）
- 视角分析法（初级开发者、产品经理、行业人）
- 场景分析法（可比性、社交动机、用户思考）
- 本质分析法（节约时间/金钱、心理/金钱收获）
- 总分<8.0自动优化

### 3. 工作区感知
- 自动检测Materials/、Medias/
- 智能创建Output/目录结构
- 按平台维度组织输出
- 完整的中间产物追踪

### 4. 多平台自动适配
- 自动裁剪压缩图片
- 应用平台特定格式规则
- 生成metadata.json
- 创建publish-checklist.md

## 📝 输出文件清单

### 中间产物（Output/_drafts/）
- `00_extracted_meta.json` - 素材提取
- `01_topic_proposals.md` - 选题策划（3个方案）
- `02_titles_and_outline.md` - 标题+大纲（5个标题）
- `03_writing_plan.md` - 写作剧本
- `04_draft.md` - 通用初稿
- `05_quality_score_v1.md` - 首次评分
- `05_draft_optimized_v2.md` - 优化版（如需）
- `05_quality_score_v2.md` - 二次评分（如需）
- `05_optimization_history.json` - 优化历史

### 平台输出（Output/[platform]/）
每个平台包含：
- `article.md` - 平台版本文章
- `metadata.json` - 平台元数据
- `publish-checklist.md` - 发布检查清单
- `images/` - 处理后的图片

### 质量报告（Output/_reports/）
- `seo-analysis.json` - SEO分析
- `readability-score.json` - 可读性评分
- `platform-compliance.json` - 平台合规性

## 🎓 使用示例

### 示例1：创建技术教程

```
@content-creator 帮我创建一篇关于"使用Cursor开发iOS App"的技术教程，发布到微信公众号和知乎
```

### 示例2：创建产品评测

```
@content-creator 基于Materials/文件夹的素材，生成一篇AI工具对比评测，发布到小红书
```

### 示例3：创建经验分享

```
@content-creator 帮我写一篇"从0到1独立开发的经验分享"，发布到小红书、微信公众号和知乎
```

## ⚠️ 常见问题

### Q1: 提示"资源文件损坏或缺失"？
**A**: Skill 资源可能不完整。解决方案：
```bash
# 检查 memories/ 目录
ls ~/.cursor/skills/content-creator/memories/

# 重新安装 Skill（推荐）
# 或从备份恢复 memories/ 目录
```

### Q2: 评分一直低于8分？
**A**: 检查素材质量，补充具体案例、数据、故事。参考评分报告的改进建议。

### Q3: 平台适配后风格不对？
**A**: 检查 `templates/platform_styles_lib.json` 配置，参考 `memories/examples/wechat/` 中的标杆案例。

### Q4: 工作流中断如何恢复？
**A**: 检查 `workspace.config.json` 的 `generation_status`，重新调用 Skill 并说明从哪个阶段开始。

## 📚 详细文档

完整的使用说明、配置指南、最佳实践、故障排查，请参考：
- `SKILL.md` - 完整 Skill 文档（必读）
- `DEPENDENCIES.md` - 依赖管理和资源说明
- `CHANGELOG.md` - 版本更新历史

## 🔗 Skill 内置资源

本 Skill 完全自包含，所有资源已内置：
- ✅ 工作流模板：`~/.cursor/skills/content-creator/templates/`
- ✅ 记忆系统配置：`~/.cursor/skills/content-creator/memories/`
- ✅ 自有内容库：`~/.cursor/skills/content-creator/memories/contents/`
- ✅ 标杆案例库：`~/.cursor/skills/content-creator/memories/examples/`

---

**Version**: v1.0.0
**Created**: 2025-01-24
**Author**: 超级峰
**Powered by**: Cursor AI
**Package Size**: ~840KB (完全自包含)
