![cover_image](https://mmbiz.qpic.cn/mmbiz_jpg/fbRX0iaT8Egeib7gv03R3rteIrYuwIeflfpENJaWEibibJ38ibd6d8cunQZbcbEvk3oc8ONpzTBsxibMx72Clf4iaZRrw/0?wx_fmt=jpeg)

Figma MCP + GPT-Codex：新的 Vibe Coding 之王
=======================================

原创 歸藏的 AI 工具箱 歸藏的 AI 工具箱 [歸藏的AI工具箱](javascript:void\(0\);)

在小说阅读器中沉浸阅读

昨天刷到了新的 Figma 远程 MCP 服务，进行了一大堆升级，然后又看到 GPT-5 Codex 有 API 了。

于是就都研究了一下，没想到这么顶啊，这个美学表现直接拉满了，下面这是直接给 GPT-5 Codex 设计稿的链接，只修改了一次得到的结果。

  

另外我还用之前的提示词把 Qwen 3 MAX 的播客文章内容给到 GPT-5 Codex 生成了一个网页，也非常顶。

即使没有设计稿，单纯的提示词 Codex 的设计风格也跟其他模型有很大的区别，这图片你就让我照着画，也需要画一段时间的。

  

  

早上发了以后很多朋友问怎么用，刚好就写个教程，主要新的 Figma 远程 MCP 服务这部分需要介绍一下。

GPT-5 Codex 的话因为有了 API 所以常见的 AI IDE 比如 Cursor 等都加上了，选择后直接用就行。

  

Figam MCP 这次升级最大的一个更新就是不再需要原来复杂的添加流程和本地 Figma 客户端了。

你不需要管之前咋装，我们直接看现在就行，这里我先按 Cursor 的操作路径介绍一下。

首先我们需要找到 Cursor 的设置，在设置里面找到 MCP 这个 TAB，然后点击“New MCP Server”将下面的 Json 代码复制进去保存就行不需要做任何改动。

  

    {  "mcpServers": {    "figmaRemoteMcp": {      "url": "https://mcp.figma.com/mcp"    }  }}

然后回到设置页面你就会看到多了一个 Figam 的 MCP，右边还有个“Connect”按钮，我们点击，系统会询问是不是要打开外部网站，你选择打开就行。

  

然后在打开的页面里面点击这个“Allow access”授权按钮就行，然后如果你没有登录的话需要登录 Figma 才行。

还有就是这个 Figma 的远程 MCP 服务需要订阅用户才行，如果你没有的话中国暗网“闲鱼”会帮你解决。

  

这时候我们看到设置里面 Figma 的 MCP 已经开启了，而且还可以看到里面包含的工具。

  

如果你用的 Claude Code，你可以直接在终端输入下面的命令。

    claude mcp add --transport http figma-remote-mcp https://mcp.figma.com/mcp command in your terminal to add the Figma MCP to Claude Code

然后启动 Claude Code ，用 /MCP 命令选择登录选项，然后也是会弹出一个网页，点击授权按钮就可以。

  

  

然后我们就能找一个设计稿使用 Figma MCP 了，Figma 社区有非常多很好的组件库和设计稿，你可以找一个你喜欢的打开改一改。

然后页面最下方切换到开发者模式，选中你想要复刻的页面然后右键选择复制所选的链接。

  

在之后就可以在 Cursor 里面将模型换成 GPT-5 Codex ，然后让 Agent 调用 Figma MCP 查询对应链接的设计信息还原成网页了。

需要注意的是如果你只是想写 HTML 的话最好加上 Tailwind CDN  和 Apache ECharts 5 CDN 这种它可以节省一些 Token。

  

然后就是 Figma MCP 这次传输的信息相当多，连设计稿素材图都变成图片链接返回了。

如果你的页面超级复杂 AI 会不可避免的偷懒，可以让他一部分一部分完成，比如先把关键的组件和页面框架搭出来，然后再填充内容，这样的话不至于上下文一下被挤爆。

另外 Figma MCP 传输的信息跟设计稿本身质量也有关系，如果设计稿本身没有用自动布局以及层级关系有误的话，可能表面上看没啥问题，但是 Figma 传给 AI 的内容是够呛可以生成好的网页了。

  

可能很多朋友想要我前面 Qwen 3 那个网页的的提示词，我这里也写一下，另外这个网页是我用 Codex 的 Cursor 插件写的，如果你只有 GPT 会员的话，也可以试试用这种方式尝试 GPT-5。

  

直接在插件市场搜索 Codex 然后安装就行，或者点这里（developers.openai.com/codex/ide）这个简单，然后点击那个 Open AI 的图标启用，这时候登录后走的就是你 GPT 会员的 Token 额度了。

  

帮我将这个Qwen3 的模型介绍文章生成中文可视化网页，帮助受众理解，不要遗漏信息

 根据上面内容生成一个 HTML 动态网页 

1.  a.使用Aurora Gradient Hero风格的视觉设计，背景色为#FDFDFD，#161615作为高亮按钮色和文字色，# 5751D5 作为特殊高亮色
2.  b.强调超大字体或数字突出核心要点，画面中有超大视觉元素强调重点，与小元素的比例形成反差 
3.  c.中英文混用，中文大字体粗体，英文小字作为点缀 
4.  d.使用Apache ECharts 5 CDN 版做简洁的勾线图形化作为数据可视化或者配图元素
5.  e.运用高亮色自身透明度渐变制造科技感，但是不同高亮色不要互相渐变 
6.  f.模仿 apple 官网的动效（段落切屏 & 视差缩放等），向下滚动鼠标配合动效 
7.  g.数据可以引用在线的图表组件，样式需要跟主题一致 
8.  h.使用 anime.js （通过CDN引入：jsdelivr.com）
9.  i.使用HTML5、TailwindCSS 3.0+（通过CDN引入）和必要的JavaScript 
10.  j.使用专业图标库如Font Awesome或Material Icons（通过CDN引入） 
11.  k.避免使用emoji作为主要图标 
12.  l.不要省略内容要点

风格的具体要求是：

Hero 背景 = Aurora Gradient；

CSS conic-gradient(from 120deg at 50% 50%, 0%, 60%, 100%);

背景层 blur(120px) & opacity 0.8，随滚动 scale(1.2 → 1)；

前景放置设备 Mockup / 超大数字 KPI；

进入视口时 GSAP from {y:60, opacity:0} 0.8s ease-out。

  

今天的教程就到这里了，从这次 Figma MCP 的更新来看，Vibe Coding 的基建还有非常多的增长空间。

无论是成熟的设计系统设计稿，还是对应的前端组件库，用好以后配合 MCP 都可以极大的降低 Token 的消耗，将上下文让给更有意义更需要智能的逻辑和数据部分。

同时 AI 接入以后不代表对设计稿或者对编程的人就没需求了，只是效率提高了，但是你该有的审美和你需要的基本功知识依然是需要的。