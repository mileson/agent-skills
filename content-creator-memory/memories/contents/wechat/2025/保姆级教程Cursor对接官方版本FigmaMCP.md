![cover_image](https://mmbiz.qpic.cn/sz_mmbiz_jpg/CfXolaPDUHicKtL0ic2YIxkvZRSh7lLLRrJhGSpokfghe0N3xicQwlXuX5MUWboXf20oHL1YD5zIBgyqA5HndOwkw/0?wx_fmt=jpeg)

【保姆级教程】Cursor 对接官方版本 Figma MCP
==============================

原创 超级峰 超级峰 [超级峰](javascript:void\(0\);)

在小说阅读器中沉浸阅读

上周，Figma 官方发布了全新的基于开发模式下的 MCP 原生支持功能。相比原先的需要安装插件，然后保证端口一致之类的繁杂的各种操作的不稳定的第三方版本，提供了原生级别的的稳定服务、便捷使用、能力更强大的 MCP能力。

  

今天，我将通过图文的形式，保姆级教会你如何快速对接上这个 Figma 官方的 MCP，帮助你能够通过设计稿就能让 Cursor 等 AI 编程工具实现你所见即所得的想法！

  

### 一、开启 Figma MCP 服务

首先，你需要将本地的 Figma 客户端，并将客户端更新到最新版本（即 version 125.4.9 以及以上）

然后在「设置页（Preferences）」内开启“Enable Dev Mode MCP Server”选项

  

### 二、配置 Figma MCP 服务（以 Cursor 为例）

打开 Cursor ，并前往 Cursor 设置页 ，点击「New MCP Server」按钮，添加 Figma MCP 配置

  

复制下述 MCP 配置，原文粘贴到 mcp.json 内，并保存即可

    "Figma Dev Mode MCP": { 

       "type": "sse",      

       "url": "http://127.0.0.1:3845/sse"

    },

  

  

最后，返回 Cursor 设置页 ，通过如下 3 要素 ，确认下 MCP 配置是否已激活：

1.  1. “Figma Dev Mode MCP”的开关是否已开启
    
2.  2. 指示灯是否已变绿
    
3.  3. Tools 区域是否已获取到具体数量
    

  

### 三、使用 Figma MCP 服务（以 Cursor 为例）

配置完成 Figma MCP 后，返回 Figma 客户端内，右击打算实现的设计稿，并复制链接

  

将复制的链接粘贴到 Cursor 内，并进行对话，我们可以看到 Cursor 能准确读取到

  

最后，附上目前 Figma MCP 已支持的四大能力，帮助你后续更好的使用这款 AI 编程神器：

  

希望本次的分享对你有所帮助：）