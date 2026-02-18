# TLD WHOIS 服务器列表

本文件列出 `check_domain.py` 脚本内置支持的 TLD 后缀及其对应的 WHOIS 服务器。

## 优选后缀（默认查询）

| 后缀 | WHOIS 服务器 | 注册局 | 备注 |
|:----:|:------------|:------|:-----|
| .com | whois.verisign-grs.com | Verisign | 最主流，全球通用 |
| .ai | whois.nic.ai | AI 注册局（安圭拉） | 科技/AI 领域首选，响应较慢 |
| .net | whois.verisign-grs.com | Verisign | 技术/网络领域常用 |
| .io | whois.nic.io | NIC.IO | 开发者/科技项目常用 |
| .co | whois.registry.co | .CO Internet SAS | 公司/商业简写 |

## 备选后缀

| 后缀 | WHOIS 服务器 | 注册局 | 备注 |
|:----:|:------------|:------|:-----|
| .org | whois.pir.org | PIR | 非营利/开源组织 |
| .dev | whois.nic.google | Google | 开发者专用（强制 HTTPS） |
| .app | whois.nic.google | Google | 应用类项目（强制 HTTPS） |
| .me | whois.nic.me | .ME Registry | 个人品牌/个人项目 |
| .cc | ccwhois.verisign-grs.com | Verisign | 短域名替代 |
| .tv | tvwhois.verisign-grs.com | Verisign | 视频/媒体领域 |
| .xyz | whois.nic.xyz | XYZ.COM LLC | 通用新顶级域名 |
| .tech | whois.nic.tech | Radix | 科技领域 |
| .online | whois.nic.online | Radix | 在线业务 |
| .site | whois.nic.site | Radix | 网站通用 |
| .store | whois.nic.store | Radix | 电商领域 |
| .club | whois.nic.club | .CLUB Domains | 社群/俱乐部 |
| .info | whois.afilias.net | Afilias | 信息类网站 |
| .biz | whois.nic.biz | Neustar | 商业网站 |
| .top | whois.nic.top | .TOP Registry | 通用新顶级域名 |

## WHOIS 未注册判定规则

不同 WHOIS 服务器返回"未注册"的关键词不同，脚本内置了以下匹配模式：

| 匹配关键词（不区分大小写） | 说明 |
|:--------------------------|:-----|
| `no match for` | Verisign 系列 |
| `not found` | 通用 |
| `no data found` | 部分注册局 |
| `no entries found` | 部分注册局 |
| `domain not found` | 通用 |
| `no object found` | 部分 RIPE/注册局 |
| `nothing found` | 通用 |
| `status: free` | 部分欧洲注册局 |
| `status: available` | 部分新 TLD |
| `% no matching objects` | RIPE 格式 |
| `is available for purchase` | 部分商业注册局 |

## 扩展方法

如需添加新后缀支持，编辑 `scripts/check_domain.py` 中的 `WHOIS_SERVERS` 字典：

```python
WHOIS_SERVERS = {
    ".新后缀": "whois.对应服务器.com",
    # ...
}
```

查找 WHOIS 服务器的方法：
1. 访问 https://www.iana.org/domains/root/db 查看 IANA 官方列表
2. 使用 `whois -h whois.iana.org .后缀` 查询
