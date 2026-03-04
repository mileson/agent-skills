# Web Slides Workflow

本文件定义 `/pptx` 中“网页版输出”的执行标准。首版方法论基于 `frontend-slides`，目标是生成零依赖、浏览器运行、设计感明确的 HTML 演示稿。

配套参考：
- [web-style-presets.md](web-style-presets.md)
- [web-viewport-rules.md](web-viewport-rules.md)

## 核心原则

1. `Zero Dependencies`
   - 默认输出单文件 HTML
   - 默认不引入 npm、打包器、前端框架
2. `Show, Don't Tell`
   - 先给 preview，再让用户选风格
   - 避免让用户只靠抽象形容词做审美决策
3. `Distinctive Design`
   - 拒绝 generic AI 审美
   - 风格必须鲜明，有明确字体、配色、构图特征
4. `Viewport Fitting`
   - 每一页必须完整容纳在 viewport 内
   - slide 内禁止滚动
5. `Production Quality`
   - HTML 结构语义化
   - 动画、交互、响应式、无障碍都有基本标准

## Phase 0：Detect Mode

先识别网页版内的具体任务：

### Mode A：New Web Presentation

用户从零开始做 HTML 演示稿。

进入 `Phase 1: Content Discovery`

### Mode B：PPT Conversion

用户提供 `.ppt` / `.pptx`，要转换成 HTML slides。

进入 `Phase 4: PPT Conversion`

### Mode C：Existing Presentation Enhancement

用户已有 HTML 演示稿，需要美化、重构、修复或增强。

先读现有文件结构，再进入 `Phase 2` 或 `Phase 3`

## Phase 1：Content Discovery

目标：在设计前先拿到演示目的、长度、内容成熟度和图片资源状态。

### Step 1.1：一次性收集核心信息

优先一次性收集下面 4 类信息，避免来回追问：

| 维度 | 要确认的内容 |
|---|---|
| Purpose | 这是 pitch、教学、会议演讲，还是内部汇报 |
| Length | 预计页数：短 / 中 / 长 |
| Content | 已有完整内容、粗略笔记，还是只有主题 |
| Images | 没有图片、使用默认素材目录，或提供自定义路径 |

### Step 1.2：用户图片评估

如果用户没有图片，跳过图片流程，直接走样式探索和 HTML 生成。

如果用户提供了图片目录，先做评估，不要直接塞进页面。

评估维度：
- 文件名和大致尺寸
- 图片内容类型：logo、截图、图表、架构图、人物照等
- 与演示主题的相关性
- 清晰度是否足够
- 是否可直接用于演示页面
- 与页面风格的颜色适配难度

评估结果统一标记为：
- `USABLE`
- `NOT USABLE`

若为 `NOT USABLE`，必须说明原因，例如：
- 模糊
- 构图太乱
- 与主题不相关
- 尺寸过小
- 文件损坏

### Step 1.3：Co-design 规划

图片不是“最后再摆进去”的附件，而是和文案一起参与页面规划。

示例：
- 3 张产品截图 -> 规划 3 张 feature slide
- 1 个 logo -> 规划封面页和结尾页
- 1 张架构图 -> 规划 “How it Works” 或 “系统架构” 页

在进入样式选择前，先把大纲和图片分配关系给用户确认。

## Phase 2：Style Discovery

这是网页版最关键的环节。默认使用 preview 机制，而不是直接问“你想要什么风格”。

### 两种选风格路径

#### Path A：Guided Discovery

默认路径，适合大多数用户。

流程：
1. 询问观众感受目标
2. 生成 3 个风格预览
3. 用户打开预览文件
4. 用户选择一个，或指定混合

#### Path B：Direct Selection

若用户明确知道自己要哪个 preset，可直接选风格名后进入生成。

### Step 2.1：询问感受目标

允许用户从以下方向中选 1~2 个：

- `Impressed / Confident`
- `Excited / Energized`
- `Calm / Focused`
- `Inspired / Moved`

### Step 2.2：生成 3 个风格预览

将 preview 输出到：

```text
.claude-design/slide-previews/
├── style-a.html
├── style-b.html
└── style-c.html
```

每个 preview 的要求：
- 单文件 HTML
- 仅做 1 张 title slide
- 能体现字体、配色、动效、装饰语言
- 尽量 50~100 行级别，够看风格即可

如果用户提供了 `USABLE` 的 logo，可嵌入 preview，提升感知准确度。

### Step 2.3：组织用户决策

给用户看完 preview 后，要求明确选择：
- `A`
- `B`
- `C`
- `Mix`

若选择 `Mix`，必须让用户说明混合规则，例如：
- 字体用 A
- 布局用 B
- 色调和装饰用 C

## Phase 3：Generate Presentation

根据内容规划和最终风格，生成完整网页版演示。

### 交付结构

默认有两种：

#### 方案 1：单个演示

```text
presentation.html
assets/
```

#### 方案 2：多个演示或独立项目

```text
[presentation-name].html
[presentation-name]-assets/
```

### HTML 架构要求

必须包含以下部分：

1. 语义化结构
   - `section.slide`
   - `nav`
   - 标题和内容层级清晰
2. 单页一屏
   - 每个 `.slide` 占满一个 viewport
3. 主题变量
   - 用 `:root` 管理色彩、字号、间距和动效常量
4. 基础导航
   - 键盘切页
   - 滚轮或触控切页
   - 可选导航点和进度条
5. 动画控制
   - 使用 `IntersectionObserver` 触发 `.visible`
   - CSS 负责 reveal 动效

### 必备 JavaScript 能力

网页版演示至少包含：
- 键盘导航
- 触控 / swipe 支持
- 鼠标滚轮切页
- 当前页状态同步
- reveal 动画触发

可以按风格增加增强特效，但不是每次都必须，例如：
- 粒子背景
- 自定义光标
- 轻量 3D tilt
- parallax

### 图片处理流程

若有用户图片，生成前先做加工，不覆盖原图。

常见处理：
- logo 圆形裁切
- 过大图片缩放
- 给截图增加留白或边框
- 根据页面样式增加 framing

基本规则：
- 不要在多个内容页重复使用同一张图，logo 除外
- 截图、图表要和风格颜色做桥接
- 默认使用相对路径引用图片，而不是 base64 内嵌
- 只有用户明确要求“完全单文件”时，才考虑把图片也转成 data URI

## Phase 4：PPT Conversion

当用户提供 `.ppt` / `.pptx` 时，执行转换路径。

### Step 4.1：提取内容

使用 `python-pptx` 提取：
- slide 标题
- 文本内容
- 图片资源
- speaker notes

推荐输出中间结构：

```json
[
  {
    "number": 1,
    "title": "Slide title",
    "content": ["..."],
    "images": ["assets/slide1_img1.png"],
    "notes": "..."
  }
]
```

### Step 4.2：与用户确认提取结果

不要提取完就直接生成网页。

必须先向用户说明：
- 共提取到多少页
- 每页标题和要点概况
- 每页有几张图
- 哪些 notes 被保留

确认后，再进入风格探索。

### Step 4.3：样式探索

PPT 转网页依然需要走 `Phase 2`

因为 `.pptx` 里的内容结构可以保留，但最终网页的视觉风格仍需重新决定。

### Step 4.4：生成 HTML Slides

转换时要尽量保留：
- 文本内容
- 图片资源
- 原始页序
- 备注信息

其中备注可以：
- 放进 HTML 注释
- 另存为旁路文档

## Phase 5：Delivery

### 交付动作

完成后执行：
1. 清理 preview 临时目录
2. 打开最终 HTML 演示
3. 告知用户文件路径、风格名、页数和导航方式

### 交付说明应至少包含

- 输出文件名
- 使用的 style preset
- 总页数
- 键盘导航方式
- 鼠标 / 触控切页方式
- 可调节区域：
  - 颜色变量
  - 字体链接
  - reveal 动画节奏

## 代码质量要求

### HTML / CSS / JS

必须满足：
- 结构语义化
- 样式变量集中
- 注释说明关键模块
- 避免堆砌无意义装饰
- 保持可维护性

### Accessibility

至少做到：
- 键盘可导航
- 合理标题层级
- 必要时有 `aria-label`
- 适配 `prefers-reduced-motion`

### 性能

优先使用：
- `transform`
- `opacity`

避免默认引入高成本动画，尤其是：
- 大量粒子
- 高频 mousemove 监听
- 复杂阴影叠加

## 禁止事项

不要这样做：
- 把 HTML 幻灯片做成普通长网页
- 在 slide 内允许滚动
- 内容太多时硬压字体
- 未评估图片就直接使用
- 用 generic SaaS 模板敷衍网页版输出

## 最终检查

- [ ] 模式识别正确
- [ ] 已做内容发现
- [ ] 已做风格选择
- [ ] 每页符合 viewport fitting
- [ ] 交互和导航可用
- [ ] 图片与文本关系清晰
- [ ] 输出与用户预期一致
