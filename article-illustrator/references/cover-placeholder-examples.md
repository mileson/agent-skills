# 封面占位扫描示例

本文档提供 `AI封面图` 的标准占位模板，便于 `article-illustrator` 和 `content-creator` 统一识别。

## 1. 微信公众号

适用场景：
- 图文混排平台
- 封面图直接出现在文章头部
- 推荐比例 `21:9`

标准模板：

```markdown
![[AI封面图][wechat][21:9][AI 工作流通道] 电影感编辑风封面，发光的 AI 工作流通道，科技媒体质感，无文字](Materials/Medias/images/cover-wechat.jpg)
```

字段说明：
- `AI封面图`：封面图专用标记
- `wechat`：平台 ID
- `21:9`：平台推荐比例
- `电影感编辑风封面...`：纯画面中文提示词
- `Materials/Medias/images/cover-wechat.jpg`：封面源文件输出路径

## 2. 即刻

适用场景：
- 图文分离平台
- 正文保持纯文字
- 封面图只在头部写注释块
- 推荐比例 `1:1`

标准模板：

```html
<!-- AI封面图
platform: jike
aspect_ratio: 1:1
caption: 个人知识控制台
prompt: 极简科技封面，发光的个人知识控制台，构图干净，适合社区信息流，无文字
output: Materials/Medias/images/cover-jike.jpg
-->
```

字段说明：
- `platform`：平台 ID
- `aspect_ratio`：平台推荐比例
- `caption`：最终给读者看的简短图注
- `prompt`：纯画面中文提示词
- `output`：封面源文件输出路径

## 3. Twitter / X

适用场景：
- 图文分离平台
- feed 首图强调移动端停留
- 推荐比例 `4:5`

标准模板：

```html
<!-- AI封面图
platform: twitter
aspect_ratio: 4:5
caption: AI Agent 控制台
prompt: 电影感编辑风封面，发光的 AI Agent 控制台，主体聚焦强，移动端信息流优先，高对比，无文字
output: Materials/Medias/images/cover-twitter.jpg
-->
```

## 4. 混合示例

同一篇文章既有封面图，也有正文插图时，推荐写法如下：

```markdown
![[AI封面图][wechat][21:9][AI 工作流通道] 电影感编辑风封面，发光的 AI 工作流通道，科技媒体质感，无文字](Materials/Medias/images/cover-wechat.jpg)

# 我把内容工作流重做了一遍

开篇这次最大的变化，不是多了多少模板，而是把封面和正文插图彻底拆开了。

![[AI生图][数据安全隧道][16:9] 数据包在发光的安全隧道中流动，赛博科技氛围，无文字](Materials/Medias/images/01-concept.png)

这里我还需要一张真实的后台界面截图。

![[待截图] 工作流后台配置页](Materials/Medias/images/02-dashboard.png)
> 💡 **截图指引**：打开工作流设置页，圈出平台封面图策略区域。
```

## 5. 不推荐写法

不要这样写：

```markdown
![[AI生图][微信封面图][21:9] 微信公众号头图，横向科技内容封面，无文字](Materials/Medias/images/cover.jpg)
```

原因：
- 这只是普通正文 AI 生图占位
- 没有平台信息
- 没有封面语义
- 没有比例信息
- 后续无法稳定写入 `medias.cover.*`
