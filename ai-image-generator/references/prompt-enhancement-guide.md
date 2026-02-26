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
   - **默认无文字**：除非用户明确要求（或场景绝对需要），否则**不要**在提示词中加入要求生成文字的指令。图像生成模型在处理复杂文字时容易出错。
   - **简体中文优先**：如果用户要求“图上写着 XXX”，或者该场景（如 UI 界面、海报）不可避免地需要文字，并且用户没有指定语言，请**默认在提示词中加上生成简体中文的要求**。
     *(提示词示例：`with Simplified Chinese text "数据安全"`)*
   - **遵循用户指定语言**：如果用户明确指定了文字的语言（如“图上写上英文的 ERROR”或“繁体中文”），则严格按照用户的要求在提示词中注明。
     *(提示词示例：`with English text "ERROR"` 或 `with Traditional Chinese text "數據安全"`)*

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