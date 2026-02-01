---
name: appstore-screenshot-generator
description: 使用 AI 图像生成技术创建专业的 App Store 商店图。通过 XcodeBuildMCP 自动截取 iOS 模拟器截图，结合参考模板和优化的提示词，调用 Gemini API 生成高质量的 App Store 营销图片。适用于需要批量生成多语言、多尺寸商店图的场景。
---

# App Store Screenshot Generator Skill

这个 Skill 指导使用 AI 图像生成技术创建专业的 App Store 商店图。整个流程自动化程度高，从截图到生成营销图片一气呵成。

## Skill 文件结构

```
appstore-screenshot-generator/
├── SKILL.md                 # 本文件 - 主 Skill 指导文档
├── config.yaml              # 核心配置 - 包含所有预设 prompt 模板
├── .env                     # 环境变量配置 - 直接编辑填写 API Key
├── scripts/                 # Python 脚本（自动加载 .env）
│   ├── gemini_client.py     # Gemini API 客户端
│   ├── prompt_builder.py    # Prompt 构建器
│   └── image_processor.py   # 图像处理器
├── references/              # 参考文档
│   └── app-store-guidelines.md  # App Store 设计指南
├── assets/                  # 资源文件
│   └── templates/           # 参考模板图片目录
│       ├── photography/     # 摄影类模板
│       ├── fitness/         # 健身类模板
│       ├── productivity/    # 生产力类模板
│       └── gaming/          # 游戏类模板
└── examples/                # 生成示例输出目录
```

## 工作流程概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    App Store Screenshot Generator                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. 截图采集          2. 模板选择          3. AI 生图                    │
│  ┌──────────┐        ┌──────────┐        ┌──────────┐                   │
│  │XcodeBuild│   →    │config.yaml│  →    │ Gemini   │                   │
│  │   MCP    │        │ 预设模板  │        │   API    │                   │
│  └──────────┘        └──────────┘        └──────────┘                   │
│       ↓                   ↓                   ↓                          │
│  iOS 模拟器截图      选择应用类型模板       生成营销图片                    │
│                      (photography等)                                    │
│                                                                          │
│  4. 输出处理                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ image_processor.py: 多尺寸适配 × 多语言输出                        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 快速开始

### 步骤 1: 配置环境变量

直接编辑 skill 目录下的 `.env` 文件：

```bash
# 打开配置文件
open ~/.claude/skills/appstore-screenshot-generator/.env

# 或使用编辑器
vim ~/.claude/skills/appstore-screenshot-generator/.env
```

**必填配置：**
```bash
GEMINI_API_KEY=your_google_ai_studio_api_key
```

**可选配置（使用 Cloudflare AI Gateway）：**
```bash
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_GATEWAY_ID=your_gateway_name
```

> 脚本会自动从 skill 目录加载 `.env`，无需手动 export。

### 步骤 2: 验证 XcodeBuildMCP

```bash
claude mcp list
# 确认看到 XcodeBuildMCP
```

### 步骤 3: 使用 Skill

在 Claude Code 中说：

```
使用 appstore-screenshot-generator skill，为我的应用生成 App Store 商店图。
应用类型是摄影类，标题用"捕捉完美瞬间"。
```

---

## 预设 Prompt 模板

所有预设模板定义在 `config.yaml` 中，包含以下类型：

| 模板名称 | 适用类型 | 特点 |
|---------|---------|------|
| `base` | 通用 | 适合所有类型的基础模板 |
| `photography` | 摄影/相机 | 深色背景、镜头光效、专业感 |
| `fitness` | 健身/健康 | 能量感、动态效果、激励风格 |
| `productivity` | 生产力/工具 | 简约干净、留白设计、专业可信 |
| `social` | 社交/生活 | 温暖色调、连接感、活力风格 |
| `gaming` | 游戏 | 视觉冲击、特效元素、沉浸感 |
| `finance` | 金融/商务 | 深蓝金色、安全可信、专业感 |

### 使用 prompt_builder.py 生成 Prompt

```python
from scripts.prompt_builder import PromptBuilder, photography_prompt

# 方式 1: 使用快捷函数
prompt = photography_prompt(headline="Capture Perfect Moments")

# 方式 2: 使用 PromptBuilder 类
builder = PromptBuilder()
prompt = builder.build_quick_prompt(
    app_type="photography",
    headline="专业级照片",
    language="zh"
)
```

### 预设标题选项

每个模板都预设了多语言标题选项（见 config.yaml），例如：

**摄影类 (photography):**
- EN: "Capture Perfect Moments", "Pro-Level Photos", "Photography Reimagined"
- ZH: "捕捉完美瞬间", "专业级照片", "重新定义摄影"

**健身类 (fitness):**
- EN: "Transform Your Body", "Track Every Rep", "Crush Your Goals"
- ZH: "改变你的身体", "追踪每一次训练", "粉碎你的目标"

---

## 详细执行流程

### 步骤 1: 截图采集

使用 XcodeBuildMCP 截取 iOS 模拟器截图：

1. 确保 iOS 模拟器正在运行目标应用
2. 导航到需要截图的界面
3. 调用 XcodeBuildMCP 的 `screenshot` 工具
4. 截图会以 Base64 格式返回

```
// Claude 会自动使用 XcodeBuildMCP
使用 XcodeBuildMCP 截取当前模拟器截图
```

### 步骤 2: 选择应用类型和模板

根据应用类型从 `config.yaml` 选择对应模板：

- 摄影/相机应用 → `photography` 模板
- 健身/健康应用 → `fitness` 模板
- 工具/效率应用 → `productivity` 模板
- 社交应用 → `social` 模板
- 游戏应用 → `gaming` 模板
- 金融应用 → `finance` 模板

### 步骤 3: 构建 Prompt

使用 `prompt_builder.py` 或直接从 `config.yaml` 获取模板，替换变量：

- `{headline_text}` → 标题文案
- `{device_model}` → 设备型号
- `{primary_color}` → 主色调
- `{width}` / `{height}` → 输出尺寸

### 步骤 4: 调用 Gemini API 生成图片

使用 `gemini_client.py` 调用 API：

```python
from scripts.gemini_client import GeminiClient

client = GeminiClient()
result = client.generate_image(
    prompt=prompt,
    input_image="screenshot.png",
    output_path="appstore_output.png"
)
```

### 步骤 5: 多尺寸输出

使用 `image_processor.py` 生成所有 App Store 需要的尺寸：

```python
from scripts.image_processor import ImageProcessor

processor = ImageProcessor()
result = processor.generate_all_sizes(
    input_path="appstore_output.png",
    output_dir="./outputs",
    sizes=["iphone_67", "iphone_65"]
)
```

---

## Gemini API 调用说明

### 方式一：直接调用 Google AI Studio

```bash
curl -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent" \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -d '{
    "contents": [{
      "parts": [
        {"inline_data": {"mime_type": "image/png", "data": "<BASE64>"}},
        {"text": "<PROMPT>"}
      ]
    }],
    "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]}
  }'
```

### 方式二：通过 Cloudflare AI Gateway

```bash
curl -X POST \
  "https://gateway.ai.cloudflare.com/v1/${CLOUDFLARE_ACCOUNT_ID}/${CLOUDFLARE_GATEWAY_ID}/google-ai-studio/v1beta/models/gemini-2.5-flash-image:generateContent" \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: ${GEMINI_API_KEY}" \
  -d '{...同上...}'
```

---

## App Store 截图规格

### 必需尺寸

| 设备 | 像素尺寸 | 配置键名 |
|-----|---------|---------|
| iPhone 6.7" | 1290×2796 | `iphone_67` |
| iPhone 6.5" | 1284×2778 | `iphone_65` |

### 可选尺寸

| 设备 | 像素尺寸 | 配置键名 |
|-----|---------|---------|
| iPhone 5.5" | 1242×2208 | `iphone_55` |
| iPad 12.9" | 2048×2732 | `ipad_129` |
| iPad 11" | 1668×2388 | `ipad_11` |

---

## 设计最佳实践

详细设计指南请参考 `references/app-store-guidelines.md`，核心要点：

1. **首图最关键** - 决定 70%+ 下载转化
2. **文案简洁** - 2-6 个词传达核心价值
3. **视觉一致** - 统一风格、配色、字体
4. **设备 Mockup** - 使用最新设备型号
5. **本地化** - 针对不同市场调整文案

---

## 常见问题

### Q: API 调用失败？
1. 检查 `GEMINI_API_KEY` 是否正确
2. 确认 API 配额未超限
3. 检查网络连接

### Q: 生成质量不佳？
1. 提供更清晰的原始截图
2. 使用更具体的提示词（颜色代码、精确位置）
3. 尝试不同的模板类型

### Q: XcodeBuildMCP 截图失败？
1. 确保模拟器正在运行
2. 运行 `claude mcp list` 确认 MCP 已加载
3. 重启 Claude Code

---

## 参考资源

- [Apple App Store 截图规格](https://developer.apple.com/help/app-store-connect/reference/screenshot-specifications/)
- [Gemini API 图像生成文档](https://ai.google.dev/gemini-api/docs/image-generation)
- [Cloudflare AI Gateway](https://developers.cloudflare.com/ai-gateway/)
- [XcodeBuildMCP GitHub](https://github.com/cameroncooke/XcodeBuildMCP)
- [How to prompt Gemini for best results](https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/)

---

*此 Skill 由 Claude Code 创建，用于自动化 App Store 商店图生成流程。*
