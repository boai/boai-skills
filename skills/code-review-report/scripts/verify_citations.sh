#!/usr/bin/env bash
# 校验评审报告里引用的 文件:行号 是否真实存在，防止编造引用
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "用法: verify_citations.sh <报告.md> [仓库路径]" >&2
  exit 2
fi

REPORT="$1"
REPO="${2:-.}"

if [[ ! -f "$REPORT" ]]; then
  echo "错误：报告不存在：$REPORT" >&2
  exit 1
fi
if [[ ! -d "$REPO" ]]; then
  echo "错误：仓库路径不存在：$REPO" >&2
  exit 1
fi

FAIL=0
TOTAL=0

# 匹配任意 路径.扩展名:行号 或 :起始-结束（不限定语言）
while IFS= read -r ref; do
  [[ -n "$ref" ]] || continue
  FILE="${ref%:*}"
  # 排除 URL、IP、版本号等伪引用
  case "$ref" in
    //*|*://*) continue ;;
  esac
  if [[ "$FILE" =~ ^v?[0-9]+\.[0-9]+\.[0-9]+$ ]]; then continue; fi
  if [[ "$FILE" =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]]; then continue; fi

  TOTAL=$((TOTAL + 1))
  REST="${ref##*:}"
  START="${REST%%-*}"
  END="${REST##*-}"
  FULL="$REPO/$FILE"

  if [[ ! -f "$FULL" ]]; then
    echo "❌ 文件不存在: $ref"
    FAIL=$((FAIL + 1))
    continue
  fi

  MAX=$(wc -l < "$FULL" | tr -d ' ')
  for LINE in "$START" "$END"; do
    if [[ "$LINE" =~ ^[0-9]+$ ]] && (( LINE == 0 || LINE > MAX )); then
      echo "❌ 行号越界: ${ref}（文件共 $MAX 行）"
      FAIL=$((FAIL + 1))
      break
    fi
  done
done < <(grep -oE '[A-Za-z0-9_./-]+\.[A-Za-z0-9_]+:[0-9]+(-[0-9]+)?' "$REPORT" | sort -u)

echo "----------------------------------------"
if (( TOTAL == 0 )); then
  echo "❌ 报告中未发现任何 文件:行号 引用；评审报告必须给出可核验的引用"
  exit 1
fi
if (( FAIL > 0 )); then
  echo "结果：共 $TOTAL 条引用，$FAIL 条有问题，请修正后再交付"
  exit 1
else
  echo "结果：共 $TOTAL 条引用，全部有效 ✅"
fi
