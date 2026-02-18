---
name: camcheese-deploy
description: |
  一键部署后端项目到 camcheese 生产服务器。通过 SSH 连接云端，执行代码同步、
  Docker 服务重启和健康检查，输出结构化部署报告。
  Use this skill when: (1) 用户说"部署"、"deploy"、"同步到云端"、"更新服务器",
  (2) 后端代码变更需要发布到生产环境, (3) 用户调用 /camcheese-deploy。
disable-model-invocation: true
allowed-tools: ["Bash", "Read"]
context: fork
---

# Camcheese Deploy

一键部署后端项目到云端生产服务器。

## 部署流程

### Step 1: 检查本地 Git 状态

```bash
git status
git log origin/main..HEAD --oneline
```

- 若有未提交变更或本地领先远程 → 调用 `/feature-git-commit` 自动提交并推送
- 若本地与远程一致 → 继续下一步

### Step 2: SSH 部署

执行以下命令序列（单条 SSH 连接完成）：

```bash
ssh root@47.98.106.211 << 'DEPLOY'
cd /www/wwwroot/camcheese-backend
echo "=== 拉取最新代码 ==="
git fetch origin main
git reset --hard origin/main

echo "=== 检查迁移文件 ==="
NEW_MIGRATIONS=$(git diff HEAD~1 --name-only | grep -c "alembic/versions/" || true)
if [ "$NEW_MIGRATIONS" -gt 0 ]; then
  echo "⚠️ 检测到 $NEW_MIGRATIONS 个新迁移文件"
fi

echo "=== 重启 Docker 服务 ==="
docker compose -f docker-compose.prod.yml stop api celery_worker celery_beat flower
docker compose -f docker-compose.prod.yml up -d api celery_worker celery_beat flower

echo "=== 等待服务启动 ==="
sleep 5

echo "=== 健康检查 ==="
curl -s -o /dev/null -w "%{http_code}" https://camcheese.com/health

echo ""
echo "=== 最近日志 ==="
docker logs posecam-api --tail=20
DEPLOY
```

### Step 3: 迁移处理

若 Step 2 检测到新迁移文件，提示用户确认后执行：

```bash
ssh root@47.98.106.211 "cd /www/wwwroot/camcheese-backend && docker exec posecam-api alembic upgrade head"
```

### Step 4: 输出部署报告

以结构化文本回复（不创建文件），格式：

```
## 部署结果

- 服务器: 47.98.106.211
- 项目: camcheese-backend
- 分支: main
- Commit: <最新 commit hash 前 7 位>
- 健康检查: ✅ 200 / ❌ <状态码>
- 迁移: 无新迁移 / ⚠️ 已执行 N 个迁移
- 服务状态: api ✅ | celery_worker ✅ | celery_beat ✅ | flower ✅
```

## 服务器信息

详细服务器配置见 [references/server-info.md](references/server-info.md)。

## 异常处理

- **SSH 连接失败** → 检查网络和 SSH key 配置
- **健康检查非 200** → 查看 `docker logs posecam-api --tail=50` 定位问题
- **Docker 启动失败** → 执行 `docker compose -f docker-compose.prod.yml ps` 检查状态
