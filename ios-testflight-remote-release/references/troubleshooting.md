# 故障排查手册（TestFlight Internal）

## 1) TestFlight 看不到新版本

可能原因：
1. build 仍在 processing；
2. tester 不在目标 Internal Group；
3. 手机 TestFlight 账号与 tester 邮箱不一致；
4. 首次测试者尚未完成接受流程。

处理：
1. 在 App Store Connect 的 TestFlight 页面确认 build 状态为 `Testing`；
2. 执行 `assign_internal_tester` 再次绑定 tester；
3. 校验邮箱是否在 `Users and Access -> People` 且已接受邀请；
4. 退出并重新登录 TestFlight，对应 Apple ID 必须一致。

## 2) 报错：`Tester(s) cannot be assigned`

说明：
1. 该邮箱不是可分配的内部测试用户；
2. 用户还未在 `People` 中完成邀请与权限配置。

处理：
1. 先在 `People` 添加并完成接受；
2. 给该用户分配 App 访问权限；
3. 重新执行分发脚本。

## 3) 报错：`MISSING_EXPORT_COMPLIANCE`

说明：
上传后缺少导出合规声明，build 无法进入可测状态。

处理：
1. 使用带自动修复逻辑的 lane（项目中已处理）；
2. 如果仍失败，在 App Store Connect 手工确认加密声明；
3. 再次触发 build 状态轮询。

## 4) 已收到邀请邮件，但仍需 Redeem code

说明：
通常出现在“不是内部用户”或“通过 app-specific 测试邀请路径”场景。

处理：
1. 优先改为 Internal Testing（People 用户）；
2. 完成一次首次接受后，后续一般直接在 TestFlight 内更新。

## 5) 远程场景没有 USB，是否可安装？

结论：
1. 无法通过本地直装方式安装；
2. 可以通过 TestFlight 分发实现远程安装更新；
3. 前提是已完成签名、上传、分发与 tester 授权。

## 6) 上传被拒：`Invalid Pre-Release Train x.y.z`

说明：
1. 项目实际版本号与本次要上传的目标版本不一致；
2. 常见于 `MARKETING_VERSION` 未按确认值更新，或 `skip-build` 传入了旧版 ipa。

处理：
1. 先用 `--dry-run` 确认本次 `Target Version`；
2. 正式执行前，脚本会强校验：
   - `xcodebuild` 读取到的 `MARKETING_VERSION` 是否等于目标版本；
   - `Info.plist` 的 `CFBundleShortVersionString` 是否与目标版本一致（或为 `$(MARKETING_VERSION)`）；
   - `skip-build=true` 时，ipa 内版本是否与目标版本一致；
3. 若失败，按报错修正版本后重试，禁止带不一致版本继续上传。

## 7) 上传时报错：`'prices' is not a valid relationship name`

说明：
1. 这是 App Store Connect API 变更后，低版本 fastlane/Spaceship 的兼容性问题；
2. 典型表现为 `upload_to_testflight` 在提交元数据时失败。

处理：
1. 本 Skill 已设置最低 fastlane 版本（默认 `2.232.1`）；
2. `preflight_scan.sh` / `release_internal.sh` 会自动检测并在允许时自动升级；
3. `bootstrap_fastlane.sh` 会生成 `Gemfile`（`gem "fastlane", ">= 2.232.1"`）用于统一环境；
4. 若仍失败，优先执行：
   - `bundle update fastlane`
   - 或 `/opt/homebrew/opt/ruby/bin/gem install fastlane -v 2.232.1 --no-document`
