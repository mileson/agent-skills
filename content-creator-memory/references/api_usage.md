# API 使用手册 - API Usage Guide

本文档提供 content-creator-memory skill 的详细使用示例和最佳实践。

---

## 快速开始

### 1. 初始化索引（首次使用）

```bash
python3 ~/.cursor/skills/content-creator-memory/scripts/rebuild_index.py \
  --contents-dir ~/.cursor/skills/content-creator-memory/memories/contents/wechat \
  --examples-dir ~/.cursor/skills/content-creator-memory/memories/examples/wechat \
  --output-dir ~/.cursor/skills/content-creator-memory/data
```

**输出示例**:
```
🔍 开始扫描文件...
✓ 发现自有内容: 34 篇
✓ 成功提取: 34 篇自有内容
✓ 发现作者目录: 3 个
✓ 成功提取: 45 篇标杆案例

🔨 构建倒排索引...
✓ 倒排索引: 1234 个关键词

📊 计算 TF-IDF 分数...
✓ TF-IDF 计算完成: 79 个文档

💾 保存索引文件...
✓ 自有内容索引: data/own_works.json
✓ 标杆案例索引: data/reference_examples.json
✓ 搜索索引: data/search_index.json
✓ 元数据: data/metadata.json

✅ 索引重建完成！耗时: 12.3s
```

### 2. 搜索自有内容

```bash
python3 ~/.cursor/skills/content-creator-memory/scripts/search_content.py \
  --query "AI编程" \
  --top-k 3
```

**输出示例**:
```json
{
  "results": [
    {
      "id": "ai-app-in-1-day-case-study",
      "title": "我花1天时间，用 AI 开发出了一款排行榜第107名的产品",
      "file_path": ".cursor/skills/content-creator-memory/memories/contents/wechat/我花1天时间用AI开发出了一款排行榜第107名的产品.md",
      "relevance_score": 0.85,
      "quality_score": 9.2,
      "reusable_elements": {
        "golden_sentences": ["关键不是技术的深度，而是完成的速度。"],
        "core_workflows": ["AI产品命名流程", "AI编程调试三步法"]
      }
    },
    {
      "id": "ai-programming-deep-dive",
      "title": "万字长文深度解读：AI编程的工程化与技术突破",
      "relevance_score": 0.78,
      "quality_score": 9.5,
      ...
    }
  ],
  "total_found": 12,
  "search_time_ms": 45
}
```

---

## 常见使用场景

### 场景1: content-creator 阶段1（选题策划）

**需求**: 基于用户需求，检索相关的自有内容作为选题参考

```bash
# 提取用户需求的关键词
USER_QUERY="AI编程实战经验"

# 搜索自有内容
python3 search_content.py \
  --query "$USER_QUERY" \
  --top-k 3 \
  --min-quality 8.0
```

**如何使用结果**:
1. 提取 `reusable_elements.golden_sentences` 作为金句参考
2. 提取 `reusable_elements.core_workflows` 作为流程参考
3. 分析 `title` 和 `summary` 了解成功的选题角度

---

### 场景2: content-creator 阶段2（标题+大纲）

**需求**: 借鉴标杆案例的标题钩子技巧

```bash
# 搜索标杆案例
python3 search_reference.py \
  --query "标题钩子" \
  --filters "platform:wechat" \
  --top-k 2
```

**如何使用结果**:
1. 提取 `title_hooks` 了解标题技巧（数字钩子、情绪词汇等）
2. 参考 `structural_patterns` 了解文章结构模式
3. 借鉴 `expression_techniques` 优化表达方式

---

### 场景3: 新增内容后更新索引

**需求**: 发布新文章后，增量更新索引

```bash
# 增量添加新内容
python3 add_content.py \
  --file ~/.cursor/skills/content-creator-memory/memories/contents/wechat/新文章.md \
  --auto-extract
```

**输出示例**:
```
✓ 读取文件: 新文章.md
✓ 提取元数据: 新文章标题...
✓ 添加新条目: #35
✓ 保存自有内容索引: data/own_works.json
✓ 更新搜索索引...
✓ 保存搜索索引: data/search_index.json
✓ 更新元数据: data/metadata.json

✅ 增量添加完成！耗时: 1.2s
```

---

## 高级用法

### 1. 多条件过滤搜索

```bash
# 搜索特定受众 + 特定技术栈的内容
python3 search_content.py \
  --query "编程实战" \
  --filters "target_audience:独立开发者,technical_stack:Cursor" \
  --top-k 5 \
  --min-quality 7.0
```

### 2. 按作者过滤标杆案例

```bash
# 只搜索特定作者的案例
python3 search_reference.py \
  --query "产品开发" \
  --filters "author:AI产品黄叔" \
  --top-k 3
```

### 3. 程序化调用（Python）

```python
import subprocess
import json

def search_own_works(query: str, top_k: int = 3) -> dict:
    """搜索自有内容"""
    result = subprocess.run([
        "python3",
        "~/.cursor/skills/content-creator-memory/scripts/search_content.py",
        "--query", query,
        "--top-k", str(top_k),
        "--min-quality", "8.0"
    ], capture_output=True, text=True)
    
    return json.loads(result.stdout)

# 使用示例
results = search_own_works("AI编程", top_k=3)
for item in results["results"]:
    print(f"标题: {item['title']}")
    print(f"相关度: {item['relevance_score']}")
    print(f"质量分: {item['quality_score']}")
    print("---")
```

---

## 性能优化建议

### 1. 索引大小优化

**当前索引大小**（34篇自有内容 + 45篇标杆案例）:
- `own_works.json`: ~150KB
- `reference_examples.json`: ~120KB
- `search_index.json`: ~80KB
- 总大小: ~350KB

**优化建议**:
- 如果索引文件 >1MB，考虑拆分为多个文件
- 如果内容 >200篇，考虑按年份或分类拆分索引

### 2. 搜索性能优化

**当前性能**（79个文档）:
- 搜索耗时: ~50ms
- TF-IDF 计算: ~100ms

**优化建议**:
- 如果搜索耗时 >200ms，考虑引入缓存机制
- 如果索引重建耗时 >60s，考虑并行处理

---

## 常见问题 (FAQ)

### Q1: 如何提高搜索准确度？

**A**: 
1. 使用更具体的查询词（如"AI编程实战"而非"编程"）
2. 使用过滤条件缩小范围
3. 调高 `--min-quality` 阈值

### Q2: 如何手动标注字段？

**A**: 直接编辑 `data/own_works.json` 文件，补充以下字段：
- `target_audience`: 目标受众列表
- `technical_stack`: 技术栈列表
- `reusable_elements.golden_sentences`: 金句列表
- `reusable_elements.core_workflows`: 核心流程列表

### Q3: 如何删除某篇内容？

**A**: 
1. 直接从 `data/own_works.json` 中删除对应条目
2. 重新运行 `rebuild_index.py` 更新搜索索引

### Q4: 如何备份索引数据？

**A**:
```bash
# 备份整个 data/ 目录
cp -r ~/.cursor/skills/content-creator-memory/data \
     ~/.cursor/skills/content-creator-memory/data.backup.$(date +%Y%m%d)
```

---

## 集成示例

### 与 content-creator 集成

在 content-creator 的 SKILL.md 中，修改阶段1和阶段2的逻辑：

**原逻辑**:
```markdown
通过内容记忆系统检索...
```

**新逻辑**:
```markdown
# 调用 content-creator-memory API
python3 ~/.cursor/skills/content-creator-memory/scripts/search_content.py \
  --query "基于用户需求的关键词" \
  --top-k 3 \
  --min-quality 8.0

# 解析 JSON 结果，提取 reusable_elements
```

---

## 版本历史

### v1.0 (2026-02-04)

**功能**:
- ✅ 全量重建索引
- ✅ 增量添加内容
- ✅ 搜索自有内容（关键词+过滤+质量筛选）
- ✅ 搜索标杆案例（关键词+过滤）
- ✅ TF-IDF 相关度计算

**限制**:
- 手动标注字段（`target_audience`, `technical_stack`, `reusable_elements`）需人工补充
- 质量评分基于简单的字数公式，未接入 AI 评分

**未来计划**:
- v1.1: 接入 AI 自动标注（使用 Claude/GPT 提取元数据）
- v1.2: 支持语义搜索（基于 embedding）
- v1.3: 支持多平台索引（小红书、知乎等）
