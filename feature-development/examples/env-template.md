# 环境变量模板示例

> 本文件提供了完整的环境变量配置模板，用于在任务拆解阶段参考。

---

## 完整模板

```env
# ============================================
# 环境变量配置
# 生成时间: [自动填充]
# 项目名称: [自动填充]
# ============================================

# ============================================
# 应用配置
# ============================================
NEXT_PUBLIC_APP_URL="https://your-domain.com"
NEXT_PUBLIC_APP_NAME="应用名称"
NODE_ENV="production"

# ============================================
# 数据库 (Supabase PostgreSQL)
# ============================================
DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"

# ============================================
# Supabase
# ============================================
NEXT_PUBLIC_SUPABASE_URL="https://[PROJECT-REF].supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="[ANON-KEY]"
SUPABASE_SERVICE_ROLE_KEY="[SERVICE-ROLE-KEY]"

# ============================================
# X (Twitter) OAuth
# ============================================
X_CLIENT_ID="[CLIENT-ID]"
X_CLIENT_SECRET="[CLIENT-SECRET]"
X_CALLBACK_URL="https://your-domain.com/api/auth/x/callback"

# ============================================
# GitHub OAuth（如需要）
# ============================================
GITHUB_CLIENT_ID="[CLIENT-ID]"
GITHUB_CLIENT_SECRET="[CLIENT-SECRET]"
GITHUB_CALLBACK_URL="https://your-domain.com/api/auth/github/callback"

# ============================================
# Google OAuth（如需要）
# ============================================
GOOGLE_CLIENT_ID="[CLIENT-ID]"
GOOGLE_CLIENT_SECRET="[CLIENT-SECRET]"
GOOGLE_CALLBACK_URL="https://your-domain.com/api/auth/google/callback"

# ============================================
# Vercel 部署
# ============================================
VERCEL_TOKEN="[TOKEN]"
VERCEL_ORG_ID="[ORG-ID]"
VERCEL_PROJECT_ID="[PROJECT-ID]"

# ============================================
# Stripe 支付（如需要）
# ============================================
STRIPE_PUBLISHABLE_KEY="[PUBLISHABLE-KEY]"
STRIPE_SECRET_KEY="[SECRET-KEY]"
STRIPE_WEBHOOK_SECRET="[WEBHOOK-SECRET]"

# ============================================
# SendGrid 邮件（如需要）
# ============================================
SENDGRID_API_KEY="[API-KEY]"
SENDGRID_FROM_EMAIL="noreply@your-domain.com"

# ============================================
# AWS S3 存储（如需要）
# ============================================
AWS_ACCESS_KEY_ID="[ACCESS-KEY]"
AWS_SECRET_ACCESS_KEY="[SECRET-KEY]"
AWS_REGION="us-east-1"
AWS_S3_BUCKET="[BUCKET-NAME]"

# ============================================
# Redis 缓存（如需要）
# ============================================
REDIS_URL="redis://localhost:6379"

# ============================================
# JWT 密钥（自建认证时使用）
# ============================================
JWT_SECRET="[RANDOM-SECRET]"
JWT_EXPIRES_IN="7d"
```

---

## 按场景精简

### 场景1: Supabase + Vercel + X OAuth

```env
# 数据库 (Supabase)
DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"

# Supabase
NEXT_PUBLIC_SUPABASE_URL="https://[PROJECT-REF].supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="[ANON-KEY]"
SUPABASE_SERVICE_ROLE_KEY="[SERVICE-ROLE-KEY]"

# X OAuth
X_CLIENT_ID="[CLIENT-ID]"
X_CLIENT_SECRET="[CLIENT-SECRET]"
X_CALLBACK_URL="https://your-domain.com/api/auth/x/callback"

# Vercel
VERCEL_TOKEN="[TOKEN]"
VERCEL_ORG_ID="[ORG-ID]"

# 应用
NEXT_PUBLIC_APP_URL="https://your-domain.com"
```

### 场景2: 仅 Supabase（开发测试）

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL="https://[PROJECT-REF].supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="[ANON-KEY]"
SUPABASE_SERVICE_ROLE_KEY="[SERVICE-ROLE-KEY]"
DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"

# 应用
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

### 场景3: 完整生产配置

```env
# 数据库
DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"

# Supabase
NEXT_PUBLIC_SUPABASE_URL="https://[PROJECT-REF].supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="[ANON-KEY]"
SUPABASE_SERVICE_ROLE_KEY="[SERVICE-ROLE-KEY]"

# OAuth
X_CLIENT_ID="[CLIENT-ID]"
X_CLIENT_SECRET="[CLIENT-SECRET]"
X_CALLBACK_URL="https://your-domain.com/api/auth/x/callback"

# 支付
STRIPE_PUBLISHABLE_KEY="[PUBLISHABLE-KEY]"
STRIPE_SECRET_KEY="[SECRET-KEY]"
STRIPE_WEBHOOK_SECRET="[WEBHOOK-SECRET]"

# 邮件
SENDGRID_API_KEY="[API-KEY]"
SENDGRID_FROM_EMAIL="noreply@your-domain.com"

# Vercel
VERCEL_TOKEN="[TOKEN]"
VERCEL_ORG_ID="[ORG-ID]"

# 应用
NEXT_PUBLIC_APP_URL="https://your-domain.com"
```

---

## 用户信息收集表单

复制以下表单，让用户填写：

```
请提供以下部署配置信息：

## Supabase
□ Supabase URL: https://______.supabase.co
□ Anon Key: ________________________
□ Service Role Key: ________________________
□ Database URL: postgresql://...

## X OAuth（如需要）
□ Client ID: ________________________
□ Client Secret: ________________________

## Vercel
□ Token: ________________________
□ Team ID: ________________________

## 域名
□ 主域名: ________________________

## 其他（如需要）
□ Stripe Secret Key: ________________________
□ SendGrid API Key: ________________________
```

---

## 转换说明

Agent 在收到用户提供的原始信息后，应按以下格式转换为 .env 内容：

```
<根据用户提供的凭证信息>

# 数据库 (Supabase)
DATABASE_URL="postgresql://postgres:xxx@db.xxx.supabase.co:5432/postgres"

# Supabase
NEXT_PUBLIC_SUPABASE_URL="https://xxx.supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="xxx"
SUPABASE_SERVICE_ROLE_KEY="xxx"

# X OAuth
X_CLIENT_ID="xxx"
X_CLIENT_SECRET="xxx"
X_CALLBACK_URL="https://your-domain.com/api/auth/x/callback"

# Vercel
VERCEL_TOKEN="xxx"
VERCEL_ORG_ID="xxx"

# 应用
NEXT_PUBLIC_APP_URL="https://your-domain.com"

</根据用户提供的凭证信息>
```
