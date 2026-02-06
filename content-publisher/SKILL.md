---
name: content-publisher
description: |
  多平台内容发布器，通过 API 将文章发布到各平台。当前支持微信公众号（Phase 1），
  小红书和知乎开发中（Phase 2）。凭证通过 secrets-vault skill 获取，实现安全解耦。
  This skill should be used when: (1) User wants to publish content after
  content-creator workflow completes, (2) User explicitly asks to publish
  to WeChat Official Account or other platforms, (3) content-creator Stage 6
  completes and user confirms publishing. Triggers: "发布到微信", "publish
  to wechat", "发布文章", "自动发布".
argument-hint: "[platform]"
---

# Content Publisher

多平台内容发布器，通过官方 API 将 content-creator 生成的文章发布到各平台。

## 支持平台

| 平台 | 状态 | 发布方式 |
|:-----|:---:|:--------|
| 微信公众号 | ✅ Phase 1 | 官方 API (wechatpy SDK) |
| 小红书 | 🔜 Phase 2 | 待定 |
| 知乎 | 🔜 Phase 2 | 待定 |

## 前置条件

1. **secrets-vault** skill 已安装且已配置凭证
2. 微信公众号需在 secrets-vault 中配置 `wechat_mp` 命名空间：
   ```bash
   python3 ~/.cursor/skills/secrets-vault/scripts/manage_secrets.py set wechat_mp app_id "your_id"
   python3 ~/.cursor/skills/secrets-vault/scripts/manage_secrets.py set wechat_mp app_secret "your_secret"
   ```
3. Python 依赖：`pip install wechatpy pyyaml requests`
4. 工作区需有 `Output/wechat/article.html` 和 `Output/wechat/metadata.yaml`

## 使用方式

### 命令行调用

```bash
PUBLISHER="python3 ~/.cursor/skills/content-publisher/scripts/publisher.py"

# 查看支持的平台
$PUBLISHER list

# 发布到微信（仅创建草稿，安全模式）
$PUBLISHER publish --platform wechat --workspace /path/to/workspace

# 发布到微信（自动发布，需谨慎）
$PUBLISHER publish --platform wechat --workspace /path/to/workspace --auto-publish

# 查询发布状态
$PUBLISHER status --platform wechat --workspace /path/to/workspace --publish-id PUBLISH_ID
```

### Agent 调用流程

content-creator 阶段6完成后，Agent 引导用户：

1. 询问用户是否需要发布
2. 用户确认后，执行 `publisher.py publish --platform wechat --workspace ...`
3. 默认创建草稿（安全），告知用户 draft_id
4. 用户确认后，可选执行发布

## 微信公众号发布流程

完整 6 步流程（`full_publish_flow`）：

1. **认证** — 通过 secrets-vault 获取 wechat_mp 凭证，初始化 SDK
2. **加载元数据** — 读取 `Output/wechat/metadata.yaml` 中的 title、digest、author
3. **加载 HTML** — 读取 `Output/wechat/article.html`
4. **上传图片** — 扫描 HTML 中的本地图片，上传到微信 CDN 并替换 URL
5. **创建草稿** — 调用 `draft/add` API，获取 draft media_id
6. **发布**（可选） — 调用 `freepublish/submit` API

输出 JSON 结果：
```json
{
  "status": "draft_created",
  "message": "Draft created successfully. media_id=...",
  "draft_id": "MEDIA_ID"
}
```

## 平台 API 参考

详见 [references/platform-api-guide.md](references/platform-api-guide.md)。

## 扩展新平台

1. 在 `scripts/platforms/` 下创建 `new_platform.py`
2. 继承 `PlatformPublisher` 基类，实现 5 个抽象方法
3. 在 `publisher.py` 的 `PLATFORM_MAP` 中注册
4. 在 secrets-vault 中添加对应凭证命名空间
