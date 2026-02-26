#!/usr/bin/env python3
"""iOS Internal Release 资料收敛工具（本地优先 + memory 回写）。"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REQUIRED_KEYS = ["ASC_ISSUER_ID", "ASC_KEY_FILEPATH"]

TRACKED_KEYS = [
    "ASC_KEY_ID",
    "ASC_ISSUER_ID",
    "ASC_KEY_FILEPATH",
    "ASC_KEY_IS_BASE64",
    "TESTER_EMAILS",
    "INTERNAL_GROUP_NAME",
    "IOS_WORKSPACE",
    "IOS_SCHEME",
    "IOS_APP_IDENTIFIER",
    "XCODEPROJ_PATH",
    "APPLE_ID",
    "TEAM_ID",
]

DISPLAY_KEYS = [k for k in TRACKED_KEYS if k != "ASC_KEY_ID"]

DEFAULTS = {
    "INTERNAL_GROUP_NAME": "Agent Internal Testing",
    "ASC_KEY_IS_BASE64": "false",
}

SENSITIVE_KEYS = {
    "ASC_KEY_ID",
    "ASC_ISSUER_ID",
    "ASC_KEY_FILEPATH",
    "TESTER_EMAILS",
    "APPLE_ID",
}

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

HELP_BY_FIELD = {
    "ASC_KEY_FILEPATH": [
        "进入 App Store Connect -> Users and Access -> Integrations -> App Store Connect API，在 Team Keys 标签下操作。",
        "点击 Active 旁边的加号（+），输入名称（例如 Agent Internal Testing）。",
        "在 Access 中选择 App Manager 并点击生成。",
        "生成后在对应行点击下载按钮获取 .p8 文件（仅下载一次），然后填写该文件绝对路径。",
        "推荐文件名保持 AuthKey_<KEY_ID>.p8，便于自动推导 ASC_KEY_ID。",
    ],
    "ASC_ISSUER_ID": [
        "进入 App Store Connect -> Users and Access -> Integrations -> App Store Connect API，在 Team Keys 标签下操作。",
        "在 Team Keys 标签上方复制 Issuer ID（UUID）。",
        "将完整 UUID 填入 ASC_ISSUER_ID。",
    ],
}

REQUEST_FIELDS_IN_ORDER = ["ASC_KEY_FILEPATH", "ASC_ISSUER_ID", "TESTER_EMAILS"]


def now_iso() -> str:
    return dt.datetime.now().replace(microsecond=0).isoformat()


def mask_value(key: str, value: str) -> str:
    if not value:
        return ""
    if key not in SENSITIVE_KEYS:
        return value
    if key == "ASC_KEY_FILEPATH":
        p = Path(value)
        return str(p.parent / ("***" + p.name[-10:])) if p.name else "***"
    if "@" in value:
        name, domain = value.split("@", 1)
        return (name[:2] + "***@" + domain) if len(name) >= 2 else "***@" + domain
    if len(value) <= 6:
        return "***"
    return value[:2] + "***" + value[-2:]


def run_cmd(cmd: list[str], cwd: Path | None = None) -> str:
    try:
        out = subprocess.check_output(cmd, cwd=str(cwd) if cwd else None, stderr=subprocess.DEVNULL, text=True)
        return out.strip()
    except Exception:
        return ""


def parse_email_list(raw: str) -> List[str]:
    if not raw:
        return []
    parts = re.split(r"[,;\s]+", raw.strip())
    emails: List[str] = []
    seen = set()
    for part in parts:
        email = part.strip()
        if not email:
            continue
        if not EMAIL_RE.match(email):
            continue
        lower = email.lower()
        if lower in seen:
            continue
        seen.add(lower)
        emails.append(email)
    return emails


def merge_email_lists(*raw_lists: str) -> str:
    merged: List[str] = []
    seen = set()
    for raw in raw_lists:
        for email in parse_email_list(raw):
            lower = email.lower()
            if lower in seen:
                continue
            seen.add(lower)
            merged.append(email)
    return ",".join(merged)


def parse_set_values(pairs: list[str]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"--set 参数格式错误（应为 KEY=VALUE）: {pair}")
        key, value = pair.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"--set 参数 KEY 为空: {pair}")
        result[key] = value.strip()
    return result


def derive_key_id_from_key_filepath(key_filepath: str) -> str:
    """从 AuthKey_<KEY_ID>.p8 文件名提取 ASC_KEY_ID。"""
    if not key_filepath:
        return ""
    base = Path(key_filepath).name
    # Apple 官方下载文件名通常为 AuthKey_<KEYID>.p8
    m = re.match(r"^AuthKey_([A-Za-z0-9]+)\.p8$", base, flags=re.IGNORECASE)
    if m:
        return m.group(1)
    return ""


def extract_newbie_guide_section_one(skill_root: Path) -> List[str]:
    """提取 newbie-guide.md 的“1. 获取 ASC_KEY_ID/ASC_ISSUER_ID/ASC_KEY_FILEPATH”章节。"""
    guide = skill_root / "references" / "newbie-guide.md"
    fallback = [
        "## 1. 获取 `ASC_KEY_ID`、`ASC_ISSUER_ID`、`ASC_KEY_FILEPATH`",
        "",
        "### Step 1: 进入 Team Keys 页面",
        "1. 打开 App Store Connect。",
        "2. 进入 `Users and Access` -> `Integrations` -> `App Store Connect API` -> `Team Keys`。",
        "",
        "### Step 2: 创建 Key（如果还没有）",
        "1. 点击 `Active` 旁边的 `+` 新建 Key。",
        "2. `Access` 选择 `App Manager`。",
        "3. 下载 `.p8` 文件并记录保存路径（仅下载一次）。",
        "",
        "### Step 3: 对应三个字段",
        "1. `ASC_KEY_FILEPATH`：`.p8` 文件绝对路径。",
        "2. `ASC_ISSUER_ID`：复制 Team Keys 页面上方 Issuer ID（UUID）。",
        "3. `ASC_KEY_ID`：默认由 `ASC_KEY_FILEPATH` 文件名 `AuthKey_<KEY_ID>.p8` 自动推导。",
    ]
    if not guide.exists():
        return fallback

    lines = guide.read_text(encoding="utf-8", errors="ignore").splitlines()
    start = None
    end = None
    for idx, line in enumerate(lines):
        if re.match(r"^##\s+1\.\s*获取", line.strip()):
            start = idx
            continue
        if start is not None and re.match(r"^##\s+", line.strip()):
            end = idx
            break
    if start is None:
        return fallback

    section = lines[start:end] if end is not None else lines[start:]
    while section and not section[0].strip():
        section.pop(0)
    while section and not section[-1].strip():
        section.pop()
    return section or fallback


def detect_workspace(project_root: Path) -> str:
    items = sorted(project_root.glob("*.xcworkspace"))
    return items[0].name if items else ""


def detect_xcodeproj(project_root: Path) -> str:
    items = sorted(project_root.glob("*.xcodeproj"))
    return items[0].name if items else ""


def detect_scheme(project_root: Path, workspace_name: str, preferred: str = "") -> str:
    if not workspace_name:
        return ""
    workspace_path = project_root / workspace_name
    raw = run_cmd(["xcodebuild", "-list", "-json", "-workspace", str(workspace_path)])
    if not raw:
        return ""
    try:
        data = json.loads(raw)
        schemes = data.get("workspace", {}).get("schemes") or []
        if not schemes:
            return ""
        if preferred:
            p = preferred.strip().lower()
            for s in schemes:
                if s.lower() == p:
                    return s
        return schemes[0]
    except Exception:
        return ""


def parse_appfile(appfile: Path) -> Dict[str, str]:
    if not appfile.exists():
        return {}
    text = appfile.read_text(encoding="utf-8", errors="ignore")
    values: Dict[str, str] = {}

    m = re.search(r'^\s*app_identifier\s+"([^"]+)"', text, re.MULTILINE)
    if m:
        values["IOS_APP_IDENTIFIER"] = m.group(1).strip()

    m = re.search(r'^\s*team_id\s+"([^"]+)"', text, re.MULTILINE)
    if m:
        values["TEAM_ID"] = m.group(1).strip()

    # apple_id "xx@xx.com" 或 apple_id ENV.fetch("APPLE_ID", "xx@xx.com")
    m = re.search(r'^\s*apple_id\s+"([^"]+)"', text, re.MULTILINE)
    if m:
        values["APPLE_ID"] = m.group(1).strip()
    else:
        m = re.search(r'^\s*apple_id\s+ENV\.fetch\("APPLE_ID",\s*"([^"]+)"\)', text, re.MULTILINE)
        if m:
            values["APPLE_ID"] = m.group(1).strip()

    return values


def detect_local_values(project_root: Path) -> Dict[str, str]:
    appfile_values = parse_appfile(project_root / "fastlane" / "Appfile")
    workspace = detect_workspace(project_root)
    xcodeproj = detect_xcodeproj(project_root)
    preferred = ""
    if workspace:
        preferred = workspace.removesuffix(".xcworkspace")
    elif xcodeproj:
        preferred = xcodeproj.removesuffix(".xcodeproj")
    scheme = detect_scheme(project_root, workspace, preferred=preferred)
    git_email = run_cmd(["git", "config", "user.email"], cwd=project_root)

    tester_candidates = merge_email_lists(git_email, appfile_values.get("APPLE_ID", ""))
    tester_primary = parse_email_list(tester_candidates)[0] if tester_candidates else ""

    values = {
        "IOS_WORKSPACE": workspace,
        "XCODEPROJ_PATH": xcodeproj,
        "IOS_SCHEME": scheme,
        "TESTER_EMAILS": tester_primary,
        "TESTER_EMAILS_CANDIDATES": tester_candidates,
    }
    values.update(appfile_values)
    return {k: v for k, v in values.items() if v}


def load_memory(memory_file: Path) -> Dict:
    if not memory_file.exists():
        return {"schema_version": 1, "projects": {}}
    try:
        return json.loads(memory_file.read_text(encoding="utf-8"))
    except Exception:
        return {"schema_version": 1, "projects": {}}


def save_memory(memory_file: Path, data: Dict) -> None:
    memory_file.parent.mkdir(parents=True, exist_ok=True)
    memory_file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_memory_md(memory_md_path: Path, memory_json: Dict) -> None:
    lines = [
        "# iOS TestFlight Remote Release Memory",
        "",
        "> 说明：本文件为人类可读视图；机器读写以 `memory.json` 为准。",
        "",
    ]
    projects = memory_json.get("projects", {})
    if not projects:
        lines.extend(
            [
                "## 最近项目记录",
                "",
                "当前暂无记录。首次执行 `resolve_materials.py --write-memory` 后自动生成。",
                "",
            ]
        )
    else:
        for project_root, item in projects.items():
            values = item.get("values", {})
            lines.extend([f"## Project: `{project_root}`", "", f"- updated_at: `{item.get('updated_at', '')}`"])
            for key in TRACKED_KEYS:
                val = values.get(key, "")
                if val:
                    lines.append(f"- {key}: `{mask_value(key, str(val))}`")
            lines.append("")
    memory_md_path.write_text("\n".join(lines), encoding="utf-8")


def resolve_values(
    explicit: Dict[str, str],
    env_values: Dict[str, str],
    local_values: Dict[str, str],
    memory_values: Dict[str, str],
) -> Tuple[Dict[str, str], Dict[str, str]]:
    resolved: Dict[str, str] = {}
    source: Dict[str, str] = {}
    for key in TRACKED_KEYS:
        if key in explicit and explicit[key]:
            resolved[key] = explicit[key]
            source[key] = "explicit"
            continue
        env_v = env_values.get(key, "")
        if env_v:
            resolved[key] = env_v
            source[key] = "env"
            continue
        local_v = local_values.get(key, "")
        if local_v:
            resolved[key] = local_v
            source[key] = "local"
            continue
        mem_v = memory_values.get(key, "")
        if mem_v:
            resolved[key] = mem_v
            source[key] = "memory"
            continue
        default_v = DEFAULTS.get(key, "")
        if default_v:
            resolved[key] = default_v
            source[key] = "default"
            continue
        resolved[key] = ""
        source[key] = "missing"

    # 补充推导：若 ASC_KEY_ID 缺失，尝试从 ASC_KEY_FILEPATH 文件名推导
    if not resolved.get("ASC_KEY_ID"):
        derived_key_id = derive_key_id_from_key_filepath(resolved.get("ASC_KEY_FILEPATH", ""))
        if derived_key_id:
            resolved["ASC_KEY_ID"] = derived_key_id
            source["ASC_KEY_ID"] = "derived_from_key_filepath"
    return resolved, source


def print_scan(
    project_root: Path,
    skill_root: Path,
    resolved: Dict[str, str],
    source: Dict[str, str],
    tester_candidates: str,
) -> None:
    missing_required = [k for k in REQUIRED_KEYS if not resolved.get(k)]
    newbie_section = extract_newbie_guide_section_one(skill_root)
    tester_source = source.get("TESTER_EMAILS", "missing")
    tester_needs_confirm = tester_source in {"local", "memory"}

    print("# Materials Scan")
    print(f"- project_root: `{project_root}`")
    print("")

    print("## 1) 字段扫描总览")
    print("| 字段 | 状态 | 值(掩码) | 来源 |")
    print("|---|---|---|---|")
    for key in DISPLAY_KEYS:
        value = resolved.get(key, "")
        status = "OK" if value else "MISSING"
        print(f"| `{key}` | {status} | `{mask_value(key, value)}` | `{source.get(key, '')}` |")
    print("")

    print("## 2) 缺失必填项（固定顺序）")
    if missing_required:
        for key in missing_required:
            print(f"- {key}")
    else:
        print("- 无")
    print("")

    print("## 3) 缺失项获取教程（固定结构）")
    print("### 新手指引第 1 节（内嵌，可直接照做）")
    for line in newbie_section:
        print(line)
    if missing_required:
        print("")
        print("| 缺失字段 | 获取步骤（固定） |")
        print("|---|---|")
        for key in missing_required:
            steps = HELP_BY_FIELD.get(key, ["请参考新手教程中的对应章节。"])
            joined = "<br>".join([f"{idx + 1}. {step}" for idx, step in enumerate(steps)])
            print(f"| `{key}` | {joined} |")
    else:
        print("- 当前无必填项缺失。")
    print("")

    print("## 4) 一次性回复模板（含教程内容摘录）")
    print("请按以下顺序一次性回复，避免多轮补充：")
    print("")
    for field in REQUEST_FIELDS_IN_ORDER:
        print(f"- `{field}`：")
        if field == "TESTER_EMAILS":
            print("  1) 提供用于 Internal Testing 的邮箱（可多个，逗号分隔）。")
            print("  2) 建议与手机 TestFlight 当前登录 Apple ID 一致。")
            print(f"  3) 当前候选：`{tester_candidates or 'you@example.com'}`。")
            continue
        steps = HELP_BY_FIELD.get(field, [])
        for idx, step in enumerate(steps):
            print(f"  {idx + 1}) {step}")
    print("")
    print("可直接复制以下模板填写：")
    print("```text")
    print("ASC_KEY_FILEPATH=<绝对路径，例如 /Users/you/Downloads/AuthKey_XXXXXX.p8>")
    print("ASC_ISSUER_ID=<Issuer ID(UUID)>")
    print(f"TESTER_EMAILS=<{tester_candidates or 'you@example.com'}>")
    print("```")
    print("")

    print("## 5) Tester 邮箱确认状态（固定结构）")
    print(f"- 当前 TESTER_EMAILS: `{mask_value('TESTER_EMAILS', resolved.get('TESTER_EMAILS', ''))}`")
    print(f"- 来源: `{tester_source}`")
    print(f"- 本地候选: `{tester_candidates or '<none>'}`")
    print(f"- 是否必须用户显式确认: `{'YES' if tester_needs_confirm else 'NO'}`")
    print("")

    print("## 6) 使用提示（固定结构）")
    print("- 已内嵌新手指引第 1 节步骤，按上文执行即可。")
    print("- `ASC_KEY_ID` 默认由 `ASC_KEY_FILEPATH` 自动推导，不需要单独提供。")
    print("- 若 `.p8` 文件名不是 `AuthKey_<KEY_ID>.p8`，请先改名后重试。")


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve internal release materials with local-first strategy.")
    parser.add_argument("--project-root", default=os.getcwd(), help="iOS 项目根目录")
    parser.add_argument("--memory-file", default="", help="自定义 memory.json 路径（默认 data/memory.json）")
    parser.add_argument("--set", action="append", default=[], help="手动注入 KEY=VALUE，可重复")
    parser.add_argument("--scan", action="store_true", help="输出扫描表")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--print-export", action="store_true", help="输出 export 语句")
    parser.add_argument("--write-memory", action="store_true", help="将解析结果回写 memory")
    args = parser.parse_args()

    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.exists():
        print(f"[ERROR] project root 不存在: {project_root}", file=sys.stderr)
        return 2

    explicit = parse_set_values(args.set)
    env_values = {k: os.getenv(k, "") for k in TRACKED_KEYS}
    local_values = detect_local_values(project_root)

    skill_root = Path(__file__).resolve().parents[1]
    memory_json_path = Path(args.memory_file).expanduser().resolve() if args.memory_file else (skill_root / "data" / "memory.json")
    memory_md_path = memory_json_path.with_name("memory.md")

    memory_all = load_memory(memory_json_path)
    projects = memory_all.setdefault("projects", {})
    project_key = str(project_root)
    memory_values = projects.get(project_key, {}).get("values", {})

    resolved, source = resolve_values(explicit, env_values, local_values, memory_values)

    if args.write_memory:
        values_to_save = {k: v for k, v in resolved.items() if v}
        projects[project_key] = {"updated_at": now_iso(), "values": values_to_save}
        save_memory(memory_json_path, memory_all)
        render_memory_md(memory_md_path, memory_all)

    tester_candidates = merge_email_lists(
        explicit.get("TESTER_EMAILS", ""),
        env_values.get("TESTER_EMAILS", ""),
        local_values.get("TESTER_EMAILS_CANDIDATES", ""),
        memory_values.get("TESTER_EMAILS", ""),
    )

    if args.scan:
        print_scan(project_root, skill_root, resolved, source, tester_candidates)

    if args.print_export:
        for key in TRACKED_KEYS:
            value = resolved.get(key, "")
            if value:
                safe = value.replace('"', '\\"')
                print(f'export {key}="{safe}"')
        tester_source = source.get("TESTER_EMAILS", "")
        if tester_source:
            print(f'export TESTER_EMAILS_SOURCE="{tester_source}"')
        if tester_candidates:
            safe_candidates = tester_candidates.replace('"', '\\"')
            print(f'export TESTER_EMAILS_CANDIDATES="{safe_candidates}"')

    if args.json:
        print(json.dumps({"resolved": resolved, "source": source}, ensure_ascii=False, indent=2))

    missing_required = [k for k in REQUIRED_KEYS if not resolved.get(k)]
    if missing_required:
        print(f"[WARN] 缺失必填项: {', '.join(missing_required)}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
