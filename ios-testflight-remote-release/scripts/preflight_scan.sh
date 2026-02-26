#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$PWD"
WORKSPACE=""
SCHEME=""
APP_IDENTIFIER=""
XCODEPROJ=""
INTERNAL_GROUP_NAME="${INTERNAL_GROUP_NAME:-Agent Internal Testing}"
AUTO_BOOTSTRAP_FASTLANE="true"
MIN_FASTLANE_VERSION="${MIN_FASTLANE_VERSION:-2.232.1}"
AUTO_FIX_FASTLANE="${AUTO_FIX_FASTLANE:-true}"
FASTLANE_EFFECTIVE_CMD=""
FASTLANE_ACTIVE_VERSION=""

usage() {
  cat <<'EOF'
Usage:
  bash scripts/preflight_scan.sh [options]

Options:
  --project-root <path>       iOS 项目根目录（默认当前目录）
  --workspace <name>          workspace 文件名（如 ReadFast.xcworkspace）
  --scheme <name>             scheme 名称（如 ReadFast）
  --xcodeproj <name>          xcodeproj 文件名（如 ReadFast.xcodeproj）
  --app-identifier <bundle>   App Identifier
  --no-auto-bootstrap         缺少 fastlane 时不自动初始化（默认自动初始化）
  -h, --help                  显示帮助
EOF
}

fail() {
  echo "[FAIL] $*" >&2
  exit 1
}

has_cmd() {
  command -v "$1" >/dev/null 2>&1
}

semver_ge() {
  local current="$1"
  local minimum="$2"
  [[ -n "${current}" && -n "${minimum}" ]] || return 1
  [[ "$(printf '%s\n%s\n' "${current}" "${minimum}" | sort -V | head -n1)" == "${minimum}" ]]
}

extract_fastlane_version() {
  local raw="$1"
  local strict_line
  strict_line="$(echo "${raw}" | awk '/^fastlane [0-9]+\.[0-9]+\.[0-9]+$/ {print $2; exit}')"
  if [[ -n "${strict_line}" ]]; then
    echo "${strict_line}"
    return 0
  fi

  local current_line
  current_line="$(echo "${raw}" | sed -n 's/.*You are on \([0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\).*/\1/p' | head -n1)"
  if [[ -n "${current_line}" ]]; then
    echo "${current_line}"
    return 0
  fi

  echo "${raw}" | grep -Eo 'fastlane [0-9]+\.[0-9]+\.[0-9]+$' | awk '{print $2}' | head -n1
}

prepend_homebrew_ruby_gem_bin() {
  local ruby_gem="/opt/homebrew/opt/ruby/bin/gem"
  [[ -x "${ruby_gem}" ]] || return 0
  local gem_bin
  gem_bin="$("${ruby_gem}" env 2>/dev/null | awk -F': ' '/EXECUTABLE DIRECTORY/ {print $2; exit}' || true)"
  if [[ -n "${gem_bin}" && -d "${gem_bin}" && ":${PATH}:" != *":${gem_bin}:"* ]]; then
    PATH="${gem_bin}:${PATH}"
  fi
}

detect_fastlane_version() {
  has_cmd fastlane || return 0
  local output
  output="$(fastlane --version 2>&1 || true)"
  extract_fastlane_version "${output}"
}

detect_locked_fastlane_version() {
  has_cmd fastlane || return 0
  local output selector
  selector="_${MIN_FASTLANE_VERSION}_"
  output="$(fastlane "${selector}" --version 2>&1 || true)"
  extract_fastlane_version "${output}"
}

ensure_fastlane_min_version() {
  prepend_homebrew_ruby_gem_bin
  local current_version
  current_version="$(detect_locked_fastlane_version)"
  if [[ "${current_version}" == "${MIN_FASTLANE_VERSION}" ]]; then
    FASTLANE_EFFECTIVE_CMD="fastlane _${MIN_FASTLANE_VERSION}_"
    FASTLANE_ACTIVE_VERSION="${current_version}"
    echo "[OK] fastlane 版本满足要求: ${current_version} (locked: ${FASTLANE_EFFECTIVE_CMD})"
    return 0
  fi

  local plain_version
  plain_version="$(detect_fastlane_version)"
  echo "[WARN] fastlane 版本过低或缺失: ${current_version:-<missing>}，最低要求 ${MIN_FASTLANE_VERSION}"
  if [[ -n "${plain_version}" ]]; then
    echo "[INFO] 当前默认 fastlane 版本: ${plain_version}"
  fi
  [[ "${AUTO_FIX_FASTLANE}" == "true" ]] || fail "请先安装/升级 fastlane 到 >= ${MIN_FASTLANE_VERSION}（可设置 AUTO_FIX_FASTLANE=true 自动修复）"

  local ruby_gem="/opt/homebrew/opt/ruby/bin/gem"
  [[ -x "${ruby_gem}" ]] || fail "未找到 ${ruby_gem}，无法自动安装 fastlane。请先安装 Homebrew Ruby 或手动升级 fastlane。"
  echo "[INFO] 正在自动安装 fastlane ${MIN_FASTLANE_VERSION} ..."
  "${ruby_gem}" install fastlane -v "${MIN_FASTLANE_VERSION}" --no-document >/dev/null
  prepend_homebrew_ruby_gem_bin

  current_version="$(detect_locked_fastlane_version)"
  [[ "${current_version}" == "${MIN_FASTLANE_VERSION}" ]] || fail "fastlane 自动升级后仍无法锁定到目标版本: 期望=${MIN_FASTLANE_VERSION}，实际=${current_version:-<missing>}"
  FASTLANE_EFFECTIVE_CMD="fastlane _${MIN_FASTLANE_VERSION}_"
  FASTLANE_ACTIVE_VERSION="${current_version}"
  echo "[OK] fastlane 自动升级完成: ${current_version} (locked: ${FASTLANE_EFFECTIVE_CMD})"
}

resolve_gem_installer() {
  if [[ -x "/opt/homebrew/opt/ruby/bin/gem" ]]; then
    echo "/opt/homebrew/opt/ruby/bin/gem"
    return 0
  fi
  if has_cmd gem; then
    command -v gem
    return 0
  fi
  return 1
}

ensure_xcpretty_ready_for_fastlane() {
  prepend_homebrew_ruby_gem_bin
  if has_cmd xcpretty; then
    echo "[OK] xcpretty 可用: $(command -v xcpretty)"
    return 0
  fi

  local fastlane_bin
  fastlane_bin="$(command -v fastlane 2>/dev/null || true)"
  echo "[WARN] fastlane 运行环境缺少 xcpretty（fastlane: ${fastlane_bin:-<missing>}）"
  [[ "${AUTO_FIX_FASTLANE}" == "true" ]] || fail "请先安装 xcpretty，或设置 AUTO_FIX_FASTLANE=true 自动修复。"

  local gem_installer
  gem_installer="$(resolve_gem_installer || true)"
  [[ -n "${gem_installer}" ]] || fail "未找到可用 gem 命令，无法自动安装 xcpretty。"

  echo "[INFO] 正在自动安装 xcpretty（使用: ${gem_installer}）..."
  if ! "${gem_installer}" install xcpretty --no-document --user-install >/dev/null 2>&1; then
    "${gem_installer}" install xcpretty --no-document >/dev/null 2>&1 \
      || fail "xcpretty 自动安装失败，请手动执行: ${gem_installer} install xcpretty --no-document"
  fi

  prepend_homebrew_ruby_gem_bin
  has_cmd xcpretty || fail "xcpretty 安装完成但未出现在 PATH，请检查 gem 可执行目录。"
  echo "[OK] xcpretty 自动安装完成: $(command -v xcpretty)"
}

detect_workspace() {
  if [[ -n "${WORKSPACE}" ]]; then
    echo "${WORKSPACE}"
    return 0
  fi
  local first
  first="$(find "${PROJECT_ROOT}" -maxdepth 1 -type d -name "*.xcworkspace" | head -n1 || true)"
  if [[ -n "${first}" ]]; then
    basename "${first}"
  fi
}

detect_xcodeproj() {
  if [[ -n "${XCODEPROJ}" ]]; then
    echo "${XCODEPROJ}"
    return 0
  fi
  local first
  first="$(find "${PROJECT_ROOT}" -maxdepth 1 -type d -name "*.xcodeproj" | head -n1 || true)"
  if [[ -n "${first}" ]]; then
    basename "${first}"
  fi
}

detect_scheme() {
  if [[ -n "${SCHEME}" ]]; then
    echo "${SCHEME}"
    return 0
  fi
  local ws="$1"
  local preferred="$2"
  if [[ -z "${ws}" ]]; then
    return 0
  fi
  if ! has_cmd xcodebuild || ! has_cmd python3; then
    return 0
  fi
  local raw
  raw="$(xcodebuild -list -json -workspace "${PROJECT_ROOT}/${ws}" 2>/dev/null || true)"
  if [[ -z "${raw}" ]]; then
    return 0
  fi
  python3 - "${raw}" "${preferred}" <<'PY' || true
import json
import sys

raw = sys.argv[1]
preferred = (sys.argv[2] or "").strip().lower()
try:
    data = json.loads(raw)
except Exception:
    sys.exit(0)
workspace = data.get("workspace", {})
schemes = workspace.get("schemes") or []
if not schemes:
    sys.exit(0)
if preferred:
    for s in schemes:
        if s.lower() == preferred:
            print(s)
            sys.exit(0)
print(schemes[0])
PY
}

detect_app_identifier() {
  if [[ -n "${APP_IDENTIFIER}" ]]; then
    echo "${APP_IDENTIFIER}"
    return 0
  fi
  local appfile="${PROJECT_ROOT}/fastlane/Appfile"
  if [[ ! -f "${appfile}" ]]; then
    return 0
  fi
  sed -n 's/^[[:space:]]*app_identifier[[:space:]]*"\(.*\)".*/\1/p' "${appfile}" | head -n1
}

detect_connected_iphone() {
  if ! has_cmd xcrun; then
    return 0
  fi
  xcrun xctrace list devices 2>/dev/null | awk '/iPhone/ && $0 !~ /Simulator/ {print; exit}'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-root)
      PROJECT_ROOT="${2:-}"
      shift 2
      ;;
    --workspace)
      WORKSPACE="${2:-}"
      shift 2
      ;;
    --scheme)
      SCHEME="${2:-}"
      shift 2
      ;;
    --xcodeproj)
      XCODEPROJ="${2:-}"
      shift 2
      ;;
    --app-identifier)
      APP_IDENTIFIER="${2:-}"
      shift 2
      ;;
    --no-auto-bootstrap)
      AUTO_BOOTSTRAP_FASTLANE="false"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "未知参数: $1"
      ;;
  esac
done

[[ -d "${PROJECT_ROOT}" ]] || fail "project root 不存在: ${PROJECT_ROOT}"
if [[ ! -f "${PROJECT_ROOT}/fastlane/Fastfile" ]]; then
  if [[ "${AUTO_BOOTSTRAP_FASTLANE}" == "true" ]]; then
    echo "[INFO] 检测到缺少 fastlane/Fastfile，开始自动初始化 fastlane..."
    bootstrap_cmd=(bash "${SCRIPT_DIR}/bootstrap_fastlane.sh" --project-root "${PROJECT_ROOT}")
    bootstrap_cmd+=(--fastlane-version "${MIN_FASTLANE_VERSION}")
    [[ -n "${WORKSPACE}" ]] && bootstrap_cmd+=(--workspace "${WORKSPACE}")
    [[ -n "${XCODEPROJ}" ]] && bootstrap_cmd+=(--xcodeproj "${XCODEPROJ}")
    [[ -n "${SCHEME}" ]] && bootstrap_cmd+=(--scheme "${SCHEME}")
    [[ -n "${APP_IDENTIFIER}" ]] && bootstrap_cmd+=(--app-identifier "${APP_IDENTIFIER}")
    "${bootstrap_cmd[@]}"
    echo "[INFO] fastlane 初始化完成，继续预检。"
  else
    fail "缺少 fastlane/Fastfile: ${PROJECT_ROOT}"
  fi
fi

FASTFILE="${PROJECT_ROOT}/fastlane/Fastfile"
grep -q "lane :internal_release" "${FASTFILE}" || fail "Fastfile 中缺少 lane :internal_release"
grep -q "lane :assign_internal_tester" "${FASTFILE}" || fail "Fastfile 中缺少 lane :assign_internal_tester"
ensure_fastlane_min_version
ensure_xcpretty_ready_for_fastlane

WORKSPACE="$(detect_workspace)"
XCODEPROJ="$(detect_xcodeproj)"
scheme_preferred=""
if [[ -n "${WORKSPACE}" ]]; then
  scheme_preferred="${WORKSPACE%.xcworkspace}"
elif [[ -n "${XCODEPROJ}" ]]; then
  scheme_preferred="${XCODEPROJ%.xcodeproj}"
fi
SCHEME="$(detect_scheme "${WORKSPACE}" "${scheme_preferred}")"
APP_IDENTIFIER="$(detect_app_identifier)"

echo "== Preflight Scan =="
echo "Project Root        : ${PROJECT_ROOT}"
echo "Workspace           : ${WORKSPACE:-<missing>}"
echo "Scheme              : ${SCHEME:-<missing>}"
echo "Xcodeproj           : ${XCODEPROJ:-<missing>}"
echo "App Identifier      : ${APP_IDENTIFIER:-<missing>}"
echo "Internal Group      : ${INTERNAL_GROUP_NAME}"

echo
echo "== Toolchain Check =="
for tool in xcodebuild ruby fastlane git; do
  if has_cmd "${tool}"; then
    echo "[OK] ${tool}: $(command -v "${tool}")"
  else
    echo "[WARN] ${tool}: not found"
  fi
done
if [[ -n "${FASTLANE_EFFECTIVE_CMD}" ]]; then
  echo "[OK] fastlane_effective_cmd: ${FASTLANE_EFFECTIVE_CMD}"
fi
if [[ -n "${FASTLANE_ACTIVE_VERSION}" ]]; then
  echo "[OK] fastlane_effective_version: ${FASTLANE_ACTIVE_VERSION}"
fi

if [[ -f "${PROJECT_ROOT}/Gemfile" ]]; then
  if has_cmd bundle; then
    echo "[OK] bundle: $(command -v bundle)"
  else
    echo "[WARN] Gemfile 存在但 bundle 不可用"
  fi
fi

echo
echo "== Connected Device Check =="
iphone_line="$(detect_connected_iphone || true)"
if [[ -n "${iphone_line}" ]]; then
  echo "[OK] 检测到已连接 iPhone: ${iphone_line}"
else
  echo "[INFO] 未检测到已连接 iPhone（可继续走 TestFlight 远程分发）"
fi

echo
echo "[DONE] 预检完成。"
