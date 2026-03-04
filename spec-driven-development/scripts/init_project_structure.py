#!/usr/bin/env python3
"""
初始化项目文档结构（Greenfield 模式）

使用方法:
    python3 init_project_structure.py --project-name "电商平台" --output-dir Documentation/
"""

import sys
from datetime import datetime
from pathlib import Path


def resolve_documentation_root(output_dir: str) -> Path:
    """将输出路径规范化为 Documentation 根目录。"""
    base_path = Path(output_dir)
    if base_path.name == "Documentation":
        return base_path
    return base_path / "Documentation"


def build_doc_header(
    title: str,
    project_name: str,
    system_name: str,
    version: str,
    author: str,
    updater: str,
) -> str:
    """构造统一的文档头部。"""
    today = datetime.now().strftime("%Y-%m-%d")
    return "\n".join(
        [
            f"# {title}",
            "",
            "---",
            "",
            f"**项目名称**：{project_name}",
            f"**所属系统**：{system_name}",
            f"**文档版本**：{version}",
            f"**编写日期**：{today}",
            f"**更新日期**：{today}",
            f"**编写人**：{author}",
            f"**更新人**：{updater}",
            "",
            "---",
            "",
            "## 文档修订历史",
            "",
            "| 版本 | 日期 | 修订人 | 修订内容 |",
            "|------|------|--------|----------|",
            f"| {version} | {today} | {updater} | 初始版本 |",
            "",
        ]
    )


def create_directory_structure(base_path: Path):
    directories = [
        "Basic",
        "Basic/PRD",
        "Basic/Architecture",
        "Basic/Database",
        "Basic/API",
        "Basic/Testing",
        "Basic/UI",
        "Framework",
        "Framework/Standards",
        "Framework/CommonCapabilities",
        "Framework/ProblemSolutions",
        "Modules",
        "Modules/_template",
        "DevLogs",
        "DevLogs/errors",
    ]
    for dir_name in directories:
        (base_path / dir_name).mkdir(parents=True, exist_ok=True)


def build_folder_manual_filename(dir_name: str) -> str:
    """根据文件夹名生成带前缀的说明书文件名。"""
    folder_name = Path(dir_name).name or dir_name
    return f"{folder_name}_README.md"


def build_folder_manual(title: str, core_function: str, folder_input: str, output: str, position: str, dependencies: list[str]) -> str:
    """构造统一的文件夹说明书。"""
    dependency_lines = "\n".join(f"- {item}" for item in dependencies) if dependencies else "- 无显式依赖"
    return "\n".join(
        [
            f"# {title} 说明书 (Folder Manual)",
            "## 核心功能 (Core Function)",
            core_function,
            "",
            "## 输入 (Input)",
            folder_input,
            "",
            "## 输出 (Output)",
            output,
            "",
            "## 定位 (Position)",
            position,
            "",
            "## 依赖 (Dependency)",
            dependency_lines,
            "",
        ]
    )


def build_default_folder_manual_spec(relative_dir: str) -> dict[str, object]:
    """为未显式配置的目录生成默认说明书模板。"""
    parts = Path(relative_dir).parts
    folder_name = Path(relative_dir).name

    if parts and parts[0] == "Modules" and len(parts) >= 2 and folder_name != "_template":
        return {
            "title": folder_name,
            "core_function": f"承载 {folder_name} 模块的需求文档、技术文档与模块级回写内容，形成该模块的知识闭环。",
            "input": "模块定位、业务场景、技术设计、实施现状与回写结论。",
            "output": f"{folder_name} 模块的需求文档、技术文档与模块文件夹说明书。",
            "position": "Modules 下的业务模块目录，连接全局共识与具体功能落地。",
            "dependencies": ["模块需求文档定义业务侧需求", "模块技术文档定义研发侧落地方案"],
        }

    return {
        "title": folder_name,
        "core_function": f"承载 {folder_name} 目录下的文档资产，统一该目录的职责边界与维护方式。",
        "input": "该目录对应的规范、需求、技术设计或执行信息。",
        "output": f"{folder_name} 目录中的正式文档与配套说明。",
        "position": f"{relative_dir} 对应的文档分层目录，用于组织同类知识资产。",
        "dependencies": ["上层目录定义总体边界", "子文档承接具体内容"],
    }


def create_folder_manual_files(base_path: Path):
    manual_specs = {
        "Basic": {
            "title": "Basic",
            "core_function": "沉淀系统级基础共识文档，统一产品、架构、数据、契约、测试和全局 UI 规范。",
            "input": "产品定位结论、需求澄清结果、架构共识、数据与接口规范。",
            "output": "系统级基础文档、跨模块共享的产品与技术共识。",
            "position": "Documentation 的基础层，连接产品定义、模块设计与后续研发执行。",
            "dependencies": ["PRD 子目录沉淀产品共识", "Architecture 子目录沉淀技术共识"],
        },
        "Basic/PRD": {
            "title": "PRD",
            "core_function": "记录产品概述、目标用户、核心流程与边界场景，作为全局需求输入源。",
            "input": "需求访谈结论、产品定位摘要、业务场景与验收标准。",
            "output": "全局需求文档、产品级 ASCII 草图与范围定义。",
            "position": "Basic 层中的产品需求区，连接前期澄清与模块需求文档。",
            "dependencies": ["1_产品概述.md 定义产品主目标", "3_核心流程.md 定义全局业务流程"],
        },
        "Basic/Architecture": {
            "title": "Architecture",
            "core_function": "沉淀全局架构方案、关键时序和技术选型，为模块技术文档提供统一约束。",
            "input": "系统边界、核心流程、关键技术决策。",
            "output": "架构图、时序图、技术选型与全局技术原则。",
            "position": "Basic 层中的全局技术设计区，连接需求定义与模块实现设计。",
            "dependencies": ["系统架构文档提供全局分层", "交互时序图提供关键协作流程"],
        },
        "Basic/Database": {
            "title": "Database",
            "core_function": "记录全局数据模型、表结构和数据字典，为模块数据设计提供统一基线。",
            "input": "领域对象、状态定义、持久化约束。",
            "output": "表设计文档、字段字典、索引与数据约束说明。",
            "position": "Basic 层中的数据设计区，连接业务规则与持久化实现。",
            "dependencies": ["系统架构文档定义数据边界", "模块技术文档引用全局数据规则"],
        },
        "Basic/API": {
            "title": "API",
            "core_function": "沉淀全局 Contract、接口规范和错误码规则，统一系统交互方式。",
            "input": "接口约束、事件定义、错误处理共识。",
            "output": "API / Contract 文档、查询规范、错误码说明。",
            "position": "Basic 层中的契约设计区，连接模块技术设计与外部交互。",
            "dependencies": ["RESTful API 文档定义接口基线", "错误码文档定义统一失败语义"],
        },
        "Basic/Testing": {
            "title": "Testing",
            "core_function": "定义测试策略和验证门禁，为 Agent 执行和验收提供统一标准。",
            "input": "验收标准、关键风险、回归范围。",
            "output": "测试策略、验证规则与测试基线。",
            "position": "Basic 层中的质量保障区，连接需求验收与开发验证。",
            "dependencies": ["测试策略文档定义验证方法", "Framework/Standards/测试框架规范.md 提供测试范式"],
        },
        "Basic/UI": {
            "title": "UI",
            "core_function": "沉淀全局信息架构、导航结构和交互规范，不承载模块级页面细节。",
            "input": "产品主流程、导航结构、全局交互原则。",
            "output": "信息架构总览、全局导航规范、全局交互共识。",
            "position": "Basic 层中的全局体验区，连接产品定位与模块级交互设计。",
            "dependencies": ["PRD 文档定义产品主路径", "模块需求文档承接模块级 ASCII 与流程"],
        },
        "Framework": {
            "title": "Framework",
            "core_function": "沉淀跨模块复用的规范、通用能力和问题解决方案，减少重复设计与重复踩坑。",
            "input": "项目级范式、跨模块能力抽象、历史问题复盘。",
            "output": "Standards、CommonCapabilities、ProblemSolutions 三类框架资产。",
            "position": "Documentation 的框架层，连接全局共识与模块落地实践。",
            "dependencies": ["Standards 提供统一规范", "ProblemSolutions 提供历史坑与标准解法"],
        },
        "Framework/Standards": {
            "title": "Standards",
            "core_function": "定义项目级标准，如业务模块文档规范、架构模式规范和测试框架规范。",
            "input": "项目方法论、设计标准、质量门禁。",
            "output": "规范文档、模板规则、统一执行标准。",
            "position": "Framework 中的标准层，作为模块需求和技术文档的统一写作与设计基线。",
            "dependencies": ["业务模块技术文档规范.md 约束模块文档结构", "测试框架规范.md 约束测试策略"],
        },
        "Framework/CommonCapabilities": {
            "title": "CommonCapabilities",
            "core_function": "沉淀可在多个模块复用的能力文档，统一能力边界、输入输出与使用方式。",
            "input": "跨模块复用能力、通用服务方案、能力约束。",
            "output": "能力说明文档、能力模板、最佳实践与反模式。",
            "position": "Framework 中的通用能力层，连接基础规范与模块技术实现。",
            "dependencies": ["Standards 提供统一结构要求", "模块技术文档回写可复用能力"],
        },
        "Framework/ProblemSolutions": {
            "title": "ProblemSolutions",
            "core_function": "沉淀历史问题、反模式和标准解法，帮助 Agent 在实现前复用已有经验。",
            "input": "踩坑记录、故障复盘、约束与验证方式。",
            "output": "问题方案文档、风险约束、验证清单。",
            "position": "Framework 中的问题治理层，连接历史经验与当前实现决策。",
            "dependencies": ["CommonCapabilities 提供能力基线", "模块技术文档回写偏差与解决方案"],
        },
        "Modules": {
            "title": "Modules",
            "core_function": "承载业务模块的需求文档和技术文档，形成模块级知识闭环。",
            "input": "模块级需求澄清结果、模块架构设计、执行回写结论。",
            "output": "模块需求文档、模块技术文档、模块文件夹说明书。",
            "position": "Documentation 的模块层，连接全局共识与具体功能落地。",
            "dependencies": ["模块需求文档承接业务定义", "模块技术文档承接研发实现"],
        },
        "Modules/_template": {
            "title": "_template",
            "core_function": "提供模块需求文档模板和模块技术文档模板，统一新模块文档起点。",
            "input": "模块文档规范、常用章节模板、写作约束。",
            "output": "模块需求文档模板、模块技术文档模板。",
            "position": "Modules 下的模板层，服务新模块初始化。",
            "dependencies": ["Framework/Standards/业务模块技术文档规范.md 约束模板结构"],
        },
        "DevLogs": {
            "title": "DevLogs",
            "core_function": "沉淀版本化执行跟踪、TODO 分片、风险、待确认项和文档回写记录，支撑长任务推进。",
            "input": "阶段任务、当前进度、当前任务指针、风险、回写结果。",
            "output": "版本化执行跟踪文档、TODO 清单与错误日志索引。",
            "position": "Documentation 的执行层，连接规划、开发执行与回写闭环。",
            "dependencies": ["执行跟踪文档承接总体导航", "TODO 清单承接详细顺序任务", "errors 子目录承接结构化错误日志"],
        },
        "DevLogs/errors": {
            "title": "errors",
            "core_function": "存放结构化错误日志，帮助定位长任务执行中的异常与回写问题。",
            "input": "任务异常、失败上下文、错误摘要。",
            "output": "结构化错误日志文件。",
            "position": "DevLogs 下的错误记录区，服务问题追踪与复盘。",
            "dependencies": ["执行跟踪文档引用错误上下文", "ProblemSolutions 沉淀复盘后的标准解法"],
        },
    }

    all_directories = sorted(
        str(path.relative_to(base_path))
        for path in base_path.rglob("*")
        if path.is_dir()
    )

    for dir_name in all_directories:
        spec = manual_specs.get(dir_name, build_default_folder_manual_spec(dir_name))
        manual_path = base_path / dir_name / build_folder_manual_filename(dir_name)
        if not manual_path.exists():
            manual_path.write_text(
                build_folder_manual(
                    title=spec["title"],
                    core_function=spec["core_function"],
                    folder_input=spec["input"],
                    output=spec["output"],
                    position=spec["position"],
                    dependencies=spec["dependencies"],
                ),
                encoding="utf-8",
            )


def create_doc_standard(base_path: Path, project_name: str, system_name: str):
    today = datetime.now().strftime("%Y-%m-%d")
    content = f"""# 文档规范

**项目名称**：{project_name}
**所属系统**：{system_name}
**创建时间**：{today}

## 目录分层规则

```text
Documentation/
├── Basic/
├── Framework/
│   ├── Standards/
│   ├── CommonCapabilities/
│   └── ProblemSolutions/
├── Modules/
│   └── <模块名>/
│       ├── <模块名>_README.md
│       ├── <模块名>_需求文档.md
│       └── <模块名>_技术文档.md
└── DevLogs/
    ├── v1.0_执行跟踪.md
    └── v1.0_TODO_01.md
```

## 层级职责

1. `Basic/`：系统级基础共识文档
2. `Framework/Standards/`：项目级规范与范式
3. `Framework/CommonCapabilities/`：跨模块复用能力
4. `Framework/ProblemSolutions/`：历史坑、反模式、标准解法
5. `Modules/`：模块级知识闭环，业务模块使用双文档模型
6. `DevLogs/`：版本化执行跟踪、TODO 分片与错误日志

## 文件夹说明书命名规则

所有目录说明文档统一采用“文件夹前缀 + `_README.md`”命名，避免出现大量同名 `README.md`：

- `Basic/Basic_README.md`
- `Basic/PRD/PRD_README.md`
- `Framework/CommonCapabilities/CommonCapabilities_README.md`
- `Modules/<模块名>/<模块名>_README.md`

文件夹说明书统一采用 `Folder Manual` 结构，至少包含：

1. 核心功能 (Core Function)
2. 输入 (Input)
3. 输出 (Output)
4. 定位 (Position)
5. 依赖 (Dependency)

## Greenfield 需求沟通规则

必须先完成 4 轮访谈，再允许初始化正式文档：

1. 产品定位访谈（战略层 / 范围层 / 交互认知预判）
2. 目标 / 边界 / 验收访谈
3. 业务场景循环访谈
4. 业务场景流程澄清

## Brownfield 需求沟通规则

必须先完成：

1. 读取现有文档
2. 输出“产品定位审计摘要”
3. 用户确认定位是否变化

之后再进入 4 轮增量访谈。

## 模块双文档模型

### 模块需求文档

必须至少包含：

1. 模块概览卡
2. 业务背景
3. 目标用户与产品定位
4. 业务场景
5. 业务场景流程（Mermaid）
6. 功能需求
7. 业务规则
8. 业务 ASCII 交互稿
9. 验收标准
10. 边界与待确认项

### 模块技术文档

必须至少包含：

1. 模块说明书 (Module Manual)
2. 需求映射
3. 系统架构
4. 数据 / 状态模型
5. Contract / API / 事件
6. 技术流程设计
7. 异常与补偿
8. 实施现状
9. 测试设计
10. FAQ / 检查清单 / 代码同步说明 / 附录

## ASCII 与图稿职责

- `Basic/PRD/1_产品概述.md`：产品级 ASCII 草图
- `Basic/UI/1_信息架构总览.md`：全局信息架构 / 全局导航 / 全局交互规范
- `Modules/<模块名>/<模块名>_需求文档.md`：模块级业务 ASCII
- `Modules/<模块名>/<模块名>_技术文档.md`：技术流程 / 状态 / 关系图

## 执行跟踪与 TODO 规则

不再默认拆分 `feature_list.json + PROGRESS.md`。

改为每个版本维护：

- `v1.0_执行跟踪.md`
- `v1.0_TODO_01.md`
- `v1.1_执行跟踪.md`
- `v1.1_TODO_01.md`
- `v2.0_执行跟踪.md`
- `v2.0_TODO_01.md`

其中：

1. `执行跟踪.md`：维护总体状态、当前 TODO 文件、当前任务指针、阶段进展与回写记录
2. `TODO_01.md / TODO_02.md ...`：维护详细任务清单

### TODO 约束

- 每个 TODO 文件最多 30 条任务
- 超过 30 条必须继续拆分到下一个 TODO 文件
- 所有任务必须顺序编号
- 所有依赖只能指向更早任务
- 禁止交叉依赖、循环依赖和未来依赖

`执行跟踪.md` 必须包含：

1. 项目状态
2. 当前版本目标
3. 当前 TODO 文件
4. 当前检查点
5. 本轮进展
6. 待确认项
7. 风险与阻塞
8. 文档回写记录

## 交叉验证规则

只保留 3 条核心对照链：

1. 模块需求文档 -> 模块技术文档
2. 模块需求文档 -> 版本 TODO 清单
3. 模块技术文档 -> 修订历史 / 代码同步说明

## 轻量 Evaluation

每阶段结束都要输出：

- 是否可放行
- 当前歧义等级
- 当前风险等级
- 进入下一阶段前必须解决的问题

评估维度：

1. 完整性
2. 清晰度
3. 可落地性
4. 可验证性

## 轻量 Correction

偏差出现后至少要：

1. 判断是需求偏差 / 设计偏差 / 实现偏差
2. 更新对应文档
3. 追加修订历史
4. 更新对应版本执行跟踪文档
5. 必要时同步更新对应版本 TODO 清单
5. 必要时沉淀到 `ProblemSolutions` 或 `CommonCapabilities`

## 文档修订历史

所有正式文档必须维护修订历史：

| 版本 | 日期 | 修订人 | 修订内容 |
|------|------|--------|----------|
| v1.0 | {today} | AI Agent | 初始版本 |
"""
    (base_path / "00_文档规范.md").write_text(content, encoding="utf-8")


def create_basic_documents(base_path: Path, project_name: str, system_name: str):
    docs = {
        "Basic/PRD/1_产品概述.md": (
            "产品概述",
            """
## 项目背景

- 当前业务痛点：待补充
- 为什么现在要做：待补充

## 目标用户

- 主用户群体：待补充
- 次用户群体：待补充
- 用户关键诉求：待补充

## 核心价值

- 对用户的核心价值：待补充
- 对业务的核心价值：待补充
- 与现有方案的差异点：待补充

## 首版产品级 ASCII 草图

```text
+----------------------------------------------------------------------------------+
| Logo / 项目名                          搜索 / 全局操作 / 用户入口                 |
+---------------------------+------------------------------------------------------+
| 产品级导航 / 模块入口       | 产品级主画布                                         |
| - 模块A                   | +---------------------------+ +--------------------+ |
| - 模块B                   | | 核心主任务区              | | 辅助信息 / 说明区 | |
| - 设置                    | | - 关键输入 / 关键结果     | | - 风险 / 提示     | |
|                           | | - 主 CTA                  | | - 次要 CTA        | |
|                           | +---------------------------+ +--------------------+ |
+---------------------------+------------------------------------------------------+
| 底部：全局状态 / 帮助 / 次要操作                                                 |
+----------------------------------------------------------------------------------+
```

## 遗留问题

- [ ] 核心使用场景是否明确
- [ ] 产品边界是否明确
- [ ] 是否存在必须先补充的业务约束
""",
        ),
        "Basic/PRD/2_用户画像.md": (
            "用户画像",
            """
## 用户分层

| 角色 | 核心诉求 | 当前痛点 | 使用频率 |
|------|----------|----------|----------|
| 主用户 | 待补充 | 待补充 | 待补充 |
| 次用户 | 待补充 | 待补充 | 待补充 |

## 用户能力假设

- 技术熟练度：待补充
- 设备偏好：待补充
- 决策权重：待补充
""",
        ),
        "Basic/PRD/3_核心流程.md": (
            "核心流程",
            """
## 关键流程说明

1. 用户进入系统
2. 定位核心入口
3. 执行主任务
4. 系统反馈结果
5. 用户完成闭环

## Mermaid 流程图

```mermaid
%%{init: { 'theme': 'base', 'themeVariables': { 'primaryColor': '#e3f2fd', 'primaryBorderColor': '#1565c0' } }}%%
flowchart TD
    A[进入系统] --> B[进入主入口]
    B --> C[完成关键输入 / 操作]
    C --> D[系统处理]
    D --> E[返回结果]
    E --> F[完成主任务]
```
""",
        ),
        "Basic/PRD/4_边界场景.md": (
            "边界场景",
            """
## 边界与异常

- 未登录访问：待补充
- 权限不足：待补充
- 第三方依赖异常：待补充
- 大数据量 / 高并发：待补充
- 用户误操作恢复：待补充
""",
        ),
        "Basic/PRD/5_商业模式.md": (
            "商业模式",
            """
## 收益与成本

- 收益方式：待补充
- 定价策略：待补充
- 成本结构：待补充
""",
        ),
        "Basic/PRD/6_运营模式.md": (
            "运营模式",
            """
## 运营策略

- 拉新：待补充
- 激活：待补充
- 留存：待补充
- 分享：待补充
""",
        ),
        "Basic/Architecture/1_技术选型.md": (
            "技术选型",
            """
## 运行时与主技术栈

- 主要语言 / 运行时：待补充
- 框架 / 平台：待补充
- 状态管理 / 模块组织：待补充

## 数据与集成

- 存储方案：待补充
- 外部集成：待补充
- 可观测性：待补充

## 交付环境

- 代码托管：待补充
- 构建 / 发布：待补充
- 运行环境：待补充
""",
        ),
        "Basic/Architecture/2_系统架构.md": (
            "系统架构",
            """
## 分层说明

- 表现层：待补充
- 用例 / 应用层：待补充
- 领域 / 业务规则层：待补充
- 基础设施 / 集成层：待补充

## Mermaid 架构图

```mermaid
%%{init: { 'theme': 'base', 'themeVariables': { 'primaryColor': '#e8f5e9', 'primaryBorderColor': '#2e7d32' } }}%%
flowchart LR
    Client[用户 / 调用方] --> Interface[接口 / 页面 / 入口层]
    Interface --> UseCase[用例 / 应用服务层]
    UseCase --> Domain[业务规则 / 模块层]
    Domain --> Infra[基础设施 / 第三方服务]
    Infra --> Storage[(存储 / 外部系统)]
```
""",
        ),
        "Basic/Architecture/3_交互时序图.md": (
            "交互时序图",
            """
## 关键交互场景

```mermaid
%%{init: { 'theme': 'base', 'themeVariables': { 'primaryColor': '#fff3e0', 'primaryBorderColor': '#ef6c00' } }}%%
sequenceDiagram
    participant User as 用户/调用方
    participant Entry as 接口/页面
    participant UseCase as 用例层
    participant Domain as 业务层
    participant Infra as 基础设施

    User->>Entry: 发起核心操作
    Entry->>UseCase: 提交请求
    UseCase->>Domain: 执行业务规则
    Domain->>Infra: 调用外部依赖
    Infra-->>Domain: 返回结果
    Domain-->>UseCase: 产出领域结果
    UseCase-->>Entry: 返回响应
    Entry-->>User: 展示结果与反馈
```
""",
        ),
        "Basic/Database/1_数据表设计.md": (
            "数据设计",
            """
## 核心实体清单

| 实体 / 资源 | 用途 | 主标识 | 备注 |
|-------------|------|--------|------|
| 待补充 | 待补充 | 待补充 | 待补充 |

## 状态与生命周期

- 待补充：核心状态枚举
- 待补充：生命周期流转
""",
        ),
        "Basic/Database/2_建表SQL.sql": (None, "-- 待补充：首版建表 / 初始化脚本\n"),
        "Basic/Database/3_索引设计.sql": (None, "-- 待补充：首版索引 / 查询优化脚本\n"),
        "Basic/Database/4_数据字典.md": (
            "数据字典",
            """
## 字段说明

| 实体 / 资源 | 字段名 | 类型 | 说明 |
|-------------|--------|------|------|
| 待补充 | 待补充 | 待补充 | 待补充 |
""",
        ),
        "Basic/API/1_RESTful_API.md": (
            "契约设计",
            """
## 接口 / Contract 列表

| 类型 | 标识 | 说明 | 认证 / 权限 |
|------|------|------|-------------|
| HTTP / Event / Method | 待补充 | 待补充 | 待补充 |

## 输入输出约束

- 输入参数：待补充
- 响应 / 返回值：待补充
- 幂等 / 重试：待补充
""",
        ),
        "Basic/API/2_OData查询.md": (
            "查询规范",
            """
## 查询能力

- 待补充：筛选
- 待补充：排序
- 待补充：分页
- 待补充：字段白名单 / 安全约束
""",
        ),
        "Basic/API/3_错误码定义.md": (
            "错误码定义",
            """
## 错误码表

| 错误码 | 含义 | 处理建议 |
|--------|------|----------|
| TODO-001 | 待补充 | 待补充 |
""",
        ),
        "Basic/Testing/1_测试策略.md": (
            "测试策略",
            """
## 测试金字塔

- 单元测试：70%~80%
- 集成测试：15%~20%
- 端到端测试：5%~10%

## Agent 验证要求

- 关键流程必须有自动化验证
- 编码前必须绑定测试规范
- 文档状态未达可放行前不允许进入编码
- 代码变更后必须回写测试结果与文档同步结果
""",
        ),
        "Basic/UI/1_信息架构总览.md": (
            "信息架构总览",
            """
## 全局信息架构

- 产品级导航：待补充
- 全局页面地图：待补充
- 主要入口层级：待补充

## 全局导航草图

```text
+----------------------------------------------------------------------------------+
| 全局导航：品牌 / 搜索 / 通知 / 用户中心                                          |
+------------------------------+---------------------------------------------------+
| 一级导航                      | 二级内容区                                        |
| - 首页                        | - 列表 / 详情 / 配置 / 帮助                       |
| - 模块A                       | - 全局状态提示                                    |
| - 模块B                       | - 全局返回路径                                    |
| - 设置                        |                                                   |
+------------------------------+---------------------------------------------------+
```

## 全局交互规范

- 优先保证主任务路径明显
- 全局导航命名必须自解释
- 不在本文件承载模块页面级线框
""",
        ),
    }

    for relative_path, (title, body) in docs.items():
        file_path = base_path / relative_path
        if file_path.exists():
            continue
        if title is None:
            file_path.write_text(body, encoding="utf-8")
            continue

        content = build_doc_header(
            title=title,
            project_name=project_name,
            system_name=system_name,
            version="v1.0",
            author="AI Agent",
            updater="AI Agent（初始化文档骨架）",
        )
        file_path.write_text(content + body, encoding="utf-8")


def create_framework_documents(base_path: Path, project_name: str, system_name: str):
    standards = {
        "Framework/Standards/业务模块技术文档规范.md": (
            "业务模块技术文档规范",
            """
## 规范说明书 (Standard Manual)

### 核心功能 (Core Function)
定义业务模块双文档模型、修订历史、实施现状和文档回写方式。

### 输入 (Input)
- 业务需求
- 基础文档
- 实际代码实现与接口行为

### 输出 (Output)
- 标准化的模块需求文档
- 标准化的模块技术文档
- Agent 可读取的模块关系映射与实施现状

### 定位 (Position)
Spec-Driven 体系下的模块文档母规范。

### 依赖 (Dependency)
- `Documentation/00_文档规范.md`
- `Documentation/Basic/Architecture/2_系统架构.md`
- `Documentation/Modules/_template/模块需求文档模板.md`
- `Documentation/Modules/_template/模块技术文档模板.md`

### 被依赖 (Dependents)
- 所有模块文档
- Brownfield 文档读取与更新流程
- Agent 文档驱动编码流程

## 双文档模型

### 模块需求文档

必须包含：
1. 模块概览卡
2. 业务背景
3. 目标用户与产品定位
4. 业务场景
5. 业务场景流程（Mermaid）
6. 功能需求
7. 业务规则
8. 业务 ASCII 交互稿
9. 验收标准
10. 边界与待确认项

### 模块技术文档

必须包含：
1. 模块说明书 (Module Manual)
2. 需求映射
3. 系统架构
4. 数据 / 状态模型
5. Contract / API / 事件
6. 技术流程设计
7. 异常与补偿
8. 实施现状
9. 测试设计
10. FAQ / 检查清单 / 代码同步说明 / 附录

## 回写规则

1. 文档先于编码
2. 需求变更优先回写需求文档
3. 设计与实现变更优先回写技术文档
4. 每次同步实际代码时必须追加修订历史
5. 版本执行跟踪文档必须同步更新
6. 对应版本 TODO 清单必须同步更新

## FAQ / 常见问题

- 问：模块需求和模块技术文档是否可以混写？
  答：不建议。需求文档承接业务与验收，技术文档承接设计与实现。

## 变更检查清单

- [ ] 模块需求文档是否已同步
- [ ] 模块技术文档是否已同步
- [ ] 执行跟踪文档是否已同步
- [ ] TODO 清单是否已同步
- [ ] 是否需要沉淀到 CommonCapabilities / ProblemSolutions
""",
        ),
        "Framework/Standards/架构模式规范.md": (
            "架构模式规范",
            """
## 规范说明书 (Standard Manual)

### 核心功能 (Core Function)
定义与具体语言、平台无关的 Spec-Driven 架构范式，确保 Agent 先理解业务规则、模块边界和执行约束，再生成代码。

### 输入 (Input)
- 业务目标
- 系统约束
- 集成依赖
- 运行环境

### 输出 (Output)
- 一致的模块边界
- 统一的 Contract / 状态 / 数据建模方式
- 可复用的执行链路与扩展点

### 定位 (Position)
项目级架构模式母规范，面向任何代码类型项目。

### 依赖 (Dependency)
- `Documentation/Basic/PRD/1_产品概述.md`
- `Documentation/Basic/Architecture/2_系统架构.md`

### 被依赖 (Dependents)
- 模块技术文档
- 通用能力文档
- 问题解决方案文档

## 核心原则

1. 业务规则先于实现细节
2. Contract 先于接口代码
3. 状态机先于状态流转实现
4. 依赖边界先于集成代码
5. 文档回写是交付的一部分
""",
        ),
        "Framework/Standards/测试框架规范.md": (
            "测试框架规范",
            """
## 规范说明书 (Standard Manual)

### 核心功能 (Core Function)
定义测试分层、验证职责和 Agent 测试门禁，确保文档驱动开发具备可验证性。

### 输入 (Input)
- 模块需求文档
- 模块技术文档
- 问题解决方案文档
- 关键流程

### 输出 (Output)
- 测试分层模型
- 命名与组织规范
- 执行门禁与覆盖率要求

### 定位 (Position)
项目级测试规范，不依赖具体语言或测试框架。

### 依赖 (Dependency)
- `Documentation/Basic/Testing/1_测试策略.md`
- `Documentation/Framework/ProblemSolutions/问题解决方案模板.md`

### 被依赖 (Dependents)
- 所有模块任务
- 验收标准
- CI / 自动化验证

## 测试分层

- 单元测试：验证最小业务规则、纯逻辑、状态转换
- 集成测试：验证跨层协作、外部依赖、持久化或协议交互
- 端到端测试：验证核心业务闭环与关键用户路径

## Agent 验证门禁

1. 关键流程必须有自动化验证
2. 高风险任务必须绑定问题方案
3. 测试失败不得更新文档为可放行状态

## 反模式

- 只有 happy path，没有异常验证
- 只写测试策略，不绑定到任务
- 只做人工验证，不保留结果
- 模块文档已变更，但测试文档不更新

## FAQ / 常见问题

- 问：什么时候必须补自动化验证？
  答：核心业务闭环、关键异常路径和高风险问题都必须补。

## 检查清单

- [ ] 核心流程是否有验证
- [ ] 异常路径是否有验证
- [ ] 文档与测试是否一致
""",
        ),
        "Framework/CommonCapabilities/通用能力文档模板.md": (
            "通用能力文档模板",
            """
## 能力说明书 (Capability Manual)

### 核心功能 (Core Function)
描述一个可被多个模块复用的能力。

### 输入 (Input)
- 触发条件
- 输入参数 / 资源
- 外部依赖

### 输出 (Output)
- 能力产出
- 错误结果
- 状态变化

### 定位 (Position)
该能力位于哪一层、服务哪些模块、解决什么通用问题。

### 依赖 (Dependency)
- 相关基础文档
- 相关规范文档

### 被依赖 (Dependents)
- 依赖该能力的模块或任务类型

## 推荐正文结构

1. 适用场景
2. 设计目标
3. 输入输出与 Contract
4. 状态与约束
5. 关键流程
6. 扩展点
7. 最佳实践
8. 反模式
9. 使用示例
10. FAQ / 常见问题
11. 检查清单
12. 修订历史
""",
        ),
        "Framework/ProblemSolutions/问题解决方案模板.md": (
            "问题解决方案模板",
            """
## 问题说明书 (Problem Manual)

### 问题背景 (Background)
说明这个问题出现的业务背景和工程背景。

### 触发场景 (Trigger Scenarios)
- 场景1
- 场景2
- 场景3

### 问题表现 (Symptoms)
- 表现1
- 表现2
- 表现3

### 根因分析 (Root Cause)
说明问题为什么发生。

### 错误做法 / 反模式 (Anti-Patterns)
- 错误做法1
- 错误做法2
- 错误做法3

### 标准解决方案 (Standard Solution)
说明项目内统一采用的解决方式。

### 实施约束 (Implementation Constraints)
- 必须遵守的约束1
- 必须遵守的约束2
- 禁止做法1
- 禁止做法2

### 验证方式 (Verification)
- 如何验证方案生效
- 需要哪些测试
- 需要观察哪些日志 / 指标 / 状态

### 适用边界 (Boundaries)
说明该方案不适用的场景和需要特殊处理的边界。

### 相关文档 (Related Docs)
- `Documentation/Basic/...`
- `Documentation/Framework/...`
- `Documentation/Modules/...`

### 关联任务类型 (Related Task Types)
- 异步任务
- 文件处理
- 查询接口
- 状态同步

## 推荐正文结构

1. 问题复现样例
2. 标准实现步骤
3. 验证清单
4. 常见误区
5. FAQ / 常见问题
6. 修订历史
""",
        ),
    }

    for relative_path, (title, body) in standards.items():
        file_path = base_path / relative_path
        if file_path.exists():
            continue
        content = build_doc_header(
            title=title,
            project_name=project_name,
            system_name=system_name,
            version="v1.0",
            author="AI Agent",
            updater="AI Agent（初始化规范）",
        )
        file_path.write_text(content + body, encoding="utf-8")


def create_module_templates(base_path: Path, project_name: str, system_name: str):
    today = datetime.now().strftime("%Y-%m-%d")

    requirement_template = f"""# 示例模块需求文档

---

**项目名称**：{project_name}
**所属系统**：{system_name}
**文档版本**：v1.0
**编写日期**：{today}
**更新日期**：{today}
**编写人**：产品团队
**更新人**：AI助手（初始化模块模板）

---

## 文档修订历史

| 版本 | 日期 | 修订人 | 修订内容 |
|------|------|--------|----------|
| v1.0 | {today} | AI助手 | 初始化模块需求模板 |

## 模块概览卡

### 模块定位
待补充

### 目标用户
待补充

### 核心价值
待补充

### 触发入口
待补充

### 核心场景
- 待补充

### 成功结果
待补充

### 成功标准
待补充

## 1. 业务背景

- 待补充：业务背景
- 待补充：为什么需要这个模块

## 2. 目标用户与产品定位

- 主用户：待补充
- 次用户：待补充
- 模块在产品中的定位：待补充

## 3. 业务场景

- 场景1：待补充
- 场景2：待补充

## 4. 业务场景流程

```mermaid
%%{{init: {{ 'theme': 'base', 'themeVariables': {{ 'primaryColor': '#e3f2fd', 'primaryBorderColor': '#1565c0' }} }} }}%%
flowchart TD
    A[前置条件] --> B[触发动作]
    B --> C[主流程处理]
    C --> D[结果反馈]
```

## 5. 功能需求

- 需求1：待补充
- 需求2：待补充

## 6. 业务规则

- 规则1：待补充
- 规则2：待补充

## 7. 业务 ASCII 交互稿

```text
+------------------------------------------------------------------+
| 页面标题 / 返回 / 主操作                                           |
+----------------------+-------------------------------------------+
| 模块导航 / 状态区      | 主工作区                                  |
| - 子入口A             | +-------------------+ +-----------------+ |
| - 子入口B             | | 核心内容区        | | 辅助信息 / 提示 | |
|                       | | - 主任务          | | - 状态         | |
|                       | | - 主 CTA          | | - 次要 CTA     | |
|                       | +-------------------+ +-----------------+ |
+----------------------+-------------------------------------------+
```

## 8. 验收标准

- [ ] 验收项1：待补充
- [ ] 验收项2：待补充

## 9. 边界与待确认项

- [ ] 待确认1：待补充
- [ ] 待确认2：待补充
"""

    technical_template = f"""# 示例模块技术文档

---

**项目名称**：{project_name}
**所属系统**：{system_name}
**文档版本**：v1.0
**编写日期**：{today}
**更新日期**：{today}
**编写人**：系统架构组
**更新人**：AI助手（初始化模块模板）

---

## 文档修订历史

| 版本 | 日期 | 修订人 | 修订内容 |
|------|------|--------|----------|
| v1.0 | {today} | AI助手 | 初始化模块技术模板 |

## 模块说明书 (Module Manual)

### 核心功能 (Core Function)
提供示例能力说明，帮助快速建立模块级技术知识入口。

### 输入 (Input)
- 请求 / 命令 / 事件
- 外部资源

### 输出 (Output)
- 结果
- 错误
- 状态变化

### 定位 (Position)
该模块位于系统中的位置、解决的问题和边界。

### 依赖 (Dependency)
- 依赖1：待补充
- 依赖2：待补充

### 被依赖 (Dependents)
- 被依赖方1：待补充
- 被依赖方2：待补充

### 相关文档 (Related Docs)
- `Documentation/Basic/Architecture/2_系统架构.md`
- `Documentation/Framework/Standards/业务模块技术文档规范.md`

### 关联模块 (Related Modules)
- 模块A
- 模块B

## 1. 需求映射

- 对应业务需求：待补充
- 对应验收标准：待补充

## 2. 系统架构

- 模块边界：待补充
- 关键依赖：待补充
- 关键约束：待补充

## 3. 数据 / 状态模型

- 核心实体：待补充
- 状态流转：待补充

## 4. Contract / API / 事件

- 输入契约：待补充
- 输出契约：待补充
- 错误契约：待补充

## 5. 技术流程设计

- 主流程：待补充
- 异常流程：待补充

## 6. 异常与补偿

- 异常1：待补充
- 补偿策略：待补充

## 7. 实施现状

- 当前状态：planned / partial / done
- 已实现内容：待补充
- 与原设计差异：待补充
- 本次迭代同步点：待补充

## 8. 测试设计

- 单元测试：待补充
- 集成测试：待补充
- 验收验证：待补充

## 9. 风险与待办

- 风险1：待补充
- 待办1：待补充

## 10. 附录

- 相关文档：待补充
- 术语 / 示例：待补充

## 11. FAQ / 常见问题

- 问题1：待补充
- 问题2：待补充

## 12. 变更检查清单

- [ ] 需求映射是否已同步
- [ ] 数据 / 状态模型是否已同步
- [ ] Contract / API 是否已同步
- [ ] 测试设计与结果是否已同步
- [ ] 文档修订历史是否已追加
- [ ] 是否存在需要沉淀到 CommonCapabilities / ProblemSolutions 的内容

## 13. 代码同步说明

- 本次基于实际代码实现同步：待补充
- 对应代码文件：待补充
- 与设计差异：待补充
"""

    templates = {
        "Modules/_template/模块需求文档模板.md": requirement_template,
        "Modules/_template/模块技术文档模板.md": technical_template,
    }

    for relative_path, content in templates.items():
        file_path = base_path / relative_path
        if not file_path.exists():
            file_path.write_text(content, encoding="utf-8")


def create_devlog_documents(base_path: Path, project_name: str, system_name: str):
    tracking = build_doc_header(
        title="执行跟踪",
        project_name=project_name,
        system_name=system_name,
        version="v1.0",
        author="AI Agent",
        updater="AI Agent（初始化执行跟踪）",
    ) + """
## 项目状态

- 当前阶段：阶段1 / 需求沟通
- 当前总体状态：进行中
- 当前版本：v1.0

## 当前版本目标

- 完成需求沟通 4 轮访谈
- 建立 Basic / Framework / Modules 骨架
- 明确首批核心模块

## 当前 TODO 定位

- 当前 TODO 文件：v1.0_TODO_01.md
- 当前任务：TODO-001
- 当前阶段：阶段1 / 需求沟通
- 当前任务状态：待开始

## 当前检查点

- checkpoint-id：v1.0-stage1-bootstrap
- 最近完成：初始化文档结构
- 下一步：进入需求沟通

## 本轮进展

### 初始化

- 完成：创建 Documentation 基础骨架
- 完成：创建 Framework 规范模板
- 完成：创建模块双文档模板
- 完成：创建版本化执行跟踪文档

## 待确认项

- [ ] 产品定位是否稳定
- [ ] 首批核心模块是否确定
- [ ] 首版边界是否稳定

## 风险与阻塞

- 风险：需求尚未完成 4 轮澄清
- 风险：模块边界尚未最终确认

## 文档回写记录

- v1.0：初始化文档结构
"""
    tracking_path = base_path / "DevLogs" / "v1.0_执行跟踪.md"
    if not tracking_path.exists():
        tracking_path.write_text(tracking, encoding="utf-8")

    todo = build_doc_header(
        title="TODO 01",
        project_name=project_name,
        system_name=system_name,
        version="v1.0",
        author="AI Agent",
        updater="AI Agent（初始化 TODO 清单）",
    ) + """
## TODO 文件说明

- 文件范围：TODO-001 ~ TODO-030
- 当前用途：承接 v1.0 的详细任务拆解
- 任务约束：
  - 每个 TODO 文件最多 30 条任务
  - 所有任务必须顺序编号
  - 所有依赖只能依赖更早任务
  - 禁止交叉依赖、循环依赖和未来依赖

## 任务清单

### TODO-001 [ ] 完成产品定位访谈
- 所属阶段：阶段1 / 需求沟通
- 所属模块：全局
- 来源需求文档：Basic/PRD/1_产品概述.md
- 来源技术文档：无
- 前置任务：无
- 输出：产品定位摘要、目标用户、典型需求场景
- 验收：用户确认产品定位、用户群体与典型需求场景

### TODO-002 [ ] 完成目标 / 边界 / 验收访谈
- 所属阶段：阶段1 / 需求沟通
- 所属模块：全局
- 来源需求文档：Basic/PRD/1_产品概述.md
- 来源技术文档：无
- 前置任务：TODO-001
- 输出：首版范围、非范围、验收口径
- 验收：用户确认首版范围、边界与成功标准

### TODO-003 [ ] 完成业务场景循环访谈
- 所属阶段：阶段1 / 需求沟通
- 所属模块：全局
- 来源需求文档：Basic/PRD/3_核心流程.md
- 来源技术文档：无
- 前置任务：TODO-002
- 输出：主成功场景、关键分支场景、异常场景
- 验收：至少 3 个关键场景与 1 个异常场景已澄清

### TODO-004 [ ] 完成业务场景流程澄清
- 所属阶段：阶段1 / 需求沟通
- 所属模块：全局
- 来源需求文档：Basic/PRD/3_核心流程.md
- 来源技术文档：Basic/Architecture/3_交互时序图.md
- 前置任务：TODO-003
- 输出：可落盘的 Mermaid 流程定义与业务 ASCII 结构
- 验收：关键流程的前置、主流程、异常流程与用户反馈已明确

### TODO-005 [ ] 完成首批模块双文档设计
- 所属阶段：阶段2 / 架构设计
- 所属模块：待补充
- 来源需求文档：Modules/<模块名>/<模块名>_需求文档.md
- 来源技术文档：Modules/<模块名>/<模块名>_技术文档.md
- 前置任务：TODO-004
- 输出：首批模块需求文档与技术文档
- 验收：至少 1 个核心模块完成双文档落盘
"""
    todo_path = base_path / "DevLogs" / "v1.0_TODO_01.md"
    if not todo_path.exists():
        todo_path.write_text(todo, encoding="utf-8")


def init_project_structure(project_name: str, output_dir: str, system_name: str):
    base_path = resolve_documentation_root(output_dir)
    base_path.mkdir(parents=True, exist_ok=True)

    create_directory_structure(base_path)
    print("✅ 目录结构已创建", file=sys.stderr)

    create_folder_manual_files(base_path)
    print("✅ 文件夹说明书已创建", file=sys.stderr)

    create_doc_standard(base_path, project_name, system_name)
    print("✅ 文档规范已创建", file=sys.stderr)

    create_basic_documents(base_path, project_name, system_name)
    print("✅ 基础文档骨架已创建", file=sys.stderr)

    create_framework_documents(base_path, project_name, system_name)
    print("✅ Framework 文档已创建", file=sys.stderr)

    create_module_templates(base_path, project_name, system_name)
    print("✅ 模块双文档模板已创建", file=sys.stderr)

    create_devlog_documents(base_path, project_name, system_name)
    print("✅ 版本化执行跟踪文档与 TODO 清单已创建", file=sys.stderr)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="初始化项目文档结构")
    parser.add_argument("--project-name", required=True, help="项目名称")
    parser.add_argument("--system-name", default="待补充系统名称", help="所属系统名称")
    parser.add_argument("--output-dir", default="Documentation", help="输出目录路径")
    args = parser.parse_args()

    doc_root = resolve_documentation_root(args.output_dir)
    init_project_structure(args.project_name, args.output_dir, args.system_name)
    print(f"\n✅ 项目文档结构初始化完成：{doc_root}", file=sys.stderr)


if __name__ == "__main__":
    main()
