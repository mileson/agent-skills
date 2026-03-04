# GitHub + Vercel 部署完整示例

> 本文档提供一个完整的 GitHub 创建到 Vercel 自动部署的示例。

---

## 场景描述

假设我们正在开发一个名为 `my-awesome-app` 的 Next.js 项目，需要：
1. 创建 GitHub 私有仓库
2. 初始化本地 Git 并推送代码
3. 关联到已有的 Vercel 项目
4. 验证自动部署功能

---

## 前置条件

### 1. secrets-vault 配置

```bash
# 初始化 vault
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py init

# 配置 GitHub 凭证
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set github token "ghp_xxxx"
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set github username "your_username"
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set github default_visibility "private"

# 配置 Vercel 凭证
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set vercel token "xxxx"
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set vercel team_id "team_xxxx"
```

### 2. 项目目录结构

```
my-awesome-app/
├── src/
│   └── app/
│       └── page.tsx
├── package.json
├── next.config.ts
└── .vercel/
    └── project.json    # Vercel 项目已存在
```

---

## 步骤1: 创建 .gitignore

```bash
cat > .gitignore << 'EOF'
# Dependencies
node_modules/

# Next.js
.next/

# Misc
.DS_Store

# Local env files
.env
.env*.local

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

---

## 步骤2: 创建 GitHub 仓库

```bash
# 使用脚本创建
python3 ~/.claude/skills/spec-driven-development/scripts/deployment/create_github_repo.py \
  --name "my-awesome-app" \
  --description "My awesome Next.js application" \
  --private
```

**预期输出**:
```json
{
  "success": true,
  "repo_id": 123456789,
  "name": "my-awesome-app",
  "full_name": "your_username/my-awesome-app",
  "html_url": "https://github.com/your_username/my-awesome-app",
  "clone_url": "https://github.com/your_username/my-awesome-app.git",
  "private": true
}
```

---

## 步骤3: 初始化 Git 并推送

```bash
# 初始化 Git
git init

# 添加文件
git add .

# 创建首次提交
git commit -m "Initial commit: My awesome Next.js app

功能模块:
- 首页
- 用户认证
- 数据展示

Co-Authored-By: Claude <noreply@anthropic.com>"

# 添加远程仓库
git remote add origin https://github.com/your_username/my-awesome-app.git

# 推送
git branch -M main
git push -u origin main
```

---

## 步骤4: 关联 Vercel

首先获取 Vercel 项目 ID：

```bash
# 查看 .vercel/project.json
cat .vercel/project.json
# {"projectId":"prj_xxxx","orgId":"team_xxxx","projectName":"my-awesome-app"}
```

关联 GitHub 仓库：

```bash
# 使用脚本关联
python3 ~/.claude/skills/spec-driven-development/scripts/deployment/link_vercel_github.py \
  --project-id "prj_xxxx" \
  --repo "your_username/my-awesome-app" \
  --branch "main"
```

**预期输出**:
```json
{
  "success": true,
  "link": {
    "type": "github",
    "repo": "my-awesome-app",
    "org": "your_username",
    "production_branch": "main",
    "repo_id": 123456789
  },
  "project_name": "my-awesome-app"
}
```

---

## 步骤5: 验证部署

等待 Vercel 自动部署完成后验证：

```bash
# 等待 30 秒后验证
python3 ~/.claude/skills/spec-driven-development/scripts/deployment/verify_deployment.py \
  --project-id "prj_xxxx" \
  --wait 30
```

**预期输出**:
```json
{
  "success": true,
  "project": {
    "name": "my-awesome-app",
    "id": "prj_xxxx",
    "framework": "nextjs"
  },
  "github_link": {
    "connected": true,
    "type": "github",
    "repo": "your_username/my-awesome-app",
    "branch": "main"
  },
  "latest_deployment": {
    "state": "READY",
    "branch": "main",
    "commit_message": "Initial commit: My awesome Next.js app",
    "url": "my-awesome-app-xxx.vercel.app"
  },
  "deployment_count": 1
}
```

---

## 后续工作流

关联完成后，每次代码更新：

```bash
# 1. 修改代码
vim src/app/page.tsx

# 2. 提交
git add .
git commit -m "feat: 添加新功能"

# 3. 推送（自动触发 Vercel 部署）
git push origin main

# 4. 验证部署
python3 ~/.claude/skills/spec-driven-development/scripts/deployment/verify_deployment.py \
  --project-id "prj_xxxx" \
  --wait 60
```

---

## 常见问题

### Q1: 仓库已存在怎么办？

如果仓库已存在，脚本会返回错误：

```json
{
  "success": false,
  "error": "Repository already exists"
}
```

解决方案：
- 使用现有仓库，跳过创建步骤
- 或删除现有仓库后重新创建

### Q2: Vercel 关联失败？

检查：
1. Vercel Token 是否有效
2. GitHub 仓库是否存在
3. Vercel 是否已安装 GitHub App（访问 https://vercel.com/account/integrations）

### Q3: 推送后没有触发部署？

检查：
1. Vercel 项目的 Git 设置
2. 分支名称是否正确
3. 查看 Vercel Dashboard 的 Deployments 页面

---

## 总结

```
┌─────────────────────────────────────────────────────────────────┐
│                      部署流程总结                                │
│                                                                 │
│  1. 配置 secrets-vault (一次性)                                  │
│     └─> 存储 GitHub Token, Vercel Token                         │
│                                                                 │
│  2. 创建 GitHub 仓库                                             │
│     └─> create_github_repo.py                                   │
│                                                                 │
│  3. 初始化 Git 并推送                                            │
│     └─> git init → git push                                     │
│                                                                 │
│  4. 关联 Vercel                                                  │
│     └─> link_vercel_github.py                                   │
│                                                                 │
│  5. 验证部署                                                     │
│     └─> verify_deployment.py                                    │
│                                                                 │
│  后续: git push → 自动部署                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
