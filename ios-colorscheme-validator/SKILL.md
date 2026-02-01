---
name: ios-colorscheme-validator
description: 自动扫描 Swift 代码文件，检测硬编码颜色和不符合规范的颜色使用，确保所有颜色引用来自 ColorTheme.swift，保持视觉一致性
---

# iOS 颜色主题验证器

## When to Use

Use this skill when you need to:
- 代码审查时检查颜色规范
- 重构项目统一配色方案
- 新人代码质量检查
- 定期维护代码质量
- 检查 iOS 项目中的颜色使用是否符合规范，识别硬编码颜色和不当使用

## Prerequisites

- 项目中存在 `ColorTheme.swift` 配色文件
- 需要检查的文件为 `.swift` 格式

## ColorTheme Standards

项目中应使用 `ColorTheme.swift` 统一配色：

```swift
// ✅ 正确使用
.foregroundColor(ColorTheme.primaryText)
.background(ColorTheme.background)
.tint(ColorTheme.accent)

// ❌ 禁止使用
.foregroundColor(.black)        // 硬编码颜色
.background(Color.white)        // 系统颜色
.tint(Color(hex: "#FF0000"))   // 十六进制颜色
```

## Instructions

### 步骤 1: 扫描目标文件或目录

支持扫描范围：
- 单个文件：检查指定的 `.swift` 文件
- 目录：递归检查目录下所有 `.swift` 文件
- 批量：检查 `Features/`、`Components/`、`Views/` 等目录

### 步骤 2: 识别违规模式

检测以下违规模式：

#### A. 系统颜色直接使用
```swift
// 违规模式
.foregroundColor(.black)
.foregroundColor(.white)
.foregroundColor(.red)
.background(.blue)
.tint(.green)

// 正则: \.(foregroundColor|background|tint|fill|stroke)\s*\(\s*\.(black|white|red|blue|green|yellow|orange|purple|pink|gray)\s*\)
```

#### B. UIColor/Color 初始化
```swift
// 违规模式
Color(red: 1.0, green: 0.0, blue: 0.0)
Color(hex: "#FF0000")
UIColor(red: 1.0, green: 0.0, blue: 0.0, alpha: 1.0)

// 正则: (Color|UIColor)\s*\(\s*(red|hex)
```

#### C. 字符串颜色名称
```swift
// 违规模式
Color("MyColor")
UIColor(named: "SomeColor")

// 正则: (Color|UIColor)\s*\(\s*"[^"]*"\s*\)
```

### 步骤 3: 生成违规清单

输出格式：

```
========================================
iOS 颜色主题验证报告
========================================
扫描时间：2026-01-10 15:30:00
扫描范围：Features/AIAlbum/

📊 统计摘要
-----------------
总文件数：25
违规文件数：3
违规次数：7

⚠️ 违规详情
-----------------

文件：Features/AIAlbum/Views/AIAlbumView.swift
  第 45 行：.foregroundColor(.black)
  → 建议：使用 ColorTheme.primaryText
  
  第 78 行：.background(Color.white)
  → 建议：使用 ColorTheme.background
  
  第 102 行：Color(red: 1.0, green: 0.0, blue: 0.0)
  → 建议：在 ColorTheme.swift 中定义此颜色

文件：Features/AIAlbum/Views/Components/FilterCard.swift
  第 23 行：.tint(.blue)
  → 建议：使用 ColorTheme.accent
  
  第 56 行：Color(hex: "#FF6B81")
  → 建议：使用 ColorTheme.accent 或定义新颜色

========================================
🔧 修复建议
========================================

1. 常用颜色映射：
   - .black → ColorTheme.primaryText
   - .white → ColorTheme.background (浅色模式)
   - .gray → ColorTheme.secondaryText
   - .blue → ColorTheme.accent
   - .red → ColorTheme.error
   - .green → ColorTheme.success

2. 如需新颜色：
   在 ColorTheme.swift 中添加：
   ```swift
   static let newColor = Color("NewColorName")
   ```
   
3. 批量替换命令：
   sed -i '' 's/\.foregroundColor(\.black)/\.foregroundColor(ColorTheme.primaryText)/g' [文件路径]
```

### 步骤 4: 提供修复方案

针对每个违规项，提供具体的修复代码：

```swift
// ❌ 违规代码
Text("标题")
    .foregroundColor(.black)
    .background(.white)

// ✅ 修复后
Text("标题")
    .foregroundColor(ColorTheme.primaryText)
    .background(ColorTheme.background)
```

### 步骤 5: 检查 ColorTheme.swift 完整性

确保 `ColorTheme.swift` 包含常用颜色：

**必需的颜色定义**：
```swift
struct ColorTheme {
    // 文本颜色
    static let primaryText: Color
    static let secondaryText: Color
    static let disabledText: Color
    
    // 背景颜色
    static let background: Color
    static let secondaryBackground: Color
    static let tertiaryBackground: Color
    
    // 强调颜色
    static let accent: Color
    static let accentSecondary: Color
    
    // 状态颜色
    static let success: Color
    static let warning: Color
    static let error: Color
    
    // 边框和分隔线
    static let border: Color
    static let separator: Color
}
```

如缺少定义，输出警告：
```
⚠️ ColorTheme.swift 缺少以下颜色定义：
  - error (用于替换 .red)
  - warning (用于替换 .orange)
```

### 步骤 6: 生成自动修复脚本（可选）

对于简单的替换，生成批量修复脚本：

```bash
#!/bin/bash
# auto_fix_colors.sh
# 自动修复颜色使用规范

echo "开始批量修复颜色使用..."

# 替换 .black
find Features/ -name "*.swift" -type f -exec sed -i '' 's/\.foregroundColor(\.black)/\.foregroundColor(ColorTheme.primaryText)/g' {} \;

# 替换 .white
find Features/ -name "*.swift" -type f -exec sed -i '' 's/\.background(\.white)/\.background(ColorTheme.background)/g' {} \;

# 替换 .gray
find Features/ -name "*.swift" -type f -exec sed -i '' 's/\.foregroundColor(\.gray)/\.foregroundColor(ColorTheme.secondaryText)/g' {} \;

echo "修复完成！请检查并测试修改。"
```

## Special Scenarios

### 场景 1：Preview 预览代码
Preview 中的测试颜色可以豁免：

```swift
struct MyView_Previews: PreviewProvider {
    static var previews: some View {
        MyView()
            .background(.gray)  // ✅ Preview 中允许
    }
}
```

检测规则：跳过 `_Previews` 结构体内的颜色使用。

### 场景 2：第三方库组件
某些第三方库组件可能要求特定颜色格式：

```swift
// 第三方库要求
ThirdPartyButton(color: .blue)  // ✅ 允许
```

添加注释标记豁免：
```swift
// swiftlint:disable:next color_literal
ThirdPartyButton(color: .blue)
```

### 场景 3：渐变色
渐变色的处理建议：

```swift
// ❌ 硬编码渐变
LinearGradient(
    colors: [.red, .blue],
    startPoint: .top,
    endPoint: .bottom
)

// ✅ 使用 ColorTheme
LinearGradient(
    colors: [ColorTheme.accent, ColorTheme.accentSecondary],
    startPoint: .top,
    endPoint: .bottom
)
```

## CI/CD Integration

将验证器集成到持续集成流程：

```yaml
# .github/workflows/color-check.yml
name: Color Theme Validation

on: [pull_request]

jobs:
  validate-colors:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Color Validator
        run: |
          # 运行验证器（假设有命令行工具）
          swift run color-validator Features/
      - name: Comment PR
        if: failure()
        run: |
          # 在 PR 中评论违规情况
          echo "发现颜色使用违规，请修复后再合并"
```

## Output Checklist

完成后确认：
- ✅ 违规文件清单已生成
- ✅ 每个违规项有具体位置和修复建议
- ✅ ColorTheme.swift 完整性已检查
- ✅ 自动修复脚本已生成（如适用）
- ✅ 修复前后对比代码已提供
