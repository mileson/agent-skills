# 一键在Mac任意文件夹启动Claude Code，完全免费

先给你看看最终效果。配置好之后，你在任意项目文件夹里，只需要点击Finder工具栏上的一个按钮，终端就会自动弹出，自动定位到当前目录，自动启动Claude Code。

![图片：01 预览效果](Medias/images/01-preview.png)

*▲ 配置完成后的效果展示*

之前需要30秒甚至更久的操作，现在1秒搞定。

想象一下，你正在某个项目文件夹里，准备用Claude Code帮你看代码。

你打开终端，开始了一顿操作。先输入一长串环境变量，ANTHROPIC_AUTH_TOKEN、ANTHROPIC_BASE_URL、API_TIMEOUT_MS...然后cd到目标文件夹，最后才能输入claude命令。

每次都这样重复一遍，是不是太烦了。

其实Mac自带了一个工具，可以让你一键搞定这一切。

## 核心原理是什么

Automator是Mac自带的自动化工具，不用额外下载任何东西。

我们的思路很简单。用AppleScript捕获当前Finder窗口正在浏览的文件夹路径，然后自动cd到这个路径，同时注入所有需要的环境变量，最后启动Claude Code。

这样做的好处是什么。不需要修改你的.zshrc或系统配置，所有东西都封装在一个独立的小应用里，不会污染你的全局环境。而且你可以随意切换API提供商，比如用智谱GLM来降低成本。

## 第一步，创建自动化应用

打开Mac上的Automator。你可以在Spotlight里搜索，或者去应用文件夹找。

![图片：02 查询 mac 自带的应用 automator](Medias/images/02-automator-search.png)

*▲ 在 Spotlight 中搜索 Automator*

点击新建文稿，会弹出一个类型选择的窗口。这里很关键，一定要选应用程序Application，不是快速操作也不是其他选项。

![图片：03 选择 Application 类型，并确定选择](Medias/images/03-application-type.png)

*▲ 选择应用程序类型*

在左侧搜索栏输入AppleScript，然后双击运行AppleScript，把它加入到右侧的工作流区域。

![图片：04 查找 AppleScript 并双击后在右侧输入框内输入如下指令替换掉成自己的 claude code 配置](Medias/images/04-applescript-code.png)

*▲ 添加 AppleScript 代码块*

接下来是最重要的一步。请完全删除编辑器里默认的代码，然后复制粘贴下面的代码。

⚠️ 重要提醒。代码里的YOUR_API_KEY_HERE需要替换成你真实的API Key。当前配置是智谱GLM，用Claude原生或其他API的话，把ANTHROPIC_BASE_URL改成对应地址就行。

另外代码里的注释已经写得很清楚了，里面有空格路径的处理逻辑。

## 第二步，保存应用

按Command+S保存，名称可以叫Claude Launcher，位置选应用程序文件夹。

![图片：05 保存 automator 为 App 应用](Medias/images/05-save-app.png)

*▲ 保存为应用程序*

## 测试示例

这是一个示例 Markdown 文件，包含多张本地图片，用于测试图床上传功能。

**图片说明**：
- 所有图片路径符合 `Medias/images/` 格式
- 每张图片都有描述性的 alt 文本
- 每张图片下方添加了小字说明

测试命令：
```bash
python scripts/cli.py examples/sample_with_images.md -o test_output.md --article-name "claude-launcher-tutorial"
```
