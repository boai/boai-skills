# 🧹 Sogou Ad Killer — 搜狗输入法广告清理

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](#)
[![Version: 1.0.0](https://img.shields.io/badge/Version-1.0.0-green.svg)](#)

> Claude Code 插件 | 永久关闭搜狗输入法所有广告，释放 200MB+ 内存

## 一键安装

在 Claude Code 中运行：

```
/plugin install sogou-ad-killer@claude-plugins-official
```

或通过 `/plugin` → Discover → 搜索 "sogou ad"

## 效果

| 广告类型 | 组件 | 状态 |
|----------|------|------|
| 🛒 商业推广卡片 | `biz_center` | ✅ 已禁用 |
| 🎮 游戏推荐弹窗 | `game_center` | ✅ 已禁用 |
| 💬 桌面右下角广告 | `SGDeskControl` | ✅ 已禁用 |
| 🖥️ Chromium 广告引擎 (占 ~200MB) | `SGRender` (CEF) | ✅ 已禁用 |
| ✍️ 写作助手推荐 | `WriteSpirit` | ✅ 已禁用 |
| ☁️ 云端推荐 | `SogouCloud.exe` | ✅ 已禁用 |
| ⏰ 广告定时推送 | `userNetSchedule.exe` | ✅ 已禁用 |
| 🎨 皮肤/主题推广 | 各种 `.cupf` | ✅ 已禁用 |

**共禁用 31+ 广告组件，全部可逆（重命名为 .bak，不删除）**

## 使用

安装后在 Claude Code 中说：

```
帮我去掉搜狗输入法广告
```

或手动运行脚本（无需 Claude Code）：

```powershell
# 右键以管理员身份运行
.\scripts\sogou_ad_killer.ps1

# 恢复所有广告
.\scripts\sogou_ad_killer.ps1 -Restore
```

## 原理

**非破坏性、完全可逆**——仅将广告相关文件重命名为 `.bak` 后缀，使搜狗输入法无法加载它们。不修改注册表，不留后门。

## 兼容性

| 版本 | 状态 |
|------|------|
| 搜狗拼音 15.9.x | ✅ 已验证（Windows 11）|
| 搜狗拼音 15.x | ✅ 理论兼容 |
| 搜狗五笔 | ❌ 暂不支持（目录不同） |

## 安全说明

- 所有操作可逆：运行 `-Restore` 即可恢复
- 不修改系统文件
- 不联网传输数据
- 开源透明，可审计完整代码

## 许可

MIT License © 2025
