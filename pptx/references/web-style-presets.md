# Web Style Presets

本文件定义 `/pptx` 网页版的首批风格预设。初版以 `frontend-slides` 的风格体系为基础，要求风格鲜明、可区分、可复用，不允许退回到 generic AI 模板。

## 选择规则

1. 默认优先走 preview 机制，再让用户选
2. 如果用户已明确指定 preset 名称，可直接使用
3. 所有 preset 都必须遵守 viewport fitting 规则
4. 可以混搭，但必须明确“保留什么、替换什么”

## Presets

### 1. Bold Signal

- 气质：强势、自信、高冲击
- 适合：pitch deck、keynote、对外汇报
- 排版特征：深色背景上叠加高饱和卡片，标题与章节号强存在感
- 字体建议：`Archivo Black` + `Space Grotesk`
- 颜色方向：炭黑、深灰、橙红或珊瑚色强调

### 2. Electric Studio

- 气质：专业、干净、对比强
- 适合：咨询提案、agency 演示、商务方案
- 排版特征：上下或左右双区块结构，蓝白强对比
- 字体建议：`Manrope`
- 颜色方向：黑、白、亮蓝

### 3. Creative Voltage

- 气质：创意、躁动、复古未来感
- 适合：创意提案、品牌发布、视觉型产品
- 排版特征：电蓝与霓虹黄的对撞，分栏、纹理和徽章感装饰
- 字体建议：`Syne` + `Space Mono`
- 颜色方向：电蓝、深蓝黑、霓虹黄

### 4. Dark Botanical

- 气质：优雅、艺术、高级
- 适合：高端品牌、讲故事型发布、情绪表达较强的演示
- 排版特征：深底、柔和模糊抽象形状、细线和温暖强调色
- 字体建议：`Cormorant` + `IBM Plex Sans`
- 颜色方向：深灰黑、暖金、粉棕、旧纸色

### 5. Notebook Tabs

- 气质：编辑感、条理清晰、纸张触感
- 适合：研究报告、复盘、评审、文档型表达
- 排版特征：纸张容器、侧边 tab、轻微文档装饰
- 字体建议：`Bodoni Moda` + `DM Sans`
- 颜色方向：奶油白、深灰、薄荷 / 淡紫 / 粉色标签

### 6. Pastel Geometry

- 气质：友好、现代、亲和
- 适合：产品说明、教育内容、面向非技术受众的介绍
- 排版特征：卡片化内容区、柔和 pills、低压迫感
- 字体建议：`Plus Jakarta Sans`
- 颜色方向：浅蓝灰、奶油白、粉紫绿 pastel 组合

### 7. Split Pastel

- 气质：活泼、现代、创意感强
- 适合：创意团队、品牌工作室、轻商务方案
- 排版特征：双色分屏、大面积柔和底色、标签式装饰
- 字体建议：`Outfit`
- 颜色方向：蜜桃、薰衣草、奶油色

### 8. Vintage Editorial

- 气质：有观点、有个性、杂志感
- 适合：个人品牌、故事型演讲、观点表达
- 排版特征：强 typography、几何装饰、对话式 copy
- 字体建议：`Fraunces` + `Work Sans`
- 颜色方向：奶油纸色、黑、暖棕

### 9. Neon Cyber

- 气质：未来感、技术感、发光效果明显
- 适合：AI、开发工具、科技 startup
- 排版特征：深色舞台、网格、glow、粒子或线框装饰
- 字体建议：`Clash Display` + `Satoshi`
- 颜色方向：深海军蓝、青色、洋红

### 10. Terminal Green

- 气质：开发者、终端、hacker 风格
- 适合：API、基础设施、开发工具、技术演讲
- 排版特征：近似终端界面、scan line、monospace 氛围
- 字体建议：`JetBrains Mono`
- 颜色方向：GitHub dark、终端绿

### 11. Swiss Modern

- 气质：克制、精准、现代主义
- 适合：数据表达、企业简报、结构化内容
- 排版特征：强网格、留白、非对称布局、红色点睛
- 字体建议：`Archivo` + `Nunito`
- 颜色方向：白、黑、鲜红

### 12. Paper & Ink

- 气质：文学、沉静、叙事感
- 适合：讲述型演示、文化内容、品牌故事
- 排版特征：衬线大标题、引用、横线、段落节奏
- 字体建议：`Cormorant Garamond` + `Source Serif 4`
- 颜色方向：暖白、炭黑、深红

## Mood 到 Preset 的映射

| Mood | 优先候选 |
|---|---|
| Impressed / Confident | Bold Signal, Electric Studio, Dark Botanical |
| Excited / Energized | Creative Voltage, Neon Cyber, Split Pastel |
| Calm / Focused | Notebook Tabs, Swiss Modern, Paper & Ink |
| Inspired / Moved | Dark Botanical, Vintage Editorial, Paper & Ink |

## 禁用的 generic 模式

默认禁止以下低辨识度方案：

- `Inter` / `Roboto` / 系统字体做主展示字体
- 白底紫渐变 SaaS 模板感
- 千篇一律的 hero + 三卡片布局
- 没有理由的玻璃拟态
- 为了“高级”堆过重阴影
- 与主题无关的写实插画

## 风格混搭规则

允许混搭，但必须只在以下层面混：
- 字体系统
- 色彩系统
- 装饰语言
- 版式结构

不要无规则拼接 3 套风格，避免页面失控。

推荐做法：
- 结构来自 `Swiss Modern`
- 色彩来自 `Bold Signal`
- 装饰节奏来自 `Dark Botanical`

## CSS 注意事项

### 禁止直接对函数取负值

错误写法：

```css
right: -clamp(24px, 4vw, 40px);
top: -min(8vh, 64px);
```

正确写法：

```css
right: calc(-1 * clamp(24px, 4vw, 40px));
top: calc(-1 * min(8vh, 64px));
```

原因：
- 浏览器会静默忽略前一种写法
- 页面会出现定位失效，但控制台不一定报错

## 选择输出建议

- 高冲击对外场景：`Bold Signal` / `Neon Cyber`
- 可信赖商务场景：`Electric Studio` / `Swiss Modern`
- 研究与报告场景：`Notebook Tabs` / `Paper & Ink`
- 艺术和品牌叙事场景：`Dark Botanical` / `Vintage Editorial`
