---
name: "react-scan-devtools-qa"
description: "用 react-scan 启用性能可视化，并用 Chrome DevTools MCP 生成/更新用例文档后自动跑浏览器测试。Invoke when 需要自动化回归或性能回归排查。"
---

# React Scan + DevTools 自动化 QA

## 适用场景（何时调用）

当你需要同时完成下面三件事时调用本 Skill：

1. 确保目标页面已启用 React Scan（优先“零改代码”的运行时注入；必要时降级方案）
2. 为指定“模块（包含多个关键路径）”生成或静默更新自动化测试用例 Markdown（Always Green）
3. 用浏览器自动化工具执行用例并输出一份独立的测试报告 Artifact（包含证据与根因）

## 输入（你需要从用户处拿到的信息）

- **模块名称**：用于命名用例文档文件
- **目标环境**：例如 `http://localhost:3000` 或 `https://staging.example.com`
- **关键路径清单**：一个模块的多个路径（例如：`/login`、`/dashboard`、`/settings/profile`）
- **每个路径的关键用户流**：登录/搜索/提交表单/列表筛选/支付等（只需要点）

## 输出（落盘文件）

- 用例文档（Always Green）：`/tests/cases/{模块名称}.md`
- 测试报告（单独输出）：`/tests/reports/{YYYY-MM-DD}_test_execution_report.md`

## Phase 0：安全与前置约束

- 不在日志、报告、截图里暴露任何真实密钥/Token/账号密码。
- 默认在“断言粒度”上遵循最佳实践：UI 可见性与关键文案、导航/URL、console error、关键网络请求（xhr/fetch）状态码；必要时补充性能 trace。

## 附录：用例生成“提示词模板”（原样保留，供生成/更新文档时参考）

```md
# Role: 高级 QA 自动化工程师 (Senior QA & Automation Engineer)

# Goal
负责管理和维护指定模块的《自动化测试用例》文档。
核心职责是：**基于最新代码逻辑，维护一份“始终最新（Always Green）”的测试用例文档**。如果文档已存在，则静默合并更新（追加新用例或修正旧逻辑，**不保留**修订痕迹）；如果不存在，则创建新文档。文档就绪后，执行模拟测试并输出报告。

# Critical Configuration (Inject into Document)
**注意：** 在创建或更新测试用例文档时，**必须**将以下 YAML 内容原封不动地写入文档的 **首部 (Frontmatter)**，不要遗漏任何字段：

```yaml
---
config:
  test_case_style: "Structured Markdown"
  report_output:
    enabled: true
    path: "/tests/reports/"
    filename_pattern: "{YYYY-MM-DD}_test_execution_report.md"
  execution_behavior:
    trigger: "在生成/更新测试用例后，必须单独输出一份测试报告 Artifact"
---
```

# Section 1: Test Case Documentation Format

**生成/更新测试用例文档时，请严格遵守以下结构（包含 YAML 头）：**

[此处插入上方的 YAML Frontmatter]

## [序号]、[模块名称]

### [序号].[子序号] [测试用例标题]

**测试场景**: [一句话描述核心场景]
**前置条件**:

* [条件1]
* [条件2]
**测试步骤**:

1. [动作] (必须包含技术细节: 如 `GET /api/path` 或 `Click #submitBtn`)
2. [动作]
3. [性能采集动作] (必须可量化，见“性能断言”)
**预期结果**:

* [UI/数据变化]
* [关键配置] (如 `config: value` 或 `DB status: updated`)
* [性能预算] (必须可量化，见下方默认指标或模块自定义预算)

---

# Section 1.1: 性能断言（Performance Budgets）

**目标**：把“性能”拆解成可量化、可回归的指标，并写进用例的“预期结果”里；执行时要能采集到数据并落到报告。

建议采用“两层预算”：

1. **Web 性能（页面层）**：来自浏览器 Trace / Web Vitals（偏用户体验、跨技术栈一致）
2. **React 性能（组件层）**：来自 React Scan 回调（偏渲染效率、定位组件级问题）

**默认可量化指标（可按模块覆盖）**

* Web Vitals（一次导航/交互流的采集窗口内）：
  * LCP ≤ 2500ms（或不劣化于 baseline + 15%）
  * CLS ≤ 0.1（或不劣化于 baseline + 0.02）
  * INP ≤ 200ms（或不劣化于 baseline + 20%）
  * TBT ≤ 200ms（或不劣化于 baseline + 20%）
* React Scan（同一采集窗口内聚合）：
  * commitDurationP95 ≤ 50ms（或不劣化于 baseline + 20%）
  * commitDurationMax ≤ 120ms（或不劣化于 baseline + 20%）
  * totalRenders ≤ baseline + 20%
  * unnecessaryRenderRatio ≤ 10%（需开启 `trackUnnecessaryRenders: true` 才能统计）
  * slowRendersTopN：列出 selfTime 最大的 Top 10 组件（用于 RCA，不做 hard-fail 也可）

**采集建议（最佳实践）**

* Web Vitals：用浏览器 Performance trace（可 reload 并自动 stop）拿到 CWV/Insight 或 metrics。
* React Scan：在被测项目的 react-scan 初始化里设置回调（`onCommitStart/onCommitFinish/onRender`）把数据累计到 `window.__REACT_SCAN_METRICS__`，自动化侧再读取并清零。

# Section 2: Test Report Output Format

**测试用例更新完毕后，请立即执行模拟测试，并单独输出一份报告（不要写在测试用例文档里），格式如下：**

# [YYYY-MM-DD] 自动化测试执行报告

## 1. 概览 (Summary)

| 指标 | 结果 |
| --- | --- |
| **执行时间** | YYYY-MM-DD HH:MM:SS |
| **覆盖模块** | [模块名] |
| **测试结果** | [通过/失败/警告] |

## 2. 执行详情 (Details)

| ID | 用例标题 | 状态 | 关键日志/备注 (Root Cause Analysis) |
| --- | --- | --- | --- |
| 1.1 | [标题] | ✅ Pass | 检测到关键函数调用，断言成功 |
| 1.2 | [标题] | ❌ Fail | 预期返回 200，实际返回 403，权限逻辑变更 |

## 3. 性能摘要 (Performance Summary)

### 3.1 Web Vitals（页面层）

| 用例ID | URL/路径 | LCP(ms) | CLS | INP(ms) | TBT(ms) | 预算结论 |
| --- | --- | ---:| ---:| ---:| ---:| --- |
| 1.1 | /path |  |  |  |  | ✅/⚠️/❌ |

### 3.2 React Scan（组件层）

| 用例ID | commitP95(ms) | commitMax(ms) | totalRenders | unnecessaryRatio | Top Slow Components |
| --- | ---:| ---:| ---:| ---:| --- |
| 1.1 |  |  |  |  | ComponentA(12ms), ComponentB(9ms) |

---

# Workflow Guidelines

1. **文件状态检测与处理**：
* **New (新建)**: 若目标模块无测试文档，直接按照 Section 1 格式生成。
* **Existing (更新)**: 若文档已存在，**读取现有内容**，结合最新代码逻辑进行“静默更新”。
* *追加*: 发现新逻辑，直接新增用例。
* *修正*: 发现逻辑变更，直接修改原用例的步骤或预期结果（**不要**标记“已修改”、“Old”或使用删除线，直接展示最终正确版本）。
* *清理*: 若功能已彻底移除，直接从文档中移除对应及用例。

2. **YAML 完整性守护**：
* 无论新建还是更新，必须确保文档顶部的 YAML Frontmatter 完整存在且符合 `Critical Configuration` 的定义。

3. **执行与报告**：
* 文档更新不仅是文字工作，更是执行测试的前提。根据**更新后**的文档逻辑进行模拟执行，输出 Section 2 格式的报告。

# Execution Instruction

当接收到代码变更或模块测试指令时：

1. **Phase 1 (Documentation)**: 输出/更新 Markdown 格式的测试用例文档（含 YAML 头）。
2. **Phase 2 (Report)**: 基于 Phase 1 的最终文档，输出测试执行报告。
```

## Phase 1：检测并启用 React Scan（优先可控且可重复）

### 1.1 打开目标页面并做基线采集

用浏览器工具打开目标 URL，然后：

- 采集一次页面文本快照（用于定位元素与识别是否有 React Scan UI）
- 拉取一次 console error/warn 基线（避免把既有错误误判为本次回归引入）

### 1.2 判断 React Scan 是否已启用（页面证据优先）

按优先级做以下检查（任一命中即可视为“已启用”）：

1. 文本快照中出现明显的 React Scan UI 入口文案（例如 “React Scan”/“Why did this render”等）
2. 运行时探测（执行脚本）：检查页面是否出现疑似工具栏容器（class/id 含 `react-scan`），或全局对象存在（若可检测到）

补充：若能检测到 `window.__REACT_SCAN__` 但工具栏未出现在页面上，可额外检查 `window.__REACT_SCAN_TOOLBAR_CONTAINER__` 是否已挂载到 DOM。若存在但未挂载，可在本地测试环境里将其追加到 `document.body`（用于保证可视化入口可用）：

```js
() => {
  const c = window.__REACT_SCAN_TOOLBAR_CONTAINER__
  if (c && !document.contains(c)) document.body.appendChild(c)
  return {
    hasReactScan: typeof window.__REACT_SCAN__ !== "undefined",
    hasToolbarContainer: !!c,
    toolbarInDom: c ? document.contains(c) : false,
  }
}
```

### 1.3 未启用时：优先 NPM 模块集成（最小改动、可控）

React Scan 需要在 React 运行前被加载，才能可靠地完成 Fiber 仪表化；如果在页面已完成渲染后才注入，可能出现类似 `Must import React Scan before React runs` 的错误。

按优先级选择（先 NPM，后脚本，最后 CLI）：

1. **NPM 模块集成（推荐）**：安装 `react-scan`，并确保入口文件的最顶端先 import，再初始化
   - 依赖检测：在被测项目 `package.json` 里检查是否已存在 `react-scan`
   - 若未安装：用项目的包管理器安装（npm/pnpm/yarn/bun 任选其一）
   - 初始化原则：
     - **import 必须是 top-most**（要在 React/ReactDOM/框架运行前加载）
     - SSR/框架场景一般在 hydration 后执行 `scan()`（常见做法是 `useEffect`）
   - 最小改动建议：新增一个独立文件（例如 `src/react-scan-setup.(js|ts)`），在其中做启用开关与 `scan()`，然后在入口文件第一行 import 该文件

   **Vite / CRA（入口文件示例）**

   ```jsx
   // src/main.jsx 或 src/index.jsx
   import "./react-scan-setup";
   import React from "react";
   import ReactDOM from "react-dom/client";
   ```

   ```jsx
   // src/react-scan-setup.jsx
   import { scan } from "react-scan";

   window.__REACT_SCAN_METRICS__ = {
     commits: [],
     renders: [],
   };

   let commitStart = 0;

   scan({
     enabled: true,
     trackUnnecessaryRenders: true,
     onCommitStart: () => {
       commitStart = performance.now();
     },
     onCommitFinish: () => {
       const durationMs = performance.now() - commitStart;
       window.__REACT_SCAN_METRICS__.commits.push({ durationMs, ts: Date.now() });
     },
     onRender: (_fiber, renders) => {
       for (const r of renders) window.__REACT_SCAN_METRICS__.renders.push(r);
     },
   });
   ```

   **Next.js Pages Router（_app 示例）**

   ```jsx
   // pages/_app.jsx
   // react-scan must be the top-most import
   import { scan } from "react-scan";
   import { useEffect } from "react";

   export default function App({ Component, pageProps }) {
     useEffect(() => {
       scan({ enabled: true });
     }, []);
     return <Component {...pageProps} />;
   }
   ```

2. **脚本预加载集成**：在 HTML head / 框架 layout 的 head 里提前加载 `auto.global.js`，并确保位于其它脚本之前
3. **不可改代码但可接受独立扫描**：使用 React Scan CLI 针对 URL 扫描（性能排查与回归分析优先）
   - `npx react-scan@latest https://your-site`
   - `npx react-scan@latest http://localhost:3000`
4. **仅用于临时尝试**：运行时注入（见 1.4），并以 console 输出为准判断是否成功启用

### 1.4 运行时注入（临时尝试，可能失败）

在页面内动态插入：

`https://unpkg.com/react-scan/dist/auto.global.js`

注入脚本（示例逻辑，执行脚本工具里跑）：

```js
() => new Promise((resolve) => {
  const existing = document.querySelector('script[src*="react-scan"][src*="auto.global.js"]')
  if (existing) return resolve({ ok: true, reason: "already-injected" })
  const s = document.createElement("script")
  s.src = "https://unpkg.com/react-scan/dist/auto.global.js"
  s.async = true
  s.onload = () => resolve({ ok: true, reason: "loaded" })
  s.onerror = () => resolve({ ok: false, reason: "load-failed (CSP or network)" })
  document.head.appendChild(s)
})
```

注入后等待 UI 出现，并检查 console 是否出现 React Scan 初始化失败类错误；若失败，按 1.3 的优先级升级到“预加载集成”或 CLI 扫描。

### 1.5 降级方案（当 CSP 禁止外链脚本）

若 CSP 导致外链脚本加载失败：

1. **项目可改代码时**：改用 npm 方式集成（安装 `react-scan` 并在入口最先 import/初始化），或将 `auto.global.js` 自托管到允许的静态资源域名。
2. **完全不可改代码时**：使用 React Scan CLI 对同一 URL 进行性能扫描（注意：CLI 可能启动独立浏览器实例，不一定与本 Skill 的自动化执行共享同一页）。

## Phase 2：生成/静默更新“自动化测试用例”文档（Always Green）

### 2.1 文档存在性与静默更新规则

- 若 `/tests/cases/{模块名称}.md` 不存在：创建新文档。
- 若已存在：读取旧文档并基于“当前关键路径与用户流”静默更新：
  - 新增：新增路径/新逻辑的用例
  - 修正：逻辑变更则直接改步骤/预期为最终正确版本（不保留修订痕迹）
  - 清理：功能彻底移除则移除用例

### 2.2 YAML Frontmatter（必须原封不动写在首部）

```yaml
---
config:
  test_case_style: "Structured Markdown"
  report_output:
    enabled: true
    path: "/tests/reports/"
    filename_pattern: "{YYYY-MM-DD}_test_execution_report.md"
  execution_behavior:
    trigger: "在生成/更新测试用例后，必须单独输出一份测试报告 Artifact"
---
```

### 2.3 用例结构（严格遵守）

每个模块一个一级标题；每个关键路径至少 2~5 条用例（覆盖 happy path + 常见异常）：

```md
## 1、{模块名称}

### 1.1 {路径A} - {用例标题}

**测试场景**: ...
**前置条件**:
* ...
**测试步骤**:
1. Navigate `{baseUrl}{path}`
2. WaitForText `...`
3. Click `...`
4. Fill `...` = `...`
5. AssertNoConsoleErrors
6. AssertNetwork `GET /api/...` status 200
**预期结果**:
* ...
---
```

### 2.4 步骤可执行性约束（写用例时就要保证“可跑”）

- 所有交互都要落到**可自动化执行**的动作上：Navigate / Click / Fill / PressKey / WaitForText。
- 默认不要把元素写死成“uid=xxx”（uid 每次快照可能变化）。更推荐写成：
  - 可访问名称（a11y label / 按钮文案 / 输入框 placeholder）
  - 或可稳定 selector（如 `#submitBtn`、`[data-testid="save"]`）
- 网络断言写成“方法 + 路径 + 期望状态码”，例如：`AssertNetwork GET /api/users 200`。

## Phase 3：执行自动化（Chrome DevTools MCP）

### 3.1 执行策略（最佳实践默认值）

- 每条用例执行前：Navigate 到路径并重新 take_snapshot，以获取本次页面的元素 uid。
- 执行中：对每一步做最小等待（`wait_for`）而不是盲目 sleep。
- 执行后：
  - 拉取 console error/warn（error 默认视为 Fail；warn 视为 Warning）
  - 拉取 xhr/fetch 网络请求列表并对照用例中的 `AssertNetwork`
  - 失败时截图（可选：成功也截图做基线）
  - 性能采集（可量化）：
    - Web Vitals：对关键路径/关键交互做一次 Performance trace（必要时 `reload: true`），并从 trace/insight 中提取 LCP/CLS/INP/TBT（至少 LCP/CLS）
    - React Scan：若存在 `window.__REACT_SCAN_METRICS__`，读取并聚合 commits/renders，输出 commitP95/commitMax/totalRenders/unnecessaryRatio/topSlowComponents

### 3.2 典型工具调用映射（用来把“文档步骤”变成可执行动作）

- Navigate：`navigate_page({ url })`
- 定位元素：`take_snapshot()` → 用返回的 uid 做后续 click/fill
- Fill：`fill({ uid, value })` 或 `fill_form({ elements })`
- Click：`click({ uid })`
- WaitForText：`wait_for({ text, timeout })`
- 断言 Console：`list_console_messages({ types: ["error","warn"] })`
- 断言 Network：`list_network_requests({ resourceTypes: ["xhr","fetch"] })` + `get_network_request({ reqid })`
- 性能回归（建议开启）：`performance_start_trace({ reload: true, autoStop: true })` + `performance_analyze_insight({ insightName })`

## Phase 4：输出测试报告 Artifact（单独文件，不写回用例文档）

报告输出路径：`/tests/reports/{YYYY-MM-DD}_test_execution_report.md`

报告格式：

```md
# {YYYY-MM-DD} 自动化测试执行报告

## 1. 概览 (Summary)

| 指标 | 结果 |
| --- | --- |
| **执行时间** | YYYY-MM-DD HH:MM:SS |
| **覆盖模块** | {模块名} |
| **测试结果** | [通过/失败/警告] |

## 2. 执行详情 (Details)

| ID | 用例标题 | 状态 | 关键日志/备注 (Root Cause Analysis) |
| --- | --- | --- | --- |
| 1.1 | ... | ✅ Pass | ... |
| 1.2 | ... | ❌ Fail | 期望 ...，实际 ...；console error: ...；network: ... |

## 3. 性能摘要 (Performance Summary)

### 3.1 Web Vitals（页面层）

| 用例ID | URL/路径 | LCP(ms) | CLS | INP(ms) | TBT(ms) | 预算结论 |
| --- | --- | ---:| ---:| ---:| ---:| --- |
| 1.1 | /path |  |  |  |  | ✅/⚠️/❌ |

### 3.2 React Scan（组件层）

| 用例ID | commitP95(ms) | commitMax(ms) | totalRenders | unnecessaryRatio | Top Slow Components |
| --- | ---:| ---:| ---:| ---:| --- |
| 1.1 |  |  |  |  | ComponentA(12ms), ComponentB(9ms) |
```

## 输出检查清单（完成标准）

- React Scan：`window.__REACT_SCAN__` 可验证已启用；必要时工具栏容器可挂载到 DOM
- 用例文档：存在且 YAML 头完整、结构正确、步骤可执行
- 测试报告：单独生成在 `/tests/reports/`，每条用例都有 Pass/Fail/Warning 与 RCA
- 性能数据：报告包含 Web Vitals 与 React Scan 的量化指标（或明确标注未采集原因）
