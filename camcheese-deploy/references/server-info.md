# 服务器信息

## 连接

| 项目 | 值 |
|------|------|
| SSH | `ssh root@47.98.106.211` |
| 认证 | SSH key 已授权，无需密码 |
| 域名 | `camcheese.com` |
| 健康检查 | `https://camcheese.com/health` |

## 路径

| 路径 | 用途 |
|------|------|
| `/www/wwwroot/camcheese-backend` | 项目根目录 |
| `/www/wwwroot/camcheese-backend/.env` | 生产环境变量（不在 Git 中） |
| `/www/wwwroot/camcheese-backend/docker-compose.prod.yml` | 生产 Docker Compose |

## Docker 服务

| 服务名 | 容器名 | 说明 |
|--------|--------|------|
| api | posecam-api | FastAPI 后端 |
| celery_worker | — | Celery 工作进程 |
| celery_beat | — | Celery 定时任务 |
| flower | — | Celery 监控面板 |
| postgres | — | PostgreSQL 数据库 |
| redis | — | Redis 缓存 |

## 常用命令

```bash
# 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 查看 API 日志
docker logs posecam-api --tail=50

# 执行数据库迁移
docker exec posecam-api alembic upgrade head

# 重启单个服务
docker compose -f docker-compose.prod.yml restart api
```

## Git 仓库

- 远程: GitHub (`pose-cam`)
- 分支: `main`
- 同步方式: `git fetch origin main && git reset --hard origin/main`
