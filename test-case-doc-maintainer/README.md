# 测试用例文档维护器 (Test Case Documentation Maintainer)

## 📚 概述

这是一个自动化测试用例文档维护工具，专注于基于代码分析生成和更新测试用例文档，支持版本追踪、模拟执行、性能指标监控和关键日志分析。

### 核心能力

- ✅ **自动分析测试代码**：从 Swift/XCTest 或 Python/pytest 代码中提取测试逻辑
- ✅ **增量版本追踪**：使用 Git 集成，保留历史版本，自动递增版本号
- ✅ **模拟测试执行**：基于静态分析模拟测试结果，无需实际运行
- ✅ **性能指标监控**：追踪执行时间、内存占用、CPU 使用率
- ✅ **关键日志分析**：提取代码中的日志语句，模拟执行流
- ✅ **双格式报告**：生成 Markdown 文档 + HTML 可视化报告

### 适用场景

- iOS 项目（Swift/XCTest）
- Python 后端项目（pytest）

---

## 🚀 快速开始

### 使用方式

1. **触发 Skill**：

```
你：请帮我生成测试用例文档
或：更新测试文档
或：使用 test-case-doc-maintainer
```

2. **回答 AI 的问题**：

AI 会询问以下信息：
- 项目类型（iOS 或 Python）
- 操作类型（生成新文档或更新现有文档）
- 目标模块名称
- 测试文件路径（可选）

3. **确认并执行**：

AI 会展示执行计划，确认后自动完成整个流程。

---

## 📂 文件结构

Skill 包含以下文件：

```
.cursor/skills/test-case-doc-maintainer/
├── SKILL.md                      # Skill 主文件（核心逻辑）
├── html-report-template.md       # HTML 报告生成提示词模板
└── README.md                     # 本文件（使用说明）
```

生成的文件将保存到：

```
项目根目录/
├── tests/
│   ├── docs/
│   │   ├── iOS/
│   │   │   └── TEST-<ModuleName>.md      # iOS 测试文档
│   │   └── Python/
│   │       └── TEST-<ModuleName>.md      # Python 测试文档
│   └── reports/
│       └── <YYYY-MM-DD>/
│           ├── TEST-<ModuleName>-report.md    # Markdown 报告
│           └── TEST-<ModuleName>-report.html  # HTML 报告
```

---

## 📋 使用示例

### 示例 1：为新模块生成测试文档

```
用户：请帮我生成用户认证模块的测试文档

AI：👋 您好！我将帮您生成测试用例文档。

请告诉我以下信息：
1. 项目类型：iOS 或 Python？
2. 操作类型：生成新文档还是更新现有文档？
3. 目标模块：用户认证模块 ✅
4. 测试文件路径（可选）：如果知道具体路径请提供

用户：iOS 项目，生成新文档，文件在 PoseCamTests/Features/Auth/LoginViewModelTests.swift

AI：📋 确认信息：
- 项目类型：iOS (Swift/XCTest)
- 操作类型：生成新文档
- 目标模块：用户认证模块 - 登录功能
- 测试文件：PoseCamTests/Features/Auth/LoginViewModelTests.swift

🎯 执行计划：
1. 分析测试代码文件（约 30 秒）
2. 提取测试用例和断言逻辑
3. 生成测试文档（包含 YAML 配置）
4. 模拟执行测试并生成报告
5. 生成 HTML 可视化报告

预计耗时：2-3 分钟
是否继续？(Y/n)

用户：Y

AI：✅ 开始执行...
[执行流程...]
🎉 完成！

已生成以下文件：
1. 测试文档：/tests/docs/iOS/TEST-Auth-Login.md
2. Markdown 报告：/tests/reports/2026-01-22/TEST-Auth-Login-report.md
3. HTML 报告：/tests/reports/2026-01-22/TEST-Auth-Login-report.html

📊 摘要：
- 总用例数：8
- 通过率：100%
- 平均执行时间：0.42s
```

### 示例 2：更新现有测试文档

```
用户：代码有变更，请更新用户认证模块的测试文档

AI：👋 检测到您要更新现有文档。

正在检查 Git 变更...
发现以下变更：
- 修改：LoginViewModelTests.swift
- 新增方法：testLoginWithBiometrics_Success()

📋 确认信息：
- 当前版本：v1.1.0
- 新版本：v1.2.0（Minor 递增，因为新增了用例）

是否继续更新？(Y/n)

用户：Y

AI：🎉 更新完成！

变更摘要：
- 新增用例：1
- 修改用例：1
- 版本号：v1.1.0 → v1.2.0

性能变化：
- 执行时间：0.45s → 0.42s (-6.7%) ✅ 改善
```

---

## 📄 生成的文档格式

### 测试文档（Markdown）

测试文档包含以下章节：

```yaml
---
# YAML Frontmatter（配置和元数据）
config:
  test_case_style: "Structured Markdown"
  platform: "iOS"
  framework: "XCTest"
  version_tracking:
    enabled: true
    strategy: "incremental"
  performance_monitoring:
    enabled: true
  logging:
    enabled: true

metadata:
  module_name: "用户认证模块"
  version: "v1.2.0"
  git_tracking:
    last_commit: "abc1234"
  performance_baseline:
    execution_time_avg: "0.42s"
---

# 模块：用户认证模块

## 1. 测试套件概述
## 2. 测试用例清单
  ### 2.1 登录功能测试
    #### 2.1.1 成功登录 - 有效凭证
    #### 2.1.2 登录失败 - 无效密码
## 3. 测试覆盖率矩阵
## 4. 关键日志索引（新增）
## 5. 性能监控配置（新增）
## 6. 待办事项
## 7. 附录
```

### 测试报告（Markdown + HTML）

#### Markdown 报告
- 概览统计
- 详细测试结果
- 失败分析
- 性能趋势
- 日志统计
- 版本变更追踪

#### HTML 报告（可视化）
- 🎨 现代化仪表板
- 📊 交互式图表（Chart.js）
- 🔍 搜索和筛选功能
- 📱 响应式设计（支持移动端）

---

## ⚙️ 配置说明

### YAML Frontmatter 配置

```yaml
config:
  # 报告输出配置
  report_output:
    enabled: true
    path: "/tests/reports/"
    filename_pattern: "{YYYY-MM-DD}_test_execution_report.md"
    html_enabled: true
    html_template_path: ".cursor/skills/test-case-doc-maintainer/html-report-template.md"
  
  # 性能监控配置
  performance_monitoring:
    enabled: true
    metrics:
      - "execution_time"
      - "memory_usage"
      - "cpu_usage"
    baseline_comparison: true
    alert_threshold: 20  # 性能下降超过 20% 时警告
  
  # 日志配置
  logging:
    enabled: true
    log_level: "INFO"
    capture_key_logs: true
    include_in_report: true
```

### 版本号规则

版本号遵循语义化版本控制（Semantic Versioning）：

- **Major (x.0.0)**：测试模块重构，大量用例变更（>50%）
- **Minor (0.x.0)**：新增用例（新增测试方法）
- **Patch (0.0.x)**：修正用例细节、更新断言、文档修正

AI 会根据代码变更类型自动递增版本号。

---

## 🎯 特色功能

### 1. 增量版本追踪

每次更新文档时：
- ✅ 保留历史版本记录
- ✅ 记录 Git Commit 信息
- ✅ 在版本历史表中追加记录
- ✅ 不删除旧用例，标记为"已废弃"

### 2. 性能指标监控

自动追踪以下性能指标：
- ⏱️ 执行时间（秒）
- 💾 内存占用（MB）
- 🖥️ CPU 使用率（%）

支持：
- 对比基线
- 趋势分析
- 性能告警（退化 >20% 时提示）

### 3. 关键日志分析

从代码中提取日志语句：
- 📝 成功路径日志
- ❌ 失败路径日志
- ⚡ 性能相关日志

生成：
- 日志级别分布统计
- 高频日志 Top 5
- 时间轴日志视图

### 4. HTML 可视化报告

使用独立的提示词模板生成 HTML 报告：
- 🎨 美观的仪表板设计
- 📊 Chart.js 图表（执行时间、内存、CPU 趋势）
- 🔍 实时搜索和筛选
- 📱 响应式布局

---

## 🔧 高级功能

### 批量更新多个模块

```
用户：请更新用户认证模块和支付模块的测试文档

AI：好的，我将依次处理以下模块：
1. 用户认证模块
2. 支付模块

[依次执行...]

最后生成汇总报告。
```

### 性能回归检测

如果性能指标下降 > 20%，自动触发告警：

```
⚠️ 性能退化警告

模块：用户认证模块
用例：testLoginPerformance

当前性能：
- 执行时间：0.60s（基线：0.42s，退化 42.9%）❌
- 内存占用：9.5MB（基线：7.8MB，退化 21.8%）❌

建议：
1. 检查是否引入了不必要的同步操作
2. 分析内存泄漏可能性
3. 使用 Instruments 进行深度分析
```

### 测试用例推荐

基于现有用例，推荐缺失的测试场景：

```
💡 测试用例推荐

基于当前覆盖情况，建议补充以下场景：
1. 空值处理：testLoginWithEmptyCredentials()
2. 并发场景：testConcurrentLoginAttempts()
3. 网络异常：testLoginWithNetworkTimeout()
4. 边界值：testLoginWithMaxLengthPassword()
```

---

## 🔍 工作原理

### Phase 1: 用户交互
1. 询问项目类型、操作类型、目标模块
2. 确认测试文件路径
3. 展示执行计划，等待用户确认

### Phase 2: 代码分析
1. 读取测试代码文件
2. 解析测试类、方法、断言
3. 提取日志语句和性能测试
4. 识别 Given-When-Then 结构

### Phase 3: 文档生成
1. 检查文档是否已存在
2. 提取 Git 版本信息
3. 自动递增版本号
4. 生成/更新 Markdown 文档

### Phase 4: 模拟执行
1. 基于断言逻辑推断测试结果
2. 估算性能指标（执行时间、内存、CPU）
3. 生成模拟日志输出
4. 分析潜在风险

### Phase 5: 报告生成
1. 生成 Markdown 报告
2. 调用 HTML 模板提示词
3. 生成可视化 HTML 报告
4. 保存到指定路径

---

## ⚠️ 注意事项

### 1. 静态分析的局限性

此 Skill 使用静态分析，不实际运行测试：
- ✅ 优势：快速、无需测试环境、不影响数据库
- ❌ 局限：无法发现运行时错误、性能指标为估算值

**建议**：配合实际测试执行（如 CI/CD）使用。

### 2. 性能指标为估算值

性能指标基于代码复杂度估算：
- 执行时间：基于操作数量和网络请求
- 内存占用：基于对象大小和数量
- CPU 使用率：基于计算密集度

**建议**：首次运行后，使用实际测量值更新基线。

### 3. 日志为模拟输出

日志从代码中的 `print`/`logger` 语句提取：
- ✅ 优势：无需运行即可看到日志流
- ❌ 局限：动态日志（条件日志）可能不准确

**建议**：仅作参考，实际日志以运行时为准。

### 4. 语言支持

当前仅支持：
- iOS：Swift/XCTest
- Python：pytest

其他语言（如 JavaScript/Jest）需要扩展。

---

## 🆚 与其他 Skill 的关系

### 与 `ios-test-script-generator` 的区别

| 特性 | ios-test-script-generator | test-case-doc-maintainer |
|------|--------------------------|-------------------------|
| **目标** | 生成测试代码 | 生成测试文档 |
| **输入** | 功能需求 | 现有测试代码 |
| **输出** | `.swift` 测试文件 | `.md` 文档 + `.html` 报告 |
| **用途** | 编写新测试 | 记录现有测试 |

**配合使用**：
1. 使用 `ios-test-script-generator` 生成测试脚本
2. 使用 `test-case-doc-maintainer` 为测试脚本生成文档

### 与 `doc-auto-sync-checker` 的关系

- `doc-auto-sync-checker`：检查文档同步状态，发现需要更新的文档
- `test-case-doc-maintainer`：实际更新测试文档

**配合使用**：
1. 代码提交前，运行 `doc-auto-sync-checker`
2. 如果发现测试文档需要更新，调用 `test-case-doc-maintainer`

---

## 🛠️ 故障排除

### 问题 1：无法找到测试文件

**症状**：提示"未找到测试文件"

**解决方案**：
1. 检查文件路径是否正确
2. 检查文件命名是否符合规范：
   - iOS: `*Tests.swift`
   - Python: `test_*.py`
3. 使用搜索功能定位文件

### 问题 2：Git 信息提取失败

**症状**：文档中 Git 信息显示为空

**解决方案**：
1. 检查是否在 Git 仓库中：`git status`
2. 检查是否有提交记录：`git log`
3. 如果是新仓库，先进行一次提交

### 问题 3：HTML 报告生成失败

**症状**：Markdown 报告正常，但 HTML 报告未生成

**解决方案**：
1. 检查 `html-report-template.md` 文件是否存在
2. 检查 Markdown 报告格式是否正确
3. 手动调用模板提示词进行调试

### 问题 4：性能指标明显不合理

**症状**：模拟的性能指标与实际差异很大

**解决方案**：
1. 首次运行后，使用实际测量值更新基线
2. 编辑文档的 YAML Frontmatter 中的 `performance_baseline`
3. 后续更新将基于新基线对比

---

## 📈 未来增强

计划中的功能：
- [ ] 实际测试执行（集成 XCTest / pytest 运行器）
- [ ] 更多语言支持（JavaScript/Jest、Java/JUnit）
- [ ] AI 辅助分析（使用 LLM 分析测试逻辑）
- [ ] 可视化增强（交互式覆盖率地图、依赖关系图）
- [ ] CI/CD 集成（GitHub Actions、GitLab CI）
- [ ] 实时性能监控（集成 Instruments、pytest-monitor）
- [ ] 日志聚合分析（集成 ELK Stack）

---

## 📞 支持

如有问题或建议，请通过以下方式联系：
- 在项目中创建 Issue
- 或直接询问 AI："test-case-doc-maintainer 如何使用？"

---

**Skill 版本**: v1.0.0  
**最后更新**: 2026-01-22  
**维护者**: AI Agent
