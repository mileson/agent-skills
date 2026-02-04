# 故障排查指南

> 常见问题的诊断和解决方案

---

## 问题1：提示"Memories目录不存在"

### 症状

```
❌ 错误：Skill 资源文件损坏

缺少必需文件：
- ~/.cursor/skills/content-creator-memory/memories/
```

### 原因

- Skill 内置资源损坏或缺失
- content-creator-memory skill 未安装

### 解决方案

```bash
# 1. 检查配套 Skill 完整性
ls ~/.cursor/skills/content-creator-memory/

# 2. 验证 content-creator-memory 是否正常
ls ~/.cursor/skills/content-creator-memory/memories/
ls ~/.cursor/skills/content-creator-memory/data/

# 3. 验证索引文件
ls ~/.cursor/skills/content-creator-memory/data/*.json

# 4. 如果文件缺失，重新安装两个 skills
# 或联系维护者获取完整版本
```

---

## 问题2：评分一直低于8分

### 症状

```
📊 总体评分: 6.5/10
⚠️ 需要优化后再发布

执行优化后：
📊 总体评分: 6.8/10 (仅提升0.3分)
```

### 原因

- 素材质量不足
- 选题角度问题
- 缺少吸引力元素

### 解决方案

**步骤1：检查评分报告**
```markdown
查看 05_quality_score_v1.md 的核心问题诊断
重点查看<6分的维度
```

**步骤2：分析低分原因**
```
新鲜感不足（5分）→ 缺少新颖角度
好奇心不足（4分）→ 缺少悬念/反差
金钱收获不足（3分）→ 未量化收益
```

**步骤3：针对性改进**
```
方案A：回到阶段1重新选择选题
方案B：补充更多具体案例、数据、故事到素材
方案C：调整标题，增强钩子
方案D：添加意外元素、制造反差
```

**步骤4：参考高分案例**
```bash
# 查看高分自有内容
@content-creator-memory 搜索自有内容 quality_score:>8

# 分析成功要素
- 标题钩子模式
- 开篇技巧
- 结构安排
```

---

## 问题3：平台适配后风格不对

### 症状

```
小红书版本：语调过于正式，缺少Emoji
微信公众号版本：错别字过多，不够专业
```

### 原因

- 平台规则未正确应用
- humanization 规则执行不当

### 解决方案

**步骤1：检查平台规则**
```bash
# 查看平台配置
cat templates/platform_styles_lib.json | grep -A 10 "\"id\": \"xhs\""
```

**步骤2：验证humanization规则**
```json
{
  "xhs": {
    "humanization": "每200字≥1错别字，避免过度正式，多用叹号和问号"
  },
  "wechat": {
    "humanization": "错别字≤3，保留专业术语"
  }
}
```

**步骤3：手动微调**
```bash
# 编辑平台版本
vi Output/xhs/article.md

# 调整语调、格式、Emoji等
```

**步骤4：参考标杆案例**
```bash
# 查看该平台的标杆案例
ls ~/.cursor/skills/content-creator-memory/memories/examples/wechat/
```

---

## 问题4：图片处理失败

### 症状

```
❌ 错误：无法处理图片 Medias/images/cover.jpg
原因：格式不支持
```

### 原因

- 图片格式不支持
- 图片尺寸过大或过小
- 文件损坏

### 解决方案

**步骤1：检查图片格式**
```bash
# 查看图片信息
file Medias/images/*.jpg
identify Medias/images/*.jpg  # 需安装 ImageMagick
```

**步骤2：转换格式**
```bash
# 转换为支持的格式（jpg/png/webp）
convert cover.heic cover.jpg  # HEIC → JPG
convert diagram.bmp diagram.png  # BMP → PNG
```

**步骤3：调整尺寸**
```bash
# 压缩大图片
convert cover.jpg -resize 1920x1080 cover-optimized.jpg

# 放大小图片（不推荐，建议使用原图）
convert icon.png -resize 1080x1080 icon-large.png
```

**步骤4：验证图片完整性**
```bash
# 检查图片是否损坏
identify -verbose Medias/images/*.jpg | grep -i error
```

---

## 问题5：工作流中断如何恢复

### 症状

```
执行到阶段3时AI会话断开
或因错误导致流程中断
```

### 原因

- AI 会话超时
- 网络连接中断
- 执行错误

### 解决方案

**步骤1：检查工作区状态**
```bash
# 查看 workspace.config.yaml
cat workspace.config.yaml | grep generation_status
```

**步骤2：确定恢复点**
```json
{
  "generation_status": "extraction_completed"  → 从阶段1开始
  "generation_status": "topic_selected"        → 从阶段2开始
  "generation_status": "outline_confirmed"     → 从阶段3开始
  "generation_status": "draft_completed"       → 从阶段5开始
  "generation_status": "scoring_completed"     → 从阶段6开始
}
```

**步骤3：恢复执行**
```
重新调用 Skill，说明：
"继续完成[工作区名称]的内容创作，从[阶段X]开始"

示例：
"继续完成'AI编程实战经验分享'的内容创作，从阶段3开始"
```

---

## 问题6：敏感词检测失败

### 症状

```
⚠️ 敏感词检测失败
原因：无法读取敏感词库
```

### 原因

- 敏感词库文件缺失
- 文件路径错误
- 文件格式错误

### 解决方案

**步骤1：检查敏感词库**
```bash
# 验证文件存在
ls references/sensitive-words/xhs.md
ls references/sensitive-words/wechat.md
```

**步骤2：检查文件格式**
```bash
# 确保是UTF-8编码
file -I references/sensitive-words/xhs.md

# 如果编码错误，转换
iconv -f GBK -t UTF-8 xhs.md > xhs-utf8.md
mv xhs-utf8.md xhs.md
```

**步骤3：添加缺失的敏感词库**
```bash
# 复制模板
cp references/sensitive-words/template.md references/sensitive-words/wechat.md

# 编辑并填写敏感词
vi references/sensitive-words/wechat.md
```

---

## 问题7：自动替换后语句不通顺

### 症状

```
原文："这是最好的解决方案"
自动替换后："这是优秀的解决方案" ❌（不够自然）
```

### 原因

- 替代词未考虑上下文
- 机械替换导致语义不连贯

### 解决方案

**步骤1：选择手动修改**
```
当检测到敏感词时：
选项：[N] 我手动修改
```

**步骤2：根据上下文调整**
```
原文："这是最好的解决方案"
手动修改：
  → "这是很好的解决方案"
  → "这是个不错的解决方案"
  → "这是我认为最合适的方案"
```

**步骤3：通读全文**
```
修改后通读全文，确保：
- 语句通顺
- 逻辑连贯
- 语义准确
```

---

## 问题8：生成内容被识别为AI

### 症状

```
发布后被平台标记为"AI生成内容"
或被限流
```

### 原因

- humanization 规则未执行
- 内容过于完美/正式
- 缺少真实体验细节

### 解决方案

**步骤1：检查humanization设置**
```yaml
# 确保在 extracted_meta.yaml 中配置了 humanization
humanization:
    "typos": "小红书每200字≥1错别字，微信≤3个",
    "informal_connectors": "避免'首先''其次'等正式连接词",
    "colloquial": "增加口语化表达",
    "punctuation": "不要破折号、冒号、双引号",
    "paragraph": "不要过度分行，采用自然段"

```

**步骤2：手动润色**
```
技巧1：增加口语化表达
  "该方法能够有效提升效率" 
  → "这招真的超有用"

技巧2：添加真实细节
  "经过测试，效果很好"
  → "我试了3天，第2天就看到明显变化"

技巧3：适量错别字
  "非常好用" → "非长好用"（小红书）

技巧4：减少正式连接词
  "首先...其次...最后..." 
  → "第一个方法是...还有一个..."
```

---

## 问题9：平台检测提示"需要添加敏感词库"

### 症状

```
ℹ️ 知乎平台暂无敏感词库
跳过合规检查，已记录日志
```

### 原因

- 该平台的敏感词库尚未创建

### 解决方案

**步骤1：创建敏感词库**
```bash
# 复制模板
cp references/sensitive-words/template.md references/sensitive-words/zhihu.md
```

**步骤2：收集敏感词**
```
方法1：参考平台官方规范
方法2：参考已有的 xhs.md
方法3：根据实际审核反馈添加
```

**步骤3：测试**
```
生成知乎版本时，自动触发检测
验证检测结果是否准确
```

---

## 问题10：记忆检索结果不准确

### 症状

```
80/20记忆校准时：
检索到的自有内容与当前主题不相关
标杆案例与期望风格差距大
```

### 原因

- 索引未更新
- 检索关键词不准确
- 内容分类不清晰

### 解决方案

**步骤1：重建索引**
```bash
# 使用 content-creator-memory skill
@content-creator-memory 重建索引
```

**步骤2：检查内容分类**
```bash
# 查看自有内容索引
cat ~/.cursor/skills/content-creator-memory/data/own_works.json

# 确认分类准确
{
  "target_audience": "初级开发者",
  "technical_stack": ["AI", "Python"],
  "quality_score": 8.5
}
```

**步骤3：优化检索策略**
```
在 extracted_meta.yaml 中明确：
- target_audience（更精准）
- technical_stack（更详细）
- primary_keywords（更相关）
```

---

## 调试技巧

### 1. 启用详细日志

```bash
# 检查中间产物
ls -lh Output/_drafts/

# 查看每个阶段的输出
cat Output/_drafts/00_extracted_meta.yaml
cat Output/_drafts/01_topic_proposals.md
cat Output/_drafts/05_quality_score_v1.md
```

### 2. 对比不同版本

```bash
# 对比优化前后
diff Output/_drafts/04_draft.md Output/_drafts/05_draft_optimized_v2.md
```

### 3. 验证配置文件

```bash
# 验证 JSON 格式
cat templates/platform_styles_lib.json | python3 -m json.tool

# 验证敏感词库格式
head -20 references/sensitive-words/xhs.md
```

---

## 获取帮助

如果以上方案无法解决问题：

1. **检查文档**：
   - [SKILL.md](../SKILL.md) - 核心流程
   - [configurations.md](configurations.md) - 配置说明
   - [best-practices.md](best-practices.md) - 最佳实践

2. **查看示例**：
   - 参考 content-creator-memory 的标杆案例
   - 参考成功的自有内容

3. **联系支持**：
   - 提供详细的错误信息
   - 提供 workspace.config.yaml
   - 提供中间产物文件
