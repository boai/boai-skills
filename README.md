# 🧰 boai skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](#) [![Platform: macOS](https://img.shields.io/badge/Platform-macOS-silver.svg)](#)

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

### 💬 mac-wechat-dual-instance — Mac 微信双开/多开

在 macOS 上同时运行多个微信实例，支持微信 4.x（Electron 架构）。

| 方法 | 适用人群 |
|------|----------|
| 🔧 手动三命令 | 熟悉终端、偶尔双开 |
| 🤖 WeChatMulti-macOS 脚本 | 需要多开、自动重建 |
| 🖥️ 交互式菜单 | 不熟悉终端 |

**核心原理**：复制应用 → 修改 Bundle ID → 重新签名。无需禁 SIP，无需 Rosetta 2，原生支持 Apple Silicon。

触发词：`微信双开` `微信多开` `Mac微信双开` `微信分身` `wechat dual` `wechat multi open`

### 🔒 mac-wechat-anti-recall — Mac 微信防撤回

防止 Mac 微信中的消息被撤回，全类型消息支持（文字/图片/视频/语音/表情/文件/小程序/拍一拍等）。

| 方案 | 微信版本 | 芯片支持 | 活跃度 |
|------|:------:|:------:|:------:|
| 🔌 **X1a0HeWeChatPlugin** | 4.1.x ✅ | ARM64 | 🟢 活跃 |
| 🔧 WeChatTweak-macOS | ≤4.0 ✅ | 通用 | 🟡 较慢 |

**附带功能**：微信多开、禁用日志上报、禁用更新检测、自定义撤回提示。

> ⚠️ 第三方注入有理论封号风险，建议大号仅用防撤回，多开仅在工号/小号使用。

触发词：`微信防撤回` `防撤回` `微信撤回拦截` `Mac微信防撤回` `wechat anti recall` `anti revoke`

## 📁 目录结构

```
boai-skills/
├── .claude-plugin/plugin.json     ← 插件注册（新增技能改这里）
├── skills/
│   ├── sogou-ad-killer/SKILL.md   ← 搜狗广告清理
│   ├── 360-cleaner/SKILL.md       ← 360 软件管理器
│   ├── mac-wechat-dual-instance/SKILL.md  ← Mac 微信双开
│   └── mac-wechat-anti-recall/SKILL.md    ← Mac 微信防撤回
├── scripts/                       ← 独立脚本（可脱离 Claude 运行）
├── README.md
└── LICENSE
```

## 👤 作者

**博爱 (boai)** — [GitHub](https://github.com/boai)

## 📄 许可

MIT License
