# 图片智能配图工作流说明

> 本文档说明 content-creator 中的图片处理完整流程

## 📁 标准目录结构

```
[文章工作区]/
├── Materials/                  # 原始素材
│   └── origin.md              # 主素材文件
├── Medias/                    # 媒体资源 ⭐
│   └── images/                # 图片文件目录（标准位置）
│       ├── 01-preview.png
│       ├── 02-workflow.png
│       ├── 03-result.png
│       └── ...
└── Output/                    # 生成内容
    ├── _drafts/
    │   └── 04_draft.md        # 图片已嵌入对应章节
    └── wechat/
        └── article.md         # 保持 Medias/images/ 路径
```

## 🔄 完整工作流程

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
- 图片目录: `/Users/xxx/my-article/Medias/images`
- 目录存在: ✅ 是
- 图片总数: **5** 张

### 图片清单
1. `Medias/images/01-preview.png` (序号: 01) [关键词: preview]
2. `Medias/images/02-workflow.png` (序号: 02) [关键词: workflow]
3. `Medias/images/03-result.png` (序号: 03) [关键词: result]
4. `Medias/images/04-detail.png` (序号: 04) [关键词: detail]
5. `Medias/images/cover.jpg` [关键词: cover]
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
     ![主界面预览](Medias/images/01-preview.png)
     *▲ 简洁的主界面设计*
  6. 继续写后续内容
```

**标准格式**：

```markdown
## 第一章：快速上手指南

在开始使用这个工具之前，我想先带你看看它的界面。整个界面设计得非常简洁。

![工具主界面预览](Medias/images/01-preview.png)

*▲ 简洁的主界面设计，一目了然*

这个设计的核心理念就是：让你专注于核心功能。

接下来，我会教你如何配置...

![工具栏配置界面](Medias/images/02-toolbar-config.png)

*▲ 拖拽即可添加应用到工具栏*

配置完成后，你的工作效率会提升不少...
```

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

#### 步骤6.3：图片路径处理

| 平台 | 路径格式 | 说明 |
|-----|---------|------|
| **微信公众号** | `Medias/images/xxx.png` ⭐ | 保持原路径，供 markdown-to-wechat 上传 |
| **小红书** | `./images/xxx.png` | 复制到 Output/xhs/images/ |
| **知乎** | `./images/xxx.png` | 复制到 Output/zhihu/images/ |

**微信公众号特殊处理**：

```markdown
# Output/wechat/article.md 中保持原路径
![工具主界面](Medias/images/01-preview.png)

*▲ 主界面设计*
```

**原因**：markdown-to-wechat skill 会自动：
1. 检测 `Medias/images/` 路径
2. 调用 markdown-image-uploader 上传到阿里云 OSS
3. 替换为 CDN URL
4. 生成最终 HTML

---

## 🛠️ 工具使用指南

### scan_images.py 详细说明

**功能**：扫描工作区的 `Medias/images/` 目录，输出图片清单

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
      "path": "/Users/xxx/my-article/Medias/images/01-preview.png",
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
| `cover.jpg` | null | cover | 开篇封面 |
| `screenshot-03.png` | 3 | screenshot | 第3章节 |

---

## ✅ 质量检查清单

### 阶段3检查（写作剧本）

- [ ] 已运行 scan_images.py 工具？
- [ ] 所有图片都已匹配到章节？
- [ ] 每个章节的配图指令包含完整路径（`Medias/images/xxx.ext`）？
- [ ] 没有单独创建"配图方案"章节？

### 阶段4检查（写作执行）

- [ ] 图片已嵌入到对应章节内（不是最后）？
- [ ] 每张图片都紧跟相关描述段落？
- [ ] 所有扫描到的图片都已使用（没有遗漏）？
- [ ] 图片路径格式正确（`Medias/images/xxx.ext`）？
- [ ] 每张图片都有 alt 文本和图注？

### 阶段6检查（多平台适配）

- [ ] 微信公众号版本保持 `Medias/images/` 路径？
- [ ] 其他平台已复制图片到对应目录？
- [ ] 图片路径已根据平台规则调整？

---

## 🔗 相关文档

- [workflow-stages.md](workflow-stages.md) - 完整6阶段执行流程
- [markdown-to-wechat skill](../../markdown-to-wechat/SKILL.md) - 微信转换工具
- [troubleshooting.md](troubleshooting.md) - 常见问题排查

---

## 📝 常见问题

### Q1: 为什么图片要放在 Medias/images/ 而不是 Materials/images/？

**A**: 
- `Materials/` - 原始素材（Markdown 文件）
- `Medias/` - 媒体资源（图片、视频等）

这样分离是为了清晰区分文本内容和媒体资源。

### Q2: 为什么 Markdown 引用路径是 `Medias/images/` 而不是相对路径？

**A**: 这是为了兼容 markdown-to-wechat skill，该工具支持以下格式：
- ✅ `Medias/images/01.png`
- ✅ `images/01.png`
- ✅ `Output/wechat/images/01.png`
- ❌ `./images/01.png`（不支持）

### Q3: 如果 Medias/images/ 目录不存在怎么办？

**A**: scan_images.py 会输出错误信息：
```
❌ 错误: 图片目录不存在: /path/to/Medias/images
```

Agent 应该：
- 标记：本文无配图
- 在写作剧本中注明"无配图"
- 继续执行后续步骤

### Q4: 图片文件名有什么命名规范吗？

**A**: 推荐使用以下格式：
- `01-preview.png` - 带序号，方便自动匹配章节
- `02-workflow.png` - 关键词描述图片内容
- `cover.jpg` - 特殊用途图片用描述性名称

**避免**：
- `IMG_1234.png` - 无意义命名
- `屏幕截图 2024.png` - 包含中文和空格

---

**最后更新**: 2026-02-04
**维护者**: content-creator skill
