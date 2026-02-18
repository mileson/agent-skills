# 部署凭证信息清单

> 本文档列出了各部署平台所需的凭证信息。
> **所有敏感信息通过 secrets-vault 管理，不在代码或文档中存储。**

---

## 凭证管理方式

### 使用 secrets-vault（推荐）

所有凭证通过 `~/.secrets/vault.yaml` 集中管理，其他 skill 通过脚本调用获取：

```bash
# 获取凭证
python3 ~/.claude/skills/secrets-vault/scripts/get_secret.py github
python3 ~/.claude/skills/secrets-vault/scripts/get_secret.py vercel
python3 ~/.claude/skills/secrets-vault/scripts/get_secret.py supabase

# 在脚本中调用
import subprocess, json
result = subprocess.run(
    ["python3", "~/.claude/skills/secrets-vault/scripts/get_secret.py", "github"],
    capture_output=True, text=True
)
creds = json.loads(result.stdout)
```

---

## GitHub 凭证

**收集时机**: 需要创建 GitHub 仓库或推送代码时

### 必需信息

| 信息项 | secrets-vault 命名空间 | 说明 |
|--------|----------------------|------|
| Token | `github.token` | Personal Access Token |
| 用户名 | `github.username` | GitHub 用户名 |
| 默认可见性 | `github.default_visibility` | public 或 private |

### 配置命令

```bash
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set github token "ghp_xxxx"
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set github username "your_username"
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set github default_visibility "private"
```

### Token 获取方式

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选权限: `repo`（完整仓库访问权限）
4. 复制 Token 并存储到 secrets-vault

### Token 权限要求

- `repo` - 完整仓库访问权限（必需）
- `workflow` - GitHub Actions（可选）

---

## Vercel 凭证

**收集时机**: 选择 Vercel 作为前端部署平台时

### 必需信息

| 信息项 | secrets-vault 命名空间 | 说明 |
|--------|----------------------|------|
| Token | `vercel.token` | Vercel API Token |
| Team ID | `vercel.team_id` | 团队 ID（可选） |

### 配置命令

```bash
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set vercel token "xxxx"
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set vercel team_id "team_xxxx"
```

### Token 获取方式

1. 访问 https://vercel.com/account/tokens
2. 点击 "Create Token"
3. 选择 "Full Account" 权限
4. 复制 Token 并存储到 secrets-vault

---

## Supabase 凭证

**收集时机**: 选择 Supabase 作为后端部署平台时

**命名规范**: 使用 `<project_name>_supabase` 格式，如 `molthands_supabase`

### 必需信息

| 信息项 | secrets-vault 命名空间 | 获取方式 |
|--------|----------------------|----------|
| 项目 ID | `<project>_supabase.project_id` | Dashboard → Settings → General |
| 项目 URL | `<project>_supabase.url` | Dashboard → Settings → API → Project URL |
| Anon Key | `<project>_supabase.anon_key` | Dashboard → Settings → API → anon public |
| Service Role Key | `<project>_supabase.service_role_key` | Dashboard → Settings → API → service_role |
| 数据库连接 | `<project>_supabase.database_url` | Dashboard → Settings → Database → URI |

### 配置命令

```bash
# 使用项目名前缀，如 molthands_supabase
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set molthands_supabase project_id "xxxx"
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set molthands_supabase url "https://xxxx.supabase.co"
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set molthands_supabase anon_key "eyJhbGci..."
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set molthands_supabase service_role_key "eyJhbGci..."
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set molthands_supabase database_url "postgresql://postgres.xxxx:[PASSWORD]@aws-0-us-west-2.pooler.supabase.com:6543/postgres"
```

---

## OAuth 集成凭证

### X/Twitter OAuth

| 信息项 | secrets-vault 命名空间 |
|--------|----------------------|
| Client ID | `x_oauth.client_id` |
| Client Secret | `x_oauth.client_secret` |
| Callback URL | `x_oauth.callback_url` |

### GitHub OAuth

| 信息项 | secrets-vault 命名空间 |
|--------|----------------------|
| Client ID | `github_oauth.client_id` |
| Client Secret | `github_oauth.client_secret` |
| Callback URL | `github_oauth.callback_url` |

---

## 域名信息

**收集时机**: 使用自定义域名时

### 必需信息

| 信息项 | 说明 |
|--------|------|
| 主域名 | 如 `example.com` |
| DNS 访问权限 | 用于配置 DNS 记录 |

### 询问模板

```
请提供域名信息：

1. 主域名（如 example.com）
2. 是否需要配置 www 子域名？
3. DNS 是否已指向部署平台？

💡 如使用 Vercel/Netlify，平台会自动配置 SSL
```

---

## 自行部署信息

**收集时机**: 选择自行部署（VPS/云服务器）时

### 必需信息

| 信息项 | secrets-vault 命名空间 | 说明 |
|--------|----------------------|------|
| 服务器 IP | `vps.ip` | 公网 IP 地址 |
| SSH 用户名 | `vps.ssh_user` | SSH 登录用户 |
| SSH 端口 | `vps.ssh_port` | SSH 端口（默认 22） |
| SSH 密钥 | `vps.ssh_key` | 私钥内容 |

---

## 信息收集表单

复制以下表单让用户填写（填写后存储到 secrets-vault）：

```markdown
## 部署配置信息

### GitHub
- [ ] Token: _______________
- [ ] 用户名: _______________
- [ ] 默认可见性: public / private

### Vercel
- [ ] Token: _______________
- [ ] Team ID: _______________（可选）

### Supabase（如适用）
- [ ] 项目 ID: _______________
- [ ] 项目 URL: _______________
- [ ] Anon Key: _______________
- [ ] Service Role Key: _______________
- [ ] 数据库连接字符串: _______________

### OAuth 集成（如适用）
- [ ] X Client ID: _______________
- [ ] X Client Secret: _______________
```

---

## 安全规则

1. **集中存储**: 所有敏感信息存储在 `~/.secrets/vault.yaml`
2. **脚本访问**: 通过 `get_secret.py` 获取，不直接读取文件
3. **权限控制**: `~/.secrets/` 目录权限 700，文件权限 600
4. **Git 忽略**: `.gitignore` 阻止一切敏感文件被追踪
5. **Token 轮换**: 定期更换 API Token 和密钥
6. **最小权限**: Token 仅授予必要的权限
