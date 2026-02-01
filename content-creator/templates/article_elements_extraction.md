# 任务事项：初始化与文章要素抽取（Initial And Content Element Extraction）

## 执行规则
1.  **严格遵循**: 严格按照下方的"待办事项"从上到下逐一执行，确保流程的完整性。
2.  **状态实时更新**: 每完成一个待办事项，立即更新其状态为 `[✅]`。当所有子任务完成后，父任务状态也应更新为 `[✅]`。
3.  **任务连续性**: 若任务中断，再次启动时需严格依据本文件的待办状态，从上一个未完成的任务开始，确保任务的连续性和目标一致性。

## 待办事项

- [ ] **0. 前置检查 (Pre-flight Check: Platform Confirmation)**
    - [ ] 0.1 **检查初始指令**: 分析用户的初始请求，检查是否已明确提供了目标发布平台列表（例如，在请求中直接说明 “请帮我写一篇发布在微信公众号和小红书的文章”）。
    - [ ] 0.2 **处理信息缺失**:
        *   如果初始指令中**未包含**明确的发布平台，**则必须暂停所有后续任务**。
        *   然后，主动向用户提问：“**为了更好地为您定制内容，请明确您计划发布的平台（例如：微信公众号、小红书、知乎）。我将在获得您的回复后继续执行。**”
        *   **[关键]** 在收到用户回复前，保持等待状态。
    - [ ] 0.3 **确认并记录**: 一旦从初始指令或用户后续回复中获得平台列表，将其记录下来，作为后续步骤的**关键输入**。

- [ ] **1. 初始化**
    - [ ] 1.1 确认“0. 前置检查”已完成后，生成并执行终端指令，将模板 `Templates/article_elements_extraction.md` 与 `Templates/article_creation.md` 复制到 `Articles/<文章名称>/` 目录中。

- [ ] **2. 素材整理与预处理**
    - [ ] 2.1 确认原始文件已放入 `Material/` 目录。
    - [ ] 2.2 **AI 辅助素材预处理**：读取 `Material/` 目录下所有文档，总结每个文档的核心观点、关键数据和有趣事实，作为下一步提炼的参考。
    - [ ] 2.3 **认知一致性校正**: 必须熟读 `Memories/knowledge_dict.json` 内的关键背景知识，来了解一些关键知识，以及对`Material/`内的原始内容进行校正，比如有可能原始信息将`超级峰`误读为`超级风`或将`芝士相机`误读为`知识相机`等情况，此时需要校正为正确内容，避免影响后续的创作。

- [ ] **3. 信息提炼**
    - [ ] 3.1 使用联网搜索功能梳理**相关热点**，并结合上一步的素材摘要。
    - [ ] 3.2 依据下方 JSON 模板，并**严格使用在步骤 0.3 中已确认的平台列表**来填充 `publish_platforms` 字段，完成所有其他字段的填写，最终保存为 `extracted_meta.json`。
    - [ ] 3.3 必填字段检查：`trending_topics`, `audience`, `purpose`, `brand_voice`, `writing_style`, `structure`, `key_points`, `publish_platforms`, `output_constraints`。

- [ ] **4. 校验 & 确认**
    - [ ] 4.1 验证 `extracted_meta.json` 格式无误。
    - [ ] 4.2 将 JSON 全文输出至聊天窗口，等待用户回复“**继续**”后，触发下一步骤。

- [ ] **5. 触发写作**
    - [ ] 5.1 读取 `Articles/<文章名称>/article_creation.md` 文件，开始下一阶段的内容创作任务。

---

### `extracted_meta.json` 示例（需基于实际素材和用户确认的平台重写）

```json
{
    "trending_topics": [
      "微信小程序 AI 热门模板破圈",
      "ChatGPT-4o 实时语音对话功能演示",
      "Sora 如何改变短视频创作生态"
    ],
    "audience": [
      {
        "tag": "AI 独立开发者",
        "age_range": "25-40",
        "skill_level": "中高级",
        "pains": ["工具链碎片化", "技术迭代过快跟不上", "内容变现困难"],
        "emotional_triggers": ["效率焦虑", "同行压力", "求新欲"]
      },
      {
        "tag": "内容创作者/技术小白",
        "age_range": "18-30",
        "skill_level": "入门",
        "pains": ["AI 工具上手门槛高", "缺少结构化的实战案例", "想法无法落地"],
        "emotional_triggers": ["好奇心", "对新技术的渴望", "寻求安全感和确定性"]
      }
    ],
    "purpose": ["教学", "品牌转化", "社区引流"],
    "brand_voice": {
      "mission": "让每个人都能用 AI 创造价值",
      "values": ["开放", "普惠", "幽默", "实用"],
      "tone_adjectives": ["友好", "数据驱动", "鼓励性"]
    },
    "writing_style": {
      "register": "口语化",
      "sentence_length": "短句为主，穿插少量长句增加节奏感",
      "humor_level": "轻度幽默，以技术梗和自嘲为主",
      "value_embed": "在教程中潜移默化地传递'技术普惠'和'终身学习'的理念"
    },
    "structure": {
      "model": "PAS (Problem, Agitate, Solution)",
      "outline": [
        "Hook: 以一个 AI 开发者熬夜调试、重复工作的痛苦场景作为开头。",
        "Problem: 明确指出当前 AI 应用开发和内容创作工作流中普遍存在的痛点（工具链断裂、流程繁琐、效率低下）。",
        "Agitate: 放大这些痛点带来的负面后果，如“在重复劳动中消磨创造力”、“错失热点时机”等，引发读者共鸣。",
        "Solution: 正式引入 'Vibe Coding' 理念和 'Cursor Workflow' 工具，将其作为解决上述所有问题的“银色子弹”，并分点介绍其核心优势。",
        "Demo: 提供一个'5分钟上手'的极简实战案例，引导读者完成一个具体的小任务。",
        "CTA: 呼吁读者“停止重复，开始创造”，并提供 Vibe 模板的下载链接，鼓励其立即体验。"
      ]
    },
    "key_points": [
      "Vibe Coding 的核心三步法：定义蓝图、AI 执行、人类确认。",
      "如何用 Cursor Workflow 自动化 80% 的技术文章撰写流程。",
      "分享 3 个可以直接使用的文章要素抽取模板（JSON）。"
    ],
    "humanization": {
      "style_quirks": [
        "允许使用括号来补充说明或进行吐槽（就像现在这样）。",
        "在段落结尾，有时会用一个独立的、引发思考的短句来收尾。",
        "避免使用“首先”、“其次”、“此外”、“综上所述”等过于正式的连接词，多用生活化的口语过渡。"
      ]
    },
    "seo": {
      "primary_keywords": ["Vibe Coding", "AI 编程", "Cursor AI", "自动化写作"],
      "meta_description": "学习如何使用 Cursor 和 Vibe Coding 理念，将 AI 无缝融入你的工作流，实现高质量技术文章的自动化生成。告别重复，拥抱创造。",
      "canonical_url": "https://example.com/blog/vibe-coding-with-cursor"
    },
    "quality_targets": {
      "readability_metric": "Flesch-Kincaid",
      "min_score": 65,
      "plagiarism_free": true
    },
    "assets": {
      "images_needed": 3,
      "image_placeholders": "在需要配图的地方，使用 `[图片：一句话描述图片内容]` 格式占位",
      "alt_text_required": true
    },
    "publish_platforms": {
      "微信公众号": {
          "audience": "广泛但偏专业，重知识深度与干货",
          "tone": "正式、可信、适量故事化",
          "length": "1500-3000 字",
          "title_prefix": "",
          "format_rules": ["段落 3-5 行", "首段引痛点", "图片占位符如`[图片:配图主题意向内容与目的]`", "结尾行动号召"],
          "humanization": "错别字 ≤ 3，保留专业术语"
        },
      "小红书": {
        "audience": "18-35 岁年轻女性，以及年轻互联网、白领男性用户为主，注重品质与审美",
        "tone": "第一人称 + Emoji，故事化分享",
        "length": "300-800 字",
        "title_prefix": "【体验】/【避坑】等",
        "format_rules": ["钩子开头", "3-5 行分段", "#话题 标签"],
        "humanization": "每 200 字 ≥ 1 错别字，少用公式化过渡词"
    },
    "output_constraints": {
      "format": "Markdown",
      "word_count": "1500-2000",
      "code_snippet_language": "json"
    }
  }
}
```