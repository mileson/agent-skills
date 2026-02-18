#!/usr/bin/env python3
"""
域名可用性批量查询工具
通过 WHOIS 查询域名注册状态，生成 Markdown 格式报告
"""

import subprocess
import sys
import re
import argparse
from datetime import datetime

WHOIS_SERVERS = {
    ".com": "whois.verisign-grs.com",
    ".net": "whois.verisign-grs.com",
    ".org": "whois.pir.org",
    ".ai": "whois.nic.ai",
    ".io": "whois.nic.io",
    ".co": "whois.registry.co",
    ".dev": "whois.nic.google",
    ".app": "whois.nic.google",
    ".me": "whois.nic.me",
    ".cc": "ccwhois.verisign-grs.com",
    ".tv": "tvwhois.verisign-grs.com",
    ".xyz": "whois.nic.xyz",
    ".tech": "whois.nic.tech",
    ".online": "whois.nic.online",
    ".site": "whois.nic.site",
    ".store": "whois.nic.store",
    ".club": "whois.nic.club",
    ".info": "whois.afilias.net",
    ".biz": "whois.nic.biz",
    ".top": "whois.nic.top",
}

MAX_RETRIES = 2
TIMEOUT_SECONDS = 15

DEFAULT_SUFFIXES = [".com", ".ai", ".net", ".io", ".co"]
PREFERRED_SUFFIXES = {".com", ".ai"}

NOT_FOUND_PATTERNS = [
    "no match for",
    "not found",
    "no data found",
    "no entries found",
    "domain not found",
    "no object found",
    "nothing found",
    "status: free",
    "status: available",
    "% no matching objects",
    "is available for purchase",
]

EXPIRY_PATTERNS = [
    r"Registry Expiry Date:\s*(.+)",
    r"Expiration Date:\s*(.+)",
    r"Expiry Date:\s*(.+)",
    r"paid-till:\s*(.+)",
    r"Renewal Date:\s*(.+)",
    r"Expires On:\s*(.+)",
    r"Expiry date:\s*(.+)",
]


def _exec_whois(domain: str, server: str = None) -> str:
    """执行一次 WHOIS 查询，返回原始输出"""
    cmd = ["whois"]
    if server:
        cmd.extend(["-h", server])
    cmd.append(domain)
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
    return (proc.stdout or "") + (proc.stderr or "")


def _is_iana_referral(output: str) -> bool:
    """检测是否为 IANA 转介响应（macOS 默认 whois 行为）"""
    return "% iana whois server" in output.lower() and "refer:" in output.lower()


def _parse_output(output: str, result: dict) -> dict:
    """解析 WHOIS 输出，填充结果字典"""
    output_lower = output.lower()
    if any(p in output_lower for p in NOT_FOUND_PATTERNS):
        result["available"] = True
    elif "domain name:" in output_lower or "registrar:" in output_lower:
        result["available"] = False
        for pattern in EXPIRY_PATTERNS:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                result["expiry"] = parse_date(match.group(1).strip())
                break
    elif output.strip():
        result["available"] = False
    return result


def run_whois(domain: str, suffix: str) -> dict:
    """对单个域名执行 WHOIS 查询，含重试和降级逻辑"""
    result = {
        "domain": domain,
        "suffix": suffix,
        "available": None,
        "expiry": None,
        "error": None,
        "raw": "",
    }

    server = WHOIS_SERVERS.get(suffix)

    for attempt in range(MAX_RETRIES + 1):
        try:
            if attempt == 0 and server:
                output = _exec_whois(domain, server)
            elif attempt == 1 and server:
                import time; time.sleep(1)
                output = _exec_whois(domain, server)
            else:
                output = _exec_whois(domain)

            if _is_iana_referral(output):
                refer_match = re.search(r"refer:\s*(\S+)", output)
                if refer_match:
                    fallback_server = refer_match.group(1)
                    output = _exec_whois(domain, fallback_server)

            result["raw"] = output

            if not output.strip():
                if attempt < MAX_RETRIES:
                    continue
                result["error"] = "空响应"
                return result

            return _parse_output(output, result)

        except subprocess.TimeoutExpired:
            if attempt < MAX_RETRIES:
                continue
            result["error"] = "查询超时"
        except FileNotFoundError:
            result["error"] = "whois 命令未找到"
            return result
        except Exception as e:
            if attempt < MAX_RETRIES:
                continue
            result["error"] = str(e)

    return result


def parse_date(date_str: str) -> str:
    """尝试解析日期字符串为 YYYY-MM-DD 格式"""
    for fmt in [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d-%b-%Y",
        "%d/%m/%Y",
    ]:
        try:
            dt = datetime.strptime(date_str[:19].replace("T", " ").rstrip("Z"), fmt.replace("T", " ").rstrip("Z").rstrip("%z"))
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", date_str)
    if date_match:
        return date_match.group(1)
    return date_str[:10]


def generate_report(keyword: str, results: list) -> str:
    """生成 Markdown 格式的查询报告"""
    lines = []
    lines.append(f"## 🔍 域名查询结果: {keyword}\n")
    lines.append("| 后缀 | 域名 | 状态 | 推荐 | 备注 |")
    lines.append("|:---:|:-----|:----:|:----:|:-----|")

    available_preferred = []
    available_others = []

    for r in results:
        suffix = r["suffix"]
        domain = r["domain"]
        is_preferred = suffix in PREFERRED_SUFFIXES
        rec_label = "⭐ 优选" if is_preferred else "备选"

        if r["error"]:
            status = f"⚠️ {r['error']}"
            note = "-"
        elif r["available"]:
            status = "✅ 可注册"
            note = "-"
            if is_preferred:
                available_preferred.append(domain)
            else:
                available_others.append(domain)
        else:
            status = "❌ 已注册"
            note = f"到期: {r['expiry']}" if r["expiry"] else "已注册"

        lines.append(f"| {suffix} | {domain} | {status} | {rec_label} | {note} |")

    lines.append("")
    lines.append("### 📎 购买链接")
    lines.append(f"- **阿里云万网**: https://wanwang.aliyun.com/domain/searchresult/?keyword={keyword}")
    lines.append(f"- **Namecheap**: https://www.namecheap.com/domains/registration/results/?domain={keyword}.com")

    lines.append("")
    lines.append("### 💡 建议")
    if available_preferred:
        for d in available_preferred:
            lines.append(f"- **{d}** ⭐ 可注册，推荐优先购买")
    if available_others:
        others_str = " / ".join(available_others)
        lines.append(f"- {others_str} 作为备选")
    if not available_preferred and not available_others:
        lines.append(f"- 所有查询的后缀均已注册，建议尝试换个关键词或查看更多后缀")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="域名可用性批量查询工具")
    parser.add_argument("keyword", help="要查询的域名关键词（不含后缀）")
    parser.add_argument(
        "--suffixes", "-s",
        nargs="+",
        default=None,
        help=f"要查询的后缀列表（默认: {' '.join(DEFAULT_SUFFIXES)}）",
    )
    parser.add_argument(
        "--only", "-o",
        nargs="+",
        default=None,
        help="仅查询指定后缀",
    )

    args = parser.parse_args()
    keyword = args.keyword.lower().strip().split(".")[0]

    if args.only:
        suffixes = [s if s.startswith(".") else f".{s}" for s in args.only]
    elif args.suffixes:
        suffixes = [s if s.startswith(".") else f".{s}" for s in args.suffixes]
    else:
        suffixes = DEFAULT_SUFFIXES

    results = []
    for suffix in suffixes:
        domain = f"{keyword}{suffix}"
        sys.stderr.write(f"  查询 {domain} ...\n")
        r = run_whois(domain, suffix)
        results.append(r)

    print(generate_report(keyword, results))


if __name__ == "__main__":
    main()
