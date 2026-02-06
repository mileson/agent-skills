# 部署凭证信息清单

> 本文档列出了各部署平台所需的凭证信息，用于在任务拆解时收集用户配置。

---

## Supabase 信息

**收集时机**: 选择 Supabase 作为后端部署平台时

### 必需信息

| 信息项 | 环境变量名 | 获取方式 |
|--------|------------|----------|
| 项目 ID | `SUPABASE_PROJECT_ID` | Dashboard → Settings → General |
| 项目 URL | `NEXT_PUBLIC_SUPABASE_URL` | Dashboard → Settings → API → Project URL |
| Anon Key | `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Dashboard → Settings → API → Project API keys → anon public |
| Service Role Key | `SUPABASE_SERVICE_ROLE_KEY` | Dashboard → Settings → API → Project API keys → service_role |
| 数据库连接字符串 | `DATABASE_URL` | Dashboard → Settings → Database → Connection string → URI |

### 询问模板

```
请提供以下 Supabase 配置信息：

1. Supabase 项目 ID（或项目 URL）
2. Supabase Anon Key（公开密钥）
3. Supabase Service Role Key（服务密钥，用于服务端操作）
4. 数据库连接字符串

💡 提示：
- 登录 https://supabase.com/dashboard
- 进入你的项目 → Settings → API
```

### 示例值

```env
SUPABASE_PROJECT_ID=abcdefghijklmnop
NEXT_PUBLIC_SUPABASE_URL=https://abcdefghijklmnop.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.abcdefghijklmnop.supabase.co:5432/postgres
```

---

## Vercel 信息

**收集时机**: 选择 Vercel 作为前端部署平台时

### 必需信息

| 信息项 | 环境变量名 | 获取方式 |
|--------|------------|----------|
| Vercel Token | `VERCEL_TOKEN` | https://vercel.com/account/tokens |
| Team ID | `VERCEL_ORG_ID` | Vercel Dashboard → Team Settings → General |
| Project ID | `VERCEL_PROJECT_ID` | 部署后自动生成 |

### 询问模板

```
请提供以下 Vercel 配置信息：

1. Vercel Token（访问令牌）
2. Vercel Team ID（团队 ID，如为个人账户可不提供）

💡 提示：
- 创建 Token: https://vercel.com/account/tokens
- 查看 Team ID: Vercel Dashboard → Team Settings → General
```

### 示例值

```env
VERCEL_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
VERCEL_ORG_ID=team_xxxxxxxxxxxx
VERCEL_PROJECT_ID=prj_xxxxxxxxxxxx
```

---

## 域名信息

**收集时机**: 使用自定义域名时

### 必需信息

| 信息项 | 说明 |
|--------|------|
| 主域名 | 如 `example.com` |
| DNS 访问权限 | 用于配置 DNS 记录 |
| SSL 证书 | 自签名或 Let's Encrypt |

### 询问模板

```
请提供域名信息：

1. 主域名（如 example.com）
2. 是否需要配置 www 子域名？
3. DNS 是否已指向部署平台？

💡 如使用 Vercel/Netlify，平台会自动配置 SSL
```

### 示例值

```env
NEXT_PUBLIC_APP_URL=https://example.com
NEXT_PUBLIC_APP_DOMAIN=example.com
```

---

## 自行部署信息

**收集时机**: 选择自行部署（VPS/云服务器）时

### 必需信息

| 信息项 | 说明 |
|--------|------|
| 服务器 IP | 公网 IP 地址 |
| SSH 访问 | 用户名、端口、密钥 |
| 操作系统 | Ubuntu / CentOS / Debian |
| 数据库 | MySQL / PostgreSQL 连接信息 |

### 询问模板

```
请提供服务器信息：

1. 服务器 IP 地址
2. SSH 访问方式（用户名、端口）
3. 操作系统类型
4. 是否已安装 Docker？

💡 建议使用 Docker 进行容器化部署
```

---

## 信息收集表单

复制以下表单让用户填写：

```markdown
## 部署配置信息

### Supabase（如适用）
- [ ] 项目 ID: _______________
- [ ] Anon Key: _______________
- [ ] Service Role Key: _______________
- [ ] 数据库连接字符串: _______________

### Vercel（如适用）
- [ ] Token: _______________
- [ ] Team ID: _______________

### 域名
- [ ] 主域名: _______________
- [ ] 是否需要 www: 是 / 否

### 其他
- [ ] 其他需要配置的环境变量: _______________
```

---

## 安全提示

1. **敏感信息处理**: Service Role Key、数据库密码等敏感信息不要提交到 Git
2. **环境变量分离**: 区分 `.env.local`（本地）、`.env.production`（生产）
3. **密钥轮换**: 定期更换 API Token 和密钥
4. **访问控制**: 最小权限原则，仅授予必要的权限
