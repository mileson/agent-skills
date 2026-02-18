# GitHub 仓库创建与 Vercel 关联指南

> 本文档定义了 GitHub 仓库创建、代码推送、Vercel 关联的完整流程。
> 所有敏感信息通过 secrets-vault 管理。

---

## 前置条件

### 1. secrets-vault 配置

确保以下凭证已存储在 secrets-vault：

```bash
# GitHub 凭证
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set github token "ghp_xxxx"
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set github username "your_username"
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set github default_visibility "private"

# Vercel 凭证
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set vercel token "xxxx"
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set vercel team_id "team_xxxx"
```

### 2. GitHub Token 权限要求

创建 Token 时需勾选：
- `repo` - 完整仓库访问权限
- `workflow` - GitHub Actions（可选）

### 3. Vercel Token 权限要求

创建 Token 时需选择：
- `Full Account` - 完整账户权限

---

## 流程概览

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub + Vercel 集成流程                      │
│                                                                 │
│  ┌──────────┐    API 创建     ┌──────────┐                      │
│  │  Agent   │ ─────────────> │  GitHub  │                      │
│  └──────────┘                 │  仓库    │                      │
│       │                       └────┬─────┘                      │
│       │ git push                   │                            │
│       ▼                            │ webhook                    │
│  ┌──────────┐                      ▼                            │
│  │  代码    │ ──────────> ┌──────────────┐                      │
│  │  推送    │             │    Vercel    │                      │
│  └──────────┘             │   自动部署    │                      │
│                           └──────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 阶段1: 创建 GitHub 仓库

### 方式1: 使用脚本（推荐）

```bash
python3 ~/.claude/skills/feature-development/scripts/deployment/create_github_repo.py \
  --name "my-project" \
  --description "项目描述" \
  --private
```

### 方式2: 直接调用 API

```bash
# 从 secrets-vault 获取凭证
GITHUB_TOKEN=$(python3 ~/.claude/skills/secrets-vault/scripts/get_secret.py github token)
GITHUB_USERNAME=$(python3 ~/.claude/skills/secrets-vault/scripts/get_secret.py github username)

# 创建仓库
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{
    "name": "my-project",
    "description": "项目描述",
    "private": true,
    "auto_init": false
  }'
```

### API 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `name` | string | 仓库名称（必需） |
| `description` | string | 仓库描述 |
| `private` | boolean | 是否私有（默认 false） |
| `auto_init` | boolean | 是否自动初始化（建议 false） |
| `gitignore_template` | string | .gitignore 模板（如 "Node"） |

### 返回值

成功时返回仓库信息：
```json
{
  "id": 123456789,
  "name": "my-project",
  "full_name": "username/my-project",
  "html_url": "https://github.com/username/my-project",
  "clone_url": "https://github.com/username/my-project.git"
}
```

---

## 阶段2: 初始化 Git 并推送

### 2.1 创建 .gitignore

```bash
# 标准 Next.js .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
.pnp
.pnp.js

# Next.js
.next/
out/

# Production
build/
dist/

# Misc
.DS_Store
*.pem

# Debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Local env files
.env
.env*.local
.env.production

# Vercel
.vercel

# TypeScript
*.tsbuildinfo
next-env.d.ts

# IDE
.idea/
.vscode/
EOF
```

### 2.2 初始化并推送

```bash
# 初始化 Git
git init

# 添加所有文件（.gitignore 会自动排除敏感文件）
git add .

# 创建首次提交
git commit -m "Initial commit

功能模块:
- 模块1
- 模块2

Co-Authored-By: Claude <noreply@anthropic.com>"

# 添加远程仓库
git remote add origin https://github.com/username/my-project.git

# 推送到 main 分支
git branch -M main
git push -u origin main
```

---

## 阶段3: 关联 Vercel

### 方式1: 使用脚本（推荐）

```bash
python3 ~/.claude/skills/feature-development/scripts/deployment/link_vercel_github.py \
  --project-id "prj_xxxx" \
  --repo "username/my-project" \
  --branch "main"
```

### 方式2: 直接调用 API

```bash
# 从 secrets-vault 获取凭证
VERCEL_TOKEN=$(python3 ~/.claude/skills/secrets-vault/scripts/get_secret.py vercel token)
VERCEL_TEAM_ID=$(python3 ~/.claude/skills/secrets-vault/scripts/get_secret.py vercel team_id)

# 关联 GitHub 仓库到 Vercel 项目
curl -X POST \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.vercel.com/v9/projects/{project_id}/link?teamId=$VERCEL_TEAM_ID" \
  -d '{
    "type": "github",
    "repo": "username/my-project",
    "branch": "main"
  }'
```

### 关联成功标志

响应中包含 `link` 字段：
```json
{
  "link": {
    "type": "github",
    "repo": "my-project",
    "org": "username",
    "productionBranch": "main",
    "repoId": 123456789
  }
}
```

---

## 阶段4: 验证自动部署

### 方式1: 使用脚本（推荐）

```bash
python3 ~/.claude/skills/feature-development/scripts/deployment/verify_deployment.py \
  --project-id "prj_xxxx"
```

### 方式2: 手动验证

```bash
# 1. 推送一个小改动
echo "# Update" >> README.md
git add README.md
git commit -m "docs: test deployment"
git push origin main

# 2. 检查 Vercel 部署状态
curl -H "Authorization: Bearer $VERCEL_TOKEN" \
  "https://api.vercel.com/v6/deployments?projectId={project_id}&teamId=$VERCEL_TEAM_ID&limit=3"
```

### 验证成功标志

最新部署状态为 `READY`，且包含 GitHub 提交信息：
```json
{
  "deployments": [
    {
      "readyState": "READY",
      "meta": {
        "githubCommitMessage": "docs: test deployment",
        "githubCommitRef": "main"
      }
    }
  ]
}
```

---

## 完整示例

参见 [examples/github-vercel-deployment.md](../../examples/github-vercel-deployment.md)

---

## 故障排查

### 问题1: GitHub Token 权限不足

**错误信息**: `403 Forbidden`

**解决方案**:
1. 检查 Token 是否有 `repo` 权限
2. 检查 Token 是否过期
3. 重新生成 Token 并更新 secrets-vault

### 问题2: Vercel 关联失败

**错误信息**: `Not authorized` 或 `invalidToken`

**解决方案**:
1. 检查 Vercel Token 是否有效
2. 确认 team_id 正确
3. 检查 Vercel 是否已安装 GitHub App

### 问题3: 推送后没有触发自动部署

**排查步骤**:
1. 检查 Vercel 项目的 Git 设置
2. 确认关联的分支名称正确
3. 检查 Vercel Dashboard 是否有错误日志

---

## 安全注意事项

1. **凭证隔离**: 所有敏感信息存储在 secrets-vault，不在代码中硬编码
2. **Token 轮换**: 定期更换 GitHub Token 和 Vercel Token
3. **最小权限**: Token 仅授予必要的权限
4. **审计日志**: 定期检查 GitHub 和 Vercel 的安全日志
