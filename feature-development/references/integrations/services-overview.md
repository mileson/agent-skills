# 第三方集成服务总览

> 本文档列出了 feature-development skill 支持的第三方集成服务及其配置指南。

## 目录

- [OAuth 认证集成](#oauth-认证集成)
- [支付集成](#支付集成)
- [通知服务集成](#通知服务集成)
- [存储服务集成](#存储服务集成)
- [如何添加新的集成](#如何添加新的集成)

---

## OAuth 认证集成

### X (Twitter) OAuth

**文档**: [x-twitter-oauth.md](./x-twitter-oauth.md)

**适用场景**:
- 使用 X/Twitter 账号登录
- 获取用户 X 账号信息
- 代表用户发布推文

**所需信息**:
- Client ID
- Client Secret
- Callback URL

### GitHub OAuth

**适用场景**:
- 使用 GitHub 账号登录
- 访问用户仓库
- GitHub Actions 集成

**获取方式**: https://github.com/settings/developers

**所需信息**:
- Client ID
- Client Secret
- Callback URL

### Google OAuth

**适用场景**:
- 使用 Google 账号登录
- 访问 Google 服务（Gmail、Drive 等）

**获取方式**: https://console.cloud.google.com/apis/credentials

**所需信息**:
- Client ID
- Client Secret
- Callback URL

---

## 支付集成

### Stripe

**适用场景**:
- 国际信用卡支付
- 订阅管理
- 发票处理

**获取方式**: https://dashboard.stripe.com/developers

**所需信息**:
- Publishable Key
- Secret Key
- Webhook Secret

### 支付宝

**适用场景**:
- 国内支付

**获取方式**: https://open.alipay.com/

**所需信息**:
- App ID
- 应用私钥
- 支付宝公钥

### 微信支付

**适用场景**:
- 国内支付
- 小程序支付

**获取方式**: https://pay.weixin.qq.com/

**所需信息**:
- App ID
- Mch ID（商户号）
- API Key
- API 证书

---

## 通知服务集成

### SendGrid（邮件）

**适用场景**:
- 交易邮件
- 营销邮件

**获取方式**: https://app.sendgrid.com/settings/api_keys

**所需信息**:
- API Key

### Twilio（短信）

**适用场景**:
- 短信验证码
- 语音通知

**获取方式**: https://www.twilio.com/console

**所需信息**:
- Account SID
- Auth Token
- 发送号码

---

## 存储服务集成

### AWS S3

**适用场景**:
- 文件存储
- 静态资源托管

**所需信息**:
- Access Key ID
- Secret Access Key
- Region
- Bucket Name

### Cloudflare R2

**适用场景**:
- S3 兼容存储
- 无出站费用

**所需信息**:
- Account ID
- Access Key ID
- Secret Access Key
- Bucket Name

---

## 如何添加新的集成

当项目需要新的第三方集成时，按以下步骤添加：

### 1. 创建集成文档

在 `references/integrations/` 下创建新文件，如 `slack-oauth.md`：

```markdown
# Slack OAuth 集成

## 获取凭证

1. 访问 https://api.slack.com/apps
2. 创建新应用
3. 配置 OAuth & Permissions
4. 获取 Client ID 和 Client Secret

## 所需信息

| 信息项 | 环境变量名 | 说明 |
|--------|------------|------|
| Client ID | SLACK_CLIENT_ID | OAuth Client ID |
| Client Secret | SLACK_CLIENT_SECRET | OAuth Client Secret |
| Signing Secret | SLACK_SIGNING_SECRET | Webhook 签名验证 |

## 环境变量模板

\`\`\`env
SLACK_CLIENT_ID=xxx
SLACK_CLIENT_SECRET=xxx
SLACK_SIGNING_SECRET=xxx
\`\`\`

## 回调 URL

\`\`\`
https://your-domain.com/api/auth/slack/callback
\`\`\`
```

### 2. 更新本索引文件

在 `services-overview.md` 中添加新集成的条目。

### 3. 更新 SKILL.md

在 SKILL.md 的集成询问流程中添加新的选项。

---

## 集成询问流程

在 **阶段2（架构设计）** 中，询问用户是否需要第三方集成：

```
架构设计已完成。关于第三方服务集成，是否有以下需求：

1. OAuth 登录（X/Twitter、GitHub、Google 等）？
2. 支付（Stripe、支付宝、微信支付）？
3. 邮件/短信通知？
4. 文件存储（S3、R2）？
```

根据用户选择，读取对应的集成文档并收集凭证信息。
