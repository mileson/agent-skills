---
name: company-name-cleaner
description: 自动化处理公司名称列表，两层处理：脚本规则清理 + Agent 智能品牌识别。当用户需要：从编号+公司名称的列表中提取品牌名；去除法律后缀、地点前缀、冗余词汇；识别通用品牌名（如 HP、BMW、DJI）；输出四列预览表供确认后生成最终品牌名称文档时使用此 skill。
---

# 公司名称清理器

两层处理：**脚本规则清理**（确定性）→ **Agent 品牌识别**（智能判断）→ **交互确认** → **最终输出**

## 第一层：脚本规则清理

运行预处理脚本，批量完成确定性文本清洗：

```bash
python3 ~/.cursor/skills/company-name-cleaner/scripts/preprocess.py < input_file.txt > intermediate.tsv
```

或直接传入文件路径：

```bash
python3 ~/.cursor/skills/company-name-cleaner/scripts/preprocess.py input_file.txt > intermediate.tsv
```

**脚本职责**（Low Freedom — 纯规则，不涉及判断）：
- 解析编号（decimal `101` + hex `0x0976`）
- 合并多行条目（无编号开头的行并入上一条）
- 提取括号内缩写（`(CATC)` `(QuIC)` → 作为品牌简称 hint）
- 去除括号内容（`(formerly ...)` 等）
- 去除地点前缀、法律后缀（**保护品牌中的 `&`**）、冗余描述词
- 输出 TSV：`ID\tCleaned\tExtractedAbbr\tOriginal`

**详细规则**：见 [references/cleanup-rules.md](references/cleanup-rules.md)

## 第二层：Agent 品牌识别

读取脚本输出，逐条判断是否存在更通用的品牌名。

### 判断原则

1. **清理后已经是品牌名** → 品牌简称留空（大多数情况）
2. **存在广泛使用的缩写/品牌名** → 填写品牌简称
3. **脚本提取了括号缩写** → 优先采用
4. **不确定** → 用 WebSearch 验证，仍不确定则留空

**不强行缩写**：没有通用简称的公司，品牌简称就留空。

### 判断标准示例

| 清理后 | 品牌简称 | 理由 |
|--------|---------|------|
| Hewlett-Packard | HP | 全球通用缩写 |
| Bayerische Motoren Werke | BMW | 官方缩写 |
| Matsushita Electric Industrial | Panasonic | 已改名，现用品牌 |
| Koninklijke Philips | Philips | 荷兰全称无人使用 |
| SZ DJI | DJI | SZ 为深圳前缀残留 |
| Bang & Olufsen | B&O | 业内通用简称 |
| Qualcomm | （留空） | 已经是品牌名 |
| Apple | （留空） | 已经是品牌名 |
| Aclara | （留空） | 无更短的通用名 |

### 批量处理策略

数据量大时（>500 条），分批处理：
1. 先快速扫描全部条目，标记需要品牌识别的（通常 < 10%）
2. 大部分条目：清理后即品牌名，品牌简称留空
3. 仅对需要判断的条目逐个处理
4. WebSearch 仅用于高度不确定的条目

## 第三层：输出与交互确认

### 预览输出

生成四列 Markdown 预览文件（`company_names_preview.md`）：

```markdown
# 公司名称处理预览

| ID | 原名 | 清理后 | 品牌简称 |
|----|------|--------|---------|
| 0 | Ericsson Technology Licensing | Ericsson | |
| 2 | Intel Corp. | Intel | |
| 101 | Hewlett-Packard Company | Hewlett-Packard | HP |
| 259 | Bang & Olufsen A/S | Bang & Olufsen | B&O |
```

### 统计摘要

输出完成后展示：
- 总条目数
- 脚本清理有变化的条目数
- 填写了品牌简称的条目数
- 品牌简称为空的条目数

### 主动询问

向用户确认：
1. 是否有需要修正的条目？
2. 是否有遗漏的品牌简称？
3. 是否满意输出格式？

根据反馈修正，循环直到用户满意。

### 最终文档

用户确认后，生成精简的最终文档（`company_names_final.md`）：

```markdown
# 公司品牌名称列表

| ID | 品牌名称 |
|----|---------|
| 0 | Ericsson |
| 2 | Intel |
| 101 | HP |
| 259 | B&O |
```

**逻辑**：品牌简称有值则用简称，否则用清理后名称。

写入当前工作目录，文件名可根据用户需求自定义。

## 参考文件

- `scripts/preprocess.py` — 第一层规则清理脚本
- `references/cleanup-rules.md` — 完整清理规则文档（按需查阅）
