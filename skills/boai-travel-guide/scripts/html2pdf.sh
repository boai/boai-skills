#!/bin/bash
# ============================================================
# html2pdf.sh — 用无头 Chrome/Edge 把 HTML 转成 PDF（macOS/Linux）
# 用法: html2pdf.sh <input.html> <output.pdf>
# 说明:
#   - Chrome 转完 PDF 后偶尔不退出，本脚本会检测产物并清理残留进程
#   - 纯本地渲染，不依赖外网（模板内也不应引用外网图片）
# ============================================================
set -u

INPUT="$1"
OUTPUT="$2"

if [ ! -f "$INPUT" ]; then
  echo "❌ 输入文件不存在: $INPUT" >&2
  exit 1
fi

# 按优先级找浏览器
CHROME=""
for c in \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
  "/Applications/Chromium.app/Contents/MacOS/Chromium" \
  "google-chrome" "chromium" "chromium-browser" "microsoft-edge"; do
  if [ -x "$c" ] || command -v "$c" >/dev/null 2>&1; then
    CHROME="$c"
    break
  fi
done

if [ -z "$CHROME" ]; then
  echo "❌ 未找到 Chrome/Edge/Chromium，无法生成 PDF" >&2
  echo "   请安装 Google Chrome 后重试" >&2
  exit 1
fi

# 独立 profile，避免与用户正在使用的浏览器实例冲突
PROFILE="$(mktemp -d /tmp/html2pdf-profile.XXXXXX)"

# 先渲染到临时文件再 mv 覆盖：Chrome 对已存在的目标路径可能静默写失败，
# 而旧文件仍在会让 [ -s ] 误判成功——临时文件 + 原子替换保证产物一定是最新的
TMP_OUT="$(mktemp /tmp/html2pdf-out.XXXXXX.pdf)"
rm -f "$TMP_OUT"

echo "🖨️  使用 $CHROME 渲染 PDF..."

"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
  --user-data-dir="$PROFILE" \
  --print-to-pdf="$TMP_OUT" "file://$INPUT" >/dev/null 2>&1 &
PID=$!

# 最多等 90 秒，产物出现即认为成功
for _ in $(seq 1 90); do
  if [ -f "$TMP_OUT" ] && [ -s "$TMP_OUT" ]; then
    break
  fi
  sleep 1
done

# 清理：杀掉可能挂起的渲染进程（wait 回收后台任务，避免 shell 打印 Terminated 噪音）
kill "$PID" 2>/dev/null
wait "$PID" 2>/dev/null || true
pkill -f "$PROFILE" 2>/dev/null || true
rm -rf "$PROFILE"

if [ ! -s "$TMP_OUT" ]; then
  echo "❌ PDF 生成失败（无产物或文件为空）" >&2
  exit 1
fi

# 原子替换到目标路径（即使目标文件正被 Preview 打开也能替换成功）
mv -f "$TMP_OUT" "$OUTPUT"

echo "✅ PDF 已生成: $OUTPUT"
ls -lh "$OUTPUT" | awk '{print "   大小: " $5}'

# macOS 下用 mdls 报页数；刚生成的文件可能还没建好 Spotlight 索引，查不到就跳过
if command -v mdls >/dev/null 2>&1; then
  PAGES="$(mdls -name kMDItemNumberOfPages -raw "$OUTPUT" 2>/dev/null || true)"
  if [ -n "$PAGES" ] && [ "$PAGES" != "(null)" ]; then
    echo "   页数: $PAGES"
  fi
fi

exit 0
