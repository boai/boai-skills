# 🧰 boai skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](#)
[![Platform: macOS](https://img.shields.io/badge/Platform-macOS-silver.svg)](#)

> Claude Code 插件 · 实用技能合集，持续更新

## 安装

```
/plugin install boai-skills@claude-plugins-official
```

## 只想用其中某一个技能？

不装整个合集也行——Claude Code 会自动加载 `~/.claude/skills/` 下的技能，把你要的那个目录放进去即可。下面以 **claude-token-tracker** 为例（换成任意技能名同理）。

> 本仓库为私有仓库，下面的 `git clone` 会走你本机已有的 GitHub 凭证。

**方式一：整仓 clone，只复制需要的技能（最简单）**

```bash
git clone https://github.com/boai/boai-skills.git
mkdir -p ~/.claude/skills
cp -r boai-skills/skills/claude-token-tracker ~/.claude/skills/
```

**方式二：稀疏 clone，只拉单个技能（省空间）**

```bash
git clone --filter=blob:none --sparse https://github.com/boai/boai-skills.git
cd boai-skills
git sparse-checkout set skills/claude-token-tracker scripts
mkdir -p ~/.claude/skills
cp -r skills/claude-token-tracker ~/.claude/skills/
```

复制完成后**重启 Claude Code**（或打开一次 `/skills` 刷新），技能即出现在列表中；之后提到它的触发词（claude-token-tracker 为 `token 统计` `累计 token` `token usage`）即可使用。例如对 Claude 说「安装 token 统计」，它就会按 `SKILL.md` 把 Stop hook 装好。

> 只想对某个项目生效？把目录复制到该项目的 `.claude/skills/` 而非 `~/.claude/skills/` 即可。

**关于脚本依赖**：个别技能会用到仓库根 `scripts/` 下的脚本。`claude-token-tracker` 的脚本已内联在它的 `SKILL.md` 中（找不到分发文件时自动兜底），单独取用也能正常安装；其它依赖脚本的技能，按方式二把 `scripts` 一并 checkout 即可。

## 收录技能

### 🌐 通用 / 内容创作

| 技能 | 说明 | 触发词 |
|------|------|--------|
| 📝 **boai-article-writer** | 微信公众号文章全流程：选题调研→文章撰写→配图→封面设计→发布检查 | `写文章` `公众号文章` `写一篇文章` |
| 📊 **claude-token-tracker** | 每次回答后自动统计所有历史对话累计消耗的 token，跨会话汇总显示 | `token 统计` `累计 token` `token usage` |

### 🪟 Windows

| 技能 | 说明 | 触发词 |
|------|------|--------|
| 🧹 **sogou-ad-killer** | 扫描所有搜狗产品，手动勾选关闭广告，一键全禁预设 | `去搜狗广告` `sogou ad killer` `管理搜狗` |
| 🔧 **360-cleaner** | 扫描系统所有360产品，手动勾选卸载，含快捷预设 | `清理360` `卸载360` `管理360` |

### 🍎 macOS

| 技能 | 说明 | 触发词 |
|------|------|--------|
| 💬 **mac-wechat-dual-instance** | 微信双开/多开，无需禁SIP，原生Apple Silicon | `微信双开` `微信分身` `wechat dual` |
| 🔒 **mac-wechat-anti-recall** | 微信防撤回，全消息类型支持，附带去日志/去更新 | `微信防撤回` `anti recall` `anti revoke` |

## 目录结构

```plaintext
boai-skills/
├── .claude-plugin/plugin.json
├── skills/
│   ├── boai-article-writer/SKILL.md
│   ├── claude-token-tracker/SKILL.md
│   ├── sogou-ad-killer/SKILL.md
│   ├── 360-cleaner/SKILL.md
│   ├── mac-wechat-dual-instance/SKILL.md
│   └── mac-wechat-anti-recall/SKILL.md
├── scripts/
│   ├── sogou_ad_killer.ps1
│   └── token-usage-summary.py
├── README.md
└── LICENSE
```

## 许可

MIT License
