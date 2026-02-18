# 敏感信息扫描指南

本文档为 Agent 执行 Stage 3（当前文件扫描）和 Stage 4（Git 历史扫描）时的详细参考。

---

## 扫描哲学

> **不依赖固定正则，以 AI 理解力为核心。**
>
> 经典模式作为起点，边界场景由 Agent 自主推断和补充。
> 每轮扫描后 Agent 应自问："还有没有遗漏的？"，直到没有新发现为止。

---

## 第一轮：经典敏感模式

### 1. API 密钥 / Secret

**特征**：长随机字符串，通常有固定前缀

```
扫描要点：
- 以 sk-, pk-, ghp_, gho_, ghs_, ghu_, github_pat_, AKIA, ASIA 开头的字符串
- AWS: AKIA[0-9A-Z]{16}
- GitHub: ghp_[A-Za-z0-9]{36}, github_pat_[A-Za-z0-9_]{82}
- Stripe: sk_live_[A-Za-z0-9]{24,}, pk_live_[A-Za-z0-9]{24,}
- OpenAI: sk-[A-Za-z0-9]{48}
- Supabase: eyJhbGci... (JWT 格式的 anon_key / service_role_key)
- Google: AIza[A-Za-z0-9_-]{35}
- Slack: xoxb-, xoxp-, xoxa-, xoxr-

注意：出现在 .env.example 中且值为空或占位符的不算泄露
```

### 2. 数据库连接字符串

**特征**：包含协议、用户名、密码、主机、数据库名

```
扫描要点：
- postgresql://user:password@host:port/dbname
- mysql://user:password@host:port/dbname
- mongodb://user:password@host:port/dbname
- redis://user:password@host:port
- 含 password / pwd 的连接参数
- Supabase 的 pooler 地址和直连地址

重点文件：
- prisma/schema.prisma 的 datasource 块
- docker-compose.yml 的 environment 块
- 任何 ORM 配置文件
```

### 3. Token / JWT

**特征**：Base64 编码的长字符串，通常三段点分格式

```
扫描要点：
- Bearer token 硬编码在请求头中
- JWT: eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+
- OAuth token / refresh token 作为字符串常量
- session secret 硬编码

注意区分：
- 测试用的 mock JWT（通常解码后 payload 无敏感数据）
- 文档中的示例 JWT（通常用 xxx 标注）
```

### 4. 密码 / Secret

**特征**：赋值语句中的明文密码

```
扫描要点：
- password = "xxx" / password: "xxx"
- secret = "xxx" / secret_key = "xxx"
- 默认密码如 admin, admin123, password, 123456, root
- 硬编码的 fallback 密码（如 process.env.PASSWORD || "default"）
- HMAC secret, signing key

注意：密码强度检查不是此步骤的目标
```

### 5. 内网地址 / 私有基础设施

**特征**：非公开的网络地址

```
扫描要点：
- 私有 IP: 10.x.x.x, 172.16-31.x.x, 192.168.x.x
- 公网服务器 IP（非 CDN）：具体的 IP 地址
- 内部域名: *.internal, *.corp, *.local, *.dev（自定义）
- localhost 使用真实端口号并暴露配置
- VPN 地址
- 数据库服务器地址

注意：localhost:3000 在开发文档中属于正常内容
```

### 6. 云服务标识

**特征**：项目 ID、Account ID 等标识符

```
扫描要点：
- Vercel: prj_[A-Za-z0-9]{24,}
- AWS Account ID: 12 位数字
- GCP Project ID: 带连字符的小写字符串
- Supabase Project Ref: [a-z]{20} 格式的引用 ID
- Firebase: 项目配置中的 apiKey / authDomain / projectId
- Sentry DSN: https://[key]@sentry.io/[project_id]

注意：部分公开标识（如 Supabase URL 的 project ref）
取决于项目策略是否视为敏感
```

### 7. 私钥 / 证书

**特征**：PEM 格式的密钥块

```
扫描要点：
- -----BEGIN RSA PRIVATE KEY-----
- -----BEGIN EC PRIVATE KEY-----
- -----BEGIN OPENSSH PRIVATE KEY-----
- -----BEGIN CERTIFICATE-----（如果是自签名）
- .p12 / .pfx / .jks 文件（二进制密钥库）

重点：这类文件绝对不能出现在 Git 中
```

### 8. Webhook / 回调 URL

**特征**：包含密钥或 token 的 URL

```
扫描要点：
- Slack Webhook: https://hooks.slack.com/services/T.../B.../xxx
- Discord Webhook: https://discord.com/api/webhooks/xxx/xxx
- 带 token 参数的回调 URL
- 带 API key 参数的第三方服务 URL
```

### 9. 个人信息

**特征**：开发者的私人联系信息

```
扫描要点：
- 私人邮箱地址（非通用的 info@ / support@）
- 手机号码
- 物理地址
- 社交账号 handle（如果非公开项目）

注意：MIT LICENSE 中的作者名和公开邮箱通常不算敏感
```

---

## 第二轮：技术栈推断扫描

Agent 根据项目使用的技术栈，自动推断并检查额外的敏感信息场景：

```
┌─────────────────────┬────────────────────────────────────────┐
│ 检测到的技术栈       │ 额外扫描项                              │
├─────────────────────┼────────────────────────────────────────┤
│ Next.js             │ NEXT_PUBLIC_ 变量中是否有不该公开的值     │
│ Supabase            │ service_role_key 是否硬编码              │
│ Vercel              │ 项目 ID / Team ID 是否泄露               │
│ Prisma              │ seed 文件是否包含真实数据                 │
│ OAuth (任何)        │ client_secret 是否硬编码                 │
│ Stripe / 支付       │ live 模式密钥是否在代码中                 │
│ SMTP / 邮件         │ SMTP 密码是否硬编码                      │
│ Docker              │ Dockerfile 中是否有密钥注入               │
│ CI/CD               │ workflow 文件中是否有硬编码变量            │
│ Firebase            │ 完整配置对象是否包含不该公开的密钥         │
│ Redis               │ 连接字符串是否含密码                      │
│ S3 / 对象存储       │ 桶名 + 区域是否暴露私有资源路径            │
│ Sentry              │ DSN 中是否含内部项目标识                  │
│ GraphQL             │ introspection 是否在生产环境启用          │
└─────────────────────┴────────────────────────────────────────┘
```

**检测方式**：
```bash
# 技术栈检测（非穷举，Agent 应根据实际情况补充）
cat package.json       # Node.js 依赖
cat Cargo.toml         # Rust 依赖
cat pyproject.toml     # Python 依赖
cat docker-compose.yml # Docker 服务
ls .github/workflows/  # CI/CD 配置
cat prisma/schema.prisma # 数据库 ORM
```

---

## 第三轮：边界场景补充

Agent 需要自主走查以下容易遗漏的边界场景，每发现一处新问题就记录并继续深入：

### 容易遗漏的场景清单

1. **注释中的密钥**
   ```
   // const API_KEY = "sk-abc123..."  // 被注释掉但仍在代码中
   /* old config: password = "admin" */
   ```

2. **测试报告中的服务器信息**
   ```
   tests/reports/*.md 中的真实 IP、域名、路径
   测试输出日志中的数据库连接信息
   ```

3. **嵌套 JSON/YAML 中的凭证**
   ```json
   { "config": { "nested": { "deep": { "secret": "real_value" } } } }
   ```

4. **README/文档中的真实配置**
   ```
   文档示例使用了真实的项目 ID、URL
   部署文档中的实际服务器地址
   ```

5. **Lock 文件中的私有 Registry**
   ```
   package-lock.json / yarn.lock 中的私有 npm registry URL
   ```

6. **GitHub Actions 中的硬编码**
   ```yaml
   env:
     SECRET_KEY: "hardcoded_value"  # 应使用 ${{ secrets.SECRET_KEY }}
   ```

7. **Migration 文件中的默认值**
   ```sql
   ALTER TABLE users ALTER COLUMN password SET DEFAULT 'admin123';
   INSERT INTO settings VALUES ('api_key', 'real_key_here');
   ```

8. **Commit Message 中的敏感信息**
   ```
   git log 中可能出现："fix: update password to admin456"
   ```

9. **Submodule / 子模块引用**
   ```
   .gitmodules 中是否引用了私有仓库 URL
   ```

10. **IDE / 编辑器配置**
    ```
    .vscode/launch.json 中的环境变量
    .idea/ 目录中的部署配置
    ```

---

## Git 历史扫描策略

### 基本搜索

```bash
# 对 Stage 3 发现的每个敏感字符串进行历史搜索
git log -S "<sensitive_string>" --all --oneline

# 搜索已删除的敏感文件
git log --all --diff-filter=D --summary -- "*.env" "*.pem" "*.key" "*secret*" "*credential*"

# 搜索含敏感关键词的 commit 变更
git log -p --all -S "password" -- "*.ts" "*.js" "*.py" "*.go"
git log -p --all -S "secret" -- "*.ts" "*.js" "*.py" "*.go"
git log -p --all -S "api_key" -- "*.ts" "*.js" "*.py" "*.go"
```

### 深度搜索（如有需要）

```bash
# 列出所有历史中曾存在的文件路径
git log --all --pretty=format: --name-only | sort -u

# 在上述列表中搜索可疑文件名
# 如 .env, credentials, secrets, *.pem, *.key 等

# 检查特定文件的完整历史内容
git log -p --all --follow -- <suspicious_file>
```

### 清理操作参考

```bash
# 安装 git-filter-repo
pip install git-filter-repo

# 备份当前状态
git branch backup-before-cleanup

# 完全移除文件
git filter-repo --invert-paths --path <file_to_remove>

# 批量移除多个路径
git filter-repo --invert-paths \
  --path path/to/secret1 \
  --path path/to/secret2

# 替换敏感字符串（创建 replacements.txt）
# 格式: literal:旧字符串==>literal:新字符串
echo 'literal:admin123==>literal:REDACTED' > /tmp/replacements.txt
echo 'literal:prj_abc123==>literal:prj_YOUR_PROJECT_ID' >> /tmp/replacements.txt
git filter-repo --replace-text /tmp/replacements.txt

# 清理后重新添加 remote（filter-repo 会移除 origin）
git remote add origin <remote_url>

# Force push（需用户确认！）
git push --force origin main
```

---

## 安全文件白名单

以下文件/模式通常**不需要标记为敏感**：

- `.env.example`（仅包含占位符值）
- `package.json` / `package-lock.json`（通常安全）
- 公开文档中的 `localhost:3000` 等开发地址
- MIT LICENSE 中的作者姓名
- `NEXT_PUBLIC_` 前缀的变量（设计上就是公开的，但要确认值是否恰当）
- 测试代码中的 `test_`, `mock_`, `fake_` 前缀的假数据
- `.gitignore` 文件本身

---

## 扫描终止条件

Agent 应持续扫描，直到满足以下所有条件：

1. 经典 9 大类别已全部检查
2. 技术栈推断的额外项已检查
3. 边界场景清单已走查
4. 连续一轮扫描无新发现
5. 所有发现已分类为高危/中危/低危并报告用户
