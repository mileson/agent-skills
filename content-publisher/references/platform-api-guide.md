# 平台 API 接入指南

## 微信公众号（Phase 1）

### 官方 API 文档

- 草稿管理: https://developers.weixin.qq.com/doc/subscription/api/draftbox/draftmanage/api_draft_add
- 发布能力: https://developers.weixin.qq.com/doc/subscription/api/public/api_freepublish_submit
- 图片上传: https://developers.weixin.qq.com/doc/subscription/api/material/permanent/api_uploadimage

### 核心 API 链路

| 步骤 | API | 说明 |
|:---:|:----|:-----|
| 1 | `GET /cgi-bin/token` | 获取 access_token（2h有效） |
| 2 | `POST /cgi-bin/media/uploadimg` | 上传正文图片 → 微信 CDN URL |
| 3 | `POST /cgi-bin/material/add_material` | 上传封面 → thumb_media_id |
| 4 | `POST /cgi-bin/draft/add` | 创建草稿 → media_id |
| 5 | `POST /cgi-bin/freepublish/submit` | 发布 → publish_id |
| 6 | `POST /cgi-bin/freepublish/get` | 查询发布状态 |

### draft/add 参数说明

| 参数 | 类型 | 必填 | 说明 |
|:-----|:-----|:---:|:-----|
| title | string | 是 | 标题，最大32字符 |
| content | string | 是 | HTML 正文，<20000字符，<1MB |
| digest | string | 否 | 摘要，最大128字符 |
| author | string | 否 | 作者，最大16字符 |
| thumb_media_id | string | 否 | 封面图永久素材 ID |
| content_source_url | string | 否 | 原文链接 |
| need_open_comment | number | 否 | 0=关闭评论，1=开启 |

### 关键限制

- `content` 中图片 URL 必须使用 `uploadimg` 上传，外部 URL 会被过滤
- `freepublish/submit` 成功仅表示任务提交，需轮询 `freepublish/get` 确认状态
- 通过 freepublish 发布的文章进入"已发布"列表，不推送到粉丝消息列表
- 推送消息需使用群发接口（`message/mass`），有次数限制

### wechatpy SDK 映射

| 官方 API | wechatpy 方法 |
|:---------|:-------------|
| media/uploadimg | `client.media.upload_mass_image(f)` |
| material/add_material | `client.material.add(type, f)` |
| draft/add | `client.draft.add(articles)` |
| freepublish/submit | `client.freepublish.submit(media_id)` |
| freepublish/get | `client.freepublish.get(publish_id)` |

---

## 小红书（Phase 2 — 待调研）

- 开放平台: https://miniapp.xiaohongshu.com/doc
- 发布服务: https://xiaohongshu.apifox.cn/doc-2810945
- 需企业认证才能获取 API 权限
- 个人创作者暂无官方发布 API

---

## 知乎（Phase 2 — 待调研）

- 官方 API 仅支持数据读取，不支持发布
- 可能方案：非官方 API / 浏览器自动化
- 风险：封号风险较高

---

## 即刻（Beta — 非官方接口）

### 当前实现能力

| 能力 | 状态 | 实现方式 |
|:---:|:---:|:---------|
| 登录 / 自动刷新 | ✅ | `users/loginWithPhoneAndPassword` + `app_auth_tokens.refresh` |
| 当前用户校验 | ✅ | `users/profile?username=` |
| 频道搜索 | ✅ | `users/topics/search` |
| 图片上传 | ✅ | `upload/token` + 七牛上传 |
| 发布个人动态 | ✅ | `originalPosts/create` |
| 发布到频道 | ✅ | `originalPosts/create + submitToTopic` |

### 核心接口链路

| 步骤 | 接口 | 说明 |
|:---:|:----|:-----|
| 1 | `POST /1.0/users/loginWithPhoneAndPassword` | 手机号密码登录 |
| 2 | `POST /app_auth_tokens.refresh` | 刷新 access token |
| 3 | `GET /1.0/users/profile?username=` | 校验当前登录用户 |
| 4 | `POST /1.0/users/topics/search` | 搜索频道 / 圈子 |
| 5 | `GET /1.0/upload/token?md5=...` | 获取图片上传凭证 |
| 6 | `POST https://upload.qiniup.com/` | 上传图片到七牛 |
| 7 | `POST /1.0/originalPosts/create` | 发布动态 |

### 发布请求体

个人动态：

```json
{
  "content": "动态正文",
  "pictureKeys": ["xxx", "yyy"],
  "syncToPersonalUpdate": true
}
```

频道动态：

```json
{
  "content": "动态正文",
  "pictureKeys": ["xxx", "yyy"],
  "syncToPersonalUpdate": true,
  "submitToTopic": "topic_id"
}
```

### 风险提示

- 当前实现基于非官方移动端接口，后续可能因客户端版本或风控策略变化而失效。
- 不建议自动选择模糊搜索结果中的第一个频道，必须优先使用 `topic_id`。
- 建议将即刻发布能力标记为 **Beta**，并在工作流中保留人工确认。
- 若用户未显式指定频道，建议默认确认 `AI探索站 (63579abb6724cc583b9bba9a)`，确认后再写入 `submitToTopic`。
