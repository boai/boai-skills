# 🧰 boai skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](#)
[![Platform: macOS](https://img.shields.io/badge/Platform-macOS-silver.svg)](#)

> Claude Code 插件 · 实用技能合集，持续更新

## 安装

先把本仓库添加为 marketplace（只需做一次）：

```
/plugin marketplace add boai/boai-skills
```

> 私有仓库会自动走你本机已有的 git 凭证（和 `git clone` 一样），**无需手动 clone 代码**。

### 整包安装（全部技能）

```
/plugin install boai-skills@boai-skills
```

### 只装某一个技能

只想要其中一个，就装那一个，互不影响。例如只装 token 统计：

```
/plugin install claude-token-tracker@boai-skills
```

可单独安装的技能：

| 技能 | 安装命令 |
|------|----------|
| 📊 claude-token-tracker | `/plugin install claude-token-tracker@boai-skills` |
| 📝 boai-article-writer | `/plugin install boai-article-writer@boai-skills` |
| 🧹 sogou-ad-killer | `/plugin install sogou-ad-killer@boai-skills` |
| 🔧 360-cleaner | `/plugin install 360-cleaner@boai-skills` |
| 💬 mac-wechat-dual-instance | `/plugin install mac-wechat-dual-instance@boai-skills` |
| 🔒 mac-wechat-anti-recall | `/plugin install mac-wechat-anti-recall@boai-skills` |

装完执行 `/reload-plugins` 让当前会话立即生效（或重启 Claude Code）。要卸载或管理已装插件，打开 `/plugin` 面板即可。

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
├── .claude-plugin/
│   ├── marketplace.json      # 市场清单：整包 + 每个技能可单独安装
│   └── plugin.json           # 整包 plugin 清单
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
