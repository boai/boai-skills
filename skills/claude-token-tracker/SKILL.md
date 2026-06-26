---
name: claude-token-tracker
description: 统计并显示 Claude Code 的 token 用量，分「当前对话 / 今日 / 当月 / 历史全部」四个维度多行展示；通过 Stop hook 在每次回答结束后自动汇总。当用户想查看/安装/管理 token 用量、想知道某段时间或一共花了多少 token、或要在新机器上启用「每轮自动显示 token 统计」时使用。
triggers:
  - token 统计
  - 统计 token
  - token 用量
  - 累计 token
  - 历史 token
  - 今日 token
  - 本月 token
  - 每轮 token
  - 显示 token
  - 安装 token 统计
  - token usage
  - token tracker
platform: all
verified: macOS 26 + Claude Code (Opus 4.8) + 系统自带 python3
---

# Claude Token Tracker（Token 用量统计）

在每次 Claude 回答结束后，自动统计并多行显示 token 用量，分四个维度：

- **🗨️ 当前对话** —— 本次会话累计
- **📅 今日** —— 今天所有会话（按消息时间、本地时区归类）
- **🗓️ 本月** —— 本月所有会话
- **📚 历史全部** —— 所有会话、所有时间

每个维度都给出明细（输入 / 输出 / 缓存写 / 缓存读）和合计。

> **原理**：Claude Code 把每个会话记录成 `~/.claude/projects/<项目>/<会话>.jsonl`，每条 assistant 消息带 `message.usage`（四类 token）和 `timestamp`。本 skill 安装一个 **Stop hook**，每轮回答结束触发 Python 脚本：用 hook 传入的 `transcript_path` 锁定「当前对话」，用每条消息的 `timestamp`（转本地时区）归类「今日 / 本月」，并汇总「历史全部」，以 `systemMessage` 多行展示。

## 显示效果

```
📊 Claude Token 用量

🗨️ 当前对话｜合计 21.61M
   输入 47.3K · 输出 544.8K · 缓存写 4.37M · 缓存读 16.64M
📅 今日 06-26｜合计 144.08M
   输入 1.08M · 输出 1.41M · 缓存写 7.64M · 缓存读 133.94M
🗓️ 本月 2026-06｜合计 1.65B
   输入 24.62M · 输出 10.36M · 缓存写 23.90M · 缓存读 1.59B
📚 历史全部｜合计 1.74B
   输入 95.25M · 输出 10.81M · 缓存写 24.01M · 缓存读 1.61B
   （共 182 个会话）
```

> `cache_read`（缓存读）通常占大头——每轮都会复读已缓存的上下文，所以「合计」会显得很大；真正的**新增**处理量看「输入 + 输出」。

## 能力

- 四维度统计：当前对话 / 今日 / 当月 / 历史全部，各含明细 + 合计
- 「今日 / 本月」按每条消息的 `timestamp` 转**本地时区**精确归类
- 增量缓存（按文件 + 本地日期分桶）：旧会话只解析一次，稳态每轮仅重算当前活跃会话（~0.1s，几乎无感）
- 只读、纯本地、不联网

## 安装

### 第 1 步：放置统计脚本

```bash
mkdir -p ~/.claude/hooks
SRC="${CLAUDE_PLUGIN_ROOT:-}/scripts/token-usage-summary.py"
if [ -f "$SRC" ]; then
  cp "$SRC" ~/.claude/hooks/token-usage-summary.py
  echo "✅ 已从分发包复制脚本"
else
  echo "⚠️ 未找到分发脚本，请按本文件末尾「附：脚本全文」手动写入 ~/.claude/hooks/token-usage-summary.py"
fi
```

若没找到分发脚本，就按本文件末尾的 **附：脚本全文** 创建 `~/.claude/hooks/token-usage-summary.py`。

### 第 2 步：自测脚本

```bash
echo '{}' | python3 ~/.claude/hooks/token-usage-summary.py
```

应输出一行 JSON，其 `systemMessage` 字段是多行统计文本。首次会全量建缓存（约 1 秒），之后走缓存很快。

### 第 3 步：注册 Stop hook

读 `~/.claude/settings.json`，把下面这段 **合并**进去（务必保留已有的全部设置，不要整体覆盖；若已存在 `hooks` 键，就往 `Stop` 数组里追加一个对象）：

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 $HOME/.claude/hooks/token-usage-summary.py",
            "timeout": 15,
            "suppressOutput": true
          }
        ]
      }
    ]
  }
}
```

合并后校验 JSON 合法：

```bash
python3 -c "import json; json.load(open('$HOME/.claude/settings.json')); print('settings.json 合法 ✓')"
```

### 第 4 步：生效

如果 `~/.claude/settings.json` 在本次会话启动前就已存在，设置监听器会热加载，**下一轮回答结束**就能看到统计；否则打开一次 `/hooks` 或重启 Claude Code。

## 自定义

- **时区**：脚本用系统本地时区归类「今日 / 本月」（`datetime.astimezone()`）。如需固定某时区，改 `local_day()`。
- **只统计输入+输出**（不含缓存）：改 `fmt_block()` 里的合计与明细，或在汇总处只累加前两项。
- **改显示格式 / 维度**：改 `fmt_block()` 与 `build_message()` 末尾拼装 `lines` 的部分。
- **重置缓存**：删 `~/.claude/hooks/.token-usage-cache.json`（v2 结构，按日期分桶），下次会全量重算。

## 卸载

1. 删掉 `~/.claude/settings.json` 里 `hooks.Stop` 中本 hook 对应的那个对象（若 Stop 下只有它，删掉整个 `Stop` 数组；别误删别的 hook）。
2. 删文件：

```bash
rm -f ~/.claude/hooks/token-usage-summary.py ~/.claude/hooks/.token-usage-cache.json
```

## 注意

- 脚本只**读** `~/.claude/projects/**/*.jsonl`，绝不修改任何会话数据。
- 纯本地运行，不联网、不上传任何内容。
- 跨平台：macOS / Linux / Windows 只要有 `python3` 和 `~/.claude` 即可（Windows 下 git-bash / PowerShell 里 `$HOME` 均成立）。
- 统计口径是「所有会话所有 `message.usage` 之和」，包含子 agent（subagent）的消耗，等于该机器上 Claude Code 处理过的真实 token 总量。
- 「当前对话」依赖 hook 传入的 `transcript_path`；手动运行（无该字段）时该项显示「—」，其余维度正常。

## 附：脚本全文

> 以下是 `scripts/token-usage-summary.py` 的完整内容，作为找不到分发文件时的兜底，与仓库 `scripts/` 中的版本保持一致。

```python
#!/usr/bin/env python3
"""Stop hook: 统计 Claude Code 的 token 用量,分四个维度多行展示。

维度:
- 当前对话:本次会话(由 hook stdin 的 transcript_path 指定)的累计
- 今日 / 本月:按每条消息的 timestamp(转本地时区)归类
- 历史全部:所有会话、所有时间

为避免每次全量解析(~80MB+)拖慢回复,按 文件 -> (mtime:size) 增量缓存:
每个文件缓存「按本地日期分桶」的 token,旧文件命中缓存,稳态只重算当前活跃会话。
"""
import os
import sys
import glob
import json
from datetime import datetime, timezone

PROJECTS = os.path.expanduser("~/.claude/projects")
CACHE = os.path.expanduser("~/.claude/hooks/.token-usage-cache.json")
CACHE_VERSION = 2

FIELDS = ("input_tokens", "output_tokens",
          "cache_creation_input_tokens", "cache_read_input_tokens")


def local_day(ts):
    """ISO8601 时间戳 -> 本地日期 'YYYY-MM-DD';解析失败返回 'unknown'。"""
    if not isinstance(ts, str) or "T" not in ts:
        return "unknown"
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        try:  # 退路:截断到秒,按 UTC 处理
            dt = datetime.fromisoformat(ts[:19]).replace(tzinfo=timezone.utc)
        except Exception:
            return "unknown"
    try:
        return dt.astimezone().strftime("%Y-%m-%d")
    except Exception:
        return "unknown"


def parse_file(path):
    """解析一个 jsonl,返回 {本地日期: [in, out, cc, cr]}。"""
    days = {}
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                msg = obj.get("message")
                if not isinstance(msg, dict):
                    continue
                u = msg.get("usage")
                if not isinstance(u, dict):
                    continue
                bucket = days.setdefault(local_day(obj.get("timestamp")), [0, 0, 0, 0])
                for i, f in enumerate(FIELDS):
                    v = u.get(f, 0)
                    if isinstance(v, (int, float)):
                        bucket[i] += int(v)
    except OSError:
        pass
    return days


def human(n):
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.2f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def add(dst, src):
    for i in range(4):
        dst[i] += src[i]


def read_stdin_transcript():
    """从 hook stdin 读取 transcript_path;无管道/无字段则返回 None。"""
    try:
        if sys.stdin.isatty():
            return None
        raw = sys.stdin.read()
        if not raw.strip():
            return None
        tp = json.loads(raw).get("transcript_path")
        if tp:
            return os.path.realpath(os.path.expanduser(tp))
    except Exception:
        pass
    return None


def load_cache():
    try:
        with open(CACHE, encoding="utf-8") as f:
            c = json.load(f)
        if isinstance(c, dict) and c.get("_v") == CACHE_VERSION and isinstance(c.get("files"), dict):
            return c["files"]
    except Exception:
        pass
    return {}


def save_cache(files):
    try:
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        tmp = CACHE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"_v": CACHE_VERSION, "files": files}, f)
        os.replace(tmp, CACHE)
    except Exception:
        pass


def fmt_block(title, vals):
    """两行:标题+合计,缩进明细。"""
    return (f"{title}｜合计 {human(sum(vals))}\n"
            f"   输入 {human(vals[0])} · 输出 {human(vals[1])}"
            f" · 缓存写 {human(vals[2])} · 缓存读 {human(vals[3])}")


def build_message(transcript_path):
    if not os.path.isdir(PROJECTS):
        return "📊 Claude Token 用量:暂无会话记录"

    cache = load_cache()
    files = glob.glob(os.path.join(PROJECTS, "**", "*.jsonl"), recursive=True)
    new_cache = {}

    now = datetime.now().astimezone()
    today, month = now.strftime("%Y-%m-%d"), now.strftime("%Y-%m")

    all_t = [0, 0, 0, 0]
    today_t = [0, 0, 0, 0]
    month_t = [0, 0, 0, 0]
    cur_t = [0, 0, 0, 0]

    for path in files:
        rp = os.path.realpath(path)
        try:
            st = os.stat(path)
        except OSError:
            continue
        sig = f"{int(st.st_mtime)}:{st.st_size}"
        ent = cache.get(rp)
        if isinstance(ent, dict) and ent.get("sig") == sig and isinstance(ent.get("days"), dict):
            days = ent["days"]
        else:
            days = parse_file(path)
        new_cache[rp] = {"sig": sig, "days": days}

        is_current = transcript_path is not None and rp == transcript_path
        for day, vals in days.items():
            add(all_t, vals)
            if day == today:
                add(today_t, vals)
            if day.startswith(month):
                add(month_t, vals)
            if is_current:
                add(cur_t, vals)

    save_cache(new_cache)

    lines = ["📊 Claude Token 用量", ""]
    if transcript_path is not None:
        lines.append(fmt_block("🗨️ 当前对话", cur_t))
    else:
        lines.append("🗨️ 当前对话｜—(手动运行,无会话上下文)")
    lines.append(fmt_block(f"📅 今日 {now.strftime('%m-%d')}", today_t))
    lines.append(fmt_block(f"🗓️ 本月 {month}", month_t))
    lines.append(fmt_block("📚 历史全部", all_t) + f"\n   （共 {len(files)} 个会话）")
    return "\n".join(lines)


def main():
    transcript_path = read_stdin_transcript()
    try:
        msg = build_message(transcript_path)
    except Exception as e:
        msg = f"📊 Claude Token 用量统计失败:{e}"
    print(json.dumps({"systemMessage": msg}, ensure_ascii=False))


if __name__ == "__main__":
    main()
```
