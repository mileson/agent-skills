---
name: secrets-vault
description: |
  通用敏感信息保险库，集中管理 API 密钥、个人信息、第三方服务凭证等敏感数据。
  所有敏感数据存储在 ~/.secrets/vault.yaml（与 skill 目录完全隔离），
  其他 skill 通过调用 get_secret.py 脚本获取凭证，实现安全解耦。
  This skill should be used when any other skill needs to retrieve API keys,
  tokens, personal information, or any sensitive credentials. Triggers:
  (1) Other skills need API credentials (e.g. wechat_mp, aliyun_oss, openai),
  (2) Need to store or manage sensitive configuration,
  (3) Need personal information like name/email for content authoring.
user-invocable: false
---

# Secrets Vault

集中管理所有敏感信息的通用保险库。其他 skill 通过脚本调用获取凭证，永不在 skill 代码中存储敏感数据。

## 存储结构

```
~/.secrets/
├── vault.yaml     # 所有凭证（YAML 格式，命名空间自由定义）
└── .gitignore     # 防止误提交
```

`vault.yaml` 顶层 key = 命名空间，随用随加：

```yaml
wechat_mp:
  app_id: "wx..."
  app_secret: "..."
aliyun_oss:
  access_key_id: "..."
  access_key_secret: "..."
  bucket: "my-bucket"
  endpoint: "oss-cn-hangzhou.aliyuncs.com"
personal:
  name: "你的名字"
  email: "you@example.com"
openai:
  api_key: "sk-..."
```

## 读取凭证（其他 skill 调用）

```bash
# 获取整个命名空间（JSON 输出）
python3 ~/.cursor/skills/secrets-vault/scripts/get_secret.py wechat_mp
# → {"app_id": "wx...", "app_secret": "..."}

# 获取指定字段（字符串输出）
python3 ~/.cursor/skills/secrets-vault/scripts/get_secret.py personal name
# → 你的名字
```

在 Python 脚本中调用：

```python
import subprocess, json
result = subprocess.run(
    ["python3", os.path.expanduser("~/.cursor/skills/secrets-vault/scripts/get_secret.py"), "wechat_mp"],
    capture_output=True, text=True
)
creds = json.loads(result.stdout)  # {"app_id": "...", "app_secret": "..."}
```

## 管理凭证

```bash
MANAGE="python3 ~/.cursor/skills/secrets-vault/scripts/manage_secrets.py"
$MANAGE init                              # 首次初始化 vault
$MANAGE list                              # 列出所有命名空间（脱敏显示）
$MANAGE get wechat_mp                     # 查看指定命名空间（脱敏）
$MANAGE set wechat_mp app_id wx123        # 设置 key-value
$MANAGE remove old_service                # 删除命名空间
$MANAGE remove-key wechat_mp old_field    # 删除指定 key
```

## 首次配置

首次使用前须初始化 vault，详见 [references/setup-guide.md](references/setup-guide.md)。

## 安全规则

1. `~/.secrets/` 目录权限 700，`vault.yaml` 文件权限 600
2. `.gitignore` 阻止一切文件被 Git 追踪
3. 所有 skill 仅通过 `get_secret.py` 读取，禁止直接读取 `vault.yaml`
4. 管理操作的 `list`/`get` 命令自动脱敏显示
