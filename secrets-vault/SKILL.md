---
name: secrets-vault
description: |
  通用敏感信息保险库，集中管理 API 密钥、个人信息、第三方服务凭证等敏感数据。
  所有敏感数据存储在 skill 目录的 data/vault.yaml，其他 skill 通过调用 get_secret.py 脚本获取凭证。
  This skill should be used when any other skill needs to retrieve API keys,
  tokens, personal information, or any sensitive credentials. Triggers:
  (1) Other skills need API credentials (e.g. github, vercel, supabase),
  (2) Need to store or manage sensitive configuration,
  (3) Need personal information like name/email for content authoring.
user-invocable: false
---

# Secrets Vault

集中管理所有敏感信息的通用保险库。其他 skill 通过脚本调用获取凭证，永不在 skill 代码中存储敏感数据。

## 目录结构

```
~/.claude/skills/secrets-vault/
├── data/
│   ├── vault.yaml     # 所有凭证（YAML 格式）- Git 忽略
│   └── .gitignore     # 防止 data/ 被提交
├── scripts/
│   ├── get_secret.py      # 读取凭证（供其他 skill 调用）
│   └── manage_secrets.py  # 管理凭证
├── vault.yaml.example     # 示例文件（供参考）
└── SKILL.md
```

## 支持的命名空间

| 命名空间 | 用途 | 必需字段 |
|---------|------|---------|
| `github` | GitHub 仓库操作 | token, username |
| `vercel` | Vercel 部署 | token, team_id(可选) |
| `<project>_supabase` | Supabase 后端 (按项目命名) | project_id, url, anon_key, service_role_key, database_url |
| `x_oauth` | X/Twitter 登录 | client_id, client_secret, callback_url |
| `wechat_mp` | 微信公众号 | app_id, app_secret |
| `personal` | 个人信息 | name, email |
| `apimart_image` | APIMart 生图服务 | api_url, api_token, model, task_status_url |
| `openrouter_image` | OpenRouter 生图服务 | api_url, api_key, model |

**命名规范**: 多项目时使用 `<project_name>_<service>` 格式区分，如 `molthands_supabase`

## 首次配置

### 方式1: 使用脚本初始化

```bash
# 初始化 vault
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py init

# 逐个添加凭证
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set github token "ghp_xxxx"
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set github username "your_username"
python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py set vercel token "xxxx"
```

### 方式2: 复制示例文件

```bash
# 复制示例文件
cp ~/.claude/skills/secrets-vault/vault.yaml.example ~/.claude/skills/secrets-vault/data/vault.yaml

# 编辑填入真实凭证
vim ~/.claude/skills/secrets-vault/data/vault.yaml
```

## 读取凭证（其他 skill 调用）

```bash
# 获取整个命名空间（JSON 输出）
python3 ~/.claude/skills/secrets-vault/scripts/get_secret.py github
# → {"token": "ghp...", "username": "xxx", "default_visibility": "private"}

# 获取指定字段（字符串输出）
python3 ~/.claude/skills/secrets-vault/scripts/get_secret.py github token
# → ghp_xxxx
```

在 Python 脚本中调用：

```python
import subprocess, json

def get_secret(namespace: str, key: str = None):
    """从 secrets-vault 获取凭证"""
    script = "~/.claude/skills/secrets-vault/scripts/get_secret.py"
    cmd = ["python3", os.path.expanduser(script), namespace]
    if key:
        cmd.append(key)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to get secret: {result.stderr}")
    return json.loads(result.stdout) if not key else result.stdout.strip()

# 使用示例
github_creds = get_secret("github")  # {"token": "...", "username": "..."}
token = get_secret("github", "token")  # "ghp_xxx"
```

## 管理凭证

```bash
MANAGE="python3 ~/.claude/skills/secrets-vault/scripts/manage_secrets.py"

$MANAGE init                              # 初始化 vault
$MANAGE list                              # 列出所有命名空间（脱敏显示）
$MANAGE get github                        # 查看指定命名空间（脱敏）
$MANAGE set github token ghp_xxx          # 设置 key-value
$MANAGE remove old_service                # 删除命名空间
$MANAGE remove-key github old_field       # 删除指定 key
```

## Git 安全

- `data/.gitignore` 阻止 vault.yaml 被提交
- `vault.yaml.example` 提供示例供参考
- 如需共享配置，请使用示例文件

## 安全规则

1. **权限控制**: `data/` 目录权限 700，`vault.yaml` 文件权限 600
2. **Git 忽略**: `data/.gitignore` 阻止敏感文件被追踪
3. **脚本访问**: 所有 skill 仅通过 `get_secret.py` 读取，禁止直接读取 vault.yaml
4. **脱敏显示**: 管理操作的 `list`/`get` 命令自动脱敏显示
5. **Token 轮换**: 定期更换 API Token 和密钥
6. **最小权限**: Token 仅授予必要的权限
