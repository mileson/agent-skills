# 即刻动态导入指南

## 📊 导入概要

**导入时间**: 2026-02-05  
**动态数量**: 1025 条  
**时间跨度**: 2024-11-08 ~ 2026-01-26  
**索引状态**: ✅ 已完成

---

## 📁 文件组织

### 原始文件
- **路径**: `memories/contents/jike/archive/超级峰_即刻动态_20241108_20260126_1025条.md.backup`
- **状态**: 已归档（非索引）
- **大小**: 890KB (22865 行)

### 拆分后的文件
- **路径**: `memories/contents/jike/posts/`
- **数量**: 1025 个独立 Markdown 文件
- **命名格式**: `YYYY-MM-DD_postXXXX_圈子名称.md`

**示例文件名**:
```
2024-11-08_post0001_Chrome插件分享站.md
2024-11-10_post0002_随手拍张照.md
2024-11-20_post0003_这些社会新闻都是真的.md
```

---

## 🔧 导入流程

### 步骤1: 拆分大文件

使用 `split_jike_posts.py` 脚本:

```bash
python3 scripts/split_jike_posts.py \
  --input memories/contents/jike/超级峰_即刻动态_20241108_20260126_1025条.md \
  --output-dir memories/contents/jike/posts
```

**输出**:
- ✅ 发现 1026 条动态
- ✅ 成功生成 1025 个文件

### 步骤2: 归档原始文件

```bash
mkdir -p memories/contents/jike/archive
mv memories/contents/jike/超级峰_即刻动态_20241108_20260126_1025条.md \
   memories/contents/jike/archive/超级峰_即刻动态_20241108_20260126_1025条.md.backup
```

**重要**: 重命名为非 `.md` 后缀,避免被索引系统扫描。

### 步骤3: 重建索引

```bash
python3 scripts/rebuild_index.py \
  --contents-dir memories/contents \
  --examples-dir memories/examples \
  --output-dir data
```

**输出**:
- ✅ 自有内容: 1059 篇 (新增 1025 条即刻动态)
- ✅ 标杆案例: 70 篇
- ✅ 关键词: 4955 个
- ✅ 总文档: 1129 个
- ⏱️ 耗时: 0.6s

---

## 📈 索引统计

### 更新前后对比

| 指标 | 更新前 | 更新后 | 增量 |
|------|--------|--------|------|
| 自有内容 | 34 | 1059 | **+1025** |
| 标杆案例 | 70 | 70 | - |
| 关键词 | 571 | 4955 | **+4384** |
| 索引大小 | 222KB | 977KB | **+755KB** |

### 文件大小

```
own_works.json:         775KB
reference_examples.json: 49KB
search_index.json:      977KB
metadata.json:          149B
```

---

## 🔍 搜索验证

### 测试查询1: "Cursor 开发"

```bash
python3 scripts/search_content.py \
  --query "Cursor 开发" \
  --top-k 5 \
  --output-dir data
```

**结果**:
- ✅ 返回 5 条相关内容
- 包含微信文章和即刻动态
- 搜索耗时: 35ms

### 测试查询2: "Chrome插件 豆瓣"

```bash
python3 scripts/search_content.py \
  --query "Chrome插件 豆瓣" \
  --top-k 3 \
  --output-dir data
```

**结果**:
- ✅ 成功定位到即刻动态 377
- 搜索耗时: 17ms

---

## 🎯 即刻动态元数据结构

每条即刻动态包含以下元数据:

```markdown
# 即刻动态 {编号}

**发布时间:** YYYY-MM-DD  
**圈子:** {圈子名称}

---

{动态内容}
```

**示例**:

```markdown
# 即刻动态 1

**发布时间:** 2024-11-08  
**圈子:** Chrome插件分享站

---

30分钟0基础Cursor打造的【豆瓣书籍Notion同步助手】浏览器插件！

作为热爱阅读且用 Notion 管理知识的效率爱好者...
```

---

## 📝 后续维护

### 增量添加新动态

使用 `add_content.py` 脚本（单篇添加）:

```bash
python3 scripts/add_content.py \
  --file memories/contents/jike/posts/2026-02-05_post1026_新圈子.md \
  --output-dir data
```

### 批量导入新动态

1. 将新的即刻动态导出为单个大文件
2. 使用 `split_jike_posts.py` 拆分
3. 运行 `rebuild_index.py` 重建索引

**建议**: 每次新增 10+ 条动态时,使用重建索引方式更高效。

---

## ⚠️ 注意事项

### 文件命名规范

- **日期格式**: YYYY-MM-DD（便于排序）
- **编号格式**: post0001（4位数字,补零）
- **圈子名称**: 去除特殊字符,最长 30 字符

### 索引系统限制

- ⚠️ `rglob` 会递归扫描所有子目录
- ⚠️ 归档文件必须使用非 `.md` 后缀（如 `.backup`）
- ⚠️ 大文件（1000+ 条动态）建议拆分后索引

### 性能指标

- **搜索响应**: 15-40ms
- **索引大小**: ~1MB (1000+ 篇内容)
- **内存占用**: ~5MB（索引加载后）
- **支持内容量**: 5000+ 篇（无性能下降）

---

## 🚀 集成到 content-creator

即刻动态已自动纳入内容检索系统,可在以下场景使用:

1. **选题策划**: 检索相似主题的即刻动态和微信文章
2. **标题大纲**: 提取个人在即刻的表达风格
3. **写作剧本**: 参考即刻动态的叙事节奏

**调用方式**: content-creator skill 会自动调用 `search_content.py` 检索内容

---

## 📚 相关文档

- [索引规范](./indexing_spec.md) - 字段说明、质量评分标准
- [API 使用手册](./api_usage.md) - 搜索参数、过滤条件
- [SKILL.md](../SKILL.md) - content-creator-memory 功能说明

---

## 🔄 更新日志

- **2026-02-05**: 首次导入 1025 条即刻动态 (2024-11-08 ~ 2026-01-26)
- **下次更新**: 待定（建议每月或每 100 条动态更新一次）
