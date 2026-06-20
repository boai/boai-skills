# 🧰 BoAi Skills — 博爱哥哥的 Claude Code 技能合集

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](#)

> Claude Code 插件 | 实用技能合集，持续扩充中

## 一键安装

```
/plugin install boai-skills@claude-plugins-official
```

## 📦 已收录技能

### 🧹 sogou-ad-killer — 搜狗输入法广告清理

永久关闭搜狗输入法所有广告，释放 200MB+ 内存。

| 广告类型 | 组件 | 状态 |
|----------|------|------|
| 🛒 商业推广卡片 | `biz_center` | ✅ 已禁用 |
| 🎮 游戏推荐弹窗 | `game_center` | ✅ 已禁用 |
| 💬 桌面右下角广告 | `SGDeskControl` | ✅ 已禁用 |
| 🖥️ Chromium 广告引擎 (占 ~200MB) | `SGRender` (CEF) | ✅ 已禁用 |
| ✍️ 写作助手推荐 | `WriteSpirit` | ✅ 已禁用 |
| ☁️ 云端推荐 | `SogouCloud.exe` | ✅ 已禁用 |
| ⏰ 广告定时推送 | `userNetSchedule.exe` | ✅ 已禁用 |

**共禁用 31+ 广告组件，全部可逆（.bak 重命名，不删除）**

触发词：`去搜狗广告` `关闭搜狗广告` `sogou ad killer`

### 🔮 更多技能开发中...

欢迎提 Issue 建议新技能方向！

## 📁 目录结构

```
boai-skills/
├── .claude-plugin/plugin.json     ← 插件注册（新增技能改这里）
├── skills/
│   └── sogou-ad-killer/SKILL.md   ← 搜狗广告清理
│   └── <your-skill-here>/         ← 新技能放这里！
├── scripts/                       ← 独立脚本（可脱离 Claude 运行）
├── README.md
└── LICENSE
```

## 👤 作者

**博爱哥哥 (BoAi)** — [GitHub](https://github.com/boai-dev)

## 📄 许可

MIT License
