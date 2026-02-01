# Gemini 水印批量移除 Skill

自动检测并移除 Gemini AI 生成图片中的半透明水印标志。

## 🚀 快速使用

### 在 Cursor 中使用（推荐）

只需在对话中说：

```
"帮我去除 @image.png 的水印"
"批量处理 @images/ 文件夹的水印"
"去除这个图片的 Gemini 水印"
```

Skill 会自动激活并处理！

### 命令行使用

```bash
# 单文件处理
python3 batch_processor.py input.png

# 指定输出路径
python3 batch_processor.py input.png output.png

# 批量处理文件夹
python3 batch_processor.py ./images/

# 指定输出文件夹
python3 batch_processor.py ./images/ ./cleaned/
```

## 📁 目录结构

```
gemini-watermark-remover/
├── SKILL.md                    # Skill 定义和文档
├── README.md                   # 本文件
├── batch_processor.py          # 批量处理入口（AI 调用）
├── lib/                        # 核心算法模块
│   └── remover.py             # 水印检测和移除算法
└── assets/                     # 资源文件
    ├── bg_48.png              # 48×48 水印模板
    └── bg_96.png              # 96×96 水印模板
```

### 结构说明

- **batch_processor.py**：主入口脚本，处理命令行参数、文件扫描、进度显示
- **lib/remover.py**：核心算法，实现水印检测和移除逻辑
- **assets/**：资源文件目录，存储水印模板图片

## ✨ 功能特性

- ✅ **智能检测**：自动识别 48×48 和 96×96 水印
- ✅ **数学精确**：反向 Alpha 混合，100% 无损还原
- ✅ **单文件/批量**：支持处理单张图片或整个文件夹
- ✅ **进度显示**：实时显示处理进度条
- ✅ **详细报告**：生成完整的处理统计

## 📊 处理示例

### 单文件
```
✅ 成功移除 96x96 水印！
  输入: test.png
  输出: test_no_watermark.png
  置信度: 99.97%
  耗时: 1.3秒
```

### 批量处理
```
📊 批量处理完成
统计信息:
  总文件数: 50
  成功处理: 48 ✅
  未检测到水印: 2 ○
  处理失败: 0 ❌
  总耗时: 75.2秒
  平均耗时: 1.5秒/张

输出目录: /path/to/images_no_watermark
```

## 🔧 技术细节

### 核心算法
反向 Alpha 混合公式：
```
original = (watermarked - α × logo) / (1 - α)
```

### 检测流程
1. 两阶段搜索（粗 + 精细）
2. 皮尔逊相关系数
3. 置信度阈值 ≥ 30%

### 依赖
- Python 3.7+
- Pillow (PIL)
- NumPy

## ⚙️ 配置说明

### 支持的图片格式
- PNG（推荐，保留 Alpha 通道）
- JPEG / JPG
- WebP

### 输出路径规则
- **单文件**：`原文件名_no_watermark.扩展名`
- **批量**：`原文件夹_no_watermark/` 目录

## 🐛 故障排查

### 未检测到水印
- 确认是 Gemini 生成的图片
- 检查水印是否在右下角
- 查看置信度值

### 处理失败
- 检查图片是否损坏
- 确认磁盘空间充足
- 查看错误信息

### 速度慢
- 检查 CPU 使用率
- 关闭其他占用资源的程序
- 使用 SSD 存储

## 📝 版本历史

### v1.2.0 (2026-01-23)
- 🏗️ **重构文件结构**（遵循 Python 最佳实践）
  - `core/` → `lib/`（核心算法模块）
  - 新增 `assets/` 目录（资源文件分离）
  - `gemini_watermark_remover.py` → `remover.py`（简化命名）
- 📝 更新所有路径引用和文档
- ✅ 功能测试通过，向后兼容

### v1.1.0 (2026-01-23)
- 🔧 添加 "AI 执行指令" 章节到 SKILL.md
- 📚 完善技术支持文档
- 🐛 修正 AI 误创建脚本的问题

### v1.0.0 (2026-01-23)
- ✨ 初始版本
- ✅ 支持单文件和批量处理
- ✅ 智能水印检测
- ✅ 进度显示和详细报告

## 📧 技术支持

如遇问题，请检查：
1. Python 版本 ≥ 3.7
2. 依赖库已安装（Pillow, NumPy）
3. 核心脚本完整性
4. 水印模板文件存在

---

**License**: MIT  
**Created**: 2026-01-23  
**Author**: AI Assistant
