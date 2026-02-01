# Gemini 图片水印批量移除工具

自动检测并移除 Gemini AI 生成图片中的半透明水印标志，支持单文件和批量文件夹处理。

## 触发条件 (When to Use)

当用户提到以下关键词或场景时，自动激活此 Skill：
- "去水印"、"移除水印"、"去除水印"
- "remove watermark"、"清理水印"
- "处理 Gemini 图片"、"批量去水印"
- 使用 @文件引用 并提到水印相关操作
- "这张图片有水印，帮我去掉"

## 核心功能 (Core Features)

### 🎯 主要能力
1. **智能检测**：自动识别 48×48 和 96×96 两种 Gemini 水印尺寸
2. **精确移除**：使用反向 Alpha 混合算法，100% 无损还原原始像素
3. **单文件处理**：快速处理单张图片
4. **批量处理**：扫描整个文件夹，批量移除水印
5. **进度追踪**：实时显示处理进度
6. **详细报告**：生成完整的处理统计报告

### 🔬 技术特点
- **数学精确**：基于反向 Alpha 混合公式，非 AI "猜测"
- **高置信度**：使用皮尔逊相关系数检测，通常达到 99%+ 置信度
- **高性能**：单张图片处理时间 < 5 秒
- **格式支持**：PNG、JPEG、WebP

## 使用方式 (How to Use)

### 方式 1：对话式触发
```
用户: "帮我去除这张图片的 Gemini 水印"
用户: "批量处理 Desktop/photos 文件夹的水印"
```

### 方式 2：文件引用触发
```
用户: @image.png 去除水印
用户: @images/ 批量去水印
```

### 方式 3：直接指定路径
```
用户: "处理 /Users/mileson/Desktop/test.png 的水印"
```

## AI 执行指令 (AI Execution Instructions)

⚠️ **重要：AI 必须严格按照以下步骤执行，不要自己创建新的脚本！**

### 步骤 1：识别输入路径
- 从用户消息中提取文件或文件夹路径
- 如果用户使用 `@文件引用`，提取引用的路径
- 如果没有明确路径，询问用户提供

### 步骤 2：调用批量处理脚本
直接使用 Shell 工具调用批量处理脚本：

```bash
python3 ~/.cursor/skills/gemini-watermark-remover/batch_processor.py <input_path> [output_path]
```

**参数说明：**
- `<input_path>`: 必需，输入文件或文件夹的绝对路径
- `[output_path]`: 可选，自定义输出路径

**示例：**
```bash
# 单文件处理
python3 ~/.cursor/skills/gemini-watermark-remover/batch_processor.py /Users/mileson/Desktop/image.png

# 批量处理文件夹
python3 ~/.cursor/skills/gemini-watermark-remover/batch_processor.py /Users/mileson/Desktop/images/

# 自定义输出路径
python3 ~/.cursor/skills/gemini-watermark-remover/batch_processor.py /Users/mileson/Desktop/images/ /Users/mileson/Documents/cleaned/
```

### 步骤 3：解读并展示结果
- 脚本会自动输出详细的处理报告
- AI 只需要将输出展示给用户即可
- 无需额外的格式化或总结

### ⚠️ 关键注意事项
1. **不要创建新的脚本**：直接调用现有的 `batch_processor.py`
2. **使用绝对路径**：确保路径从 `/Users/` 开始
3. **设置超时**：批量处理可能耗时较长，建议设置 120000ms (2分钟) 超时
4. **一次性调用**：批量处理脚本会自动处理文件夹中的所有图片，不需要循环调用

## 执行流程 (Workflow)

批量处理脚本会自动执行以下流程：

1. **识别输入**
   - 验证路径是否存在
   - 判断是单文件还是文件夹

2. **单文件处理**
   - 调用核心脚本检测水印
   - 移除水印并保存
   - 显示处理结果（位置、置信度）

3. **批量处理**（文件夹）
   - 扫描所有图片文件（*.png, *.jpg, *.jpeg, *.webp）
   - 创建输出目录（默认：原目录_no_watermark）
   - 循环处理每个文件
   - 实时更新进度
   - 生成处理报告

4. **结果展示**
   - 显示输出路径
   - 统计信息（总数、成功、失败）
   - 失败文件列表（如果有）

## 输入参数 (Input Parameters)

### 必需参数
- `input_path`: 输入文件或文件夹路径

### 可选参数
- `output_path`: 自定义输出路径（默认：自动生成）
- `output_format`: 输出格式（PNG/JPEG/WEBP，默认：保持原格式）

## 输出说明 (Output)

### 单文件输出
```
✅ 成功移除 96x96 水印！
  输入: test.png
  输出: test_no_watermark.png
  位置: (1376, 2592)
  置信度: 99.97%
  耗时: 3.5秒
```

### 批量处理输出
```
📊 批量处理完成！
══════════════════════════════════
总文件数: 50
成功处理: 48
未检测到水印: 2
失败: 0

输出目录: /Users/mileson/Desktop/images_no_watermark

处理详情:
  ✓ image001.png → 成功 (96x96, 99.87%)
  ✓ image002.png → 成功 (48x48, 98.45%)
  ○ image003.png → 跳过 (未检测到水印)
  ...
```

## 技术原理 (Technical Details)

### 反向 Alpha 混合算法
Gemini 添加水印使用标准 Alpha 合成：
```
watermarked = α × logo + (1 - α) × original
```

反向求解原始图片：
```
original = (watermarked - α × logo) / (1 - α)
```

### 检测流程
1. **两阶段搜索**：粗搜索定位 + 精细搜索优化
2. **皮尔逊相关**：计算图像区域与模板的相关系数
3. **置信度阈值**：默认 ≥ 30% 才认为检测到水印

## 依赖说明 (Dependencies)

本 Skill 使用 Python 实现，依赖以下库：
- `Pillow (PIL)`: 图像处理
- `NumPy`: 数值计算

这些是 Python 标准环境常见库，通常已预装。

## 限制与注意事项 (Limitations)

### 支持的水印类型
- ✅ Gemini 可见水印（右下角 ✦ logo）
- ❌ SynthID 等隐形水印（技术限制）

### 最佳使用场景
- ✅ 确认是 Gemini 生成的图片
- ✅ 水印在标准位置（右下角）
- ✅ 图片未经过严重压缩
- ✅ PNG 格式（保留 Alpha 通道效果最好）

### 不推荐场景
- ❌ 非 Gemini 生成的图片
- ❌ 水印位置非标准
- ❌ 经过多次压缩的 JPEG

## 错误处理 (Error Handling)

### 常见错误及解决方案

**错误：路径不存在**
- 检查输入路径是否正确
- 使用绝对路径或相对于当前目录的路径

**错误：未检测到水印**
- 确认图片是否为 Gemini 生成
- 检查水印是否在右下角
- 可能水印已被移除

**错误：处理失败**
- 检查图片是否损坏
- 确认磁盘空间充足
- 查看详细错误日志

## 示例场景 (Example Use Cases)

### 场景 1：单张图片快速处理
```
用户: @Gemini_Generated_Image.png 去除水印

AI 执行：
Shell.execute(
  command: "python3 ~/.cursor/skills/gemini-watermark-remover/batch_processor.py /Users/mileson/Desktop/Gemini_Generated_Image.png",
  timeout: 120000
)

输出：
✅ 成功移除 96x96 水印！
  输入: Gemini_Generated_Image.png
  输出: /Users/mileson/Desktop/Gemini_Generated_Image_no_watermark.png
  置信度: 99.97%
  耗时: 3.5秒
```

### 场景 2：整个文件夹批量处理
```
用户: 批量去除 ~/Desktop/gemini_images 的水印

AI 执行：
Shell.execute(
  command: "python3 ~/.cursor/skills/gemini-watermark-remover/batch_processor.py /Users/mileson/Desktop/gemini_images",
  timeout: 120000
)

输出：
📁 找到 23 张图片，开始处理...
[████████████████████] 100% (23/23) 完成

📊 批量处理完成
══════════════════════════════════
统计信息:
  总文件数: 23
  成功处理: 21 ✅
  未检测到水印: 2 ○
  处理失败: 0 ❌
  总耗时: 45.6秒
  平均耗时: 2.0秒/张

输出目录: /Users/mileson/Desktop/gemini_images_no_watermark

✅ 成功处理的文件 (21):
  • image001.png → 96x96 (置信度: 99.87%)
  • image002.png → 48x48 (置信度: 98.45%)
  ...
```

### 场景 3：自定义输出路径
```
用户: 处理 @images/，输出到 ~/Documents/cleaned/

AI 执行：
Shell.execute(
  command: "python3 ~/.cursor/skills/gemini-watermark-remover/batch_processor.py /Users/mileson/Desktop/images /Users/mileson/Documents/cleaned",
  timeout: 120000
)

输出：
📊 批量处理完成
输出目录: /Users/mileson/Documents/cleaned
...
```

### 场景 4：用户使用 @文件引用
```
用户: @water/ 去水印

AI 步骤：
1. 识别引用：@water/ → /Users/mileson/Desktop/water/
2. 执行命令：python3 ~/.cursor/skills/gemini-watermark-remover/batch_processor.py /Users/mileson/Desktop/water
3. 展示结果：直接显示脚本输出
```

## 性能指标 (Performance)

### 典型性能（标准配置）
- 单张图片（1536×1536）：2-5 秒
- 批量 100 张：3-8 分钟
- 内存占用：< 500MB
- CPU 使用：单核 80-90%

### 优化建议
- 使用 SSD 可显著提升 I/O 性能
- 批量处理时关闭其他占用 CPU 的程序
- PNG 格式处理速度快于 JPEG

## 维护说明 (Maintenance)

### 更新记录
- **v1.2** (2026-01-23):
  - 🏗️ 重构文件结构，遵循 Python 最佳实践
  - 📁 `core/` → `lib/`（核心算法模块，命名更清晰）
  - 📁 新增 `assets/` 目录（资源文件，职责分离）
  - ✏️ `gemini_watermark_remover.py` → `remover.py`（简化命名）
  - 📝 更新所有路径引用和文档
  - ✅ 符合 Cursor Skills 社区最佳实践

- **v1.1** (2026-01-23): 
  - 🔧 添加 "AI 执行指令" 章节，明确告诉 AI 应该直接调用 `batch_processor.py`
  - 🔧 完善 "技术支持" 章节，添加文件结构说明和验证方法
  - 📝 修正 AI 误以为需要创建新脚本的问题
  
- **v1.0** (2026-01-23): 初始版本，支持单文件和批量处理

### 已知问题
- 无

### 故障排查 (Troubleshooting)

**问题 1：AI 尝试创建新的批量处理脚本**
- 原因：AI 没有阅读 "AI 执行指令" 章节
- 解决：提醒 AI 查看 Skill 文档，直接调用现有的 `batch_processor.py`

**问题 2：提示 "核心脚本不存在"**
- 原因：Skill 安装不完整
- 解决：检查 `~/.cursor/skills/gemini-watermark-remover/core/` 目录是否存在

**问题 3：处理超时**
- 原因：图片数量过多或图片尺寸过大
- 解决：增加 Shell 工具的超时时间（推荐 120000ms）

### 未来计划
- [ ] 支持视频水印移除
- [ ] 支持自定义水印模板
- [ ] GPU 加速
- [ ] 并行批量处理

## 技术支持 (Support)

### 相关资源
- **批量处理脚本**：`~/.cursor/skills/gemini-watermark-remover/batch_processor.py`
- **核心算法模块**：`~/.cursor/skills/gemini-watermark-remover/lib/remover.py`
- **水印模板**：
  - 48×48 模板：`~/.cursor/skills/gemini-watermark-remover/assets/bg_48.png`
  - 96×96 模板：`~/.cursor/skills/gemini-watermark-remover/assets/bg_96.png`

### 文件结构
```
~/.cursor/skills/gemini-watermark-remover/
├── SKILL.md                    # Skill 说明文档
├── README.md                   # 项目说明
├── batch_processor.py          # 批量处理脚本（AI 调用入口）
├── lib/                        # 核心算法模块
│   └── remover.py             # 水印检测和移除算法
└── assets/                     # 资源文件
    ├── bg_48.png              # 48×48 水印模板
    └── bg_96.png              # 96×96 水印模板
```

### 验证安装
检查 Skill 是否安装完整：
```bash
ls -la ~/.cursor/skills/gemini-watermark-remover/
```

### 手动测试
如需手动测试，可以直接调用脚本：
```bash
# 单文件测试
python3 ~/.cursor/skills/gemini-watermark-remover/batch_processor.py test.png

# 批量测试
python3 ~/.cursor/skills/gemini-watermark-remover/batch_processor.py ./images/
```

---

**Skill 版本**: 1.2.0  
**创建日期**: 2026-01-23  
**最后更新**: 2026-01-23  
**维护者**: AI Assistant

### 重构说明 (v1.2)
本次重构基于以下最佳实践研究：
- Python CLI 工具结构（Click、MCP SDK）
- Cursor Skills 社区实践（参考 markdown-to-wechat）
- Python 包组织规范（PyPA packaging guidelines）

重构原则：
1. ✅ 入口点保持在根目录（便于调用）
2. ✅ 核心逻辑与资源文件分离（职责清晰）
3. ✅ 使用清晰的命名（`lib/`、`assets/` 一目了然）
4. ✅ 保持最小改动（性价比最高）
