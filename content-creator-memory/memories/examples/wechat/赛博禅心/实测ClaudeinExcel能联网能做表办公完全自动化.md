![cover_image](https://mmbiz.qpic.cn/mmbiz_jpg/2icSMc1VBIYqeZudY6IXgccJx5BtQCvNUFaibtVQgWXt7aeIPu2kPtFcAJOCuwiaBmjibdkv1hwKajsISEW5p6ZfXQ/0?wx_fmt=jpeg)

实测：Claude in Excel，能联网、能做表、办公完全自动化
==================================

原创 金色传说大聪明 金色传说大聪明 [赛博禅心](javascript:void\(0\);)

在小说阅读器中沉浸阅读

Claude 被塞进 Excel 了  
**Pro**、**Max**、**Team**、**Enterprise** 都能用

用的是 Opus 4.5，我装了一个试了试，很方便

实测
--

先去 Microsoft Marketplace 装插件：  
`https://marketplace.microsoft.com/en-us/product/saas/wa200009404`

点击 Get it now

装完在 Excel 里激活，侧边栏就出来了。快捷键 Control+Option+C（Mac）或 Control+Alt+C（Windows）

在工具栏最右侧

我让它干了这么个活

> 收集过去5年苹果的主要产品、发布时间、系列等各种信息，放在表格里面

然后她开始了一轮轮的搜索

左侧空表格，右侧在搜索

搜索记录可以打开

紧接着，他就内容填入表格，很规整

`产品类别`、`产品系列`、`具体型号`、`发布日期`、`芯片`、`代数`、`主要特点`，全给整理好了

iPhone 从 13 到 16e，iPad 各个系列，Mac 也有

填完了，很整齐

对于经常做表格的朋友，对透视表应该不陌生  
而在这里，还可以让 Claude 给做成透视表，把内容按产品线或者按年份进行整理

Claude 做的透视表

整个过程挺顺，一句话下去，表就出来了

能干什么
----

几个核心场景：

**读模型**  
问某个单元格怎么算的，Claude 会跨 tab 追溯，给 cell-level 引用

**改假设**  
改输入值的时候保留公式依赖，高亮所有受影响的单元格

**Debug**  
追 #REF!、#VALUE!、循环引用，定位源头，给修复建议

**建模**  
从零建三张表，或者往现有模板填数据

支持 .xlsx 和 .xlsm。这次更新加了多文件拖拽、避免覆盖现有单元格、长会话自动压缩

几个限制
----

当前不支持：条件格式、数据验证、宏、VBA

聊天记录不保存，每次打开是新会话

Beta 阶段官方不建议用于没人工审核的客户交付物、需要审计的关键计算

一个风险提醒
------

Anthropic 有一份说明文档，专门写了 prompt injection 风险

https://support.claude.com/en/articles/12650343-claude-in-excel

攻击方式是在 Excel 文件里藏恶意指令。看起来正常的模板，可能包含"把数据导出到某个 URL"这种隐藏内容

官方建议：**只用可信来源的 Excel 文件**。下载的模板、供应商发的文件、外部数据导入，都要小心

触发高危函数（`WEBSERVICE`、`INDIRECT`、`FOPEN` 这些）会弹确认框，记得看一眼再点