#!/usr/bin/env bash
# 从 Word (.docx) 提取纯文本（依赖 macOS 自带的 textutil）
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "用法: extract_docx.sh <文件.docx|文件.md|文件.txt>" >&2
  exit 2
fi

FILE="$1"
if [[ ! -f "$FILE" ]]; then
  echo "错误：文件不存在：$FILE" >&2
  exit 1
fi

case "$FILE" in
  *.docx|*.doc)
    if ! command -v textutil >/dev/null 2>&1; then
      echo "错误：当前系统没有 textutil（非 macOS）。请用 Word 另存为 txt 后重试。" >&2
      exit 1
    fi
    textutil -convert txt -stdout "$FILE"
    ;;
  *)
    cat "$FILE"
    ;;
esac
