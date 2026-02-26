# ios-testflight-remote-release

这个 Skill 用来让 Agent 帮你完成 iOS 的 TestFlight Internal 发布，适合你不在电脑旁、但需要快速推送内测版本的场景。

## 你可以直接让 Agent 做什么

- 自动检查当前项目是否具备发布条件（Xcode、fastlane、lane、项目元数据）
- 一次性收集发布所需材料（避免反复追问）
- 给出建议版本号并等待你确认
- 自动执行构建、上传、Internal Group 分发
- 发布后校验测试者是否可见最新 build

## 你怎么对 Agent 下指令

你可以直接说：

- `帮我发布到 TestFlight internal`
- `我现在不在电脑旁，帮我走远程内测发布`
- `执行 internal_release，发到 Agent Internal Testing`

## Agent 的执行流程

1. 先预检项目和环境，确认能发布。
2. 自动扫描并补齐材料，缺什么一次性告诉你。
3. 资料齐全后自动 `dry-run`，给出 4 种版本建议（build-only/patch/minor/major），你确认后才正式发布。
4. 执行构建上传和测试组分发。
5. 返回发布结果，并告诉你首装和后续更新的操作方式。

## 关键防呆（已内置）

- fastlane 版本守卫：
  - 脚本要求 fastlane `>= 2.232.1`，低于该版本会自动尝试升级，避免 `upload_to_testflight` 的 `'prices' is not a valid relationship name`。
  - bootstrap 会生成 `Gemfile`（`gem "fastlane", ">= 2.232.1"`）用于统一环境。
- 版本一致性校验：
  - 支持 `build-only`（版本不变，仅增加 build number）；
  - 执行上传前会强校验 `MARKETING_VERSION` 与你确认版本一致；
  - 若 `Info.plist` 显式写了 `CFBundleShortVersionString`，也必须一致（或为 `$(MARKETING_VERSION)`）；
  - `skip-build=true` 时会校验 ipa 内版本，避免 `Invalid Pre-Release Train`。

## 你需要提前准备

- iOS 项目可正常本地构建，并且该项目至少有一次通过数据线连接 iPhone 真机成功安装运行（用于确保签名、设备信任与本地发布链路已验证）
- App Store Connect API 凭证：
  - 登录 [App Store Connect](https://appstoreconnect.apple.com/)
  - 进入 `Users and Access`（用户和访问）
  - 打开 `Integrations` → `App Store Connect API`
  - 在页面中复制 `Issuer ID`
  - 在 `Keys` 中创建 API Key，下载一次性 `.p8` 文件（文件名通常为 `AuthKey_<KEY_ID>.p8`，下载后请妥善保存）
- 目标测试者邮箱（可多个）

首次准备可参考：`references/newbie-guide.md`
