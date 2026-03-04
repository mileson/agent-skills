# X (Twitter) OAuth 集成

> 本文档提供 X/Twitter OAuth 2.0 集成的完整配置指南。

## 前置条件

- X Developer 账号
- 已验证的手机号码
- 已验证的邮箱地址

---

## 获取凭证

### 步骤1: 创建 Twitter Developer 项目

1. 访问 [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. 使用 X 账号登录
3. 点击 **"Create Project"** 或 **"New App"**

### 步骤2: 配置应用

1. 填写项目名称
2. 选择使用场景（选择最接近的）
3. 填写应用名称（将显示在授权页面）

### 步骤3: 配置 OAuth 2.0

1. 进入应用设置 → **Settings** → **Authentication settings**
2. 启用 **OAuth 2.0**
3. 配置 **Callback URL**:
   - 本地开发: `http://localhost:3000/api/auth/x/callback`
   - 生产环境: `https://your-domain.com/api/auth/x/callback`
4. 选择 **OAuth 2.0 Scopes**:
   - `tweet.read` - 读取推文
   - `users.read` - 读取用户信息
   - `offline.access` - 离线访问（刷新令牌）

### 步骤4: 获取凭证

1. 进入 **Keys and tokens** 标签页
2. 在 **OAuth 2.0 Client ID and Client Secret** 部分获取:
   - **Client ID**
   - **Client Secret**

---

## 所需信息清单

| 信息项 | 环境变量名 | 说明 |
|--------|------------|------|
| Client ID | `X_CLIENT_ID` | OAuth 2.0 客户端 ID |
| Client Secret | `X_CLIENT_SECRET` | OAuth 2.0 客户端密钥 |
| Callback URL | `X_CALLBACK_URL` | OAuth 回调地址 |

---

## 询问模板

```
如需集成 X (Twitter) OAuth 登录，请提供以下信息：

1. X OAuth Client ID
2. X OAuth Client Secret
3. 回调 URL（通常为 https://your-domain.com/api/auth/x/callback）

💡 获取方式：
- 登录 https://developer.twitter.com/en/portal/dashboard
- 创建应用 → Settings → Authentication settings
- 启用 OAuth 2.0 并配置回调 URL
- 在 Keys and tokens 页面获取 Client ID 和 Secret
```

---

## 环境变量配置

```env
# X (Twitter) OAuth
X_CLIENT_ID="your-client-id-here"
X_CLIENT_SECRET="your-client-secret-here"
X_CALLBACK_URL="https://your-domain.com/api/auth/x/callback"
```

### 本地开发配置

```env
# .env.local
X_CLIENT_ID="your-client-id-here"
X_CLIENT_SECRET="your-client-secret-here"
X_CALLBACK_URL="http://localhost:3000/api/auth/x/callback"
```

---

## OAuth Scopes 说明

| Scope | 说明 | 使用场景 |
|-------|------|----------|
| `tweet.read` | 读取用户推文 | 展示用户推文列表 |
| `tweet.write` | 发布推文 | 代表用户发布内容 |
| `tweet.moderate.write` | 隐藏/删除回复 | 评论管理 |
| `users.read` | 读取用户资料 | 获取用户头像、昵称 |
| `follows.read` | 读取关注列表 | 社交关系分析 |
| `follows.write` | 关注/取消关注 | 社交互动 |
| `offline.access` | 离线访问 | 刷新令牌 |
| `space.read` | 读取 Spaces | 音频空间功能 |
| `mute.read` | 读取静音列表 | 内容过滤 |
| `mute.write` | 静音用户 | 内容管理 |
| `like.read` | 读取点赞 | 内容推荐 |
| `like.write` | 点赞/取消点赞 | 互动功能 |
| `list.read` | 读取列表 | 内容分类 |
| `list.write` | 管理列表 | 内容管理 |
| `block.read` | 读取屏蔽列表 | 安全功能 |
| `block.write` | 屏蔽用户 | 安全功能 |

---

## 常见问题

### Q: 回调 URL 配置错误

**错误信息**: `redirect_uri_mismatch`

**解决方案**:
1. 确认 Twitter Developer Portal 中配置的回调 URL 与代码中完全一致
2. 注意协议（http/https）和端口必须匹配
3. 如使用多个环境，需要配置多个回调 URL

### Q: Token 过期

**错误信息**: `401 Unauthorized`

**解决方案**:
1. 请求 `offline.access` scope 获取刷新令牌
2. 使用刷新令牌获取新的访问令牌
3. 存储 Token 过期时间，提前刷新

### Q: 开发环境无法测试

**解决方案**:
1. 确保使用 `http://localhost:3000` 而非 `http://127.0.0.1:3000`
2. Twitter 对 localhost 有特殊处理
3. 如仍无法测试，可使用 ngrok 等工具暴露本地服务

---

## 代码示例

### NextAuth.js 配置

```typescript
// pages/api/auth/[...nextauth].ts
import NextAuth from "next-auth"
import TwitterProvider from "next-auth/providers/twitter"

export default NextAuth({
  providers: [
    TwitterProvider({
      clientId: process.env.X_CLIENT_ID!,
      clientSecret: process.env.X_CLIENT_SECRET!,
      version: "2.0", // OAuth 2.0
    }),
  ],
  callbacks: {
    async jwt({ token, account }) {
      if (account) {
        token.accessToken = account.access_token
      }
      return token
    },
  },
})
```

### 手动 OAuth 流程

```typescript
// 1. 构建授权 URL
const authUrl = new URL("https://twitter.com/i/oauth2/authorize")
authUrl.searchParams.set("response_type", "code")
authUrl.searchParams.set("client_id", process.env.X_CLIENT_ID!)
authUrl.searchParams.set("redirect_uri", process.env.X_CALLBACK_URL!)
authUrl.searchParams.set("scope", "tweet.read users.read offline.access")
authUrl.searchParams.set("state", generateRandomState())
authUrl.searchParams.set("code_challenge", generateCodeChallenge())
authUrl.searchParams.set("code_challenge_method", "S256")

// 2. 重定向用户到授权页面
window.location.href = authUrl.toString()

// 3. 在回调端点交换 Token
const tokenResponse = await fetch("https://api.twitter.com/2/oauth2/token", {
  method: "POST",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
    Authorization: `Basic ${base64Encode(`${clientId}:${clientSecret}`)}`,
  },
  body: new URLSearchParams({
    grant_type: "authorization_code",
    code: authorizationCode,
    redirect_uri: callbackUrl,
    code_verifier: codeVerifier,
  }),
})
```
