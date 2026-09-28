#!/usr/bin/env python3
"""Stop hook: 统计 Claude Code 的 token 用量,分四个维度多行展示。

维度:
- 当前对话:本次会话(由 hook stdin 的 transcript_path 指定)的累计
- 今日 / 本月:按每条消息的 timestamp(转本地时区)归类
- 历史全部:所有会话、所有时间

为避免每次全量解析(~80MB+)拖慢回复,按 文件 -> (mtime:size) 增量缓存:
每个文件缓存「按本地日期分桶」的 token,旧文件命中缓存,稳态只重算当前活跃会话。
"""

import os, sys, glob, json
from datetime import datetime, timezone

PROJECTS = os.path.expanduser("~/.claude/projects")
CACHE = os.path.expanduser("~/.claude/hooks/.token-usage-cache.json")
CACHE_VERSION = 3

FIELDS = (
    "input_tokens",
    "output_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
)

def local_day(ts):
    """ISO8601 时间戳 → 本地日期 'YYYY-MM-DD'."""
    if not isinstance(ts, str) or "T" not in ts:
        return "unknown"
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        try:
            dt = datetime.fromisoformat(ts[:19]).replace(tzinfo=timezone.utc)
        except Exception:
            return "unknown"
    try:
        return dt.astimezone().strftime("%Y-%m-%d")
    except Exception:
        return "unknown"

def parse_file(path):
    """解析一个 jsonl,返回 {本地日期: [input, output, cache_creation, cache_read]}."""
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
                bucket = days.setdefault(
                    local_day(obj.get("timestamp")), [0, 0, 0, 0]
                )
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
    """从 hook stdin 读取 transcript_path."""
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
        if (
            isinstance(c, dict)
            and c.get("_v") == CACHE_VERSION
            and isinstance(c.get("files"), dict)
        ):
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
    """双行格式: 标题 · 有效消耗 + 明细."""
    effective = vals[0] + vals[1] + vals[2]
    raw_total = effective + vals[3]
    lines = [
        f"{title} · 有效消耗 {human(effective)}",
        f"   输入 {human(vals[0])} · 输出 {human(vals[1])} · 缓存写 {human(vals[2])}",
    ]
    if vals[3] > 0:
        pct = vals[3] / raw_total * 100 if raw_total > 0 else 0
        if pct > 20:
            lines.append(
                f"   (含缓存读的原始合计: {human(raw_total)}, 缓存读占比 {pct:.1f}%)"
            )
    return "\n".join(lines)

def build_message(transcript_path):
    if not os.path.isdir(PROJECTS):
        return "📊 Token 消耗统计: 暂无会话记录"

    cache = load_cache()
    files = glob.glob(os.path.join(PROJECTS, "**", "*.jsonl"), recursive=True)
    new_cache = {}

    now = datetime.now().astimezone()
    today, month = now.strftime("%Y-%m-%d"), now.strftime("%Y-%m")

    all_t = [0, 0, 0, 0]
    today_t = [0, 0, 0, 0]
    month_t = [0, 0, 0, 0]
    cur_t = [0, 0, 0, 0]
    cur_sub_t = [0, 0, 0, 0]

    cur_dir = None
    if transcript_path is not None:
        cur_dir = os.path.dirname(transcript_path)

    for path in files:
        rp = os.path.realpath(path)
        try:
            st = os.stat(path)
        except OSError:
            continue
        sig = f"{int(st.st_mtime)}:{st.st_size}"
        ent = cache.get(rp)
        if (
            isinstance(ent, dict)
            and ent.get("sig") == sig
            and isinstance(ent.get("days"), dict)
        ):
            days = ent["days"]
        else:
            days = parse_file(path)
        new_cache[rp] = {"sig": sig, "days": days}

        is_current = transcript_path is not None and rp == transcript_path
        is_current_sub = (
            transcript_path is not None
            and cur_dir is not None
            and "/subagents/" in rp
            and os.path.dirname(rp).startswith(cur_dir + "/subagents")
        )

        for day, vals in days.items():
            add(all_t, vals)
            if day == today:
                add(today_t, vals)
            if day.startswith(month):
                add(month_t, vals)
            if is_current:
                add(cur_t, vals)
            if is_current_sub:
                add(cur_sub_t, vals)

    save_cache(new_cache)

    cur_total = [cur_t[i] + cur_sub_t[i] for i in range(4)]
    has_cur = transcript_path is not None and sum(cur_total) > 0

    lines = ["📊 Token 消耗统计 (boai-skills/claude-token-tracker)", ""]

    if has_cur:
        cur_effective = cur_total[0] + cur_total[1] + cur_total[2]
        lines.append(f"💬 当前会话 · 有效消耗 {human(cur_effective)}")
        lines.append(f"   输入 {human(cur_total[0])} · 输出 {human(cur_total[1])} · 缓存写 {human(cur_total[2])}")
        if cur_sub_t[0] + cur_sub_t[1] + cur_sub_t[2] > 0:
            sub_eff = cur_sub_t[0] + cur_sub_t[1] + cur_sub_t[2]
            lines.append(f"   (含子 Agent: 有效 {human(sub_eff)})")
        raw_cur = sum(cur_total)
        if cur_total[3] > 0:
            pct = cur_total[3] / raw_cur * 100 if raw_cur > 0 else 0
            if pct > 20:
                lines.append(f"   (含缓存读的原始合计: {human(raw_cur)}, 缓存读占比 {pct:.1f}%)")
        lines.append("")

    lines.append(fmt_block(f"🗨️ 今日 {now.strftime('%m-%d')}", today_t))
    lines.append(fmt_block(f"🗓️ 本月 {month}", month_t))
    lines.append(
        fmt_block("📚 历史全部", all_t)
        + f"\n   共 {len(files)} 个会话文件"
    )

    lines.append("")
    lines.append("💡 有效消耗 = 输入 + 输出 + 缓存写 (排除 ~0.1× 成本的缓存读)")

    return "\n".join(lines)

def main():
    transcript_path = read_stdin_transcript()
    try:
        msg = build_message(transcript_path)
    except Exception as e:
        msg = f"📊 Token 消耗统计失败: {e}"
    print(json.dumps({"systemMessage": msg}, ensure_ascii=False))

if __name__ == "__main__":
    main()
