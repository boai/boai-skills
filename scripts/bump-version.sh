#!/usr/bin/env bash
#
# boai-skills 版本号工具
#
# 本仓库有两类版本号，别混：
#
#   ① 对外发布版本（唯一真正生效的）
#      存在 .claude-plugin/plugin.json 的 version。
#      官方规则：版本解析 plugin.json 优先，marketplace 条目里的 version 会被静默忽略。
#      所以「整包 boai-skills」和 8 个技能条目共用这一个版本号。
#      改它 = 发版，用户下次自动更新。
#
#   ② 内部技能版本（只给自己看，不影响用户）
#      存在各 skills/<名>/SKILL.md 的 frontmatter，记录每个技能自身迭代到哪了。
#
#   例外：plugins/claude-token-tracker 是真正的独立插件（有自己的 plugin.json），
#         它的版本独立生效，用 set plugin 维护。
#
# 用法：
#   ./scripts/bump-version.sh list                    查看全部版本
#   ./scripts/bump-version.sh release 1.7.0           发版（改对外版本并同步 README）
#   ./scripts/bump-version.sh skill <技能名> 2.5.0     记一次内部技能版本
#   ./scripts/bump-version.sh plugin claude-token-tracker 1.1.0   独立插件发版
#   ./scripts/bump-version.sh sync                    重新生成 README 版本区
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

command -v python3 >/dev/null 2>&1 || { echo "❌ 需要 python3" >&2; exit 1; }

VERSION_RE='^[0-9]+\.[0-9]+\.[0-9]+$'
die() { echo "❌ $*" >&2; exit 1; }
check_version() { [[ "$1" =~ $VERSION_RE ]] || die "版本号格式应为 X.Y.Z，收到：$1"; }

# ── 改源头 ────────────────────────────────────────────────────

set_plugin_json_version() {   # $1=plugin.json 路径  $2=版本
  python3 - "$1" "$2" <<'PY'
import json, sys
p, ver = sys.argv[1], sys.argv[2]
d = json.load(open(p, encoding="utf-8"))
d["version"] = ver
with open(p, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY
}

set_skill_version() {          # $1=技能名  $2=版本
  local f="skills/$1/SKILL.md"
  [ -f "$f" ] || die "找不到技能：$1（目录名如 mac-wechat-anti-recall）"
  if grep -q '^version:[[:space:]]*' "$f"; then
    sed -i '' "s/^version:[[:space:]]*.*$/version: $2/" "$f"
  else
    sed -i '' "/^description:/a\\
version: $2
" "$f"
  fi
}

# ── 生成 README 版本区 ────────────────────────────────────────

sync() {
  python3 - "$ROOT" <<'PY'
import json, os, re, sys
root = sys.argv[1]
START, END = "<!-- versions:start -->", "<!-- versions:end -->"

release = json.load(open(os.path.join(root, ".claude-plugin/plugin.json"),
                         encoding="utf-8"))["version"]

def skill_versions():
    out = []
    for name in sorted(os.listdir(os.path.join(root, "skills"))):
        p = os.path.join(root, "skills", name, "SKILL.md")
        if not os.path.isfile(p):
            continue
        ver = "—"
        for line in open(p, encoding="utf-8"):
            m = re.match(r"^version:\s*(\S+)\s*$", line)
            if m:
                ver = m.group(1)
                break
        out.append((name, ver))
    return out

def plugin_versions():
    out = []
    base = os.path.join(root, "plugins")
    if os.path.isdir(base):
        for name in sorted(os.listdir(base)):
            p = os.path.join(base, name, ".claude-plugin/plugin.json")
            if os.path.isfile(p):
                out.append((name, json.load(open(p, encoding="utf-8"))["version"]))
    return out

lines = [START, "",
         f"**对外发布版本：`{release}`** — 用户安装/更新时看到的版本，也是驱动更新的唯一版本号。",
         "整包与 8 个技能条目共用它；发版时改它，用户下次自动收到更新。", ""]

pv = plugin_versions()
if pv:
    lines += ["独立插件（拥有自己的 `plugin.json`，版本独立生效）：", "",
              "| 插件 | 版本 |", "| --- | --- |"]
    lines += [f"| `{n}` | {v} |" for n, v in pv]
    lines += [""]

lines += ["各技能内部版本（仅记录该技能自身迭代，**不影响用户看到的版本**）：", "",
          "| 技能 | 内部版本 |", "| --- | --- |"]
lines += [f"| `{n}` | {v} |" for n, v in skill_versions()]
lines += ["", END]

rd_path = os.path.join(root, "README.md")
rd = open(rd_path, encoding="utf-8").read()
if START not in rd or END not in rd:
    print(f"⚠️  README.md 缺少 {START} / {END} 标记，跳过", file=sys.stderr)
    sys.exit(0)

rd = re.sub(re.escape(START) + r".*?" + re.escape(END), "\n".join(lines), rd, flags=re.S)
rd = re.sub(r"badge/version-[0-9][0-9.]*-blue\.svg", f"badge/version-{release}-blue.svg", rd)
open(rd_path, "w", encoding="utf-8").write(rd)

print(f"✅ README 已同步 · 对外发布版本 {release}")
for n, v in pv:
    print(f"   独立插件 {n:<26} {v}")
for n, v in skill_versions():
    print(f"   内部记录 {n:<26} {v}")
PY
}

# ── 入口 ──────────────────────────────────────────────────────

case "${1:-list}" in
  list)
    python3 - "$ROOT" <<'PY'
import json, os, re, sys
root = sys.argv[1]
rel = json.load(open(os.path.join(root, ".claude-plugin/plugin.json"), encoding="utf-8"))["version"]
print(f"对外发布版本  {rel}   ← 用户看到的、驱动更新的版本")
print()
for name in sorted(os.listdir(os.path.join(root, "plugins"))):
    p = os.path.join(root, "plugins", name, ".claude-plugin/plugin.json")
    if os.path.isfile(p):
        print(f"  独立插件  {name:<28} {json.load(open(p, encoding='utf-8'))['version']}")
print()
for name in sorted(os.listdir(os.path.join(root, "skills"))):
    p = os.path.join(root, "skills", name, "SKILL.md")
    if not os.path.isfile(p):
        continue
    ver = "❌ 缺失"
    for line in open(p, encoding="utf-8"):
        m = re.match(r"^version:\s*(\S+)\s*$", line)
        if m:
            ver = m.group(1); break
    print(f"  内部记录  {name:<28} {ver}")
PY
    ;;
  release)
    [ $# -eq 2 ] || die "用法：$0 release <版本>"
    check_version "$2"
    set_plugin_json_version ".claude-plugin/plugin.json" "$2"
    echo "对外发布版本 → $2"
    sync
    echo
    echo "下一步：git commit && git push（用户下次会自动收到更新）"
    ;;
  plugin)
    [ $# -eq 3 ] || die "用法：$0 plugin <插件名> <版本>"
    check_version "$3"
    f="plugins/$2/.claude-plugin/plugin.json"
    [ -f "$f" ] || die "找不到插件：$2"
    set_plugin_json_version "$f" "$3"
    echo "$2 → $3"
    sync
    ;;
  skill)
    [ $# -eq 3 ] || die "用法：$0 skill <技能名> <版本>"
    check_version "$3"
    set_skill_version "$2" "$3"
    echo "内部记录 $2 → $3（对外版本不变）"
    sync
    ;;
  sync)
    sync
    ;;
  *)
    sed -n '3,25p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    exit 2
    ;;
esac
