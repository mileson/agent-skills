# 提示词增强指南 (Prompt Enhancement Guide)

当需要为 Markdown 文本中的占位符生成配图时，Agent 必须遵循以下规范来扩写提示词。

## 核心公式
**Final Prompt = [Subject & Action] + [Contextual Details]**
*(注意：风格后缀将由脚本通过套用 `styles.yaml` 自动添加，Agent 只需要负责核心画面描述的构建)*

## 提取步骤

1. **提取主题与动作 (Subject & Action)**
   从占位符的 `alt` 文本中提取。
   *示例*：`![用户登录注册流程](images/login.png)` -> "A user interacting with a login and registration flow"

2. **分析上下文提炼细节 (Contextual Details)**
   截取占位符前后各约 300 字的上下文，重点提炼以下维度：
   - **核心实体**：具体的人、物、界面（如：发光的安全锁，绿色的盾牌）。
   - **交互关系**：实体之间的联系（如：数据流从手机汇聚到云端服务器）。
   - **氛围色彩**：文章的情绪基调（如：科技感、温暖、明亮）。
   - **隐喻转化**：如果遇到“高并发”、“安全防御”、“云原生”等抽象技术词汇，将其转化为具象的视觉隐喻（如：“多条川流不息的高速公路”、“坚不可摧的半透明能量罩”）。

3. **处理图片中的文字 (Typography/Text in Image)**
   - **默认无文字 (Default to NO text)**：这是最重要的一条！除非场景必须，否则**绝对不要**在提示词中加入任何文字指令，以免画面中出现乱码。
   - **哪些场景需要文字？**
     1. 占位符或上下文中明确要求图中有特定文字（如“截图中显示处理成功”）。
     2. **特定类型的配图**不可避免地需要文字标注（如：业务流程图 Flowchart、系统架构图、功能说明书图解、信息图表 Infographic 等）。
   - **需要文字时的语言规则 (极其重要)**：
     - **未指定语言 -> 强制要求中文并必须提供具体中文词汇**：大模型在生成图表或文字时，如果不给它具体的中文词汇，它往往会默认生成英文字母或乱码。因此，如果场景需要文字但用户没指定，你**必须自己在提示词中补充一些符合上下文的具体中文词汇（用引号括起来）**，不能只泛泛地写 `with Simplified Chinese text labels`。
       *(错误提示词示例❌：`with Simplified Chinese text labels` - 这会导致模型依然生成英文或乱码)*
       *(正确提示词示例✅：`with Simplified Chinese text such as "开始", "系统架构", "用户端"` - 这样模型才有具体的中文可以写)*
     - **指定语言 -> 严格遵循**：如果明确指定了语言（如英文、繁体中文），则严格遵循。
       *(提示词示例：`with English text "ERROR"`)*

4. **翻译与组合**
   将以上部分组合成一段连贯的**英文描述**。提示词应多用名词短语和形容词，避免复杂的长句和语法结构。

## 实战示例

**原文上下文**：
"...为了保障用户数据的绝对安全，我们的系统采用了全新的端到端加密机制。当用户在设备上发起请求时，数据会被封装在加密通道中，即使在网络传输过程中被拦截，也无法被解密。
`![端到端加密机制](images/encryption.png)`
这套机制极大地提升了系统的抗风险能力，使得我们的平台能够抵御外部的各类攻击..."

**Agent 提取与组合过程**：
- *Subject*: End-to-end encryption mechanism
- *Details*: Data packets encapsulated in a glowing secure tunnel, traveling from a smartphone to a cloud server, unbreakable transparent energy shield, high-tech atmosphere, blue and green color tones.
- *传给生成脚本的参数 (--prompt)*: "End-to-end encryption mechanism, data packets encapsulated in a glowing secure tunnel, traveling from a smartphone to a cloud server, unbreakable transparent energy shield, high-tech atmosphere, blue and green color tones"

*(脚本会自动将这个 prompt 与你指定的模板后缀例如 3d_isometric 组合成发给大模型的最终指令)*
