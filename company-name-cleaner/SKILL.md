---
name: company-name-cleaner
description: 自动化处理公司名称列表，提取并简化为公司简称。当用户需要：从编号+公司名称的列表中提取简称；去除地点前缀、法律后缀、冗余词汇；识别通用简称（如 HP、IBM）；输出格式为"编号 - 简称"的 Markdown 文档时使用此 skill。
---

# 公司名称简化器

## 处理流程

本 skill 采用**两阶段处理**：Python 初加工 → AI 智能简化

```
原始输入 → Python 规则处理 → AI 智能简化 → Markdown 输出
```

## 阶段1: Python 初加工

运行脚本进行规则化清理：

```bash
python3 ~/.claude/skills/company-name-cleaner/scripts/preprocess.py < input_file.txt
```

或直接处理用户提供的列表。

### 清理规则

| 操作类型 | 示例 |
| :--- | :--- |
| 去除数字编号 | `2208 Aclara` → `Aclara` |
| 去除地点前缀 | `Shenzhen MXCHIP` → `MXCHIP` |
| 去除法律后缀 | `Aclara Technologies LLC` → `Aclara Technologies` |
| 清理特殊字符 | `betternotstealmybike UG (limited)` → `betternotstealmybike` |

## 阶段2: AI 智能简化

对初加工结果进行智能处理：

### 1. 已知简称（AI 知识库）

利用 AI 内部知识识别常见简称：

| 完整名称 | 简称 |
| :--- | :--- |
| Hewlett-Packard | HP |
| International Business Machines | IBM |
| Minnesota Mining and Manufacturing | 3M |
| General Electric | GE |
| Texas Instruments | TI |
| Analog Devices | ADI |

### 2. 网络搜索验证

不确定时使用 `WebSearch` 查找通用简称：

```
搜索词: "公司名" common abbreviation / short name / 简称
```

从搜索结果中提取最常用的简称。

### 3. 去除冗余描述词

去除初加工后仍存在的行业描述词：

- Technology, Technologies
- Electronics, Electronic
- Engineering, Engineers
- Systems, Solutions
- Devices, Products
- Communications, Telecommunications
- Networks, Networking
- Digital, Smart
- Innovative, Advanced
- Global, International, Worldwide

## 输出格式

```markdown
# 公司名称简称列表

101 - HP
2208 - Aclara
2269 - -Q
...
```

## 阶段3: 输出文件（重要！）

**处理完成后必须将结果写入当前工作目录的 markdown 文件：**

```python
# 使用 Write 工具输出到当前目录
file_path = f"{os.getcwd()}/company_names_cleaned.md"
```

文件名格式：`company_names_cleaned.md` 或根据用户需求自定义。

## 参考文件

- `scripts/preprocess.py` - Python 初加工脚本
- `references/cleanup-rules.md` - 完整清理规则列表
