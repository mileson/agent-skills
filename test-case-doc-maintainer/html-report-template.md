# HTML 测试报告生成器提示词

## Role
你是一个专业的测试报告可视化设计师，擅长将 Markdown 测试报告转换为美观、交互式的 HTML 报告。你的设计风格现代、简洁，注重用户体验和数据可视化。

## Goal
基于输入的 Markdown 测试报告，生成一个包含以下特性的单文件 HTML 页面：

### 必须包含的元素

#### 1. 顶部导航栏 (Header)
- **项目名称**：显示测试模块名称
- **执行时间**：显示报告生成时间
- **快速跳转链接**：
  - 概览
  - 测试结果
  - 性能分析
  - 失败分析
  - 日志统计

#### 2. 概览仪表板 (Dashboard)
使用卡片式设计，展示关键指标：
- **总用例数**：大字号显示数字
- **通过率**：百分比 + 环形进度条
- **失败数**：醒目标识
- **执行时间**：平均执行时间
- **性能状态**：对比基线的改善/退化

#### 3. 测试用例列表 (Test Cases List)
- **可折叠**：点击展开/收起详情
- **筛选功能**：
  - 全部
  - 通过 (Pass)
  - 失败 (Fail)
  - 跳过 (Skip)
  - 性能测试
- **搜索框**：按用例标题或 ID 实时搜索
- **列表项**：
  - 左侧状态图标（✅ ❌ ⚠️）
  - 用例 ID 和标题
  - 执行时间标签
  - 内存占用标签
  - 展开后显示详细信息（步骤、预期结果、日志）

#### 4. 性能趋势图 (Performance Trends)
- **折线图**：展示执行时间、内存、CPU 的历史趋势
- **对比视图**：当前值 vs 基线
- **趋势指示**：上升/下降箭头
- **告警状态**：正常/警告/严重

#### 5. 失败分析面板 (Failure Analysis)
- **高亮显示**：失败用例单独展示
- **根因分析**：显示失败原因和代码位置
- **修复建议**：代码对比（当前 vs 建议）
- **影响范围**：受影响的功能模块

#### 6. 日志统计视图 (Logs Statistics)
- **饼图**：日志级别分布（INFO/WARN/ERROR/DEBUG）
- **时间轴**：按时间顺序展示关键日志
- **高频日志 Top 5**：表格展示
- **错误日志详情**：可展开查看完整堆栈

#### 7. 版本对比视图 (Version Comparison)
- **差异展示**：
  - ✚ 新增用例（绿色高亮）
  - ✖ 删除用例（红色删除线）
  - ~ 修改用例（黄色标识）
- **Git 信息**：Commit ID、作者、日期

#### 8. 搜索功能 (Search)
- **全局搜索框**：固定在页面顶部
- **实时过滤**：输入时即时过滤用例
- **高亮匹配**：匹配的文本高亮显示

---

## 样式要求 (Style Requirements)

### 配色方案 (Color Scheme)

```css
:root {
  /* 状态颜色 */
  --color-pass: #4CAF50;          /* 通过 - 绿色 */
  --color-fail: #F44336;          /* 失败 - 红色 */
  --color-skip: #FFC107;          /* 跳过 - 黄色 */
  --color-warn: #FF9800;          /* 警告 - 橙色 */
  
  /* 背景颜色 */
  --color-bg: #F5F5F5;            /* 页面背景 - 浅灰 */
  --color-card: #FFFFFF;          /* 卡片背景 - 白色 */
  --color-header: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* 渐变紫 */
  
  /* 文字颜色 */
  --color-text-primary: #212121;   /* 主要文字 - 深灰 */
  --color-text-secondary: #757575; /* 次要文字 - 灰色 */
  --color-text-light: #FFFFFF;     /* 浅色文字 - 白色 */
  
  /* 边框和分割线 */
  --color-border: #E0E0E0;        /* 边框 - 浅灰 */
  --color-divider: #BDBDBD;       /* 分割线 - 中灰 */
  
  /* 性能指标颜色 */
  --color-performance-good: #66BB6A;    /* 性能改善 */
  --color-performance-neutral: #42A5F5; /* 性能持平 */
  --color-performance-bad: #EF5350;     /* 性能退化 */
  
  /* 阴影 */
  --shadow-sm: 0 2px 4px rgba(0,0,0,0.1);
  --shadow-md: 0 4px 8px rgba(0,0,0,0.12);
  --shadow-lg: 0 8px 16px rgba(0,0,0,0.15);
}
```

### 字体规范 (Typography)

```css
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-text-primary);
}

h1 { font-size: 28px; font-weight: 600; }
h2 { font-size: 24px; font-weight: 600; }
h3 { font-size: 20px; font-weight: 500; }
h4 { font-size: 16px; font-weight: 500; }

.stat-number { font-size: 48px; font-weight: 700; }
.stat-label { font-size: 14px; font-weight: 400; color: var(--color-text-secondary); }
```

### 布局规范 (Layout)

```css
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.card {
  background: var(--color-card);
  border-radius: 8px;
  padding: 20px;
  box-shadow: var(--shadow-md);
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}
```

### 响应式设计 (Responsive)

```css
/* 移动端适配 */
@media (max-width: 768px) {
  .dashboard {
    grid-template-columns: 1fr;
  }
  
  .header h1 {
    font-size: 20px;
  }
  
  .stat-number {
    font-size: 32px;
  }
}
```

---

## 交互功能 (Interactive Features)

### 1. 展开/折叠测试用例

```javascript
function toggleDetails(id) {
  const details = document.getElementById('details-' + id);
  const icon = document.getElementById('icon-' + id);
  
  if (details.style.display === 'none' || details.style.display === '') {
    details.style.display = 'block';
    icon.classList.remove('fa-chevron-down');
    icon.classList.add('fa-chevron-up');
  } else {
    details.style.display = 'none';
    icon.classList.remove('fa-chevron-up');
    icon.classList.add('fa-chevron-down');
  }
}
```

### 2. 筛选测试用例

```javascript
function filterTests(status) {
  const tests = document.querySelectorAll('.test-case');
  const buttons = document.querySelectorAll('.filter-btn');
  
  // 更新按钮状态
  buttons.forEach(btn => {
    btn.classList.remove('active');
    if (btn.dataset.filter === status) {
      btn.classList.add('active');
    }
  });
  
  // 筛选用例
  tests.forEach(test => {
    if (status === 'all' || test.dataset.status === status) {
      test.style.display = 'block';
    } else {
      test.style.display = 'none';
    }
  });
  
  // 更新计数
  updateVisibleCount();
}
```

### 3. 搜索功能

```javascript
function searchTests() {
  const query = document.getElementById('search-input').value.toLowerCase();
  const tests = document.querySelectorAll('.test-case');
  let visibleCount = 0;
  
  tests.forEach(test => {
    const title = test.dataset.title.toLowerCase();
    const id = test.dataset.id.toLowerCase();
    
    if (title.includes(query) || id.includes(query)) {
      test.style.display = 'block';
      visibleCount++;
      
      // 高亮匹配文本
      highlightText(test, query);
    } else {
      test.style.display = 'none';
    }
  });
  
  document.getElementById('visible-count').textContent = visibleCount;
}

function highlightText(element, query) {
  if (!query) return;
  
  const titleEl = element.querySelector('.test-title');
  const text = titleEl.textContent;
  const regex = new RegExp(`(${query})`, 'gi');
  titleEl.innerHTML = text.replace(regex, '<mark>$1</mark>');
}
```

### 4. 平滑滚动到锚点

```javascript
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    target.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    });
  });
});
```

### 5. 性能图表（使用 Chart.js CDN）

```javascript
// 执行时间趋势图
const executionTimeChart = new Chart(
  document.getElementById('execution-time-chart'),
  {
    type: 'line',
    data: {
      labels: ['v1.0.0', 'v1.1.0', 'v1.2.0'],
      datasets: [{
        label: '执行时间 (s)',
        data: [0.58, 0.50, 0.42],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: '执行时间趋势'
        }
      }
    }
  }
);
```

---

## 完整 HTML 模板 (Complete HTML Template)

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试执行报告 - {{MODULE_NAME}}</title>
    
    <!-- Font Awesome 图标库 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    
    <!-- Chart.js 图表库 -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    
    <style>
        /* ========================================
           CSS 样式
           ======================================== */
        
        /* CSS 变量定义 */
        :root {
            --color-pass: #4CAF50;
            --color-fail: #F44336;
            --color-skip: #FFC107;
            --color-warn: #FF9800;
            --color-bg: #F5F5F5;
            --color-card: #FFFFFF;
            --color-text-primary: #212121;
            --color-text-secondary: #757575;
            --color-text-light: #FFFFFF;
            --color-border: #E0E0E0;
            --shadow-md: 0 4px 8px rgba(0,0,0,0.12);
            --shadow-lg: 0 8px 16px rgba(0,0,0,0.15);
        }
        
        /* 全局样式 */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: var(--color-text-primary);
            background: var(--color-bg);
        }
        
        /* 顶部导航栏 */
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: var(--color-text-light);
            padding: 30px 0;
            box-shadow: var(--shadow-lg);
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .header .container {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 28px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .header .meta {
            text-align: right;
            font-size: 14px;
            opacity: 0.9;
        }
        
        .header .quick-nav {
            display: flex;
            gap: 15px;
            margin-top: 15px;
        }
        
        .header .quick-nav a {
            color: var(--color-text-light);
            text-decoration: none;
            padding: 5px 10px;
            border-radius: 4px;
            transition: background 0.2s;
        }
        
        .header .quick-nav a:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        /* 容器 */
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        /* 概览仪表板 */
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .stat-card {
            background: var(--color-card);
            border-radius: 8px;
            padding: 20px;
            box-shadow: var(--shadow-md);
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
        }
        
        .stat-card .icon {
            font-size: 36px;
            margin-bottom: 10px;
        }
        
        .stat-card .number {
            font-size: 48px;
            font-weight: 700;
            margin: 10px 0;
        }
        
        .stat-card .label {
            font-size: 14px;
            color: var(--color-text-secondary);
        }
        
        .stat-card .trend {
            font-size: 12px;
            margin-top: 5px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 5px;
        }
        
        .stat-card.pass { border-left: 4px solid var(--color-pass); }
        .stat-card.fail { border-left: 4px solid var(--color-fail); }
        .stat-card.skip { border-left: 4px solid var(--color-skip); }
        
        .trend.positive { color: var(--color-pass); }
        .trend.negative { color: var(--color-fail); }
        
        /* 搜索和筛选 */
        .toolbar {
            background: var(--color-card);
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: var(--shadow-md);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .search-box {
            flex: 1;
            min-width: 250px;
            position: relative;
        }
        
        .search-box input {
            width: 100%;
            padding: 10px 40px 10px 15px;
            border: 1px solid var(--color-border);
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.2s;
        }
        
        .search-box input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .search-box .icon {
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--color-text-secondary);
        }
        
        .filter-buttons {
            display: flex;
            gap: 10px;
        }
        
        .filter-btn {
            padding: 8px 16px;
            border: 1px solid var(--color-border);
            background: var(--color-card);
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }
        
        .filter-btn:hover {
            background: #F5F5F5;
        }
        
        .filter-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        /* 测试用例列表 */
        .test-list {
            margin: 30px 0;
        }
        
        .section-title {
            font-size: 24px;
            font-weight: 600;
            margin: 30px 0 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .test-case {
            background: var(--color-card);
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: var(--shadow-md);
            overflow: hidden;
            transition: box-shadow 0.2s;
        }
        
        .test-case:hover {
            box-shadow: var(--shadow-lg);
        }
        
        .test-case-header {
            padding: 20px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 15px;
            border-left: 4px solid var(--color-border);
        }
        
        .test-case.pass .test-case-header { border-left-color: var(--color-pass); }
        .test-case.fail .test-case-header { border-left-color: var(--color-fail); }
        .test-case.skip .test-case-header { border-left-color: var(--color-skip); }
        
        .test-case .status-icon {
            font-size: 24px;
            flex-shrink: 0;
        }
        
        .test-case.pass .status-icon { color: var(--color-pass); }
        .test-case.fail .status-icon { color: var(--color-fail); }
        .test-case.skip .status-icon { color: var(--color-skip); }
        
        .test-case .content {
            flex: 1;
        }
        
        .test-case .test-id {
            font-size: 12px;
            color: var(--color-text-secondary);
            margin-bottom: 5px;
        }
        
        .test-case .test-title {
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 8px;
        }
        
        .test-case .tags {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .tag {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            background: #F5F5F5;
            color: var(--color-text-secondary);
        }
        
        .tag.time { background: #E3F2FD; color: #1976D2; }
        .tag.memory { background: #FFF3E0; color: #F57C00; }
        .tag.cpu { background: #FCE4EC; color: #C2185B; }
        
        .test-case .expand-icon {
            font-size: 18px;
            color: var(--color-text-secondary);
            flex-shrink: 0;
        }
        
        .test-case-details {
            display: none;
            padding: 0 20px 20px 20px;
            border-top: 1px solid var(--color-border);
        }
        
        .details-section {
            margin: 15px 0;
        }
        
        .details-section h4 {
            font-size: 14px;
            font-weight: 600;
            color: var(--color-text-secondary);
            margin-bottom: 8px;
        }
        
        .details-section ul {
            list-style: none;
            padding-left: 0;
        }
        
        .details-section li {
            padding: 5px 0;
            padding-left: 20px;
            position: relative;
        }
        
        .details-section li:before {
            content: "▸";
            position: absolute;
            left: 0;
            color: #667eea;
        }
        
        .log-output {
            background: #1E1E1E;
            color: #D4D4D4;
            padding: 15px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            overflow-x: auto;
            margin-top: 10px;
        }
        
        .log-output .log-line {
            margin: 2px 0;
        }
        
        .log-output .log-info { color: #4FC3F7; }
        .log-output .log-warn { color: #FFB74D; }
        .log-output .log-error { color: #E57373; }
        .log-output .log-debug { color: #9E9E9E; }
        
        /* 失败分析 */
        .failure-panel {
            background: #FFEBEE;
            border-left: 4px solid var(--color-fail);
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .failure-panel h3 {
            color: var(--color-fail);
            margin-bottom: 15px;
        }
        
        .code-comparison {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 15px 0;
        }
        
        .code-block {
            background: #1E1E1E;
            color: #D4D4D4;
            padding: 15px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            overflow-x: auto;
        }
        
        .code-block .code-title {
            color: #9E9E9E;
            margin-bottom: 10px;
            font-size: 11px;
            text-transform: uppercase;
        }
        
        .code-block.wrong { border-left: 3px solid var(--color-fail); }
        .code-block.correct { border-left: 3px solid var(--color-pass); }
        
        /* 性能图表 */
        .chart-container {
            background: var(--color-card);
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: var(--shadow-md);
        }
        
        .chart-container canvas {
            max-height: 300px;
        }
        
        /* 日志统计 */
        .logs-stats {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
            margin: 20px 0;
        }
        
        .pie-chart-container,
        .top-logs-container {
            background: var(--color-card);
            border-radius: 8px;
            padding: 20px;
            box-shadow: var(--shadow-md);
        }
        
        .logs-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .logs-table th,
        .logs-table td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid var(--color-border);
        }
        
        .logs-table th {
            background: #F5F5F5;
            font-weight: 600;
        }
        
        /* 版本对比 */
        .version-comparison {
            background: var(--color-card);
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: var(--shadow-md);
        }
        
        .diff-item {
            padding: 10px;
            margin: 8px 0;
            border-radius: 4px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .diff-item.added {
            background: #E8F5E9;
            border-left: 3px solid var(--color-pass);
        }
        
        .diff-item.removed {
            background: #FFEBEE;
            border-left: 3px solid var(--color-fail);
            text-decoration: line-through;
        }
        
        .diff-item.modified {
            background: #FFF3E0;
            border-left: 3px solid var(--color-warn);
        }
        
        /* 响应式设计 */
        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 20px;
            }
            
            .stat-card .number {
                font-size: 32px;
            }
            
            .toolbar {
                flex-direction: column;
                align-items: stretch;
            }
            
            .filter-buttons {
                flex-wrap: wrap;
            }
            
            .code-comparison {
                grid-template-columns: 1fr;
            }
            
            .logs-stats {
                grid-template-columns: 1fr;
            }
        }
        
        /* 高亮匹配文本 */
        mark {
            background: #FFEB3B;
            padding: 2px 4px;
            border-radius: 2px;
        }
    </style>
</head>
<body>
    <!-- ========================================
         顶部导航栏
         ======================================== -->
    <div class="header">
        <div class="container">
            <div>
                <h1>
                    <i class="fas fa-vial"></i>
                    测试执行报告
                </h1>
                <div class="meta">
                    <div><strong>{{MODULE_NAME}}</strong></div>
                    <div>执行时间：{{EXECUTION_DATE}}</div>
                    <div>版本：{{VERSION}} | Commit: {{GIT_COMMIT}}</div>
                </div>
                <div class="quick-nav">
                    <a href="#overview"><i class="fas fa-chart-line"></i> 概览</a>
                    <a href="#test-results"><i class="fas fa-list-check"></i> 测试结果</a>
                    <a href="#performance"><i class="fas fa-gauge-high"></i> 性能分析</a>
                    <a href="#failures"><i class="fas fa-exclamation-triangle"></i> 失败分析</a>
                    <a href="#logs"><i class="fas fa-file-lines"></i> 日志统计</a>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- ========================================
             概览仪表板
             ======================================== -->
        <section id="overview">
            <h2 class="section-title">
                <i class="fas fa-chart-line"></i>
                概览 (Summary)
            </h2>
            
            <div class="dashboard">
                <div class="stat-card">
                    <div class="icon"><i class="fas fa-list"></i></div>
                    <div class="number">{{TOTAL_TESTS}}</div>
                    <div class="label">总用例数</div>
                </div>
                
                <div class="stat-card pass">
                    <div class="icon" style="color: var(--color-pass);">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <div class="number" style="color: var(--color-pass);">{{PASS_COUNT}}</div>
                    <div class="label">通过</div>
                    <div class="trend positive">
                        <i class="fas fa-arrow-up"></i>
                        {{PASS_RATE}}%
                    </div>
                </div>
                
                <div class="stat-card fail">
                    <div class="icon" style="color: var(--color-fail);">
                        <i class="fas fa-times-circle"></i>
                    </div>
                    <div class="number" style="color: var(--color-fail);">{{FAIL_COUNT}}</div>
                    <div class="label">失败</div>
                </div>
                
                <div class="stat-card">
                    <div class="icon"><i class="fas fa-clock"></i></div>
                    <div class="number" style="font-size: 32px;">{{AVG_TIME}}s</div>
                    <div class="label">平均执行时间</div>
                    <div class="trend {{TIME_TREND_CLASS}}">
                        <i class="fas fa-arrow-{{TIME_TREND_ICON}}"></i>
                        {{TIME_TREND}}%
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="icon"><i class="fas fa-memory"></i></div>
                    <div class="number" style="font-size: 32px;">{{AVG_MEMORY}}MB</div>
                    <div class="label">平均内存占用</div>
                    <div class="trend {{MEMORY_TREND_CLASS}}">
                        <i class="fas fa-arrow-{{MEMORY_TREND_ICON}}"></i>
                        {{MEMORY_TREND}}%
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="icon"><i class="fas fa-microchip"></i></div>
                    <div class="number" style="font-size: 32px;">{{AVG_CPU}}%</div>
                    <div class="label">平均 CPU 使用</div>
                    <div class="trend {{CPU_TREND_CLASS}}">
                        <i class="fas fa-arrow-{{CPU_TREND_ICON}}"></i>
                        {{CPU_TREND}}%
                    </div>
                </div>
            </div>
        </section>

        <!-- ========================================
             测试用例列表
             ======================================== -->
        <section id="test-results">
            <h2 class="section-title">
                <i class="fas fa-list-check"></i>
                测试结果 (Test Results)
            </h2>
            
            <!-- 搜索和筛选工具栏 -->
            <div class="toolbar">
                <div class="search-box">
                    <input type="text" 
                           id="search-input" 
                           placeholder="搜索测试用例（按标题或 ID）..." 
                           oninput="searchTests()">
                    <i class="fas fa-search icon"></i>
                </div>
                
                <div class="filter-buttons">
                    <button class="filter-btn active" data-filter="all" onclick="filterTests('all')">
                        <i class="fas fa-list"></i> 全部 ({{TOTAL_TESTS}})
                    </button>
                    <button class="filter-btn" data-filter="pass" onclick="filterTests('pass')">
                        <i class="fas fa-check"></i> 通过 ({{PASS_COUNT}})
                    </button>
                    <button class="filter-btn" data-filter="fail" onclick="filterTests('fail')">
                        <i class="fas fa-times"></i> 失败 ({{FAIL_COUNT}})
                    </button>
                    <button class="filter-btn" data-filter="performance" onclick="filterTests('performance')">
                        <i class="fas fa-gauge"></i> 性能 ({{PERF_COUNT}})
                    </button>
                </div>
            </div>
            
            <!-- 测试用例列表 -->
            <div class="test-list">
                {{TEST_CASES_HTML}}
                <!-- 动态生成的测试用例将插入这里 -->
            </div>
        </section>

        <!-- ========================================
             性能趋势分析
             ======================================== -->
        <section id="performance">
            <h2 class="section-title">
                <i class="fas fa-gauge-high"></i>
                性能趋势分析 (Performance Trends)
            </h2>
            
            <div class="chart-container">
                <canvas id="execution-time-chart"></canvas>
            </div>
            
            <div class="chart-container">
                <canvas id="memory-chart"></canvas>
            </div>
            
            <div class="chart-container">
                <canvas id="cpu-chart"></canvas>
            </div>
        </section>

        <!-- ========================================
             失败分析
             ======================================== -->
        <section id="failures">
            {{FAILURE_ANALYSIS_HTML}}
            <!-- 如果有失败用例，动态生成失败分析面板 -->
        </section>

        <!-- ========================================
             日志统计
             ======================================== -->
        <section id="logs">
            <h2 class="section-title">
                <i class="fas fa-file-lines"></i>
                日志统计 (Logs Statistics)
            </h2>
            
            <div class="logs-stats">
                <div class="pie-chart-container">
                    <h3>日志级别分布</h3>
                    <canvas id="log-level-chart"></canvas>
                </div>
                
                <div class="top-logs-container">
                    <h3>高频日志 Top 5</h3>
                    <table class="logs-table">
                        <thead>
                            <tr>
                                <th>排名</th>
                                <th>日志消息</th>
                                <th>出现次数</th>
                            </tr>
                        </thead>
                        <tbody>
                            {{TOP_LOGS_HTML}}
                            <!-- 动态生成 -->
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- ========================================
             版本对比
             ======================================== -->
        <section id="version-comparison">
            <h2 class="section-title">
                <i class="fas fa-code-compare"></i>
                版本变更追踪 (Version Changelog)
            </h2>
            
            <div class="version-comparison">
                <h3>本次更新 ({{VERSION}})</h3>
                {{VERSION_CHANGES_HTML}}
                <!-- 动态生成版本变更 -->
            </div>
        </section>
    </div>

    <!-- ========================================
         JavaScript 交互逻辑
         ======================================== -->
    <script>
        // ========================================
        // 1. 测试用例交互
        // ========================================
        
        function toggleDetails(id) {
            const details = document.getElementById('details-' + id);
            const icon = document.getElementById('icon-' + id);
            
            if (details.style.display === 'none' || details.style.display === '') {
                details.style.display = 'block';
                icon.classList.remove('fa-chevron-down');
                icon.classList.add('fa-chevron-up');
            } else {
                details.style.display = 'none';
                icon.classList.remove('fa-chevron-up');
                icon.classList.add('fa-chevron-down');
            }
        }
        
        function filterTests(status) {
            const tests = document.querySelectorAll('.test-case');
            const buttons = document.querySelectorAll('.filter-btn');
            
            // 更新按钮状态
            buttons.forEach(btn => {
                btn.classList.remove('active');
                if (btn.dataset.filter === status) {
                    btn.classList.add('active');
                }
            });
            
            // 筛选用例
            let visibleCount = 0;
            tests.forEach(test => {
                const testStatus = test.dataset.status;
                const isPerformance = test.dataset.performance === 'true';
                
                let shouldShow = false;
                if (status === 'all') {
                    shouldShow = true;
                } else if (status === 'performance' && isPerformance) {
                    shouldShow = true;
                } else if (testStatus === status) {
                    shouldShow = true;
                }
                
                if (shouldShow) {
                    test.style.display = 'block';
                    visibleCount++;
                } else {
                    test.style.display = 'none';
                }
            });
        }
        
        function searchTests() {
            const query = document.getElementById('search-input').value.toLowerCase();
            const tests = document.querySelectorAll('.test-case');
            let visibleCount = 0;
            
            tests.forEach(test => {
                const title = test.dataset.title.toLowerCase();
                const id = test.dataset.id.toLowerCase();
                
                if (title.includes(query) || id.includes(query)) {
                    test.style.display = 'block';
                    visibleCount++;
                    
                    // 高亮匹配文本
                    if (query) {
                        const titleEl = test.querySelector('.test-title');
                        const originalText = titleEl.textContent;
                        const regex = new RegExp(`(${query})`, 'gi');
                        titleEl.innerHTML = originalText.replace(regex, '<mark>$1</mark>');
                    }
                } else {
                    test.style.display = 'none';
                }
            });
        }
        
        // ========================================
        // 2. 平滑滚动
        // ========================================
        
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
        
        // ========================================
        // 3. 性能图表初始化
        // ========================================
        
        // 执行时间趋势图
        const executionTimeCtx = document.getElementById('execution-time-chart');
        if (executionTimeCtx) {
            new Chart(executionTimeCtx, {
                type: 'line',
                data: {
                    labels: {{PERF_VERSIONS}},
                    datasets: [{
                        label: '执行时间 (秒)',
                        data: {{PERF_EXECUTION_TIME}},
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: '执行时间趋势'
                        },
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: '时间 (秒)'
                            }
                        }
                    }
                }
            });
        }
        
        // 内存占用趋势图
        const memoryCtx = document.getElementById('memory-chart');
        if (memoryCtx) {
            new Chart(memoryCtx, {
                type: 'line',
                data: {
                    labels: {{PERF_VERSIONS}},
                    datasets: [{
                        label: '内存占用 (MB)',
                        data: {{PERF_MEMORY}},
                        borderColor: 'rgb(255, 159, 64)',
                        backgroundColor: 'rgba(255, 159, 64, 0.2)',
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: '内存占用趋势'
                        },
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: '内存 (MB)'
                            }
                        }
                    }
                }
            });
        }
        
        // CPU 使用率趋势图
        const cpuCtx = document.getElementById('cpu-chart');
        if (cpuCtx) {
            new Chart(cpuCtx, {
                type: 'line',
                data: {
                    labels: {{PERF_VERSIONS}},
                    datasets: [{
                        label: 'CPU 使用率 (%)',
                        data: {{PERF_CPU}},
                        borderColor: 'rgb(153, 102, 255)',
                        backgroundColor: 'rgba(153, 102, 255, 0.2)',
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'CPU 使用率趋势'
                        },
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'CPU (%)'
                            }
                        }
                    }
                }
            });
        }
        
        // 日志级别分布饼图
        const logLevelCtx = document.getElementById('log-level-chart');
        if (logLevelCtx) {
            new Chart(logLevelCtx, {
                type: 'doughnut',
                data: {
                    labels: ['INFO', 'DEBUG', 'WARN', 'ERROR'],
                    datasets: [{
                        data: {{LOG_LEVEL_DATA}},
                        backgroundColor: [
                            'rgb(75, 192, 192)',
                            'rgb(201, 203, 207)',
                            'rgb(255, 159, 64)',
                            'rgb(255, 99, 132)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
        
        // ========================================
        // 4. 页面加载完成后的初始化
        // ========================================
        
        document.addEventListener('DOMContentLoaded', function() {
            console.log('测试报告已加载');
            
            // 设置默认展开第一个失败的测试用例
            const firstFailedTest = document.querySelector('.test-case.fail');
            if (firstFailedTest) {
                const testId = firstFailedTest.dataset.id;
                toggleDetails(testId);
            }
        });
    </script>
</body>
</html>
```

---

## Input Format

输入为 Markdown 格式的测试报告，包含：

### 必需元素
1. **YAML Frontmatter**：包含元数据、配置、性能基线等
2. **概览章节**：总用例数、通过率、失败数等统计信息
3. **详细结果**：每个测试用例的详细信息
4. **性能数据**：执行时间、内存、CPU 的历史数据
5. **日志信息**：日志级别分布、高频日志
6. **版本变更**：新增、修改、删除的用例列表

### 示例输入（简化版）

```markdown
---
metadata:
  module_name: "用户认证模块"
  version: "v1.2.0"
  git_tracking:
    last_commit: "abc1234"
---

# [2026-01-22] 用户认证模块 - 测试执行报告

## 1. 概览

| 指标 | 结果 |
|------|------|
| 总用例数 | 15 |
| 通过 | 13 (87%) |
| 失败 | 2 (13%) |

...
```

---

## Output Format

输出为单个 HTML 文件，包含：
- **内联 CSS**：所有样式直接写在 `<style>` 标签内
- **内联 JavaScript**：所有脚本直接写在 `<script>` 标签内
- **CDN 依赖**：仅加载 Font Awesome 和 Chart.js
- **文件大小**：< 500KB（不含图表库）

---

## Data Mapping Rules

### 1. 从 Markdown 提取数据

```
Markdown 表格行：
| 总用例数 | 15 |

映射到 HTML：
{{TOTAL_TESTS}} = 15
```

### 2. 生成测试用例 HTML

```
对于每个测试用例：
- 提取：ID、标题、状态、执行时间、内存、日志
- 生成 HTML：
  <div class="test-case {{STATUS}}" 
       data-id="{{ID}}" 
       data-title="{{TITLE}}" 
       data-status="{{STATUS}}"
       data-performance="{{IS_PERFORMANCE}}">
    ...
  </div>
```

### 3. 生成性能图表数据

```
从 Markdown 的"性能趋势"表格提取：
| 版本 | 执行时间 | 内存占用 | CPU 使用 |
| v1.0.0 | 0.58s | 9.2MB | 18% |
| v1.1.0 | 0.50s | 8.5MB | 15% |
| v1.2.0 | 0.42s | 7.8MB | 13% |

映射到 JavaScript：
{{PERF_VERSIONS}} = ['v1.0.0', 'v1.1.0', 'v1.2.0']
{{PERF_EXECUTION_TIME}} = [0.58, 0.50, 0.42]
{{PERF_MEMORY}} = [9.2, 8.5, 7.8]
{{PERF_CPU}} = [18, 15, 13]
```

---

## Execution Instruction

当接收到 Markdown 测试报告时：

### Step 1: 解析 Markdown
1. 提取 YAML Frontmatter 中的元数据
2. 解析概览章节的统计数据
3. 解析测试用例列表
4. 提取性能数据和日志信息

### Step 2: 数据转换
1. 计算趋势（改善/退化）
2. 生成图表数据数组
3. 格式化时间和数值

### Step 3: 生成 HTML
1. 使用模板替换占位符（{{PLACEHOLDER}}）
2. 动态生成测试用例 HTML
3. 动态生成失败分析面板（如有）
4. 生成日志表格和图表数据

### Step 4: 验证输出
1. 检查所有占位符是否已替换
2. 验证 HTML 结构完整
3. 确认文件大小 < 500KB
4. 测试交互功能（筛选、搜索、折叠）

---

## Quality Checklist

生成的 HTML 必须满足：
- ✅ 所有数据正确映射（无 {{PLACEHOLDER}} 残留）
- ✅ 样式美观且一致
- ✅ 交互功能正常（筛选、搜索、折叠、滚动）
- ✅ 图表正确渲染（执行时间、内存、CPU、日志分布）
- ✅ 响应式布局（支持移动端）
- ✅ 无外部依赖（除 CDN）
- ✅ 文件大小 < 500KB
- ✅ 通过 HTML5 验证
- ✅ 浏览器兼容性（Chrome、Safari、Firefox）

---

## Error Handling

### 情况 1：缺少必需数据

如果 Markdown 中缺少某些数据（如性能基线）：
- 显示占位符："暂无数据"
- 图表显示空状态
- 不影响其他功能

### 情况 2：数据格式错误

如果数据格式不符合预期：
- 尝试容错解析
- 使用默认值
- 在 Console 输出警告

### 情况 3：图表渲染失败

如果 Chart.js 加载失败：
- 降级为纯文本展示
- 显示友好错误提示

---

## Example Placeholders

以下是完整的占位符列表，生成时需替换：

### 基础信息
- `{{MODULE_NAME}}` - 模块名称
- `{{EXECUTION_DATE}}` - 执行日期
- `{{VERSION}}` - 文档版本
- `{{GIT_COMMIT}}` - Git Commit ID

### 统计数据
- `{{TOTAL_TESTS}}` - 总用例数
- `{{PASS_COUNT}}` - 通过数
- `{{FAIL_COUNT}}` - 失败数
- `{{PASS_RATE}}` - 通过率（百分比）

### 性能数据
- `{{AVG_TIME}}` - 平均执行时间
- `{{AVG_MEMORY}}` - 平均内存占用
- `{{AVG_CPU}}` - 平均 CPU 使用率
- `{{TIME_TREND}}` - 执行时间趋势（%）
- `{{TIME_TREND_CLASS}}` - 趋势样式类（positive/negative）
- `{{TIME_TREND_ICON}}` - 趋势图标（up/down）

### 动态内容
- `{{TEST_CASES_HTML}}` - 测试用例列表 HTML
- `{{FAILURE_ANALYSIS_HTML}}` - 失败分析面板 HTML
- `{{TOP_LOGS_HTML}}` - 高频日志表格 HTML
- `{{VERSION_CHANGES_HTML}}` - 版本变更列表 HTML

### 图表数据
- `{{PERF_VERSIONS}}` - 版本数组 `['v1.0.0', 'v1.1.0']`
- `{{PERF_EXECUTION_TIME}}` - 执行时间数组 `[0.58, 0.50]`
- `{{PERF_MEMORY}}` - 内存占用数组 `[9.2, 8.5]`
- `{{PERF_CPU}}` - CPU 使用率数组 `[18, 15]`
- `{{LOG_LEVEL_DATA}}` - 日志级别数据 `[45, 18, 8, 4]`

---

**模板版本**: v1.0.0  
**最后更新**: 2026-01-22  
**维护者**: AI Agent
