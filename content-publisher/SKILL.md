---
name: content-publisher
description: |
  多平台内容发布器，通过 API 或平台适配器将文章发布到各平台。当前支持微信公众号（Phase 1）
  和即刻（Beta），小红书和知乎开发中（Phase 2）。凭证通过 secrets-vault skill 获取，实现安全解耦。
  This skill should be used when: (1) User wants to publish content after
  content-creator workflow completes, (2) User explicitly asks to publish
  to WeChat Official Account or other platforms, (3) content-creator Stage 6
  completes and user confirms publishing. Triggers: "发布到微信", "publish
  to wechat", "发布文章", "自动发布".
argument-hint: "[platform]"
---

# Content Publisher

多平台内容发布器，通过官方 API 将 content-creator 生成的文章发布到各平台。

## 凭证硬规则

发布所需的所有**敏感信息**必须统一通过 [`/secrets-vault` Skill](/Users/mileson/.cursor/skills/secrets-vault/SKILL.md) 获取。

适用范围包括但不限于：
- 平台 `app_id / app_secret / token / access_token`
- 登录手机号 / 密码
- 未来新增平台的 API Key、Cookie、OAuth 凭证
- 任何会影响真实发布动作的个人或组织账号凭证

禁止做法：
- 在 `workspace.config.yaml`、`metadata.yaml`、`article.md` 中存储敏感凭证
- 在 `content-publisher` 代码中硬编码凭证
- 要求用户把凭证直接写进工作区文件再执行发布
- 绕过 `secrets-vault` 直接读取其它 YAML / Markdown 文件获取账号密码

允许的运行方式：
- `content-publisher` 内部通过 `secrets-vault/scripts/get_secret.py` 读取凭证
- 某些平台适配器可将凭证临时注入子进程环境变量，但前提仍然是**先从 `secrets-vault` 获取**

## 支持平台

| 平台 | 状态 | 发布方式 |
|:-----|:---:|:--------|
| 微信公众号 | ✅ Phase 1 | 官方 API (wechatpy SDK) |
| 即刻 | ✅ Beta | Node 适配器（非官方移动端接口） |
| 小红书 | 🔜 Phase 2 | 待定 |
| 知乎 | 🔜 Phase 2 | 待定 |

## 前置条件

1. **secrets-vault** skill 已安装且已配置凭证
2. 微信公众号需在 secrets-vault 中配置 `wechat_mp` 命名空间：
   ```bash
   python3 ~/.cursor/skills/secrets-vault/scripts/manage_secrets.py set wechat_mp app_id "your_id"
   python3 ~/.cursor/skills/secrets-vault/scripts/manage_secrets.py set wechat_mp app_secret "your_secret"
   ```
3. 即刻需在 secrets-vault 中配置 `jike` 命名空间：
   ```bash
   python3 ~/.cursor/skills/secrets-vault/scripts/manage_secrets.py set jike phone "13800000000"
   python3 ~/.cursor/skills/secrets-vault/scripts/manage_secrets.py set jike password "your_password"
   ```
4. 即刻运行环境：需要 Node.js 18+（使用原生 fetch / FormData）
5. Python 依赖：`pip install wechatpy pyyaml requests`
6. 工作区需有平台对应的输出目录和元数据文件

### 凭证来源说明

`content-publisher` 只从两个地方读取发布输入：

- **工作区输出文件**：文章正文、HTML、metadata、图片
- **`/secrets-vault`**：平台发布所需敏感凭证

也就是说：

```text
工作区负责内容
secrets-vault 负责凭证
content-publisher 负责调用平台 API
```

若发布时缺少敏感信息，正确做法是：
- 提示补全 `/secrets-vault`
- 然后重新执行发布

而不是：
- 修改工作区文件塞入凭证
- 在发布脚本里临时硬编码

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

# 搜索即刻频道
$PUBLISHER search-topic --platform jike --workspace /path/to/workspace --query "AI 产品观察"

# 发布到即刻（个人动态 / 频道动态由 metadata.yaml 决定）
$PUBLISHER publish --platform jike --workspace /path/to/workspace

# 查询发布状态
$PUBLISHER status --platform wechat --workspace /path/to/workspace --publish-id PUBLISH_ID
```

### Agent 调用流程

`content-publisher` 只负责“平台侧交付”，不负责封面生成、正文清洗或 AI 生图执行。这些动作应在 `content-creator` 阶段6先完成。

推荐调用规则：

```text
content-creator Stage 6
  -> 已完成：
     - 复制图片到 Output/{platform}/images/
     - sanitize_output_markdown.py
     - run_illustration_pipeline.py
     - metadata.yaml / article.md / article.html（若适用）
  ->
读取 workspace.config.yaml > delivery.platforms.{platform}.mode
  ->
若 mode = auto_format
  -> 停止在本地发布产物完成，不调用 content-publisher

若 mode = auto_format_and_publish
  -> 自动调用 publisher.py publish --platform {platform} --workspace {workspace}
```

推荐与 `content-creator` 的单入口管道配合：

```bash
python3 ~/.cursor/skills/content-creator/scripts/stage6_delivery_pipeline.py \
  /path/to/workspace \
  --platform wechat
```

规则：
- 若 `delivery.platforms.{platform}.mode` 缺失，默认视为 `auto_format`
- `wechat` 的 `auto_format_and_publish` 默认行为是创建公众号草稿
- 仅当用户或上游流程显式要求时，才使用 `--auto-publish` 继续执行 `freepublish/submit`

## 即刻发布流程（Beta）

即刻发布走 Node 适配器，不支持草稿模式，直接发布：

1. **认证** — 从 secrets-vault 读取 `jike.phone / jike.password`
2. **读取元数据** — 加载 `Output/jike/metadata.yaml`
3. **准备正文** — 读取 `Output/jike/article.md`，清理头部封面注释和 Markdown 图片占位
4. **收集图片** — 按 `medias.cover` + `medias.inline_images` 或 `platform_specific.jike.image_paths`
5. **选择频道** — 按以下优先级：
   - `platform_specific.jike.topic_id`
   - `platform_specific.jike.topic_name` + 搜索精确匹配
   - `platform_specific.jike.topic_search_keyword` + 搜索结果唯一匹配
   - 如果用户未明确频道，Agent 在真实发布前必须确认是否使用默认频道 `AI探索站 (63579abb6724cc583b9bba9a)`
6. **直接发布** — 调用 `originalPosts/create`

### 即刻默认频道策略

```text
用户明确给出频道
   -> 使用用户指定频道

用户未给出频道
   -> 发布前询问是否投递默认频道 AI探索站
      -> 确认: 写入 topic_id=63579abb6724cc583b9bba9a 后发布
      -> 拒绝: 改为 personal 模式，仅发个人动态
```

默认频道信息：
- `topic_id`: `63579abb6724cc583b9bba9a`
- `topic_name`: `AI探索站`

### 即刻 metadata.yaml 约定

```yaml
platform:
  id: jike
  display_name: 即刻

article:
  title: "我把内容工作流重做了一遍"

publish_target:
  mode: "topic"                  # personal / topic
  sync_to_personal_update: true

platform_specific:
  jike:
    topic_id: "62b5d6xxxx"
    topic_name: "AI 产品观察"
    topic_search_keyword: ""
    image_mode: "selected"       # selected / none
    image_paths: []              # 可选，显式指定图片顺序
    max_images: 9

medias:
  cover:
    path: "./images/cover.jpg"
  inline_images:
    - path: "./images/01.png"
      alt: "流程图"
```

### 即刻注意事项

- 即刻发布属于 **Beta 非官方接口**，存在失效风险。
- 当频道搜索结果不唯一时，发布器会中止并要求显式指定 `topic_id`。
- 即刻发布默认支持：
  - 个人动态
  - 附图上传
  - 频道投稿（`submitToTopic`）
- 若用户没有明确频道，Agent 默认应在发布前询问是否发送到 `AI探索站`，不要静默自动投递。

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
