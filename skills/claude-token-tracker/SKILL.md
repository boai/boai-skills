---
name: claude-token-tracker
description: 统计并显示 Claude Code 所有历史对话累计消耗的 token 总数;通过 Stop hook 在每次回答结束后自动汇总。当用户想查看/安装/管理 token 用量、想知道一共花了多少 token、或要在新机器上启用「每轮自动显示历史累计 token」时使用。
triggers:
  - token 统计
  - 统计 token
  - token 用量
  - 累计 token
  - 历史 token
  - 每轮 token
  - 显示 token
  - 安装 token 统计
  - token usage
  - token tracker
platform: all
verified: macOS 26 + Claude Code (Opus 4.8) + 系统自带 python3
---

# Claude Token Tracker(历史累计 Token 统计)

在每次 Claude 回答结束后,自动统计并显示 `~/.claude/projects/` 下**所有历史会话**累计消耗的 token,而不只是当前这一段对话。

> **原理**:Claude Code 把每个会话记录成 `~/.claude/projects/<项目>/<会话>.jsonl`,每条 assistant 消息里带 `message.usage`(`input_tokens` / `output_tokens` / `cache_creation_input_tokens` / `cache_read_input_tokens`)。本 skill 安装一个 **Stop hook**,在每轮回答结束时触发一个 Python 脚本,累加所有 jsonl 的 usage,并以 `systemMessage` 形式显示一行汇总。

## 能力

- 每次回答末尾自动出现一行 `📊 历史累计 Token:…`
- 跨**所有项目、所有历史会话**累计(不只当前对话)
- 四项明细:输入 / 输出 / 缓存写 / 缓存读
- 增量缓存:旧会话只解析一次,稳态每轮仅重算当前活跃会话(~0.1s,几乎无感)
- 只读、纯本地、不联网

## 安装

### 第 1 步:放置统计脚本

把脚本放到 `~/.claude/hooks/`。优先用随 skill 分发的版本:

```bash
mkdir -p ~/.claude/hooks
SRC="${CLAUDE_PLUGIN_ROOT:-}/scripts/token-usage-summary.py"
if [ -f "$SRC" ]; then
  cp "$SRC" ~/.claude/hooks/token-usage-summary.py
  echo "✅ 已从分发包复制脚本"
else
  echo "⚠️ 未找到分发脚本,请按本文件末尾「附:脚本全文」手动写入 ~/.claude/hooks/token-usage-summary.py"
fi
```

若没找到分发脚本,就按本文件末尾的 **附:脚本全文** 创建 `~/.claude/hooks/token-usage-summary.py`。

### 第 2 步:自测脚本

```bash
echo '{}' | python3 ~/.claude/hooks/token-usage-summary.py
```

应输出一行形如 `{"systemMessage": "📊 历史累计 Token:…"}` 的 JSON。首次会全量建缓存(约 1 秒),之后走缓存很快。

### 第 3 步:注册 Stop hook

读 `~/.claude/settings.json`,把下面这段 **合并**进去(务必保留已有的全部设置,不要整体覆盖;若已存在 `hooks` 键,就往里加 `Stop` 数组):

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

合并后校验 JSON 合法:

```bash
python3 -c "import json; json.load(open('$HOME/.claude/settings.json')); print('settings.json 合法 ✓')"
```

### 第 4 步:生效

如果 `~/.claude/settings.json` 在本次会话启动前就已存在,设置监听器会热加载,**下一轮回答结束**就能看到 📊 行;否则打开一次 `/hooks` 或重启 Claude Code 即可加载。

## 显示效果

```
📊 历史累计 Token:总计 1,684,774,453(≈1.68B)｜输入 95.18M · 输出 9.88M · 缓存写 17.86M · 缓存读 1.56B｜179 个会话
```

> `cache_read`(缓存读)通常占大头——每轮都会复读已缓存的上下文,所以「总计」会显得很大;真正的**新增**处理量看「输入 + 输出」。

## 自定义

- **只统计输入+输出**(不含缓存):改脚本 `build_message()` 里的 `grand = sum(...)` 为 `grand = tot['input'] + tot['output']`。
- **改显示格式**:改 `build_message()` 末尾返回的那段 f-string。
- **改 hook 超时**:改 settings.json 里 Stop hook 的 `timeout`(秒)。
- **重置缓存**:删 `~/.claude/hooks/.token-usage-cache.json`,下次会全量重算。

## 卸载

1. 删掉 `~/.claude/settings.json` 里 `hooks.Stop` 那一段(如果 Stop 下只有这一个 hook,删掉整个 `Stop` 数组;别误删别的 hook)。
2. 删文件:

```bash
rm -f ~/.claude/hooks/token-usage-summary.py ~/.claude/hooks/.token-usage-cache.json
```

## 注意

- 脚本只**读** `~/.claude/projects/**/*.jsonl`,绝不修改任何会话数据。
- 纯本地运行,不联网、不上传任何内容。
- 跨平台:macOS / Linux / Windows 只要有 `python3` 和 `~/.claude` 即可(Windows 下 git-bash / PowerShell 里 `$HOME` 均成立)。
- 统计口径是「所有会话所有 `message.usage` 之和」,包含子 agent(subagent)的消耗,等于该机器上 Claude Code 处理过的真实 token 总量。

## 附:脚本全文

> 以下是 `scripts/token-usage-summary.py` 的完整内容,作为找不到分发文件时的兜底,与仓库 `scripts/` 中的版本保持一致。

```python
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
```
