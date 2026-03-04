# 图片智能配图工作流说明

> 本文档说明 content-creator 中的图片处理完整流程

## 📁 标准目录结构

```
[文章工作区]/
├── Materials/                  # 原始素材
│   ├── origin.md              # 主素材文件
│   └── Medias/                # 媒体资源 ⭐
│       └── images/            # 图片文件目录（标准位置）
│           ├── 01-preview.png
│           ├── 02-workflow.png
│           ├── 03-result.png
│           ├── cover-wechat.jpg
│           ├── cover-jike.jpg
│           ├── cover-twitter.jpg
│           └── ...
└── Output/                    # 生成内容
    ├── _drafts/
    │   └── 04_draft.md        # 图片已嵌入对应章节
    ├── wechat/
    │   ├── article.md         # 阶段6清洗后的最终版本
    │   ├── metadata.yaml      # 平台元数据（YAML格式）
    │   └── images/            # 复制的图片文件
    └── xhs/
        ├── article.md
        ├── metadata.yaml
        ├── compliance-report.json  # 敏感词检测报告
        └── images/
```

## 🔄 完整工作流程

### 平台级封面图规则（2026-03 新增）

封面图不再统一使用单一 `cover.jpg`，而是改为平台专属源文件：

| 平台 | Materials 源文件 | 正文占位形式 | 默认比例 |
|-----|------------------|--------------|----------|
| wechat | `cover-wechat.jpg` | `inline_markdown` | `21:9` |
| jike | `cover-jike.jpg` | `header_comment` | `1:1` |
| twitter | `cover-twitter.jpg` | `header_comment` | `4:5` |

说明：
- `inline_markdown`：封面图占位直接写在文章头部。
- `header_comment`：只在文章头部保留 `<!-- AI封面图 ... -->` 注释，不往正文插图。
- 输出到 `Output/{platform}/images/` 时统一重命名为 `cover.jpg` 或 `cover.{ext}`，便于发布工具读取。

### 阶段3：写作剧本生成

#### 步骤3.1：扫描图片资源（必须执行）⭐⭐⭐

```bash
# Agent 必须运行此工具
python3 ~/.cursor/skills/content-creator/scripts/scan_images.py [工作区路径] markdown
```

**输出示例**：
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
```

**⚠️ 关键规则**：
- ✅ 必须遍历所有图片（不要遗漏）
- ✅ 使用工具输出的 `Medias/images/` 格式
- ✅ 分析图片序号和关键词，智能匹配到章节

#### 步骤3.2：生成写作指令（直接包含图片）

**正确做法**：在每个章节的写作指令中直接指定图片路径

```markdown
## 写作待办事项

- [ ] 1.2 撰写章节一：快速上手指南
    - **指令**：介绍工具的主界面和核心功能
    - **配图**：在描述"主界面布局"时，嵌入 `Medias/images/01-preview.png`
    - **图片位置**：紧跟"界面设计很简洁"这段描述之后

- [ ] 1.3 撰写章节二：核心功能
    - **指令**：解释工具的核心流程
    - **配图**：在解释流程步骤时，嵌入 `Medias/images/02-workflow.png`
    - **图片位置**：插入到流程说明段落之后
```

**禁止做法**❌：
```markdown
## 图片配图方案  ← ❌ 不要单独创建配图方案章节
1. 章节1 → Medias/images/01.png
2. 章节2 → Medias/images/02.png
```

---

### 阶段4：写作执行

#### 步骤4.1：逐章节写作（严格嵌入图片）⭐⭐⭐

**执行流程**：

```
for each 章节:
  1. 读取章节写作指令
  2. ⭐ 检查是否有配图指令（必查！）
  3. 写开头段落
  4. 写核心描述段落
  5. ⭐ 立即嵌入图片（不要延后！）
     ![简洁的主界面设计](Medias/images/01-preview.png)
  6. 继续写后续内容
```

**标准格式**：

```markdown
## 第一章：快速上手指南

在开始使用这个工具之前，我想先带你看看它的界面。整个界面设计得非常简洁。

![简洁的主界面设计，一目了然](Medias/images/01-preview.png)

这个设计的核心理念就是：让你专注于核心功能。

接下来，我会教你如何配置...

![拖拽即可添加应用到工具栏](Medias/images/02-toolbar-config.png)

配置完成后，你的工作效率会提升不少...
```

> ⚠️ 图注只写在 `caption` 中，不要把 AI 生图提示词直接写进 alt，也不要另起 `*▲ ...*` 行（markdown-to-wechat 会自动将最终 alt 渲染为 figcaption，另写会重复）

**禁止做法**❌：

```markdown
## 第一章：快速上手指南
[所有内容...]

---
**[图片:配图建议]**  ← ❌ 禁止！
- 第一章：Medias/images/01-preview.png
```

---

### 阶段6：多平台适配

#### 步骤6.3：图片路径处理与发布稿清洗

| 平台 | 路径格式 | 说明 |
|-----|---------|------|
| **图文混排型平台** | `images/xxx.png` ⭐ | 通过 `sanitize_output_markdown.py` 从 draft 统一转换 |
| **图文分离型平台** | 无正文图片语法 | `article.md` 通过脚本删除正文图片占位 |
| **视觉优先平台的 image_plan.md** | `Materials/Medias/images/xxx.png` | 保留为图片执行主文件，不在此阶段清理截图指引 |

**推荐工作流**：

```markdown
# Output/wechat/article.md 中使用相对路径
![主界面设计](images/01-preview.png)
```

**原因**：`content-creator` 在阶段6默认先复制图片，再调用 `sanitize_output_markdown.py`：
1. 删除 `> 💡 **截图指引**：...` 这类作者辅助标记
2. 将 `Medias/images/` 或 `Materials/Medias/images/` 统一改写为 `images/`
3. 输出更干净的 `Output/{platform}/article.md`
4. 再交给 `markdown-to-wechat` 或发布工具继续处理

---

## 🛠️ 工具使用指南

### scan_images.py 详细说明

**功能**：扫描工作区的 `Materials/Medias/images/` 目录，输出图片清单

**调用方式**：

```bash
# JSON 格式输出
python3 ~/.cursor/skills/content-creator/scripts/scan_images.py /path/to/workspace json

# Markdown 格式输出（推荐）
python3 ~/.cursor/skills/content-creator/scripts/scan_images.py /path/to/workspace markdown
```

**输出字段说明**：

```json
{
  "workspace": "/Users/xxx/my-article",
  "images_dir": "/Users/xxx/my-article/Medias/images",
  "exists": true,
  "total_images": 5,
  "images": [
    {
      "filename": "01-preview.png",
      "path": "/Users/xxx/my-article/Materials/Medias/images/01-preview.png",
      "markdown_path": "Medias/images/01-preview.png",
      "sequence": 1,
      "keyword": "preview",
      "size": 1048576,
      "extension": ".png"
    }
  ]
}
```

**语义提取规则**：

| 文件名 | 序号 | 关键词 | 匹配建议 |
|-------|-----|-------|---------|
| `01-preview.png` | 1 | preview | 第1章节 |
| `02-workflow.png` | 2 | workflow | 第2章节（流程相关） |
| `cover-wechat.jpg` | null | cover-wechat | 微信公众号头部封面 |
| `screenshot-03.png` | 3 | screenshot | 第3章节 |

---

## ✅ 质量检查清单

### 阶段3检查（写作剧本）

- [ ] 已运行 scan_images.py 工具？
- [ ] 所有图片都已匹配到章节？
- [ ] 每个章节的配图指令包含完整路径（`Medias/images/xxx.png`，以实际扫描到的扩展名为准）？
- [ ] 没有单独创建"配图方案"章节？

### 阶段4检查（写作执行）

- [ ] 图片已嵌入到对应章节内（不是最后）？
- [ ] 每张图片都紧跟相关描述段落？
- [ ] 所有扫描到的图片都已使用（没有遗漏）？
- [ ] 图片路径格式正确（`Medias/images/xxx.png`，以实际扫描到的扩展名为准）？
- [ ] 每张图片都有 `caption`（最终图注，推荐 4-10 个字）？
- [ ] 没有另起 `*▲ ...*` 斜体行？

### 阶段6检查（多平台适配）

- [ ] 阶段6 已优先调用 `sanitize_output_markdown.py`？
- [ ] 图文混排型平台的 `article.md` 已转换为 `images/xxx.png` 路径？
- [ ] 其他平台已复制图片到对应目录？
- [ ] `article.md` 中已移除 `> 💡 **截图指引**：...`？
- [ ] 图文分离型平台的 `article.md` 已移除正文图片占位？

---

## 🔗 相关文档

- [workflow-stages.md](workflow-stages.md) - 完整6阶段执行流程
- [markdown-to-wechat skill](../../markdown-to-wechat/SKILL.md) - 微信转换工具
- [troubleshooting.md](troubleshooting.md) - 常见问题排查

---

## 📝 常见问题

### Q1: 为什么图片要放在 Materials/Medias/images/ 这个嵌套结构？

**A**: 
- `Materials/` - 所有输入素材的根目录
  - `origin.md` - 文本素材
  - `Medias/images/` - 媒体资源（图片、视频等）

这样的嵌套结构是为了将所有输入素材统一管理在 `Materials/` 目录下，便于整体移动和备份。

### Q2: 为什么 Markdown 引用路径是 `Medias/images/` 而不是相对路径？

**A**: 这是为了兼容 markdown-to-wechat skill，该工具支持以下格式：
- ✅ `Medias/images/01.png`
- ✅ `images/01.png`
- ✅ `Output/wechat/images/01.png`
- ❌ `./images/01.png`（不支持）

### Q3: 如果 Materials/Medias/images/ 目录不存在怎么办？

**A**: scan_images.py 会输出错误信息：
```
❌ 错误: 图片目录不存在: /path/to/Materials/Medias/images
```

Agent 应该：
- 标记：本文无配图
- 在写作剧本中注明"无配图"
- 继续执行后续步骤

### Q4: 图片文件名有什么命名规范吗？

**A**: 推荐使用以下格式：
- `01-preview.png` - 带序号，方便自动匹配章节
- `02-workflow.png` - 关键词描述图片内容
- `cover-wechat.jpg` - 平台封面源图使用 `cover-{platform}.jpg` 形式命名

**避免**：
- `IMG_1234.png` - 无意义命名
- `屏幕截图 2024.png` - 包含中文和空格

---

**最后更新**: 2026-02-04
**维护者**: content-creator skill
