---
name: article-illustrator
description: 文章配图助手。扫描 Markdown 文件中的图片占位符，结合上下文提炼视觉细节并应用预设风格模板，通过 APIMart Gemini API 生成高质量英文配图并精准存入占位符指定路径。当用户要求“配图”、“为文章生成插图”、“处理图片占位符”时触发。
---

# Article Illustrator (文章配图助手)

## 核心工作流：占位符驱动配图

当用户请求为某篇文章生成配图时，Agent 必须遵循以下流程：

### 1. 扫描与读取
- 使用 `Read` 或 `Shell` 工具读取用户指定的 Markdown 文章。
- 扫描文件中的图片占位符。
- **⚠️ 核心过滤规则（极其重要）**：
  - **只处理** `alt` 文本中带有 `[AI生图]` 标记的占位符（例如：`![[AI生图] 数据在安全隧道中传输](Materials/Medias/images/concept.png)`）。
  - **严格跳过/忽略** 带有 `[待截图]` 标记的占位符（例如：`![[待截图] 用户登录页面](...)`）以及没有任何标记的普通图片，这些是留给人类作者手动提供的真实系统截图，千万不能用 AI 假图覆盖！

### 2. 提示词增强与构建
针对每一个待处理的 **`[AI生图]`** 占位符，执行以下操作：
- 读取占位符前后各约 300 字的上下文。
- 提取 `alt` 中的描述（例如从 `![[AI生图] 数据加密传输]` 中提取“数据加密传输”）。
- 遵循 `references/prompt-enhancement-guide.md` 中的规范，提炼核心实体、隐喻和画面氛围。
- 查阅 `templates/styles.yaml`，选择一个最适合当前场景的风格（例如 `3d_isometric` 或 `minimalist_ui`）。
- **注意：Agent 不需要自己生成最终完整的提示词，只需将提炼的纯画面描述（英文）作为 `--prompt`，风格键名作为 `--style` 传递给生图脚本，脚本会自动拼接。**

### 3. 生图与落盘
提取所有占位符后，**并发一次性提交**所有的生成请求（通过传入多个 `--prompt` 和 `--output` 参数给脚本），并确保严格按照占位符的路径保存。

**使用示例：**
```bash
python3 ~/.cursor/skills/article-illustrator/scripts/generate_image.py \
  --prompt "A user interacting with a login and registration flow..." "Another prompt for second image..." \
  --style "3d_isometric" \
  --output "/绝对路径/login.png" "/绝对路径/second.png" \
  --size "16:9" \
  --resolution "1K"
```

**参数说明：**
- `--prompt`: 提炼后的纯画面英文描述。**支持传入多个提示词（用空格分隔的多个字符串）以实现并发生成**。
- `--style`: `styles.yaml` 中的键名（如 `flat_concept`, `3d_isometric`, `minimalist_ui`, `metaphorical_scene`）。
- `--output`: 图片必须保存的确切本地路径，**必须**与 Markdown 占位符指向的相对路径对齐并保持绝对一致！**注意：传入的路径数量必须与 `--prompt` 数量完全一致！**
- `--size`: 比例，如 `16:9`, `1:1`, `4:3`。
- `--resolution`: 分辨率，默认为 `1K`，也可选 `2K`。
- `--force`: (可选) 强制重新生成，忽略本地缓存的任务凭证。

### 4. 循环与完成
所有目标配图生成完毕后，向用户汇报最终生成的图片列表和落盘路径。

## 🛡️ 资金保护与重试规则 (Fund Protection Rules)

生图 API 调用会消耗真实资金。你必须严格遵守以下规则：
1. **绝不自动重试**：如果脚本执行失败（例如网络超时、524 错误、轮询超时等），你**绝对不能**擅自重新执行生图命令。
2. **强制汇报拦截**：遇到错误时，必须立即中止当前工作流，向用户汇报报错信息以及已获取到的 `task_id`（如果有）。
3. **把决定权交给用户**：询问用户是选择“使用相同命令继续轮询（脚本会自动读取本地缓存的 task_id）”、“放弃当前图”还是“使用 `--force` 参数强制重新扣费生成”。

## 依赖说明
- **API 通道**：生图接口请求 `https://api.apimart.ai/v1/images/generations`，基于 Gemini 3 Pro Image 模型。
- **凭证管理**：依赖 `secrets-vault` 技能，通过 `apimart_image` 命名空间获取 API Token。