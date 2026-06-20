# 🧰 boai skills

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

### 🧹 360-cleaner — 360 软件管理器

扫描系统上所有360旗下软件，由用户**手动勾选**要卸载的产品。

| 功能 | 说明 |
|------|------|
| 🔍 全面扫描 | 检测 17 种360产品 + 残留物 |
| ✅ 手动勾选 | 用户自主选择删哪些、留哪些 |
| ⚡ 快捷预设 | 一键「仅保留驱动和压缩」/「全部删除」 |
| 🧹 深度清理 | 程序目录 + 用户数据 + 注册表 + 驱动 + 服务 |

触发词：`清理360` `卸载360` `删除360` `360残留` `clean 360` `管理360`

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

**博爱 (boai)** — [GitHub](https://github.com/boai)

## 📄 许可

MIT License
