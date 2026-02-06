# Secrets Vault 配置指南

## 首次初始化

```bash
python3 ~/.cursor/skills/secrets-vault/scripts/manage_secrets.py init
```

此命令会：
1. 创建 `~/.secrets/` 目录（权限 700）
2. 创建 `vault.yaml` 模板文件（权限 600）
3. 创建 `.gitignore` 防止误提交

## 添加凭证

### 方式一：命令行设置

```bash
MANAGE="python3 ~/.cursor/skills/secrets-vault/scripts/manage_secrets.py"

# 微信公众号
$MANAGE set wechat_mp app_id "your_app_id"
$MANAGE set wechat_mp app_secret "your_app_secret"

# 阿里云 OSS
$MANAGE set aliyun_oss access_key_id "your_key_id"
$MANAGE set aliyun_oss access_key_secret "your_key_secret"
$MANAGE set aliyun_oss bucket "your-bucket"
$MANAGE set aliyun_oss endpoint "oss-cn-hangzhou.aliyuncs.com"

# 个人信息
$MANAGE set personal name "你的名字"
$MANAGE set personal email "you@example.com"
```

### 方式二：直接编辑 YAML

```bash
# 用编辑器打开（推荐 vim/nano，避免在 IDE 中打开以防泄露）
vim ~/.secrets/vault.yaml
```

## 命名空间约定

命名空间无固定规则，建议：

| 模式 | 示例 | 说明 |
|:-----|:-----|:-----|
| 服务名 | `openai`, `github` | 单一服务 |
| 服务_产品 | `wechat_mp`, `aliyun_oss` | 同一厂商多产品 |
| 分类 | `personal`, `work` | 非服务类信息 |

## 依赖

- Python 3.6+
- pyyaml: `pip install pyyaml`

## 安全注意事项

1. **切勿** 将 `~/.secrets/` 目录加入任何 Git 仓库
2. **切勿** 在聊天记录中粘贴完整的 API Key
3. 定期检查 `vault.yaml` 权限：`ls -la ~/.secrets/vault.yaml`（应显示 `-rw-------`）
4. 如怀疑凭证泄露，立即到对应平台重置
