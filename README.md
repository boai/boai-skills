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

### 🧹 360-cleaner — 360软件残留清理

清理系统上除「360驱动大师」和「360压缩」之外的所有360残留。

| 残留类型 | 位置 | 状态 |
|----------|------|------|
| 🛡️ 360安全卫士残留 | `ProgramData`, `AppData` | ❌ 清理 |
| 🦠 360杀毒残留 | `360sd` | ❌ 清理 |
| 🌐 360浏览器缓存 | `360se` 图标缓存 | ❌ 清理 |
| 🧑‍🔧 专家服务缓存 | `helpton.360.cn` | ❌ 清理 |
| 🔧 360驱动大师 | `360DrvMgr` | ✅ 保留 |
| 🗜️ 360压缩 | `360zip` | ✅ 保留 |
| 🔌 安全卫士驱动 | `360reskit64.sys` | ❌ 清理（需管理员权限）|

触发词：`清理360` `卸载360` `删除360` `360残留` `clean 360`

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
