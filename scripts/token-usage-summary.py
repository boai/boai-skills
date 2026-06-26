#!/usr/bin/env python3
"""Stop hook: 汇总 ~/.claude/projects 下所有会话 transcript 的 token 用量。

输出一行 systemMessage(JSON)给 Claude Code,在每次回答结束后显示历史累计 token。
为避免每次全量解析 ~80MB+ 的 transcript 拖慢回复,按 文件路径->(mtime:size) 做增量缓存:
只有变化过的文件(主要是当前活跃会话)才会被重新解析,其余直接复用缓存。
"""
import os
import glob
import json

PROJECTS = os.path.expanduser("~/.claude/projects")
CACHE = os.path.expanduser("~/.claude/hooks/.token-usage-cache.json")

KEYS = ("input", "output", "cc", "cr")
FIELDS = {
    "input": "input_tokens",
    "output": "output_tokens",
    "cc": "cache_creation_input_tokens",
    "cr": "cache_read_input_tokens",
}


def parse_file(path):
    t = {k: 0 for k in KEYS}
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
                for k, field in FIELDS.items():
                    v = u.get(field, 0)
                    if isinstance(v, (int, float)):
                        t[k] += int(v)
    except OSError:
        pass
    return t


def human(n):
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.2f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def build_message():
    if not os.path.isdir(PROJECTS):
        return "📊 历史累计 Token:暂无会话记录"

    cache = {}
    try:
        with open(CACHE, encoding="utf-8") as f:
            loaded = json.load(f)
        if isinstance(loaded, dict):
            cache = loaded
    except Exception:
        cache = {}

    files = glob.glob(os.path.join(PROJECTS, "**", "*.jsonl"), recursive=True)
    new_cache = {}
    tot = {k: 0 for k in KEYS}

    for path in files:
        try:
            st = os.stat(path)
        except OSError:
            continue
        sig = f"{int(st.st_mtime)}:{st.st_size}"
        ent = cache.get(path)
        if isinstance(ent, dict) and ent.get("sig") == sig and isinstance(ent.get("data"), dict):
            data = ent["data"]
        else:
            data = parse_file(path)
        new_cache[path] = {"sig": sig, "data": data}
        for k in KEYS:
            tot[k] += int(data.get(k, 0))

    # 原子写回缓存
    try:
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        tmp = CACHE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(new_cache, f)
        os.replace(tmp, CACHE)
    except Exception:
        pass

    grand = sum(tot[k] for k in KEYS)
    return (
        f"📊 历史累计 Token:总计 {grand:,}(≈{human(grand)})"
        f"｜输入 {human(tot['input'])} · 输出 {human(tot['output'])}"
        f" · 缓存写 {human(tot['cc'])} · 缓存读 {human(tot['cr'])}"
        f"｜{len(files)} 个会话"
    )


def main():
    try:
        msg = build_message()
    except Exception as e:
        msg = f"📊 历史累计 Token 统计失败:{e}"
    print(json.dumps({"systemMessage": msg}, ensure_ascii=False))


if __name__ == "__main__":
    main()
