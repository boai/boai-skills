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

### ⭐ claude-token-tracker —— 自动 token 统计（无需触发词）

```
/plugin install claude-token-tracker@boai-skills
```

装完后**重启 Claude Code**（或 `/reload-plugins`）。之后**正常对话即可，每轮回答结束会自动打印 token 统计**（当前对话 / 今日 / 本月 / 历史全部）——它是一个 Stop hook，**不需要你说任何提示词**。

### 其他技能（提到触发词时启用）

整包安装全部技能：

```
/plugin install boai-skills@boai-skills
```

或只装某一个：

| 技能 | 安装命令 |
|------|----------|
| 📝 boai-article-writer | `/plugin install boai-article-writer@boai-skills` |
| 🧹 sogou-ad-killer | `/plugin install sogou-ad-killer@boai-skills` |
| 🔧 360-cleaner | `/plugin install 360-cleaner@boai-skills` |
| 💬 mac-wechat-dual-instance | `/plugin install mac-wechat-dual-instance@boai-skills` |
| 🔒 mac-wechat-anti-recall | `/plugin install mac-wechat-anti-recall@boai-skills` |

装完执行 `/reload-plugins` 让当前会话立即生效（或重启 Claude Code）。要卸载或管理已装插件，打开 `/plugin` 面板即可。

## 收录内容

### ⚙️ 自动运行（hook，无需触发词）

| 插件 | 说明 | 启用方式 |
|------|------|----------|
| 📊 **claude-token-tracker** | 每轮回答结束自动显示 token 用量：当前对话 / 今日 / 本月 / 历史全部，各含明细+合计 | 装完重启即自动运行 |

### 🌐 通用 / 内容创作（技能，提到触发词时启用）

| 技能 | 说明 | 触发词 |
|------|------|--------|
| 📝 **boai-article-writer** | 微信公众号文章全流程：选题调研→文章撰写→配图→封面设计→发布检查 | `写文章` `公众号文章` `写一篇文章` |

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
│   ├── marketplace.json      # 市场清单：整包 + 各技能/插件可单独安装
│   └── plugin.json           # 整包 plugin 清单（5 个触发式技能）
├── plugins/
│   └── claude-token-tracker/ # 自动 token 统计（Stop hook 插件）
│       ├── .claude-plugin/plugin.json
│       ├── hooks/hooks.json
│       └── scripts/token-usage-summary.py
├── skills/                   # 触发式技能
│   ├── boai-article-writer/SKILL.md
│   ├── sogou-ad-killer/SKILL.md
│   ├── 360-cleaner/SKILL.md
│   ├── mac-wechat-dual-instance/SKILL.md
│   └── mac-wechat-anti-recall/SKILL.md
├── scripts/                  # Windows 脚本等
│   └── sogou_ad_killer.ps1
├── README.md
└── LICENSE
```

## 许可

MIT License
