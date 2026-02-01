---
name: ios-localization-auto-translator
description: 自动检查和完善 iOS 应用的多语言翻译，基于现有的本地化检查脚本，智能翻译缺失字段，确保应用的国际化完整性
---

# iOS 多语言自动翻译器

## When to Use

Use this skill when you need to:
- 新增功能后需要补充多语言翻译
- 定期检查多语言完整性
- 批量翻译缺失的字段
- 确保翻译质量和一致性
- 准备应用商店多语言版本
- 检查和完善 iOS 应用的多语言翻译

## Prerequisites

确保项目中存在以下文件和目录：
- `Scripts/localization_checker/check_localization.py` - 本地化检查脚本
- `Scripts/localization_checker/output/` - 检查结果输出目录
- `PoseCam/Resources/Localization/Localizable.xcstrings` - 多语言字符串文件

## Instructions

### 步骤 1: 运行本地化检查脚本

执行 Python 检查脚本，生成最新的翻译状态报告：

```bash
cd [项目根目录]
python3 Scripts/localization_checker/check_localization.py
```

**输出**：在 `Scripts/localization_checker/output/` 目录生成带时间戳的 CSV 文件
- 文件名格式：`localization_matrix_YYYYMMDD_HHMMSS.csv`

### 步骤 2: 读取并解析最新的检查报告

定位最新生成的 CSV 文件：
```bash
ls -t Scripts/localization_checker/output/*.csv | head -1
```

**CSV 文件结构**：
```csv
字段Key,zh-Hans翻译,de,en,es,fr,it,ja,ko,pt,ru,th,vi,zh-Hant
about,关于,X,,X,X,X,X,X,X,X,X,X,X
camera.button.flash,闪光灯,,,,,,,,,,,, 
settings.account,账号设置,X,X,,,X,,,,,,,
```

**标记说明**：
- **空单元格** = 该语言已有翻译 ✓
- **X 标记** = 该语言缺失翻译，需要处理

### 步骤 3: 提取所有待翻译字段

遍历 CSV 文件，收集所有标记为 `X` 的字段和语言组合：

**数据结构示例**：
```
待翻译清单：
[
  {
    key: "about",
    baseLang: "zh-Hans",
    baseValue: "关于",
    needTranslations: ["de", "es", "fr", "it", "ja", "ko", "pt", "ru", "th", "vi", "zh-Hant"]
  },
  {
    key: "settings.account",
    baseLang: "zh-Hans", 
    baseValue: "账号设置",
    needTranslations: ["de", "en", "fr"]
  }
]
```

### 步骤 4: 智能翻译生成

针对每个待翻译字段，生成符合 App 特性的地道译文。

#### 翻译原则
1. **简洁精炼**：App 界面文本，保持简短
2. **地道自然**：使用目标语言的地道表达，而非直译
3. **一致性**：保持术语翻译的一致性
4. **场景适配**：根据字段 Key 理解使用场景

#### 特殊场景处理

**按钮文本** (key 包含 `button`、`action`):
- 中文："拍照" → 英文："Take Photo"（不是 "Taking Photo"）
- 中文："确定" → 日文："確定" / 英文："Confirm"

**标签文本** (key 包含 `label`、`title`):
- 中文："用户名" → 英文："Username"（不是 "User Name"）
- 中文："姿势模板" → 日文："ポーズテンプレート"

**提示文本** (key 包含 `hint`、`placeholder`):
- 中文："请输入用户名" → 英文："Enter username"
- 中文："搜索模板" → 日文："テンプレートを検索"

**错误消息** (key 包含 `error`、`alert`):
- 中文："网络错误" → 英文："Network Error"
- 中文："加载失败，请重试" → 日文："読み込みに失敗しました。もう一度お試しください。"

#### 语言特殊规则

**日文 (ja)**：
- 保持礼貌语气，使用 "です/ます" 形式
- 按钮动词使用命令形或名词化
- 例："保存" → "保存する" 或 "保存"

**韩文 (ko)**：
- 使用敬语（존댓말）
- 例："保存" → "저장" 或 "저장하기"

**繁体中文 (zh-Hant)**：
- 使用台湾/香港地区常用表达
- 例："照片" → "相片"，"文件" → "檔案"

**欧洲语言 (de, es, fr, it, pt)**：
- 注意名词性别和冠词
- 保持简洁，避免冗长句式

### 步骤 5: 更新 Localizable.xcstrings 文件

将生成的翻译写入 `.xcstrings` 文件的对应位置。

**文件结构**：
```json
{
  "sourceLanguage" : "zh-Hans",
  "strings" : {
    "about" : {
      "localizations" : {
        "de" : {
          "stringUnit" : {
            "state" : "translated",
            "value" : "Über"
          }
        },
        "en" : {
          "stringUnit" : {
            "state" : "translated",
            "value" : "About"
          }
        },
        "zh-Hans" : {
          "stringUnit" : {
            "state" : "translated",
            "value" : "关于"
          }
        }
      }
    }
  }
}
```

**更新步骤**：
1. 读取 `Localizable.xcstrings` JSON 文件
2. 定位到对应的字段 Key
3. 在 `localizations` 下添加或更新目标语言
4. 设置 `state` 为 `"translated"`
5. 保存文件，保持 JSON 格式美化

### 步骤 6: 在 CSV 中标记完成状态

每成功翻译并更新一个字段后，在 CSV 文件中：
- 将原来的 `X` 替换为 `✅`
- 添加翻译值（可选，用于审核）

**更新后的 CSV**：
```csv
字段Key,zh-Hans翻译,de,en,es,fr,it,ja,ko,pt,ru,th,vi,zh-Hant
about,关于,✅,✅,✅,✅,✅,✅,✅,✅,✅,✅,✅,✅
```

### 步骤 7: 重新运行检查脚本验证

翻译完成后，再次运行检查脚本确认：

```bash
python3 Scripts/localization_checker/check_localization.py
```

检查新生成的 CSV 文件：
- 确认之前的 `X` 已消失
- 检查是否有新的缺失项
- 查看完成度统计报告

### 步骤 8: 生成翻译总结报告

输出本次翻译工作的总结：

```
========================================
多语言翻译完成报告
========================================
翻译时间：2026-01-10 15:30:00
基准语言：zh-Hans (简体中文)

📊 翻译统计
-----------------
总字段数：216
本次翻译字段：15
涉及语言：12 种

🌍 各语言完成情况
-----------------
✅ de (德语)：215/216 (99.5%)
✅ en (英语)：216/216 (100.0%)
✅ es (西班牙语)：214/216 (99.1%)
✅ fr (法语)：215/216 (99.5%)
...

📝 本次翻译字段清单
-----------------
1. about - 12 种语言
2. settings.account - 3 种语言
3. camera.button.flash - 5 种语言
...

⚠️ 仍需处理
-----------------
无（全部完成！🎉）

或

仍有 3 个字段缺少翻译：
- field.key.1: [ja, ko]
- field.key.2: [de]
```

## Quality Assurance

### 人工审核点
标记以下类型字段需要人工审核：
1. **品牌名称**：保持原文或按官方译名
   - "PoseCam" → 各语言统一保持 "PoseCam"
2. **专业术语**：
   - "AI 生成" → 确认各语言对 AI 的标准表达
3. **长文本**（>20字符）：
   - 需要人工检查语法和语境

### 测试验证清单
- ✅ 在 Xcode 中切换各语言预览，检查显示效果
- ✅ 确认文本长度不会导致界面溢出
- ✅ 检查特殊字符（如 emoji）显示正常
- ✅ 验证从右到左语言（如阿拉伯语，如有）的布局

## Batch Processing

### 分批翻译策略
对于大量待翻译字段（>50个）：

**Phase 1: 高优先级（立即翻译）**
- 用户可见的 UI 文本（按钮、标签、标题）
- 错误提示和警告信息

**Phase 2: 中优先级（近期翻译）**
- 设置项描述
- 帮助文本
- Placeholder 提示

**Phase 3: 低优先级（按需翻译）**
- 调试信息
- 内部日志文本

### 并发处理
支持多字段并行翻译，提升效率：
- 每次处理 5-10 个字段
- 避免 API 限流
- 显示进度条：`[██████░░░░] 60% (12/20)`

## Common Issues

### 问题 1：CSV 文件中文乱码
**解决方案**：
```bash
# 转换编码
iconv -f UTF-8 -t UTF-8-BOM input.csv > output.csv
```

### 问题 2：.xcstrings 文件格式错误
**解决方案**：
1. 备份原文件
2. 使用 JSON 格式验证器检查
3. 确保严格遵循 Xcode String Catalog 格式

### 问题 3：翻译后界面显示异常
**解决方案**：
1. 检查文本长度：某些语言（如德语）文本较长
2. 使用 SwiftUI 的 `.lineLimit()` 和 `.minimumScaleFactor()`
3. 调整界面布局以适应不同语言

## Output Checklist

完成后确认：
- ✅ 检查脚本已运行，CSV 报告已生成
- ✅ 所有 X 标记已替换为 ✅
- ✅ Localizable.xcstrings 已更新
- ✅ 验证脚本重新运行，确认完成度
- ✅ 翻译总结报告已生成
- ✅ 人工审核标记（如有）已记录
