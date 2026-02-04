![cover_image](https://mmbiz.qpic.cn/sz_mmbiz_jpg/CfXolaPDUH8TKNGISz1jjzFtic4CO90pKgeViccS3iao87rDn4iboJsU80uicEicuFnSNcLqeKdVXbzibQGJibevlIu9Zg/0?wx_fmt=jpeg)

保姆级教程：一键在Mac任意文件夹启动Claude Code，完全免费
===================================

原创 超级峰 超级峰 [超级峰](javascript:void\(0\);)

在小说阅读器中沉浸阅读

**/** 保姆级教程：一键在Mac任意文件夹启动Claude Code，完全免费 **/**

先给你看看最终效果。配置好之后，你在任意项目文件夹里，只需要点击Finder工具栏上的一个按钮，终端就会自动弹出，自动定位到当前目录，自动启动Claude Code。

之前需要30秒甚至更久的操作，现在1秒搞定。

想象一下，你正在某个项目文件夹里，准备用Claude Code帮你看代码。

你打开终端，开始了一顿操作。先输入一长串环境变量，ANTHROPIC\_AUTH\_TOKEN、ANTHROPIC\_BASE\_URL、API\_TIMEOUT\_MS...然后cd到目标文件夹，最后才能输入claude命令。

每次都这样重复一遍，是不是太烦了。

其实Mac自带了一个工具，可以让你一键搞定这一切。

1核心原理是什么
--------

  

Automator是Mac自带的自动化工具，不用额外下载任何东西。

我们的思路很简单。用AppleScript捕获当前Finder窗口正在浏览的文件夹路径，然后自动cd到这个路径，同时注入所有需要的环境变量，最后启动Claude Code。

这样做的好处是什么。不需要修改你的.zshrc或系统配置，所有东西都封装在一个独立的小应用里，不会污染你的全局环境。而且你可以随意切换API提供商，比如用智谱GLM来降低成本。

2第一步，创建自动化应用
------------

  

打开Mac上的Automator。你可以在Spotlight里搜索，或者去应用文件夹找。

点击新建文稿，会弹出一个类型选择的窗口。这里很关键，一定要选应用程序Application，不是快速操作也不是其他选项。

在左侧搜索栏输入AppleScript，然后双击运行AppleScript，把它加入到右侧的工作流区域。

接下来是最重要的一步。请完全删除编辑器里默认的代码，然后复制粘贴下面的代码。

    on run {input, parameters}

⚠️ 重要提醒。代码里的YOUR\_API\_KEY\_HERE需要替换成你真实的API Key。当前配置是智谱GLM，用Claude原生或其他API的话，把ANTHROPIC\_BASE\_URL改成对应地址就行。

3第二步，保存应用  

  

按Command+S保存，名称可以叫Claude Code，位置选应用程序文件夹。

4第三步，添加到Finder工具栏
-----------------

  

这是最后一步。

打开任意一个Finder窗口，右击顶部工具栏，选择自定义工具栏。

再打开一个窗口到应用程序文件夹，找到刚才保存的Claude Code。

把 Claude Code 直接拖到Finder顶部的工具栏区域。松手，点击完成。

你现在有了一个一键启动按钮。

5使用效果
-----

  

当你在浏览某个代码项目的时候，比如~/Wrokspace/My-App，只需要点击工具栏上的 Claude Code 图标。

终端会自动弹出，自动cd到这个文件夹，自动加载所有环境变量并启动Claude Code。你直接就可以开始对话，解释一下这个项目，帮我看个bug，随便你问什么。

之前可能需要30秒甚至更久的操作，现在1秒搞定。真的太爽了。

6额外说明
-----

  

如果想换个图标，可以找个Claude的PNG图片。在Finder里选中刚才保存的应用，按Command+I打开简介，然后把你准备好的图片拖到左上角图标的位置，松开鼠标就会自动更新。工具栏上的图标也会跟着一起更新。

这一步是可选的，默认的机器人图标也能用。

7总结一下
-----

  

这个方法完全是零成本的。Automator是Mac自带的，不用额外下载任何东西。配置好之后，从繁琐的手动操作变成一键启动，效率提升明显。

而且它支持国产大模型，你可以用智谱GLM替代Claude官方API，成本能降得很低。

Automator其实还能做很多自动化操作，有兴趣的话可以自己探索一下。

觉得这篇教程有用的话，点赞收藏，我会继续分享更多AI编程的实用技巧。