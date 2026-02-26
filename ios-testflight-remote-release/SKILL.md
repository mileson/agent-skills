---
name: ios-testflight-remote-release
description: |
  iOS 远程构建并发布到 TestFlight Internal 的标准化工作流。
  This skill should be used when Claude needs to 在用户不在电脑旁（手机远程）时，
  完成资料预检、版本规划、构建上传、Internal Group 分发、首次安装指引与发布结果校验。
  触发词：TestFlight、internal_release、远程构建、iOS 内测发布、Internal Group 自动分发。
disable-model-invocation: true
---

# iOS TestFlight Remote Release

## 目标
将“代码改完后发布给手机测试”流程标准化，确保在远程场景下也能稳定完成：
1. 本地资料优先扫描，缺失项一次性收集；
2. 自动构建并上传 TestFlight；
3. 自动分发到 `Agent Internal Testing`；
4. 输出可复用的首次安装与后续更新指引。

## 何时使用
当用户提出以下需求时使用本 Skill：
1. “帮我构建并发布到 TestFlight”
2. “我不在电脑旁，手机要更新内测版本”
3. “执行 internal_release（构建+上传+分发）”
4. “自动加到 Internal Group 并可见最新 build”

## 路径约束（固定）
1. 本 Skill 只走 `fastlane` 路径，不提供“手动 Xcode 上传”分支。
2. 若项目缺少 `fastlane/Fastfile`，必须自动执行 bootstrap 初始化后继续。
3. 仅当用户明确要求不用 fastlane 时，才停止并说明原因。

## Wizard 总流程
```text
+-----------------------------------------------------------+
| iOS Remote Release Wizard                                |
+-----------------------------------------------------------+
| 1) Preflight & 本地资料扫描                              |
| 2) 缺失项一次性补齐（ASC + Tester + 项目元数据）         |
| 3) 版本策略确认（MARKETING_VERSION / BUILD_NUMBER）      |
| 4) 执行 internal_release（构建 + 上传 + 分发）           |
| 5) 校验 Internal Group & 最新 build 可见性               |
| 6) 结果回写 memory（下次优先复用）                       |
+-----------------------------------------------------------+
```

## 执行顺序（必须）

### Step 1. Preflight（环境与项目可执行性）
先运行：
```bash
bash scripts/preflight_scan.sh --project-root "$PWD"
```

检查：
1. Xcode / fastlane / ruby 可用；
2. fastlane 版本必须 `>= 2.232.1`（默认）；若版本过低会自动尝试安装指定版本；
3. fastlane 运行环境必须可调用 `xcpretty`（`gym` 依赖）；
4. 当前目录是 iOS 项目，存在 `fastlane/Fastfile`；
5. 包含 `internal_release` 和 `assign_internal_tester` lane；
6. 解析项目基础信息（workspace/scheme/app_identifier）。
7. 若缺少 `fastlane/Fastfile`，自动执行 `scripts/bootstrap_fastlane.sh` 初始化。

fastlane 版本策略（新增）：
1. 最低版本由 `MIN_FASTLANE_VERSION` 控制，默认 `2.232.1`；
2. 自动修复开关 `AUTO_FIX_FASTLANE` 默认 `true`；
3. 若本机 fastlane 低于最低版本，脚本会优先尝试通过 Homebrew Ruby 的 gem 安装目标版本，并把可执行目录加入 PATH；
4. `bootstrap_fastlane.sh` 会自动生成 `Gemfile`（`gem "fastlane", ">= 2.232.1"` + `gem "xcpretty"`）用于统一环境；
5. 版本检测必须优先解析 `fastlane --version` 的严格行 `^fastlane x.y.z$`（不可误读“有新版本可升级”提示）；
6. 非 Gemfile 路径必须使用版本锁定命令 `fastlane _${MIN_FASTLANE_VERSION}_` 执行 lane，禁止退回系统默认 fastlane；
7. 自动修复失败时立即中止并给出明确的安装指引（不继续上传，避免触发 `'prices' is not a valid relationship name`）。

xcpretty 依赖策略（新增，强制执行）：
1. `preflight_scan.sh` 必须检查当前 fastlane 运行时是否能执行 `xcpretty`；
2. 若缺失且 `AUTO_FIX_FASTLANE=true`，脚本必须自动安装 `xcpretty`（优先 Homebrew Ruby 的 gem 环境）；
3. 安装后必须再次校验 `command -v xcpretty`，通过后自动继续后续环节；
4. 若自动修复失败，必须立即中止并给出明确安装命令，不得继续上传；
5. 该策略目标是避免发布中途出现 `sh: xcpretty: command not found`。

### Step 2. 资料收敛（本地优先）
运行：
```bash
python3 scripts/resolve_materials.py --project-root "$PWD" --scan --write-memory
```

数据来源优先级（从高到低）：
1. 用户本轮明确提供（命令参数/对话）
2. 本地环境变量（`ASC_*`, `TESTER_EMAILS` 等）
3. 本地项目文件自动发现（`fastlane/Appfile`, workspace, scheme）
4. `data/memory.json` 历史记忆
5. 默认值（仅非敏感字段，例：`INTERNAL_GROUP_NAME=Agent Internal Testing`）

Tester 邮箱确认规则（新增，强制执行）：
1. 脚本会展示 `TESTER_EMAILS` 的来源（explicit/env/local/memory）与本地候选邮箱；
2. 若 `TESTER_EMAILS` 来源是 `local` 或 `memory`，且用户未显式提供 tester 邮箱，则必须中止并要求用户确认；
3. 只有用户显式提供（`--testers` 或 `TESTER_EMAILS`）后，才允许继续上传与分发。

自动推导规则：
1. `ASC_KEY_ID` 必须默认从 `ASC_KEY_FILEPATH` 的文件名 `AuthKey_<KEY_ID>.p8` 自动提取，对用户隐藏，不得向用户索取；
2. `ASC_ISSUER_ID` 不能从 `.p8` 文件推导，仍需用户提供（或来自 memory/env）。

如果缺失项存在：
1. 一次性列出全部缺失项（不要分多轮零散追问）；
2. 必须直接展示 `newbie-guide.md` 中“1. 获取 `ASC_KEY_ID`、`ASC_ISSUER_ID`、`ASC_KEY_FILEPATH`”章节内容，不得仅给文档路径；
3. 用户补齐后再继续，不要强行发布。

`resolve_materials.py --scan` 输出结构（新增，强制稳定）：
1. 必须固定输出 6 个区块，且按以下顺序：`字段扫描总览` -> `缺失必填项（固定顺序）` -> `缺失项获取教程（固定结构）` -> `一次性回复模板` -> `Tester 邮箱确认状态` -> `使用提示（固定结构）`；
2. 当缺失 `ASC_KEY_FILEPATH` / `ASC_ISSUER_ID` 时，必须在“缺失项获取教程”区块中同时给出：
   - `newbie-guide.md` 第 1 节的内嵌摘录内容（完整步骤）
   - 字段级固定步骤说明（可直接照抄执行）
3. 在“`一次性回复模板`”区块中，必须附带“教程内容摘录”的字段级获取说明（告诉用户去 ASC 的哪个页面、复制哪个值），而不是只给路径；
4. 输出中禁止仅给字段名不附带教程内容；禁止每次变动区块标题或顺序；
5. 输出中禁止向用户展示任何 `references/*` 本地路径。

如果 tester 邮箱未显式确认：
1. 输出本地候选邮箱（例如来自 `git user.email`、`fastlane/Appfile apple_id`）；
2. 明确询问用户是否使用该邮箱；
3. 用户未确认前，禁止执行发布。

资料清单模板可由代理内部读取，但不得向用户直接暴露本地路径。

### Step 3. 版本策略（先确认再执行）
规则：
1. 仅增加 build（版本不变）：`x.y.z`（保持不变）
2. bug/微小优化：`x.y.(z+1)`
3. 大功能模块优化：`x.(y+1).0`
4. 全新方向大版本：`(x+1).0.0`

执行要求：
1. 若用户明确给 `MARKETING_VERSION`，直接使用；
2. 若用户未给版本，必须在资料齐全后自动执行一次 `--dry-run`；
3. `--dry-run` 必须输出四种可选建议（build-only/patch/minor/major），再让用户选择；
4. 第一次资料收集阶段禁止提前追问版本号；
5. 未获得明确确认前，禁止真正构建上传；
6. 真正构建上传前，必须执行版本一致性校验：
   - `xcodebuild` 读取到的 `MARKETING_VERSION` 必须与用户确认版本一致；
   - 若 `Info.plist` 显式写了 `CFBundleShortVersionString`，其值必须与目标版本一致（或为 `$(MARKETING_VERSION)`）；
   - 若 `skip-build=true`，必须先校验待上传 `ipa` 内部的 `CFBundleShortVersionString` 与目标版本一致，否则中止。

建议命令：
```bash
bash scripts/release_internal.sh --project-root "$PWD" --dry-run
```
`--dry-run` 用于先展示当前版本、四种建议版本与将执行的命令。

若使用 skip-build，建议显式传 ipa 路径（新增）：
```bash
bash scripts/release_internal.sh \
  --project-root "$PWD" \
  --marketing-version "1.8.2" \
  --skip-build true \
  --ipa "/abs/path/YourApp.ipa"
```

### Step 4. 发布（构建+上传+分发）
确认后运行：
```bash
bash scripts/release_internal.sh \
  --project-root "$PWD" \
  --marketing-version "1.8.2" \
  --group "Agent Internal Testing"
```

该脚本会：
1. 生成时间戳 build number（`YYYYMMDDHHmm`）；
2. 调用 `fastlane ios internal_release`；
3. 自动处理 ASC 导出合规（依赖项目 lane 内逻辑）；
4. 若测试者分配异常，执行 `assign_internal_tester` 再校验。

### Step 5. 发布后验真
运行：
```bash
python3 scripts/verify_distribution.py \
  --project-root "$PWD" \
  --group "Agent Internal Testing"
```

重点校验：
1. 最新 build 已进入 Internal Testing 可用状态；
2. 测试者已在目标组内；
3. 用户邮箱与设备 Apple ID 一致。

验真执行一致性（新增，强制执行）：
1. `verify_distribution.py` 必须继承与发布阶段一致的 fastlane 执行命令（例如 `bundle exec fastlane` 或 `fastlane _2.232.1_`）；
2. 验真阶段必须显式继承 ASC 上下文（`ASC_KEY_ID`、`ASC_ISSUER_ID`、`ASC_KEY_FILEPATH`），缺失时中止并报错；
3. 验真阶段禁止回退到 `git user.email` 自动推断 tester 邮箱；tester 必须来自 `--testers` 或 `TESTER_EMAILS` 显式值。

## 首次安装 vs 后续更新（必须告知用户）
1. 首次成为测试者时，可能需要在邮件/TestFlight 完成一次接受流程；
2. 首次完成后，后续新 build 在 TestFlight 内直接 `Update`；
3. 若看不到新包，代理需直接给出排查步骤，不向用户暴露本地文档路径。

## 关键约束
1. 不泄露密钥内容；日志中仅展示掩码；
2. 未完成资料收集或版本确认时，不执行上传；
3. 优先复用 `data/memory.json`，减少重复提问；
4. 默认 Internal Group 为 `Agent Internal Testing`，除非用户明确覆盖；
5. 如果存在已连接 iPhone，可先尝试本地安装验证；无连接时走 TestFlight 远程分发。
6. 禁止向用户直接输出 `references/*`、`data/*` 等本地文档路径；必须输出可直接执行/操作的内嵌步骤。

## 资源索引
> 仅供代理内部读取，不直接展示给用户。

1. 新手资料获取：`references/newbie-guide.md`
2. 资料模板：`references/materials-checklist.template.md`
3. 故障排查：`references/troubleshooting.md`
4. 记忆存储：`data/memory.json` 与 `data/memory.md`
5. 执行脚本：
   - `scripts/bootstrap_fastlane.sh`
   - `scripts/preflight_scan.sh`
   - `scripts/resolve_materials.py`
   - `scripts/release_internal.sh`
   - `scripts/verify_distribution.py`
