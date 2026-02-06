# 更新日志

## v2.2 (2026-02-04) - 精简输出文件 ⭐

### 🗑️ 移除内容

#### 删除 publish-checklist.md

**原因**：
- 该文件为冗余辅助文件
- 发布提示已集成到 Agent 的工作流提示中
- 简化输出目录结构

**影响范围**：
- ✅ 移除所有生成 `publish-checklist.md` 的逻辑
- ✅ 清理文档中的所有相关描述
- ✅ 保持核心功能不变

**最终输出**（微信公众号示例）：
```
Output/wechat/
├── article.md         # 文章内容
├── metadata.yaml      # 元数据
└── images/            # 图片文件
```

### 📝 文档更新

1. `references/workflow-stages.md`
   - 步骤6.5：移除生成 `publish-checklist.md` 的描述
   - 步骤6.6：简化发布提示说明

2. `references/best-practices.md`
   - 移除"检查清单"推荐做法

3. `references/sensitive-words/README.md`
   - Q4：移除 `publish-checklist.md` 警告提示说明

4. `CHANGELOG.md`
   - 更新 v2.0 改进说明

---

## v2.1 (2026-02-04) - 图片路径兼容性修复 ⭐

### 🐛 Bug 修复

#### 图片路径找不到问题

**问题**：
- 实际图片位置：`Materials/Medias/images/xxx.png`
- 文章中的路径：`Medias/images/xxx.png`（少了 `Materials/`）
- 导致外部图片上传工具无法找到图片

**根本原因**：
- content-creator 默认为 markdown-to-wechat 优化（使用 `images/` 相对路径）
- 用户可能使用 markdown-image-uploader 等工具（需要 `Materials/Medias/images/` 路径）
- 两种工具对路径格式的要求不同

**解决方案**：
1. **明确两种工作流**：
   - 工作流A（推荐）：使用 markdown-to-wechat 一键处理
   - 工作流B（高级）：使用外部图片上传工具 + markdown-to-wechat

2. **在步骤6.7提供清晰的工作流选择提示**

3. **在 troubleshooting.md 添加问题4.5**：详细的诊断和解决方案

### 📝 文档更新

1. `references/workflow-stages.md`
   - 步骤6.3后增加"图片路径策略说明"章节
   - 更新步骤6.7，提供两种工作流的选择提示
   - 添加路径兼容性对照表

2. `references/troubleshooting.md`
   - 新增问题4.5："图片上传工具报错'找不到图片文件'"
   - 提供快速诊断清单
   - 提供两种解决方案

3. `QUICK_REFERENCE.md`
   - 添加"常见问题"章节
   - 快速链接到详细故障排查

### 🎯 最佳实践更新

**推荐工作流**：
```bash
# 默认使用 markdown-to-wechat（最简单）
@markdown-to-wechat Output/wechat/article.md
```

**高级工作流**（如需自定义图床）：
```bash
# 1. 从工作区根目录运行
cd "[工作区根目录]"

# 2. 使用外部工具上传图片
markdown-image-uploader Output/wechat/article.md -o Output/wechat/article_with_cdn.md

# 3. 转换为 HTML
@markdown-to-wechat Output/wechat/article_with_cdn.md
```

**预防措施**：
- ✅ 明确告知 Agent 要使用的工具
- ✅ 使用外部工具时，从工作区根目录运行
- ✅ 默认使用工作流A，除非有特殊需求

---

## v2.0 (2026-02-04) - 图片智能配图与输出优化

### 🆕 新增功能

#### 1. 图片智能配图系统

**新增工具**：`scripts/scan_images.py`
- ✅ 递归扫描 `Materials/Medias/images/` 所有层级的图片
- ✅ 自动提取图片序号和关键词
- ✅ 按子目录分组显示
- ✅ 输出两种引用格式（draft 和 article）

**工作流增强**：
- 阶段3：增加步骤3.1（扫描图片资源）
- 阶段4：增加步骤4.4（移除元数据信息）
- 强制要求图片嵌入到对应章节，禁止堆在文章最后

#### 2. 路径标准化

**统一标准**：
- 实际文件位置：`Materials/Medias/images/`（嵌套结构）
- draft.md 引用：`Medias/images/xxx.png`
- article.md 引用：`images/xxx.png`（相对路径）

**优势**：
- ✅ 每个平台目录自包含（文章+图片）
- ✅ 便于移动和分发
- ✅ 符合 markdown-to-wechat 相对路径优先原则

#### 3. 输出文件优化

**根据 skill-creator 最佳实践**：

**改进前**：
- ❌ metadata.json（JSON 格式）
- ❌ Output/README.md（辅助文档）
- ❌ 文章头部和结尾包含元数据

**改进后**：
- ✅ metadata.yaml（YAML 格式，更易读）
- ✅ 不生成 Output/README.md
- ✅ 文章干净无元数据信息

### 📝 文档更新

#### 更新的文件

1. `SKILL.md`
   - 更新工作区目录结构
   - 添加图片扫描工具说明
   - 更新 Output Checklist

2. `references/workflow-stages.md`
   - 阶段3：新增步骤3.1（扫描图片）
   - 阶段4：新增步骤4.4（移除元数据）
   - 阶段6：优化图片路径转换规则
   - 步骤6.6：改为生成 metadata.yaml
   - 步骤6.7：改为提示调用 markdown-to-wechat
   - 删除步骤6.9（不生成 README.md）

3. `references/best-practices.md`
   - 新增章节8：文章内容规范
   - 明确禁止在文章中添加元数据

4. `references/image-workflow.md`
   - 新增完整的图片工作流说明文档

5. `scripts/scan_images.py`
   - 支持递归扫描所有子目录
   - 输出两种引用格式
   - 按子目录分组显示

### 🎯 核心改进

#### 图片处理流程

```
阶段3 → 扫描图片 → 智能匹配到章节
         ↓
阶段4 → 写作时即时嵌入图片（Medias/images/ 格式）
         ↓
阶段6 → 复制图片到平台目录 + 转换路径（images/ 格式）
         ↓
用户 → 调用 markdown-to-wechat 上传图床 + 转换 HTML
```

#### 文章质量规范

**禁止内容**：
- ❌ 文章头部：作者署名、发布时间、分类标签
- ❌ 文章结尾：字数统计、生成信息、skill 信息、适合人群等

**正确做法**：
- ✅ 直接从标题开始
- ✅ 自然收尾（行动号召、总结等）
- ✅ 元数据记录在 metadata.yaml

#### 平台输出简化

| 平台 | article.md | metadata.yaml | compliance-report | images/ | 其他 |
|-----|-----------|--------------|------------------|---------|------|
| **微信** | ✅ | ✅ | ❌ | ✅ | 无 |
| **小红书** | ✅ | ✅ | ✅ | ✅ | 无 |
| **知乎** | ✅ | ✅ | ❌ | ✅ | 无 |

---

## v1.0 (2026-01-20) - 初始版本

### 核心功能

- ✅ 6阶段工作流
- ✅ 80/20 记忆策略
- ✅ 爆款评分模型
- ✅ 多平台适配
- ✅ 敏感词检查（小红书）

---

**维护者**: content-creator skill
**最后更新**: 2026-02-04
