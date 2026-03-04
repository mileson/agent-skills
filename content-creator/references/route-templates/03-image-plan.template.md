# Image Plan / Storyboard 模板

## 基本信息
- 平台：{platform}
- 路由：visual_first
- 图片总数：{count}
- 封面优先：是

---

## 图1 封面
![[AI封面图][{platform}][{aspect_ratio}][{封面场景概述}] {中文封面提示词}](Materials/Medias/images/cover-{platform}.jpg)

### 页面角色
- 封面钩子页

### 目的
- {这张图想解决什么点击或停留问题}

---

## 图2 痛点页
![[AI生图][{痛点页场景概述}][{aspect_ratio}] {中文 AI 生图提示词}](Materials/Medias/images/{platform}-02-pain.jpg)

### 页面角色
- 痛点代入页

### 目的
- {这张图想帮助读者理解什么}

---

## 图3 实操截图页
![[待截图] {需要截图的页面或内容}](Materials/Medias/images/{platform}-03-workspace.png)
> 💡 **截图指引**：{打开哪个页面、停留在哪个状态、要标出哪个区域}

### 页面角色
- 实操证明页

### 目的
- {这张图想增强什么可信度}

---

## 统一规则
- 所有 `AI封面图` 与 `[AI生图]` 提示词统一使用中文
- 所有 AI 图片占位必须同时提供 `caption` 与 `prompt`，最终图注只能来自 `caption`
- 所有 AI 图片占位必须显式提供 `aspect_ratio`，并从接口支持的比例集合中选择；微信封面默认 `21:9`
- `caption` 只写场景概述，推荐 4-10 个字，不得出现“无文字、电影级光影、赛博朋克风”等提示词词汇
- 每张图必须明确：图序、角色、目的、来源类型
- `03_image_plan.[platform].md` 是视觉优先链路的图片主文件
- 后续 `article-illustrator` 应优先扫描此文件，而不是优先扫描正文
- 本文件只负责图片执行，不负责替代正文叙事
- 最终 `04_draft.[platform].[style].md` 应与本文件呼应，但不要求逐图逐页机械解释
