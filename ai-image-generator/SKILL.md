---
name: ai-image-generator
description: |
  Comprehensive AI image generation tool for any visual needs (e.g., presentation slides, chat stickers, UI assets, conceptual art). CRITICAL: When using this skill, you MUST determine the exact local file path where the image should be saved. If the user doesn't provide a path, you must either ask them or determine a logical default path in the workspace before proceeding. Use this skill when requested to generate, create, or draw an image.
---

# 通用生图助手 (AI Image Generator)

这是一个通用 AI 图像生成工具。当你被要求生成图片、配图、绘制插画或表情包时，你必须严格遵循以下工作流。

## ⚠️ 核心关卡 (The Checkpoint) - 路径获取

**在调用任何生图脚本之前，你必须集齐三大核心参数：`画面描述`、`风格倾向`、`绝对保存路径`。**

**路径阻断规则**：
- 如果用户指令中**未提供**保存路径（例如只说了“帮我画个苹果”），你必须**暂停生图**，自动推断一个合理的默认绝对路径（例如项目根目录下的 `downloads/images/apple.png`）或主动询问用户。
- 只有当你明确知道图片要保存在哪个绝对路径下（文件必须有 `.png` 或 `.jpg` 等后缀），才能继续下一步。

## 工作流：生成图像

### 1. 提示词增强 (Prompt Enhancement)

将用户口语化的中文要求扩写为具备高画面表现力的英文提示词。
**必须阅读并遵循：[references/prompt-enhancement-guide.md](references/prompt-enhancement-guide.md)**，了解如何提炼核心实体、添加光影细节，以及构建最终的 `--prompt`。

### 2. 匹配风格 (Style Selection)

查阅 `templates/styles.yaml`（你只需读取其 key），根据用户的诉求选择最合适的风格 ID。
常见的内置风格包括：`ppt_graphic`, `3d_isometric`, `chat_sticker`, `photorealistic`, `3d_icon`, `anime_style` 等。

### 3. 执行脚本落盘 (Execution)

使用 Python 脚本生成图片，脚本将自动处理请求并将生成的图片保存到你指定的绝对路径。

**命令模板**：
```bash
python3 ~/.cursor/skills/ai-image-generator/scripts/generate_image.py \
  --prompt "A cute fluffy cat showing an OK gesture" "A dog smiling" \
  --style "chat_sticker" \
  --output "/绝对路径/cat_ok.png" "/绝对路径/dog_smile.png" \
  --reference_image "/绝对路径/ref.png" \
  --size "1:1" \
  --resolution "1K"
```

**参数说明：**
- `--prompt`: 提炼后的纯画面英文描述。**支持传入多个提示词（用空格分隔的多个字符串）以实现并发生成**。
- `--style`: `styles.yaml` 中的键名（例如 `chat_sticker`）。
- `--output`: **[极其重要]** 图片必须保存的确切本地路径。**注意：传入的路径数量必须与 `--prompt` 数量完全一致！** 如果 `--n` 大于 1，脚本会自动在文件名后追加 `_1`, `_2` 等后缀。
- `--reference_image`: (可选) 参考图的本地路径或 URL（图生图）。如果提供 1 张参考图，则所有提示词都会使用该参考图；也可以提供多张与提示词数量一致的参考图。
- `--size`: 比例，如 `16:9`, `1:1`, `4:3`。默认推荐 `16:9`，但像表情包/头像推荐 `1:1`。
- `--n`: 每个提示词生成图片的数量，默认为 1。如果用户需要针对同一个提示词同时生成多张图，可以指定此参数。
- `--resolution`: 分辨率，默认为 `1K`，也可选 `2K`。

### 4. 结果交付 (Delivery)

脚本执行成功后：
1. 图片已实际下载到 `--output` 指定的路径。
2. 你需要向用户汇报结果。
3. 尽可能使用 Markdown 语法 `![描述](绝对路径或相对路径)` 在聊天框中渲染并展示生成的图片给用户看。

## 依赖说明
- **API 通道**：生图接口请求基于 APIMart Gemini 3 Pro Image。
- **凭证管理**：底层脚本依赖 `secrets-vault` 技能自动获取命名空间 `apimart_image` 下的 token，你无需手动处理鉴权。