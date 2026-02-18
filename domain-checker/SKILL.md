---
name: domain-checker
description: |
  Domain availability checker via WHOIS with purchase links for Aliyun and Namecheap.
  Use this skill when the user asks to check if a domain name is available, search for
  domain registration status, find purchasable domains, or query domain expiry dates.
  Triggers: "查域名", "域名能不能注册", "domain available", "查一下 xxx 域名",
  "帮我找个域名", "xxx.com 还能买吗", "domain check".
---

# Domain Checker

通过 WHOIS 查询域名可注册性，生成含阿里云 / Namecheap 购买链接的 Markdown 报告。

## Workflow

```
1. 从用户请求中提取关键词（如 "zeuxis"、"apelles"）
2. 运行 check_domain.py 查询各后缀状态
3. 将脚本输出（Markdown 表格）直接展示给用户
4. 如用户需购买，引导点击购买链接
```

## Usage

```bash
# 默认查 .com .ai .net .io .co
python3 ~/.cursor/skills/domain-checker/scripts/check_domain.py <关键词>

# 仅查指定后缀
python3 ~/.cursor/skills/domain-checker/scripts/check_domain.py <关键词> --only .com .ai

# 追加额外后缀
python3 ~/.cursor/skills/domain-checker/scripts/check_domain.py <关键词> --suffixes .com .ai .net .io .co .org .dev
```

**输入**: 域名关键词（不含后缀），如 `zeuxis`
**输出**: Markdown 报告（stdout），含状态表格 + 购买链接 + 推荐建议

### Output Example

```
## 🔍 域名查询结果: zeuxis

| 后缀 | 域名 | 状态 | 推荐 | 备注 |
|:---:|:-----|:----:|:----:|:-----|
| .com | zeuxis.com | ❌ 已注册 | ⭐ 优选 | 到期: 2026-08-06 |
| .ai | zeuxis.ai | ❌ 已注册 | ⭐ 优选 | 到期: 2026-12-04 |
| .net | zeuxis.net | ❌ 已注册 | 备选 | 到期: 2026-10-31 |
| .io | zeuxis.io | ✅ 可注册 | 备选 | - |
| .co | zeuxis.co | ✅ 可注册 | 备选 | - |

### 📎 购买链接
- **阿里云万网**: https://wanwang.aliyun.com/domain/searchresult/?keyword=zeuxis
- **Namecheap**: https://www.namecheap.com/domains/registration/results/?domain=zeuxis.com

### 💡 建议
- zeuxis.io / zeuxis.co 作为备选
```

## Key Rules

- `.com` 和 `.ai` 始终标记为 **⭐ 优选**，其他为 **备选**
- 默认查 5 个后缀：`.com` `.ai` `.net` `.io` `.co`
- 每个 WHOIS 查询超时 15s，自动重试最多 2 次
- `.dev` / `.app` (Google TLD) 的 WHOIS 在部分网络不可用，按需查询
- 如用户输入含后缀（如 `apelles.ai`），自动提取关键词部分

## Prerequisites

- Python 3.7+ 和 `whois` 命令（macOS/Linux 自带）
- 无需 API Key

## References

- **TLD WHOIS 服务器列表**: [tld-whois-servers.md](references/tld-whois-servers.md)
- 如需添加新后缀，编辑 `scripts/check_domain.py` 中的 `WHOIS_SERVERS` 字典
