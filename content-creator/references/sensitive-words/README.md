# 敏感词检查模块使用说明

> 为各平台内容提供敏感词检测和合规性检查

## 📋 功能概述

本模块在**阶段6：多平台适配**的**步骤5**中自动执行，为生成的平台内容进行敏感词检测，确保内容合规。

## 🎯 检测流程

### 1. 自动触发时机

在阶段6的步骤4（平台内容生成）完成后，自动进入步骤5：

```
步骤4：平台内容生成 ✓
    ↓
步骤5：平台内容合规检查 ⭐
    ├─ 读取平台敏感词库
    ├─ 扫描生成的内容
    ├─ 检测敏感词
    ├─ 生成检测报告
    └─ 提供替代建议
    ↓
步骤6：生成配套文件
```

### 2. 检测逻辑

对每个目标平台：

```
1. 检查敏感词库是否存在
   ├─ 存在 references/sensitive-words/{platform_id}.md
   │   └─ 读取词库，执行检测
   └─ 不存在
       └─ 跳过检测，记录日志

2. 扫描平台内容
   ├─ 读取 Output/{platform}/article.md
   ├─ 标题检测
   ├─ 正文检测（逐段）
   └─ 图片说明检测

3. 生成检测报告
   ├─ Output/{platform}/compliance-report.json
   └─ 记录所有检测到的敏感词及位置

4. 用户交互
   ├─ 展示检测结果和替代建议
   ├─ 选项1：[Y] 自动替换
   ├─ 选项2：[N] 手动修改
   └─ 选项3：[S] 跳过检查（标记警告）
```

## 📁 敏感词库结构

```
references/sensitive-words/
├── README.md（本文件）
├── xhs.md（小红书敏感词库）✅
├── wechat.md（微信公众号敏感词库）📝 待添加
├── zhihu.md（知乎敏感词库）📝 待添加
└── template.md（新平台词库模板）
```

### 平台ID映射

| 平台名称 | platform_id | 敏感词库文件 | 状态 |
|---------|-------------|-------------|------|
| 小红书 | `xhs` | `xhs.md` | ✅ 已有 |
| 微信公众号 | `wechat` | `wechat.md` | 📝 待添加 |
| 知乎 | `zhihu` | `zhihu.md` | 📝 待添加 |
| 即刻 | `jike` | `jike.md` | 📝 待添加 |
| Twitter | `twitter` | `twitter.md` | 📝 待添加 |
| LinkedIn | `linkedin` | `linkedin.md` | 📝 待添加 |
| 抖音 | `douyin` | `douyin.md` | 📝 待添加 |
| 哔哩哔哩 | `bilibili` | `bilibili.md` | 📝 待添加 |
| Instagram | `instagram` | `instagram.md` | 📝 待添加 |

## 📄 检测报告格式

生成的 `compliance-report.json` 包含：

```json
{
  "platform": "xhs",
  "scan_time": "2026-02-04T10:30:00Z",
  "detected_sensitive_words": [
    {
      "word": "第一",
      "category": "极限用语类 > 绝对化表述",
      "position": "标题",
      "line_number": 1,
      "original_text": "第一次用AI写文章",
      "suggestion": "推荐替换为：初次用AI写文章",
      "risk_level": "high"
    },
    {
      "word": "最好",
      "category": "极限用语类 > 最高级表述",
      "position": "正文第3段",
      "line_number": 12,
      "original_text": "这款产品最好用",
      "suggestion": "推荐替换为：这款产品很好用",
      "risk_level": "medium"
    }
  ],
  "total_issues": 2,
  "risk_level": "high",
  "compliance_status": "需要修改"
}
```

### 风险等级定义

| 风险等级 | 说明 | 检测到的敏感词类型 |
|---------|------|------------------|
| `critical` | 严重 | 政治敏感、色情低俗、违法内容 |
| `high` | 高风险 | 极限用语、医疗用语、虚假宣传 |
| `medium` | 中风险 | 点击诱导、刺激消费、引流导流 |
| `low` | 低风险 | 拉踩行为、诱导互动 |

### 合规状态

| 状态 | 说明 |
|-----|------|
| `通过` | 未检测到敏感词 |
| `警告` | 检测到低风险敏感词，建议修改 |
| `需要修改` | 检测到中高风险敏感词，必须修改 |
| `严重违规` | 检测到严重敏感词，禁止发布 |

## 🔧 用户交互流程

### 场景1：检测到敏感词

```
⚠️ 小红书版本检测到 3 个敏感词（高风险）：

【标题】
❌ "第一次用AI写文章" 
   问题：包含极限用语"第一"
   建议：初次用AI写文章

【正文】
❌ "这款产品最好用"（第3段）
   问题：包含极限用语"最好"
   建议：这款产品很好用

❌ "一周减肥10斤"（第5段）
   问题：包含医疗用语"减肥"
   建议：一周塑形管理身材

选项：
1. [Y] 自动替换为建议词汇
2. [N] 我手动修改
3. [S] 跳过检查，继续发布（不推荐）

请选择（Y/N/S）：
```

### 场景2：未检测到敏感词

```
✅ 小红书版本通过合规检查
   未检测到敏感词，可以安全发布

继续生成配套文件...
```

### 场景3：平台无敏感词库

```
ℹ️ 知乎平台暂无敏感词库
   跳过合规检查，已记录日志

提示：如需检查，请添加 references/sensitive-words/zhihu.md

继续生成配套文件...
```

## 🛠️ 添加新平台敏感词库

### 步骤1：复制模板

```bash
cp references/sensitive-words/template.md references/sensitive-words/新平台ID.md
```

### 步骤2：编辑敏感词库

按照模板格式，填写该平台的敏感词分类和替代建议。

### 步骤3：测试

在阶段6生成该平台内容时，自动触发检测。

## 📚 参考资料

- **小红书敏感词库**: [xhs.md](xhs.md)
- **新平台模板**: [template.md](template.md)
- **平台规则库**: `templates/platform_styles_lib.json`

## ⚙️ 技术实现

### 检测算法

```python
def check_sensitive_words(article_text, platform_id):
    # 1. 读取敏感词库
    sensitive_words = load_sensitive_words(f"references/sensitive-words/{platform_id}.md")
    
    # 2. 逐词检测
    detected = []
    for category, words in sensitive_words.items():
        for word in words:
            if word in article_text:
                position = find_position(article_text, word)
                detected.append({
                    "word": word,
                    "category": category,
                    "position": position,
                    "suggestion": get_suggestion(word)
                })
    
    # 3. 生成报告
    report = generate_report(detected, platform_id)
    return report
```

### 自动替换逻辑

```python
def auto_replace(article_path, detected_words):
    content = read_file(article_path)
    
    for item in detected_words:
        original = item["original_text"]
        suggestion = extract_suggestion(item["suggestion"])
        content = content.replace(original, suggestion, 1)
    
    write_file(article_path, content)
    return True
```

## ❓ 常见问题

### Q1: 如何更新敏感词库？

直接编辑 `references/sensitive-words/{platform_id}.md`，下次执行时自动生效。

### Q2: 检测到的敏感词是否准确？

敏感词库基于平台最新规则整理，但平台规则可能随时更新，建议：
- 定期检查平台官方公告
- 根据实际审核情况调整词库

### Q3: 自动替换会影响文章质量吗？

自动替换使用敏感词库中的"替代建议"，已优化为语义接近的词汇。但建议：
- 替换后人工复查
- 确保语句通顺

### Q4: 跳过检查有什么后果？

选择"跳过检查"会：
- 在 `metadata.json` 中标记 `compliance_warning: true`
- 在 `publish-checklist.md` 中添加警告提示
- 不影响内容生成流程，但发布后可能被平台限流

---

**Made with ❤️ by 超级峰 | Powered by Cursor AI**
