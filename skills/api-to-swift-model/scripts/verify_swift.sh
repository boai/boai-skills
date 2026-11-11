#!/usr/bin/env bash
# 校验生成的 Swift 文件是否能通过编译类型检查
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "用法: verify_swift.sh <Models.swift>" >&2
  exit 2
fi

FILE="$1"
if [[ ! -f "$FILE" ]]; then
  echo "错误：文件不存在：$FILE" >&2
  exit 1
fi

if ! command -v swiftc >/dev/null 2>&1; then
  echo "错误：未找到 swiftc。请安装 Xcode 或 Command Line Tools（xcode-select --install）。" >&2
  exit 1
fi

LOG="$(mktemp "${TMPDIR:-/tmp}/swiftc-typecheck.XXXXXX")"
if swiftc -typecheck "$FILE" 2>"$LOG"; then
  echo "✅ Swift 编译检查通过：$FILE"
  rm -f "$LOG"
else
  echo "❌ Swift 编译检查失败：$FILE"
  cat "$LOG" >&2
  rm -f "$LOG"
  exit 1
fi
