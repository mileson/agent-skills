# 公司名称清理规则

本文档列出了用于清理公司名称的完整规则列表，供参考和维护。

## 1. 地点前缀（Location Prefixes）

### 中国城市
上海、深圳、北京、重庆、广州、杭州、南京、成都、武汉、西安、天津、苏州、郑州、长沙、东莞、青岛、沈阳、宁波、昆明、合肥、福州、厦门、无锡、济南、大连、哈尔滨、佛山、南通、长春、石家庄、贵阳、南宁、南昌、太原、常州、温州、嘉兴、珠海、惠州、中山、昆山、烟台、潍坊、临沂、淄博、济宁、泰安、威海、咸阳、洛阳、南阳、安阳、新乡、焦作、日照

### 地区
台湾、香港、澳门、江苏

## 2. 公司法律后缀（Legal Suffixes）

### 简短后缀
| 后缀 | 说明 | 国家/地区 |
| :--- | :--- | :--- |
| LLC | Limited Liability Company | 美国 |
| Inc / Inc. | Incorporated | 美国 |
| Ltd / Ltd. | Limited | 英国/英联邦 |
| Co / Co. | Company | 通用 |
| Corp / Corp. | Corporation | 美国 |
| GmbH | Gesellschaft mit beschränkter Haftung | 德国 |
| AG | Aktiengesellschaft | 德国/瑞士 |
| SE | Societas Europaea | 欧盟 |
| SA | Société Anonyme / Sociedad Anónima | 法国/西班牙 |
| Kft. | Korlátolt Felelősségű Társaság | 匈牙利 |
| BV | Besloten Vennootschap | 荷兰 |
| Oy | Osakeyhtiö | 芬兰 |
| AB | Aktiebolag | 瑞典 |
| S.L. | Sociedad Limitada | 西班牙 |
| SLU | Sociedad Limitada Unipersonal | 西班牙 |
| SpA | Società per Azioni | 意大利 |
| d.o.o. | društvo s ograničenom odgovornošću | 克罗地亚/塞尔维亚 |
| Sp. z o.o. | Spółka z ograniczoną odpowiedzialnością | 波兰 |
| Pte. Ltd | Private Limited | 新加坡 |
| Pty Ltd | Proprietary Limited | 澳大利亚 |

### 复合后缀
| 后缀 | 说明 |
| :--- | :--- |
| Co. Ltd. | Company Limited |
| Co. Inc. | Company Incorporated |
| Corp. Ltd. | Corporation Limited |
| GmbH & Co. KG | 德国特殊合伙形式 |
| & Co. KG | 德国合伙公司 |
| & Affiliates | 及其关联公司 |
| Private Limited | 私人有限公司 |
| Sociedad Limitada | 西班牙有限公司 |
| (with limited liability) | 有限责任 |
| (Shanghai) / (ShenZhen) / (Xiamen) / (Jiangsu) | 地区标注 |

## 3. 冗余描述词（Redundant Words）

### 行业通用词
| 词 | 中文 |
| :--- | :--- |
| Technology / Technologies | 技术 |
| Electronics / Electronic | 电子 |
| Engineering | 工程 |
| System / Systems | 系统 |
| Solution / Solutions | 解决方案 |
| Device / Devices | 设备 |
| Product / Products | 产品 |
| Industry / Industries | 工业 |
| Group | 集团 |
| Holding / Holdings | 控股/控股公司 |
| Enterprise / Enterprises | 企业 |
| Business | 商务/业务 |
| Network / Networks | 网络 |
| Communication / Communications | 通信 |
| Telecommunication / Telecommunications | 电信 |
| Integrated | 集成 |
| Innovative | 创新 |
| Advanced | 先进 |
| Digital | 数字 |
| Smart | 智能 |
| Global | 全球 |
| International | 国际 |
| Worldwide | 世界范围 |
| Universal | 通用 |

## 4. 特殊字符清理

- 括号及其内容：`(...)` → 删除
- 引号：`" ' ` → 删除
- 多余空格：合并为单个空格
- 首尾标点：`. , ; : - _ + | / \` → 删除

## 5. 处理顺序

```
原始输入
  ↓
1. 提取数字编号和名称
  ↓
2. 去除地点前缀
  ↓
3. 去除法律后缀
  ↓
4. 去除冗余描述词（仅当名称 > 2 个词时）
  ↓
5. 清理特殊字符
  ↓
输出中间结果
```

## 6. 示例

| 输入 | 中间结果 | 说明 |
| :--- | :--- | :--- |
| `2208 Aclara Technologies LLC` | `Aclara` | 去除后缀 + 冗余词 |
| `2212 Realme Chongqing Mobile Telecommunications Corp. Ltd.` | `Realme` | 去除地点 + 后缀 + 冗余词 |
| `2255 betternotstealmybike UG (with limited liability)` | `betternotstealmybike` | 去除括号 + 后缀 |
| `2269 -Q` | `-Q` | 保持原样（无后缀） |
| `2253 ifly` | `ifly` | 保持原样（无后缀） |
