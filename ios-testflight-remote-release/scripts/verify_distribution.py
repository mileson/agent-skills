#!/usr/bin/env python3
"""发布后校验：通过 assign_internal_tester lane 做幂等校验与补齐。"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


def extract_fastlane_version(raw: str) -> str:
    for line in raw.splitlines():
        match = re.match(r"^fastlane (\d+\.\d+\.\d+)$", line.strip())
        if match:
            return match.group(1)
    match = re.search(r"You are on (\d+\.\d+\.\d+)", raw)
    if match:
        return match.group(1)
    return ""


def semver_ge(current: str, minimum: str) -> bool:
    try:
        c = tuple(int(x) for x in current.split("."))
        m = tuple(int(x) for x in minimum.split("."))
        return c >= m
    except Exception:
        return False


def run_cmd_version(cmd: list[str], cwd: Path, env: dict[str, str]) -> str:
    try:
        out = subprocess.check_output(cmd + ["--version"], cwd=cwd, env=env, text=True, stderr=subprocess.STDOUT)
        return extract_fastlane_version(out)
    except Exception:
        return ""


def prepend_homebrew_ruby_gem_bin(env: dict[str, str]) -> dict[str, str]:
    ruby_gem = Path("/opt/homebrew/opt/ruby/bin/gem")
    if not ruby_gem.exists():
        return env

    try:
        out = subprocess.check_output([str(ruby_gem), "env"], text=True, stderr=subprocess.STDOUT)
    except Exception:
        return env

    gem_bin = ""
    for line in out.splitlines():
        if "EXECUTABLE DIRECTORY" in line and ": " in line:
            gem_bin = line.split(": ", 1)[1].strip()
            break
    if not gem_bin:
        return env

    current_path = env.get("PATH", "")
    path_parts = current_path.split(":") if current_path else []
    if gem_bin not in path_parts:
        env["PATH"] = f"{gem_bin}:{current_path}" if current_path else gem_bin
    return env


def parse_export_lines(raw: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("export "):
            continue
        payload = line[len("export ") :]
        key, sep, value = payload.partition("=")
        if not sep:
            continue
        key = key.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        parsed[key] = value
    return parsed


def hydrate_materials_env(project_root: Path, env: dict[str, str]) -> dict[str, str]:
    required = ["ASC_KEY_ID", "ASC_ISSUER_ID", "ASC_KEY_FILEPATH"]
    if all(env.get(k, "").strip() for k in required):
        return env

    resolver = Path(__file__).with_name("resolve_materials.py")
    if not resolver.exists():
        return env

    try:
        out = subprocess.check_output(
            [sys.executable, str(resolver), "--project-root", str(project_root), "--print-export"],
            cwd=project_root,
            env=env,
            text=True,
            stderr=subprocess.STDOUT,
        )
    except Exception:
        return env

    parsed = parse_export_lines(out)
    hydrated = env.copy()
    for key in required:
        if not hydrated.get(key, "").strip() and parsed.get(key, "").strip():
            hydrated[key] = parsed[key].strip()
    return hydrated


def resolve_fastlane_cmd(project_root: Path, min_fastlane_version: str, env: dict[str, str]) -> list[str]:
    pinned_cmd = env.get("SKILL_FASTLANE_CMD", "").strip()
    if pinned_cmd:
        return shlex.split(pinned_cmd)

    if (project_root / "Gemfile").exists() and shutil.which("bundle"):
        bundle_cmd = ["bundle", "exec", "fastlane"]
        bundle_ver = run_cmd_version(bundle_cmd, project_root, env)
        if semver_ge(bundle_ver, min_fastlane_version):
            return bundle_cmd

    return ["fastlane", f"_{min_fastlane_version}_"]


def stream_command(cmd: list[str], cwd: Path, env: dict[str, str]) -> int:
    print("[RUN] " + " ".join(shlex.quote(c) for c in cmd))
    process = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    assert process.stdout is not None
    for line in process.stdout:
        sys.stdout.write(line)
    process.wait()
    return process.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify and fix internal tester distribution.")
    parser.add_argument("--project-root", default=os.getcwd(), help="iOS 项目根目录")
    parser.add_argument("--group", default=os.getenv("INTERNAL_GROUP_NAME", "Agent Internal Testing"))
    parser.add_argument("--testers", default=os.getenv("TESTER_EMAILS", ""))
    parser.add_argument("--app-identifier", default=os.getenv("IOS_APP_IDENTIFIER", ""))
    parser.add_argument("--min-fastlane-version", default=os.getenv("MIN_FASTLANE_VERSION", "2.232.1"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.exists():
        print(f"[FAIL] project root 不存在: {project_root}", file=sys.stderr)
        return 2
    if not (project_root / "fastlane" / "Fastfile").exists():
        print("[FAIL] 缺少 fastlane/Fastfile", file=sys.stderr)
        return 2

    testers = args.testers.strip()
    if not testers:
        print("[FAIL] 未提供 tester 邮箱。请显式传入 --testers 或设置 TESTER_EMAILS。", file=sys.stderr)
        return 2

    env = os.environ.copy()
    env = prepend_homebrew_ruby_gem_bin(env)
    env["INTERNAL_GROUP_NAME"] = args.group
    env["TESTER_EMAILS"] = testers
    if args.app_identifier:
        env["IOS_APP_IDENTIFIER"] = args.app_identifier
    env = hydrate_materials_env(project_root, env)

    missing_asc = [k for k in ("ASC_KEY_ID", "ASC_ISSUER_ID", "ASC_KEY_FILEPATH") if not env.get(k, "").strip()]
    if missing_asc:
        print(f"[FAIL] 缺少 ASC 参数: {', '.join(missing_asc)}", file=sys.stderr)
        return 2

    fastlane_cmd = resolve_fastlane_cmd(project_root, args.min_fastlane_version, env)
    fastlane_version = run_cmd_version(fastlane_cmd, project_root, env)
    if not semver_ge(fastlane_version, args.min_fastlane_version):
        cmd_str = " ".join(shlex.quote(c) for c in fastlane_cmd)
        print(
            f"[FAIL] fastlane 版本不满足要求: {fastlane_version or '<missing>'} < {args.min_fastlane_version} (cmd: {cmd_str})",
            file=sys.stderr,
        )
        return 2

    lane_cmd = fastlane_cmd + [
        "ios",
        "assign_internal_tester",
        f"group:{args.group}",
        f"testers:{testers}",
    ]
    if args.app_identifier:
        lane_cmd.append(f"app_identifier:{args.app_identifier}")

    if args.dry_run:
        print("[DRY-RUN] " + " ".join(shlex.quote(c) for c in lane_cmd))
        return 0

    print(f"[INFO] fastlane_cmd: {' '.join(shlex.quote(c) for c in fastlane_cmd)}")
    print(f"[INFO] fastlane_version: {fastlane_version}")

    rc = stream_command(lane_cmd, project_root, env)
    if rc != 0:
        print("[FAIL] 分发校验失败，请检查 fastlane 输出。", file=sys.stderr)
        return rc

    print("[DONE] Internal Group 与 tester 分发校验通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
