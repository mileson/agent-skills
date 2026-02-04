![cover_image](https://mmbiz.qpic.cn/mmbiz_jpg/2icSMc1VBIYrRr8XKliatbclGGzLaOmniay8NqdiczTdRIFBm8va80mxsraiasOw01iazdAYcJE1wIeg2nKbx6eLZjGA/0?wx_fmt=jpeg)

Gemini3 DeepThink 发布：一骑绝尘
=========================

原创 金色传说大聪明 金色传说大聪明 [赛博禅心](javascript:void\(0\);)

在小说阅读器中沉浸阅读

Google 刚刚放出了 Gemini3 DeepThink

这里有两个对比：Gemini3 DeepThink vs Gemini3 Pro

评测数据：

*   • `ARC-AGI-2`：**45.1%**
    
*   • 作为对比，Claude Sonnet 4.5 是 13.6%，GPT-5 Pro 是 15.8%，GPT-5.1 是 17.6%
    

差不多是其他模型的 3 倍，但图里没画 Opus，是 37.6%

Google 官方放的图，ARC-AGI-2 那栏的差距最明显

`Humanity's Last Exam` 上也是第一，41%，比 GPT-5 Pro 的 30.7% 高出 10 个点  
`GPQA Diamond` 是93.8%，科学知识类测试，各家差距不大

* * *

技术上，Google 说的是「parallel reasoning」，并行推理

普遍的 **reasoning model** 是 **chain-of-thought**，一步一步往下推，走一条路，走到底  
**parallel reasoning** 不一样，它同时开很多条推理路径，每条路径探索一个假设

比如遇到一个问题，传统做法是：  
`假设 A` → `推理` → `结论`

parallel reasoning 则是这样：  
同时开 A、B、C、D 四个假设，四条路同时跑，跑完再比较

理解起来，就像这样

`假设 A` → `推理` → `...可能的正确结论 A`

`假设 B` → `推理` → `...可能的正确结论 B`

`假设 C` → `推理` → `...可能的正确结论 C`

`假设 D` → `推理` → `...可能的正确结论 D`

最后，看看这些结论中，哪个更靠谱

这样的话，不会因为一开始选错方向就全盘皆输  
就很类似你在做数独，有时候要假设好几个前提，然后逐个尝试

就这种，很难说一次能试对

在 ARC-AGI-2 这种视觉推理测试上特别有用，因为这类题目需要从没见过的 pattern 里找规律，一开始很难判断哪个方向是对的

有关 ARC-AGI 的介绍，之前提过，感兴趣的可以回顾下这里：[OpenAI o3 详解：并非 AGI，比 o1 贵 1000倍（另附内测申请）](https://mp.weixin.qq.com/s?__biz=MzkzNDQxOTU2MQ==&mid=2247494349&idx=1&sn=a1b66e940dc46ca3cfa95e859b6a66aa&scene=21#wechat_redirect)

简单来说，ARC-AGI 就是一组图片题库，没有描述，对人来说较为简单，但对 AI 来说就难度异常，这里放几个典型的题目，感受一下

* * *

Gemini3 Deep Think 这套东西，是 Gemini 2.5 Deep Think 的延续

之前在 IMO（国际数学奥林匹克）和 ICPC 世界总决赛上都拿到了金牌水平，现在这套东西产品化了

使用方式：  
Gemini app 里选「Deep Think」模式，模型选 Gemini 3 Pro

点这里可以用，后续我出一份详细的测试

**已上线，需要  Ultra 订阅，$249.99/月**

修改于