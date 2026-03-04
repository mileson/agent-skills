# Web Viewport Fitting Rules

这是 `/pptx` 网页版的硬规则。任何 HTML slides 输出都必须满足本文件要求。

## Golden Rule

```text
每一页 slide = 一个完整 viewport
内容放不下 = 拆页或删减
禁止在 slide 内滚动
```

如果某一页需要滚动才看得完，这一页就是失败的。

## 内容密度上限

| 页面类型 | 上限建议 |
|---|---|
| Title slide | 1 个主标题 + 1 个副标题 + 可选 tagline |
| Content slide | 1 个标题 + 4~6 个 bullet，或 2 段正文 |
| Feature grid | 1 个标题 + 最多 6 个卡片 |
| Code slide | 1 个标题 + 8~10 行代码 |
| Quote slide | 1 段引用，最长约 3 行 + attribution |
| Image slide | 1 个标题 + 1 张主图，主图高度控制在约 60vh 内 |

超过上限时：
- 拆成两页
- 将内容改成“章节页 + 内容页”
- 缩短 bullet 文案

不要：
- 把字体缩到不可读
- 把 padding 全部挤没
- 让图片把文字顶出 viewport

## 必备 CSS 结构

### 文档级

```css
html,
body {
  height: 100%;
  overflow-x: hidden;
}

html {
  scroll-snap-type: y mandatory;
  scroll-behavior: smooth;
}
```

### Slide 级

```css
.slide {
  width: 100vw;
  height: 100vh;
  height: 100dvh;
  overflow: hidden;
  scroll-snap-align: start;
  display: flex;
  flex-direction: column;
  position: relative;
}
```

### 内容容器

```css
.slide-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  max-height: 100%;
  overflow: hidden;
  padding: var(--slide-padding);
}
```

### 响应式变量

字号和间距必须使用 `clamp()` 或 viewport 相关单位，不允许全站固定像素值。

```css
:root {
  --title-size: clamp(1.5rem, 5vw, 4rem);
  --h2-size: clamp(1.2rem, 3.5vw, 2.5rem);
  --body-size: clamp(0.8rem, 1.4vw, 1.1rem);
  --slide-padding: clamp(1rem, 4vw, 4rem);
  --content-gap: clamp(0.5rem, 2vw, 2rem);
}
```

## 图片与网格规则

### 图片

```css
img,
.image-container {
  max-width: 100%;
  max-height: min(50vh, 400px);
  object-fit: contain;
}
```

### Grid

```css
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
  gap: clamp(0.5rem, 1.5vw, 1rem);
}
```

规则：
- 卡片数量优先控制，而不是无限缩小
- 窄屏时自动变为单列
- 卡片内文字也必须受内容密度限制

## 高度断点

至少覆盖以下 viewport 高度：
- `< 700px`
- `< 600px`
- `< 500px`

建议策略：
- 减小 padding
- 缩短内容块间距
- 降低标题字号上限
- 隐藏非必要装饰

示例：

```css
@media (max-height: 700px) {
  :root {
    --slide-padding: clamp(0.75rem, 3vw, 2rem);
    --content-gap: clamp(0.4rem, 1.5vw, 1rem);
  }
}

@media (max-height: 600px) {
  :root {
    --title-size: clamp(1.1rem, 4vw, 2rem);
    --body-size: clamp(0.72rem, 1.2vw, 0.96rem);
  }

  .decorative,
  .nav-dots,
  .keyboard-hint {
    display: none;
  }
}
```

## Reduced Motion

必须兼容 `prefers-reduced-motion`：

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.2s !important;
  }

  html {
    scroll-behavior: auto;
  }
}
```

## 生成前检查清单

- [ ] 每个 `.slide` 都是 `100vh / 100dvh`
- [ ] 每个 `.slide` 都有 `overflow: hidden`
- [ ] 所有关键字号使用 `clamp()`
- [ ] 所有关键间距使用 `clamp()` 或 viewport 单位
- [ ] 图片有 `max-height` 约束
- [ ] Grid 是自适应的
- [ ] 已提供 700 / 600 / 500 高度断点
- [ ] 没有固定高度把内容撑爆
- [ ] 内容超量时已拆页

## 测试尺寸

交付前建议至少在以下尺寸检查：

- Desktop：`1920x1080`、`1440x900`、`1280x720`
- Tablet：`1024x768`、`768x1024`
- Mobile：`375x667`、`414x896`
- Landscape phone：`667x375`、`896x414`

## 常见失败模式

### 1. 页面看起来像正常网页

原因：
- 使用了 `min-height` 而不是固定 viewport 高度
- slide 容器允许自然撑开

### 2. 移动端被截断

原因：
- 没有 `100dvh`
- 没有高度断点
- 标题和图片都用了固定尺寸

### 3. 明明没报错，但装饰错位

原因：
- 直接写了 `-clamp(...)` 或 `-min(...)`
- 浏览器忽略了整条声明

正确做法：

```css
left: calc(-1 * clamp(16px, 2vw, 32px));
```
