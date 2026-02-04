![cover_image](https://mmbiz.qpic.cn/mmbiz_jpg/2icSMc1VBIYo7SqQxJ36asCuia5dlJ5SVEjakuYgHZK4iblC9jfJZpLE8h8cOuBLDGOUwwPTCjyoTPiaCBGa3iawpwQ/0?wx_fmt=jpeg)

V3→R1→V3.2｜一文看懂 DeepSeek 技术演进
=============================

原创 金色传说大聪明 金色传说大聪明 [赛博禅心](javascript:void\(0\);)

在小说阅读器中沉浸阅读

**DeepSeek，喜欢过节发模型**

DeepSeek 发布时间线，红色是主要版本

这点，老美也很抱怨  
`“去年感恩节发 V3，今年感恩节发 V3.2，淦！”`

但每个人，也深有期待  
V3.2 的性能已经追平 GPT-5 和 Gemini 3.0 Pro，而且开源

V3.2 和顶级闭源模型的 benchmark 对比，来自 DeepSeek V3.2 技术报告

接下来，让我们一起完整看看 DeepSeek 从 V3 到 V3.2 的演进过程中，看看每个版本改了什么，为什么改，以及怎么实现的

内容基于 Sebastian Raschka 的技术分析，也大量用到了他的插图；当然，更多的是我自己的补充

时间线
---

去年12月，`DeepSeek-V3` 发布  
**只用了 500 多万美金的成本，带来了不输 Claude 3.5 的成绩，并开源**

今年 1 月的，`DeepSeek R1` 发布  
**这是个推理模型，对标 OpenAI 的 o1，价格只有 OpenAI 的几十分之一**

`R1` 和 `V3` 用的是同一个架构，区别在训练方法

V3/R1 的架构图

`R1` 之后，DeepSeek 沉寂了大半年

中间他们在处理从 NVIDIA 换到华为芯片的事，据公开信息，后来又换回了 NVIDIA（具体的可以看 v3.2 的 Tech Rport）

至于今年，R2 还未发布，但发了 `V3.1` 和 `V3.2`

其中`V3.2-Exp` 发的benchmark 并不突出，关注度有限  
但这个版本其实是在给 `V3.2` 的 DSA 铺路，让各种推理框架和部署工具支持起来

`V3.2` 前几天正式发布，用的就是同样的架构，在推理类 Benchmark 中，达到了 GPT-5 的水平，略低于 Gemini-3-Pro

到这里，再让我们回顾下发布图

DeepSeek 发布时间线，红色是主要版本

几个概念
----

在讲具体技术之前，先把几个基础概念说清楚

### 大模型训练的两个阶段

**预训练**  
用海量文本训练，产出 `base model`（基座模型）  
`base model` 能续写文本，但不太会对话，不太会按指令做事

**后训练**  
在 `base model` 基础上继续训练，让模型学会对话、遵循指令、拒绝有害请求  
后训练通常包含 `SFT`（监督微调，用人工标注数据训练）和 `RL`（强化学习，用奖励信号优化）

### V3 和 R1 的关系

DeepSeek 当下的 `base model` 是 `DeepSeek-V3-Base`

DeepSeek V3、R1 都是经过后训练的，其中

*   • V3 走的是标准流程：预训练 → SFT → RL
    
*   • R1 有两个版本：
    

*   • **R1-Zero**：拿 V3 的预训练版本（V3-Base），跳过 SFT，直接用纯 RL 训练
    
*   • **R1**：先用几千条高质量数据做「冷启动」微调，再做 RL，比 R1-Zero 更好
    

### 推理模型 vs 普通模型

**普通模型**（比如 ChatGPT 默认模式）收到问题后直接给答案

**推理模型**（比如 o1、R1）会先「思考」一段，把推理过程写出来，再给最终答案

这个「思考」过程通常会用特殊标签包起来，比如 `<think>...</think>`

用户能看到模型在想什么，而且这种逐步推理的方式在数学、代码、逻辑题上效果更好

### 专用模型 vs 混合模型

今年行业里出现了两种做法：

**专用模型**  
推理是推理，聊天是聊天，分开训练成两个模型  
用户想做数学题就用推理模型，想闲聊就用聊天模型  
好处是每个模型在自己的领域做到最好

**混合模型**  
一个模型同时具备推理能力和普通聊天能力  
用户可以通过 prompt 或特殊 token 切换模式  
比如加上 `<think>` 标签就进入推理模式，不加就是普通聊天

好处是一个模型搞定所有场景，用起来方便

今年推理模型和混合模型的发布时间线

Qwen3 一开始是混合模型，用 `<think></think>` 标签切换模式  
后来发现分开训练效果更好，又拆成了 instruct 和 reasoning 两个版本

OpenAI 的 gpt-oss 是混合模型，用 system prompt 控制推理强度  
GPT-5 和 GPT-5.1 应该也是类似的处理方式

### DeepSeek 的路径

根据已经发布的信息，DeepSeek 的当前路径为：

*   • V3：base model
    
*   • R1：专用推理模型（在 V3 基础上 post-training）
    
*   • V3.1、V3.2：混合模型（同时支持推理和普通聊天）
    

R1 更多是研究性质，用来探索推理训练方法  
V3.2 是面向各种场景的产品级模型

DeepSeek 团队应该在做专门的 R2（尚未有官方公开消息）

V3 的核心：MLA 机制
-------------

现在开始讲具体技术  
V3 架构有两个重点：**MoE** 和 **MLA**

更为具体的介绍，可以看我之前的拆解  
[DeepSeek-V3 是怎么训练的｜深度拆解](https://mp.weixin.qq.com/s?__biz=MzkzNDQxOTU2MQ==&mid=2247494642&idx=1&sn=bb08acb35c778e0dcfc6fb85c82c5df8&scene=21#wechat_redirect)

### MoE 简介

MoE 是 Mixture of Experts 的缩写，中文叫「专家混合」,普通模型的每一层，所有参数都会参与计算

MoE 模型的每一层有多个「专家」（就是多组参数），每次只激活其中几个  
比如一个模型有 256 个专家，每次只用 8 个

这样模型参数总量可以很大（能力强），但每次计算只用一部分（效率高）

DeepSeek V3 用的就是 MoE 架构

### MLA 是什么

MLA 是 Multi-Head Latent Attention 的缩写，中文叫「多头潜在注意力」

这是 DeepSeek 自己设计的一种注意力机制，目的是省显存

### 为什么要省显存

大模型推理时有个东西叫 KV Cache

简单说，模型生成每个新 token 时，需要用到之前所有 token 的信息

这些信息存在 key 和 value 两个向量里

为了避免重复计算，通常会把这些向量缓存起来，这就是 KV Cache

问题是，序列越长，KV Cache 越大，显存占用越高

长文本场景下，显存很容易不够用

### MLA 怎么省显存

正常做法是把完整的 key 和 value 向量存进 KV Cache

MLA 的做法是：  
**先把 key 和 value 压缩到一个低维空间，存压缩后的版本**

推理的时候再解压回来

MLA 原理图，key 和 value 先压缩再存储

具体流程：

1.  1\. 输入的 key 和 value 通过一个下投影矩阵（down-projection），从高维压缩到低维
    
2.  2\. 压缩后的向量存入 KV Cache
    
3.  3\. 推理时，从 KV Cache 取出压缩向量
    
4.  4\. 通过上投影矩阵（up-projection）还原到原始维度
    
5.  5\. 用还原后的向量做正常的注意力计算
    

这个思路和 LoRA 类似：先降维再升维，中间存小的

代价是多了一次矩阵乘法（还原那一步），但显存省了

query 也会压缩，但只在训练时，推理时不需要

MLA 不是 V3 才有的，DeepSeek V2 就引入了这个机制

R1 的核心：RLVR 训练
--------------

R1 和 V3 架构完全一样，区别在训练方法

**R1 用的是 RLVR**（Reinforcement Learning with Verifiable Rewards，可验证奖励的强化学习）

更为具体的介绍，可以看我之前的拆解（还有个R0）  
[DeepSeek-R1 是怎么训练的｜深度拆解](https://mp.weixin.qq.com/s?__biz=MzkzNDQxOTU2MQ==&mid=2247495493&idx=1&sn=75858d12c9c7c5146db60b2ec04dfc79&scene=21#wechat_redirect)

### 什么是强化学习训练

大模型的 post-training 阶段通常会用强化学习

基本思路是：

1.  1\. 给模型一个问题
    
2.  2\. 模型生成一个回答
    
3.  3\. 用某种方式给这个回答打分（reward）
    
4.  4\. 根据分数调整模型参数，让高分回答更容易出现
    

关键问题是：怎么给回答打分？

### 传统做法：RLHF

ChatGPT 使用的便是 RLHF  
`全称：Reinforcement Learning from Human Feedback`

先收集人类对不同回答的偏好数据

然后训练一个 reward model，让它模拟人类的打分

最后用这个 reward model 给模型的回答打分

这里有一个问题  
**reward model 本身可能不准，人类标注成本也高**

### RLVR 的思路

RLVR 的想法是：  
**有些任务的答案，可以被程序自动验证**

数学题有标准答案，代码能跑通就是对的

这类任务不需要人工标注，直接用程序判断对错

可验证任务的例子

比如模型做一道数学题：

*   • 如果最终答案和标准答案一致，reward = 1
    
*   • 如果不一致，reward = 0
    

不需要 reward model，不需要人工标注

### GRPO 算法

具体的强化学习算法，R1 用的是 GRPO  
`全称：Group Relative Policy Optimization`

这是 PPO 的简化版

RLHF、GRPO、RLVR 的对比

三种方法的区别：

*   • **传统 RLHF + PPO**：需要一个 reward model（根据人类偏好训练）和一个 critic model（估计价值的辅助模型）
    
*   • **GRPO**：去掉了 critic model，只保留 reward model，简化了训练流程
    
*   • **RLVR + GRPO**：连 reward model 也不要了，直接用程序验证（计算器验证数学答案、编译器验证代码）
    

### R1 的 reward 设计

R1 用了三种 reward：

*   • **format reward**：检查答案格式是否正确（比如推理过程是否用了指定的标签）
    
*   • **language consistency reward**：防止模型在回答过程中切换语言（比如问题是中文，回答一会中文一会英文）
    
*   • **verifier reward**：最核心的，数学或代码答案是否正确
    

V3.1：成为混合模型
-----------

V3.1 变成了混合模型，用户可以通过 prompt template 切换推理模式和普通聊天模式

但这里的架构没变，以及 V3.1 基于 DeepSeek V3.1-Base，后者在 V3 基础上额外训练了 840B tokens

V3.1 的具体发布，可以看这里：[DeepSeek-V3.1 发布](https://mp.weixin.qq.com/s?__biz=MzkzNDQxOTU2MQ==&mid=2247504654&idx=1&sn=c9c29fd819504d7fe81f67a4dec360a0&scene=21#wechat_redirect)

### R1-0528 版本升级

R1-0528 是 R1 的小版本升级，架构和 V3/R1 完全一样

改进来自 post-training pipeline 的优化

性能追上了当时的 OpenAI o3 和 Gemini 2.5 Pro

具体怎么做的没有详细披露，推测是在推理时使用了更多计算资源（让模型「思考」更长时间）

V3.2-Exp：DSA 稀疏注意力
------------------

V3.2-Exp 是今年 9 月发的，架构上有实质变化

核心创新是 DSA（DeepSeek Sparse Attention，DeepSeek 稀疏注意力）

### 问题：标准注意力太慢

标准的 causal attention（因果注意力），当前 token 需要关注所有之前的 token

计算复杂度是 O(L²)，L 是序列长度

意思是：  
**序列长度翻倍，计算量变成 4 倍**

长文本场景下，这个计算量非常大

### 一种解决方案：Sliding Window Attention

Sliding Window Attention（滑动窗口注意力）是一种常见的优化方法

当前 token 不关注所有之前的 token，只关注最近的 N 个

比如 N=`4096`，那每个 token 只关注前面 `4096` 个 token

Sliding window attention，只关注固定窗口

Gemma 3 和 Olmo 3 用的是这个方案

优点是简单，复杂度从 O(L²) 降到 O(L×N)

缺点是窗口大小固定，可能漏掉重要信息

### DSA 的思路

DSA 不用固定窗口，让模型自己学习应该关注哪些 token

每个 token 只关注之前的一部分 token，但这个「一部分」是模型学出来的，不是固定的

DSA，模型自己选择要关注哪些 token

看上图，关注的 token 位置不是连续的，是「跳着」选的

### DSA 怎么实现

DSA 有两个组件：`Lightning Indexer` 和 `Token Selector`

**Lightning Indexer：计算相关性分数**

对每个新的 query token，计算它和之前所有 token 的相关性

用的是 MLA 里压缩后的向量（前面讲过，MLA 会把 key 和 value 压缩存储），做点积然后过 ReLU

相关性分数的计算公式：

DSA 相关性分数公式

公式里的符号：

*   • w：学习到的每头权重系数，决定每个 indexer head 对最终分数的贡献
    
*   • q：query 向量
    
*   • k：key 向量
    
*   • t：当前 token 位置
    
*   • s：之前的 token 位置（0 ≤ s < t）
    
*   • j：indexer head 的索引（DSA 有多个 head，类似多头注意力）
    

indexer 只处理 query，不处理 key

因为 key 已经压缩存在 KV Cache 里了，不需要再算

ReLU 函数会把负值变成 0，但因为有多个 head 的求和，最终分数通常不会是 0

真正的稀疏性来自下一步的 Token Selector

**Token Selector：选择 top-k**

根据 Lightning Indexer 算出的分数，选分数最高的 k 个 token

其他 token 被 mask 掉，不参与注意力计算

k 在 DeepSeek 公开的代码里设的是 2048

DSA 的完整流程

### DSA 的效果

复杂度从 O(L²) 降到 O(L×k)

k 是选择的 token 数量（比如 2048），远小于 L（序列长度可能是几万甚至几十万）

V3.2-Exp 的目标不是提升性能，是在保持性能的前提下提升效率

DeepSeekMath V2：自验证和自改进
-----------------------

V3.2 发布前 4 天（11 月 27 日，美国感恩节），DeepSeek 发了 DeepSeekMath V2

这是一个数学专用模型，基于 V3.2-Exp-Base

在数学竞赛上达到了金牌水平

更重要的是，它验证了两个关键技术：Self-Verification（自验证）和 Self-Refinement（自改进）

这两个技术后来用到了 V3.2 里

### RLVR 的问题

前面讲过，RLVR 用程序验证答案对不对

但 DeepSeek 团队指出了两个问题：

**问题一：correct answers don't guarantee correct reasoning**

正确答案不等于正确推理

模型可能靠错误的逻辑或者运气得到正确答案

比如做一道数学题，中间步骤全是错的，但最后答案碰巧对了

按 RLVR 的逻辑，这个回答会得到正向 reward

模型会学到错误的推理方式

**问题二：有些任务没法只看最终答案**

比如定理证明，要求严格的逐步推导

你不能只验证结论对不对，中间每一步都要对

最终结论对了，但中间步骤错了，这个证明就是无效的

### 自验证怎么做

为了解决上面的问题，DeepSeek 训练了三个模型：

**LLM 1：证明生成器（Proof Generator）**

生成数学证明

**LLM 2：证明验证器（Proof Verifier）**

检查证明是否正确

不只看最终答案，会检查每一步推理

用一个评分标准打分：

*   • 1 分：完整严谨，所有逻辑步骤都有清晰理由
    
*   • 0.5 分：整体逻辑正确，但有小错误或遗漏细节
    
*   • 0 分：有根本性逻辑错误或关键缺失
    

证明生成器和验证器的结构

**LLM 3：元验证器（Meta-Verifier）**

验证「验证器」是否正确

验证器可能会产生幻觉，错误地指出不存在的问题

元验证器就是用来检查验证器的

Meta-verifier 检查验证器是否正确

这个设置有点 GAN（生成对抗网络）的意思：

验证器推动生成器进步，生成器生成更好的证明，又推动验证器进步

**训练细节**

证明验证器（LLM 2）的训练：

*   • 基于 DeepSeek V3.2-Exp-SFT（在 V3.2-Exp 上做了监督微调的版本）
    
*   • 用强化学习训练
    
*   • 两种 reward：format reward（格式正确）+ score reward（预测分数和人工标注分数的接近程度）
    

元验证器（LLM 3）的训练方式类似

**效果**

使用 meta-verifier 后，验证器的证明分析质量从 0.85 提升到 0.96

同时保持了证明分数预测的准确率

meta-verifier 只在训练时用，推理时不需要

### 自改进怎么做

Self-Refinement（自改进）是一种推理时的技术

让模型根据验证结果修改自己的答案

**传统 Self-Refinement**

用同一个 LLM 做三件事：

1.  1\. 生成初始答案
    
2.  2\. 评估这个答案有没有问题
    
3.  3\. 根据评估结果改进答案
    

传统 self-refinement，同一个模型生成、评估、改进

**DeepSeek 发现的问题**

技术报告原文：

> when prompted to both generate and analyze its own proof in one shot, the generator tends to claim correctness even when the external verifier easily identify flaws.

用同一个模型既生成又验证，模型会自己骗自己

让模型评估自己生成的东西，它倾向于说「没问题」

但如果用外部验证器，很容易发现问题

**看起来应该用两个模型**

一个生成，一个验证

用独立验证器的 self-refinement

**但实际做法不同**

技术报告说：

> All experiments used a single model, our final proof generator, which performs both proof generation and verification.

最终版本还是用了同一个模型

关键在于：训练时用了独立的验证器和元验证器来「教」这个模型

模型学会了用同样的评分标准评估自己的输出

和 naive 的单模型 self-refinement 的区别是：这个模型被更强的验证器「教过」了

推理时用 2-in-1 的模型，省资源

**迭代次数**

self-refinement 可以做多轮

生成初始答案 → 评估 → 改进 → 再评估 → 再改进...

DeepSeek 测到了 8 轮，效果还没饱和

迭代次数和准确率的关系

更多迭代 = 更高准确率 = 更贵

这是推理时计算量和效果的 trade-off

V3.2：完整拆解
---------

先放个 DeepSeek V3.2 的跑分

DeepSeek V3.2

我之前写过一个技术报告拆解：  
[DeepSeek-V3.2｜技术报告解读](https://mp.weixin.qq.com/s?__biz=MzkzNDQxOTU2MQ==&mid=2247509217&idx=1&sn=bd60050200c0593c45ea7eeb839dc23b&scene=21#wechat_redirect)

### 架构

和 V3.2-Exp 完全一样：MoE + MLA + DSA

技术报告原文：

> DeepSeek-V3.2 uses exactly the same architecture as DeepSeek-V3.2-Exp

V3.2 架构

训练目标：

*   • 数学达到金牌水平
    
*   • 支持 tool-use（让模型学会调用外部工具，比如搜索引擎、计算器、代码解释器）
    
*   • 代码和 agent 任务表现好
    

同时保持计算效率

### DSA 的效果

DSA 带来的推理成本节省

这里，用了 H800

### RL 训练的变化

这个是 R1 的 reward 设计

*   • format reward：格式正确
    
*   • language consistency reward：语言一致
    
*   • verifier reward：答案正确
    

这个是 V3.2 的 reward 设计：

*   • rule-based outcome reward：基于规则的结果 reward
    
*   • length penalty：惩罚过长的输出（控制 agent 任务的输出长度）
    
*   • language consistency reward：语言一致
    

对于通用任务：

*   • generative reward model：用另一个 LLM 打分，每个 prompt 有自己的评分标准（rubric）
    

变化总结：

*   • 去掉了 format reward
    
*   • 加了 length penalty
    
*   • 通用任务用 LLM-as-a-judge（因为通用任务没法用程序验证）
    

数学领域用的是 DeepSeekMath V2 的数据和方法（前面讲的自验证、自改进）

所以：**V3.2 不再是纯 RLVR**  
应该是：`RLVR` + `LLM-as-a-judge`

### GRPO 的改进

过去几个月，业内有很多 GRPO 的改进版本

比较知名的是 DAPO 和 Dr. GRPO

**DAPO 的主要改进**：

*   • 非对称 clipping：上下界不一样
    
*   • 动态采样：保持 batch size
    
*   • token-level loss：用 token 数量而不是样本数量归一化 loss
    
*   • 显式的基于长度的 reward shaping
    

**Dr. GRPO 的主要改进**：

*   • 去掉 GRPO 目标函数里的长度归一化
    
*   • 去掉标准差归一化
    

这两个改进都认为原版 GRPO 有 bias，会偏向过长的错误答案，或者过度加权太难/太简单的问题

**Olmo 3 采用的改进**（和 DAPO/Dr. GRPO 类似）：

*   • Zero Gradient Signal Filtering：去掉 reward 全相同的样本组（这种样本提供不了梯度信号）
    
*   • Active Sampling：维持 batch size
    
*   • Token-level loss：用 token 数量归一化 loss
    
*   • No KL Loss：去掉 KL 损失（KL 损失是为了防止模型偏离原始模型太远，但很多团队发现去掉效果更好）
    
*   • Clip Higher：上界 clipping 比下界稍高
    
*   • Truncated Importance Sampling：调整 log probability 差异
    
*   • No standard deviation normalization：计算 advantage 时不除以标准差
    

**V3.2 的改进**比较保守，更接近原版 GRPO：

**Domain-specific KL strengths**  
不同领域用不同的 KL 权重  
数学领域可以很弱甚至为 0  
但不是完全去掉 KL，而是把它变成超参数

**Unbiased KL estimate**  
用 importance ratio 重新加权 KL term  
让 KL 梯度真正匹配「样本来自旧策略」这个事实

**Off-policy sequence masking**  
跨多个梯度步骤重用 rollout 数据时  
测量当前策略和生成这些数据的旧策略的偏离程度  
丢弃那些 advantage 为负且偏离太远的序列  
防止模型从过时或偏离的数据中学习

**Keep routing for MoE**  
记录 rollout 时激活了哪些 expert  
训练时强制用同样的 routing pattern  
让梯度更新作用于真正产生了采样答案的 expert

**Keep sampling mask for top-p/top-k**  
如果 rollout 用了 top-p 或 top-k 采样  
存储 selection mask  
计算 GRPO loss 和 KL 时重新应用这个 mask  
让训练时的 action space 和采样时一致

**Keep original GRPO advantage normalization**  
Dr. GRPO 认为 GRPO 的长度归一化和标准差归一化有问题  
V3.2 保留了原版 GRPO 的归一化，通过上面的其他修改来处理问题

### V3.2-Speciale：极端推理模式

V3.2 还有一个 Speciale 版本  
针对推理场景的极端优化

**训练差异**

*   • RL 阶段只用推理数据（不用通用聊天数据）
    
*   • 减弱 length penalty，允许更长的输出
    

这个是效果

Speciale 版本的 token 数量和准确率

**更长的输出 -> 更多推理步骤 -> 更高准确率 -> 更贵**

这是个取舍

最后
--

总结一下，从 V3 到 V3.2 的技术演进：

**V3**：`MoE + MLA`  
MoE 让模型参数大但计算量小  
MLA 通过压缩 KV Cache 省显存

**R1**：`RLVR + GRPO`  
用可验证的 reward（数学答案对不对、代码能不能跑）训练推理能力  
GRPO 是 PPO 的简化版

**V3.1**：`变成混合模型`  
支持推理和普通聊天切换

**V3.2-Exp**：`加入 DSA 稀疏注意力`  
不用固定窗口，让模型学习应该关注哪些 token  
复杂度从 O(L²) 降到 O(L×k)

**DeepSeekMath V2**：`自验证 + 自改进`  
训练时用独立验证器检查推理过程  
推理时用同一个模型，因为已经学会了验证能力

**V3.2**：`整合所有技术`  
架构：MoE + MLA + DSA  
训练：RLVR + LLM-as-a-judge 混合  
GRPO 做了稳定性改进  
支持 Thinking in Tool-Use 这样的工程内容

修改于