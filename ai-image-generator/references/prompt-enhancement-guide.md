# 提示词增强指南 (Prompt Enhancement Guide)

当需要为用户生成图像时，Agent 必须遵循以下规范，将用户简短的自然语言要求扩写为具备高画面表现力的英文提示词。

## 核心公式
**Final Prompt = [Subject & Action] + [Contextual Details]**
*(注意：风格后缀将由脚本通过套用 `styles.yaml` 自动添加，Agent 只需要负责核心画面描述的构建)*

## 提取与扩写步骤

1. **提取主题与动作 (Subject & Action)**
   从用户的指令中提取他想要画的核心主体是什么，在做什么。
   *示例*：用户说“帮我画个程序员在改bug” -> "A programmer debugging code late at night"

2. **补充画面细节 (Contextual Details)**
   根据用户的语境（如 PPT 配图、聊天表情、写实摄影等），自主丰富以下维度：
   - **核心实体细节**：具体的人、物的外貌、穿着、特征（如：戴着黑框眼镜，盯着发光的双屏幕）。
   - **背景环境**：主体所处的环境（如：摆满咖啡杯的昏暗办公室）。
   - **光影与色彩**：画面的情绪基调与照明效果（如：屏幕反射的蓝光，赛博朋克氛围）。
   - **隐喻转化**：如果用户要求表达“数据安全”、“高并发”等抽象概念，将其转化为具象的视觉隐喻（如：“发光的半透明数据隧道”，“坚不可摧的能量护盾”）。

3. **翻译与组合**
   将以上两部分组合成一段连贯的**英文描述**。提示词应多用名词短语和形容词，避免复杂的长句和语法结构。

4. **处理图片中的文字 (Typography/Text in Image)**
   - **默认无文字 (Default to NO text)**：这是最重要的一条！除非场景必须，否则**绝对不要**在提示词中加入任何文字指令，以免画面中出现乱码。
   - **哪些场景需要文字？**
     1. 用户明确要求图中有特定文字（如“牌子上写着XXX”）。
     2. **特定类型的图表**不可避免地需要文字标注（如：流程图 Flowchart、操作说明书指南、数据仪表盘图表、信息图表 Infographic 等）。
   - **需要文字时的语言规则 (极其重要)**：
     - **未指定语言 -> 强制要求中文并必须提供具体中文词汇**：大模型在生成图表或文字时，如果不给它具体的中文词汇，它往往会默认生成英文字母或乱码。因此，如果场景需要文字但用户没指定，你**必须自己在提示词中补充一些符合场景的具体中文词汇（用引号括起来）**，不能只泛泛地写 `with Simplified Chinese text labels`。
       *(错误提示词示例❌：`with Simplified Chinese text labels` - 这会导致模型依然生成英文或乱码)*
       *(正确提示词示例✅：`with Simplified Chinese text such as "开始", "处理", "结束", "系统架构", "用户端"` - 这样模型才有具体的中文可以写)*
     - **指定语言 -> 严格遵循**：如果明确指定了语言（如英文、繁体中文），则严格遵循。
       *(提示词示例：`with English text "ERROR"`)*

## 实战示例

**场景 1：PPT 抽象概念配图**
- *用户输入*: "我需要在 PPT 里放一张表示『全球数据同步』的图，风格专业点"
- *Agent 扩写思考*: PPT需要大气、科技感。实体是地球和数据流。
- *Subject*: Global data synchronization
- *Details*: A glowing holographic earth in the center, bright digital data streams connecting different continents, high-tech network nodes, dark blue background with digital grids.
- *传给生成脚本的参数 (--prompt)*: "Global data synchronization, a glowing holographic earth in the center, bright digital data streams connecting different continents, high-tech network nodes, dark blue background with digital grids"
- *选择的风格 (--style)*: `ppt_graphic` 或 `3d_isometric`

**场景 2：聊天表情包**
- *用户输入*: "帮我画个猫咪说OK的表情包"
- *Agent 扩写思考*: 表情包需要夸张、可爱、有张力。
- *Subject*: A cute fluffy cat showing an OK gesture
- *Details*: Big shiny eyes, joyful expression, wearing a red tiny scarf, holding up one paw making an OK sign.
- *传给生成脚本的参数 (--prompt)*: "A cute fluffy cat showing an OK gesture, big shiny eyes, joyful expression, wearing a red tiny scarf, holding up one paw making an OK sign"
- *选择的风格 (--style)*: `chat_sticker`

*(提示：不要在 prompt 里加 "white background", "8k" 等词汇，如果你选择的 `styles.yaml` 模板里已经有了，避免重复累赘)*