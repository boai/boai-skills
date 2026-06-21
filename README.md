# 🧰 boai skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](#)
[![Platform: macOS](https://img.shields.io/badge/Platform-macOS-silver.svg)](#)

> Claude Code 插件 · 实用技能合集，持续更新

## 安装

```
/plugin install boai-skills@claude-plugins-official
```

## 收录技能

### 🌐 通用 / 内容创作

| 技能 | 说明 | 触发词 |
|------|------|--------|
| 🎬 **boai-film-review** | 公众号"博爱光影"影评全流程：选题调研→文章撰写→TMDb配图→Vision识图→封面设计→发布检查 | `写影评` `公众号影评` `博爱光影` `写一篇XX影评` |

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
│   ├── boai-film-review/SKILL.md
│   ├── sogou-ad-killer/SKILL.md
│   ├── 360-cleaner/SKILL.md
│   ├── mac-wechat-dual-instance/SKILL.md
│   └── mac-wechat-anti-recall/SKILL.md
├── scripts/
├── README.md
└── LICENSE
```

## 作者

| 角色 | 名称 |
|------|------|
| 🧑‍💻 作者 | **博爱 (boai)** — [GitHub](https://github.com/boai) |
| 🤖 联合创作 | **Claude** & **Claude Code** — powered by Anthropic |

> 本项目由博爱与 Claude Code 协作完成 —— 从需求分析、方案设计到代码编写、文档输出，全流程 AI 协同。

## 许可

MIT License
