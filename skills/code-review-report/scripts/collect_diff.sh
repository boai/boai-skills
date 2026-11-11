#!/usr/bin/env bash
# 收集 Git 变更，输出评审所需材料：统计 + 提交 + 文件清单 + 过滤后的 diff
set -euo pipefail

usage() {
  cat <<'EOF'
用法:
  collect_diff.sh [--repo <仓库路径>] [--base <分支>] [--target <分支>] [--max-chars N] [--out <文件>] [--] [路径...]

参数:
  --repo       仓库路径，默认当前目录（可从任意目录运行本脚本）
  --base       基线分支，默认自动探测 origin/HEAD → main → master
  --target     目标分支，默认 HEAD
  --max-chars  diff 最大字符数，默认 60000，超出安全截断
  --out        写入文件，默认输出到 stdout；已存在时需加 --force
  --force      覆盖已存在的 --out 文件
  -h, --help   显示帮助

示例:
  collect_diff.sh --repo /path/to/repo --base main --target feature/login
  collect_diff.sh --repo /path/to/repo --base main --target HEAD -- Sources/
EOF
}

REPO=""
BASE=""
TARGET="HEAD"
MAX_CHARS=60000
OUT=""
FORCE=0
PATHS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --base) BASE="$2"; shift 2 ;;
    --target) TARGET="$2"; shift 2 ;;
    --max-chars) MAX_CHARS="$2"; shift 2 ;;
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

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "错误：当前目录不在 Git 仓库内。请先 cd 到仓库根目录。" >&2
  exit 1
fi

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

if [[ -z "$BASE" ]]; then
  echo "错误：无法自动识别基线分支，请用 --base 指定（例如 --base main）。" >&2
  exit 1
fi

if ! git rev-parse --verify --quiet "$TARGET" >/dev/null; then
  echo "错误：目标分支/提交不存在：$TARGET" >&2
  exit 1
fi

# 噪音过滤：锁文件、依赖目录、构建产物、二进制资源
EXCLUDES=(
  ':(exclude,glob)*.lock'
  ':(exclude,glob)Podfile.lock'
  ':(exclude,glob)package-lock.json'
  ':(exclude,glob)yarn.lock'
  ':(exclude,glob)pnpm-lock.yaml'
  ':(exclude,glob)Cargo.lock'
  ':(exclude,glob)Gemfile.lock'
  ':(exclude,glob)*.pbxproj'
  ':(exclude,glob)*.xcworkspacedata'
  ':(exclude,glob)*.xcuserstate'
  ':(exclude,glob)xcuserdata/**'
  ':(exclude,glob)*.min.js'
  ':(exclude,glob)*.min.css'
  ':(exclude,glob)Pods/**'
  ':(exclude,glob)node_modules/**'
  ':(exclude,glob).build/**'
  ':(exclude,glob)build/**'
  ':(exclude,glob)DerivedData/**'
  ':(exclude,glob)*.svg'
  ':(exclude,glob)*.png'
  ':(exclude,glob)*.jpg'
  ':(exclude,glob)*.jpeg'
  ':(exclude,glob)*.gif'
  ':(exclude,glob)*.ico'
  ':(exclude,glob)*.pdf'
  ':(exclude,glob)*.zip'
  ':(exclude,glob)*.mp3'
  ':(exclude,glob)*.mp4'
  ':(exclude,glob)*.mov'
  ':(exclude,glob)*.ttf'
  ':(exclude,glob)*.otf'
  ':(exclude,glob)*.woff'
  ':(exclude,glob)*.woff2'
)

EMIT() {
  echo "== 仓库 =="
  echo "$REPO_ROOT"
  echo
  echo "== 范围 =="
  echo "$BASE...$TARGET"
  echo
  echo "== 变更统计 =="
  git diff --shortstat "$BASE...$TARGET" -- ${PATHS[@]+"${PATHS[@]}"} "${EXCLUDES[@]}" 2>/dev/null || true
  echo
  echo "== 提交列表 =="
  git log --no-merges --pretty=format:'%h | %an | %ad | %s' --date=short "$BASE..$TARGET" -- ${PATHS[@]+"${PATHS[@]}"} 2>/dev/null | head -200 || true
  echo
  echo
  echo "== 变更文件 =="
  git diff --name-status "$BASE...$TARGET" -- ${PATHS[@]+"${PATHS[@]}"} "${EXCLUDES[@]}" 2>/dev/null || true
  echo
  echo "== Diff =="
  DIFF=$(git diff "$BASE...$TARGET" -- ${PATHS[@]+"${PATHS[@]}"} "${EXCLUDES[@]}" 2>/dev/null || true)
  DIFF_LEN=${#DIFF}
  if (( DIFF_LEN > MAX_CHARS )); then
    echo "> ⚠️ 完整 diff 共 ${DIFF_LEN} 字符，以下为前 ${MAX_CHARS} 字符；报告需注明未覆盖部分。"
    printf '%s' "$DIFF" | python3 -c 'import sys; n=int(sys.argv[1]); d=sys.stdin.read(); sys.stdout.write(d[:n])' "$MAX_CHARS"
    echo
    echo "...（已截断）"
  else
    printf '%s\n' "$DIFF"
  fi
  if [[ -z "${DIFF//[[:space:]]/}" ]]; then
    echo "（空 diff：该范围没有可评审的改动，或全部被过滤）"
  fi
}

if [[ -n "$OUT" ]]; then
  EMIT > "$OUT"
  echo "已写入: $OUT" >&2
else
  EMIT
fi
