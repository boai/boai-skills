#!/usr/bin/env bash
# 收集提测说明所需材料：提交列表（含 body）、文件变更、目录汇总、版本建议
set -euo pipefail

usage() {
  cat <<'EOF'
用法:
  collect_changes.sh [--repo <仓库路径>] [--base <分支>] [--target <分支>] [--out <文件>] [--] [路径...]

参数:
  --repo     仓库路径，默认当前目录（可从任意目录运行本脚本）
  --base     基线分支，默认自动探测 origin/HEAD → main → master
  --target   目标分支/提交，默认 HEAD
  --out      写入文件，默认输出到 stdout；已存在时需加 --force
  --force    覆盖已存在的 --out 文件
  -h, --help 显示帮助

示例:
  collect_changes.sh --repo /path/to/repo --base main --target feature/login
  collect_changes.sh --repo /path/to/repo --base v1.1.0 --target HEAD -- Sources/
EOF
}

REPO=""
BASE=""
TARGET="HEAD"
OUT=""
FORCE=0
PATHS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --base) BASE="$2"; shift 2 ;;
    --target) TARGET="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; PATHS=("$@"); break ;;
    -*) echo "未知参数: $1" >&2; usage >&2; exit 2 ;;
    *) PATHS+=("$1"); shift ;;
  esac
done

if [[ -n "$REPO" ]]; then
  if [[ ! -d "$REPO" ]]; then
    echo "错误：仓库路径不存在：$REPO" >&2
    exit 1
  fi
  cd "$REPO"
fi

if [[ -n "$OUT" && -f "$OUT" && $FORCE -eq 0 ]]; then
  echo "错误：输出文件已存在：${OUT}（加 --force 覆盖）" >&2
  exit 1
fi

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
  echo "错误：当前目录不在 Git 仓库内。请先 cd 到仓库根目录。" >&2
  exit 1
}

REPO_ROOT=$(git rev-parse --show-toplevel)

if [[ -z "$BASE" ]]; then
  REMOTE_HEAD=$(git symbolic-ref refs/remotes/origin/HEAD --short 2>/dev/null || true)
  REMOTE_HEAD=${REMOTE_HEAD#origin/}
  for candidate in "$REMOTE_HEAD" main master; do
    [[ -n "$candidate" ]] || continue
    if git rev-parse --verify --quiet "$candidate" >/dev/null; then
      BASE="$candidate"
      break
    fi
  done
fi
[[ -n "$BASE" ]] || { echo "错误：无法识别基线分支，请用 --base 指定。" >&2; exit 1; }
git rev-parse --verify --quiet "$TARGET" >/dev/null || { echo "错误：目标不存在：$TARGET" >&2; exit 1; }

EXCLUDES=(
  ':(exclude,glob)*.lock'
  ':(exclude,glob)Podfile.lock'
  ':(exclude,glob)package-lock.json'
  ':(exclude,glob)yarn.lock'
  ':(exclude,glob)pnpm-lock.yaml'
  ':(exclude,glob)*.pbxproj'
  ':(exclude,glob)xcuserdata/**'
  ':(exclude,glob)Pods/**'
  ':(exclude,glob)node_modules/**'
  ':(exclude,glob)build/**'
  ':(exclude,glob)DerivedData/**'
)

EMIT() {
  echo "== 仓库 =="
  echo "$REPO_ROOT"
  echo
  echo "== 当前分支 =="
  git rev-parse --abbrev-ref HEAD
  echo
  echo "== 范围 =="
  echo "$BASE..$TARGET"
  echo
  echo "== 变更统计 =="
  git diff --shortstat "$BASE...$TARGET" -- ${PATHS[@]+"${PATHS[@]}"} "${EXCLUDES[@]}" 2>/dev/null || true
  echo
  echo "== 提交列表（含提交说明）=="
  git log --no-merges --pretty=format:'%h | %an | %ad | %s' --date=short "$BASE..$TARGET" -- ${PATHS[@]+"${PATHS[@]}"} 2>/dev/null | head -200 || true
  echo
  echo
  echo "--- 提交正文 ---"
  git log --no-merges --pretty=format:'### %h %s%n%b' "$BASE..$TARGET" -- ${PATHS[@]+"${PATHS[@]}"} 2>/dev/null | head -400 || true
  echo
  echo
  echo "== 文件变更 =="
  git diff --name-status "$BASE...$TARGET" -- ${PATHS[@]+"${PATHS[@]}"} "${EXCLUDES[@]}" 2>/dev/null || true
  echo
  echo "== 目录汇总 =="
  git diff --name-only "$BASE...$TARGET" -- ${PATHS[@]+"${PATHS[@]}"} "${EXCLUDES[@]}" 2>/dev/null \
    | awk -F/ '{ if (NF >= 3) print $1"/"$2; else if (NF == 2) print $1; else print "(根目录)" }' \
    | sort | uniq -c | sort -rn || true
  echo
  echo "== 最近标签 =="
  git describe --tags --abbrev=0 "$TARGET" 2>/dev/null || echo "（无标签）"
  echo
  echo "== 版本建议 =="
  LATEST_TAG=$(git describe --tags --abbrev=0 "$TARGET" 2>/dev/null || true)
  if [[ -n "$LATEST_TAG" && "$LATEST_TAG" =~ ^v?([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
    MAJOR=${BASH_REMATCH[1]}; MINOR=${BASH_REMATCH[2]}; PATCH=${BASH_REMATCH[3]}
    HAS_FEAT=$(git log --no-merges --pretty=%s "$BASE..$TARGET" 2>/dev/null | grep -cE '^feat(\(|[:：]|！|!)' || true)
    if (( HAS_FEAT > 0 )); then
      echo "最新标签 ${LATEST_TAG}；本次包含新功能，建议 v${MAJOR}.$((MINOR + 1)).0"
    else
      echo "最新标签 ${LATEST_TAG}；本次以修复/优化为主，建议 v${MAJOR}.${MINOR}.$((PATCH + 1))"
    fi
  else
    echo "未能从标签推断版本号，请手动指定（例如 v1.2.0）"
  fi
}

if [[ -n "$OUT" ]]; then
  EMIT > "$OUT"
  echo "已写入: $OUT" >&2
else
  EMIT
fi
