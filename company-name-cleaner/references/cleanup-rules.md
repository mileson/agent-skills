# 清理规则参考

脚本 `preprocess.py` 使用的完整规则。Agent 按需查阅。

## 1. ID 解析

支持两种格式：
- Decimal: `101 Hewlett-Packard Company`
- Hex: `0x0976 Fauna Audio GmbH`

无 ID 开头的行自动合并到上一条（处理多行条目）。

## 2. 括号处理

| 括号内容 | 处理方式 |
|----------|----------|
| 全大写缩写 2-8 字符，如 `(CATC)` `(QuIC)` | **提取**为 `ExtractedAbbr` 列，作为品牌简称 hint |
| `(formerly ...)` | 删除 |
| `(Shanghai)` / `(HK)` 等地区标注 | 删除 |
| 其他括号内容 | 删除 |

排除列表（不提取为缩写）：`HK` `UK` `US` `EU` `OPC`

## 3. 地点前缀

去除公司名称开头的城市/省份名，覆盖：
- 中国主要城市：Shanghai、Shenzhen、Beijing、Guangzhou、Hangzhou 等 60+
- 地区：Taiwan、Hong Kong、Macau、Jiangsu、Guangdong 等
- 缩写：SZ（深圳）、GD（广东）

仅去除**开头**的地点，不影响中间或结尾的地点词。

## 4. 法律后缀

### 复合后缀（优先匹配）

`GmbH & Co. KGaA` · `GmbH & Co. KG` · `SE & Co. KG` · `AG & Co. KG` · `Sp. z o.o. sp. k.` · `Sp. z o.o.` · `Pte. Ltd.` · `Pty Ltd` · `Private Limited` · `Co., Ltd.` · `Co. Ltd.` · `with limited liability` · `Sociedad Limitada` · `Limited Liability`

### 标准后缀

| 后缀 | 地区 |
|------|------|
| LLC, Inc, Ltd, Co, Corp | 美国/英国 |
| GmbH, AG, SE, KG, KGaA, UG | 德国/瑞士 |
| SA, SAS, SARL, SL, SLU, SpA | 法国/西班牙/意大利 |
| BV, NV | 荷兰 |
| Oy, Oyj, AB, ASA, A/S, ApS | 北欧 |
| Kft | 匈牙利 |
| d.o.o., s.r.o., Sp. z o.o. | 中东欧 |
| Pte Ltd, Pty Ltd | 新加坡/澳大利亚 |
| LTDA, OÜ, PLC | 其他 |
| Corporation, Company, Incorporated, Enterprises, Holdings, Group, Laboratories, Foundation, Institute, Partners, Associates | 通用英文 |

### & 保护规则

**仅在法律后缀模式中处理 `&`**（如 `& Co. KG`），不全局替换。品牌名中的 `&` 保留：
- `Bang & Olufsen` → 保留
- `Rohde & Schwarz` → 保留
- `B&W Group` → 去除 `Group`，保留 `B&W`

## 5. 冗余描述词

去除以下行业通用词（大小写不敏感）：

Technology · Technologies · Electronics · Electronic · Semiconductor · Semiconductors · Microelectronics · Optoelectronics · Engineering · Systems · System · Solutions · Solution · Devices · Device · Products · Product · Industries · Industry · Networks · Network · Networking · Communications · Communication · Telecommunications · Innovative · Advanced · Digital · Smart · Global · International · Worldwide · Universal · Integrated · Manufacturing · Automation

### 最小长度保护

- 处理后结果 < 2 字符 → 回退到处理前
- 确保不会清空公司名

## 6. 特殊字符

- 引号 `" ' `` → 删除
- 反斜杠 `\` → 删除
- 结尾标点 `. , ; :` → 删除
- 开头标点 `. , ; : _ + | / \` → 删除（保留 `-`）
- 多余空格 → 合并

## 7. 处理顺序

```
原始名称
 → 提取括号缩写 + 去除括号
 → 去除地点前缀
 → 去除法律后缀
 → 去除冗余描述词
 → 清理特殊字符
 → 最终保护检查
 → 输出
```
