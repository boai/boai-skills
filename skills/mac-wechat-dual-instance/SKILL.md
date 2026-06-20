---
name: mac-wechat-dual-instance
description: 在 macOS 上同时运行多个微信实例（双开/多开），支持微信 4.x（Electron 架构），Apple Silicon 和 Intel 均可使用
triggers:
  - 微信双开
  - 微信多开
  - Mac微信双开
  - 微信分身
  - WeChat dual
  - WeChat multi instance
  - Mac微信多开
  - 双开微信
  - 多开微信
  - wechat multi open
platform: darwin
verified: macOS 15 Sequoia + 微信 4.x + Apple Silicon (M1/M2/M3)
---

# Mac 微信双开/多开

在 macOS 上同时运行两个或多个微信实例，支持微信 4.x 及以上版本（Electron 架构）。

> **背景**：微信 Mac 版从 v4.0 起采用 Electron 架构重构，传统的 `open -n /Applications/WeChat.app` 终端命令已经**失效**。当前可行方案的核心原理是：复制应用 → 修改 Bundle ID → 重新签名。

## 原理

macOS 通过 Bundle ID 区分不同应用实例。同一个 Bundle ID 的应用系统只允许运行一个实例。通过复制应用、修改其 Bundle ID、再用 ad-hoc 签名使其通过 Gatekeeper 验证，即可实现多实例共存。

```
原版微信 (com.tencent.xinWeChat) → 分身微信 (com.tencent.xinWeChat2) → 分身微信3 (com.tencent.xinWeChat3) → ...
```

## 用法

### 方法一：手动三命令（推荐，最透明）

直接对 Claude 说以下任意一句即可触发自动执行：

```
/oh-my-claudecode:mac-wechat-dual-instance
```

或提及触发词：
- "帮我在 Mac 上双开微信"
- "微信多开怎么做"
- "wechat dual instance"

Claude 将自动执行以下三行命令：

```bash
# 步骤 1：复制微信应用
sudo cp -R /Applications/WeChat.app /Applications/WeChat2.app

# 步骤 2：修改 Bundle ID（关键——让系统识别为不同应用）
sudo /usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier com.tencent.xinWeChat2" /Applications/WeChat2.app/Contents/Info.plist

# 步骤 3：重新签名（否则 macOS Gatekeeper 阻止打开）
sudo codesign --force --deep --sign - /Applications/WeChat2.app
```

完成后在「应用程序」文件夹中找到 **WeChat2.app**，双击打开扫码登录即可。

> **想三开/四开？** 重复以上步骤，把 `WeChat2` 改为 `WeChat3`，Bundle ID 改为 `com.tencent.xinWeChat3` 即可。理论上无上限。

### 方法二：一键脚本（更方便，支持自动重建）

#### WeChatMulti-macOS（推荐，功能最全）

```bash
# 下载脚本
curl -O https://raw.githubusercontent.com/MaoTouHU/WeChatMulti-macOS/main/wechat-2.sh
chmod +x wechat-2.sh

# 一键双开
sudo ./wechat-2.sh auto --force

# 多开 N 个实例（如 3 个）
sudo ./wechat-2.sh multi 3 --force

# 微信更新后重建所有副本
sudo ./wechat-2.sh rebuild --force

# 关闭所有微信进程
sudo ./wechat-2.sh kill
```

#### wechat-multi-open（交互式菜单，适合新手）

```bash
curl -fsSL https://raw.githubusercontent.com/nullbyte-lab/wechat-multi-open/main/wechat-multi-open.sh -o ~/wechat-multi.sh
chmod +x ~/wechat-multi.sh
~/wechat-multi.sh
```

### 方法三：WeChatTweak / X1a0He 插件自带多开

如果已安装 WeChatTweak-macOS 或 X1a0HeWeChatPlugin（见防撤回 skill），这些插件自带了多开功能，无需额外操作。详见 `mac-wechat-anti-recall` skill。

## 自动化执行流程

当触发此 skill 时，按以下步骤执行：

### 第 1 步：检测环境

```bash
# 确认 macOS
uname -a

# 确认微信已安装
ls /Applications/WeChat.app/Contents/Info.plist

# 检查是否已有分身
ls -d /Applications/WeChat*.app 2>/dev/null
```

### 第 2 步：执行复制 + 修改 Bundle ID + 签名

```bash
# 以 WeChat2 为例
sudo cp -R /Applications/WeChat.app /Applications/WeChat2.app
sudo /usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier com.tencent.xinWeChat2" /Applications/WeChat2.app/Contents/Info.plist
sudo codesign --force --deep --sign - /Applications/WeChat2.app
```

### 第 3 步：验证

```bash
# 确认 Bundle ID 已修改
/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier" /Applications/WeChat2.app/Contents/Info.plist
# 应输出：com.tencent.xinWeChat2

# 确认签名成功
codesign -dvvv /Applications/WeChat2.app 2>&1 | head -5
# 应包含 "adhoc" 或 "Signed Time"
```

### 第 4 步：提示用户

完成后告知用户：
1. ✅ 微信分身 WeChat2.app 已创建，位于 `/Applications/WeChat2.app`
2. 🔍 在「应用程序」文件夹中找到 WeChat2.app，双击打开并扫码登录
3. ⚠️ **每次微信更新后**，分身副本需要重建（运行 `rebuild` 命令）
4. 💡 建议关闭微信自动更新：微信 → 设置 → 通用 → 取消「自动升级微信」
5. 📝 如需卸载分身：直接删除 `/Applications/WeChat2.app` 即可

## 常见问题与解决方法

### "无法打开，已损坏" / "无法验证开发者"

**原因**：ad-hoc 签名不完整或文件损坏

**解决**：重新签名

```bash
sudo codesign --force --deep --sign - /Applications/WeChat2.app
# 然后右键 WeChat2.app → 打开（首次需要 bypass Gatekeeper）
```

### 打开后闪退

**原因**：应用不在 `/Applications` 目录（如在 iCloud 同步目录或桌面）

**解决**：确保分身放在 `/Applications` 目录下，不要在 iCloud Drive 或 OneDrive 同步目录中。

```bash
# 如果放在其他位置，移回 /Applications
sudo mv ~/Desktop/WeChat2.app /Applications/WeChat2.app
```

### 微信更新后分身失效

**原因**：微信更新只更新原版 `/Applications/WeChat.app`，分身仍是旧版本，可能不兼容新数据格式或登录协议。

**解决**：重新执行步骤 1-3（复制新版微信并修改 Bundle ID）：

```bash
sudo rm -rf /Applications/WeChat2.app
sudo cp -R /Applications/WeChat.app /Applications/WeChat2.app
sudo /usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier com.tencent.xinWeChat2" /Applications/WeChat2.app/Contents/Info.plist
sudo codesign --force --deep --sign - /Applications/WeChat2.app
```

或使用脚本的 `rebuild` 命令（方法二）。

### 提示输入密码 / 管理员权限

`cp` 到 `/Applications`、修改 `PlistBuddy`、`codesign` 均需要管理员权限，终端会提示输入密码。这是正常行为，不会记录或泄露密码。

### 分身无法登录 / 提示版本过低

**原因**：微信客户端版本过旧，服务端拒绝登录。

**解决**：先更新原版微信到最新版本，再重建分身。

## Apple Silicon 兼容性

| 芯片 | 原生支持 | 备注 |
|------|:------:|------|
| M1 | ✅ | 完全支持，原生 ARM64 运行 |
| M2 | ✅ | 完全支持，原生 ARM64 运行 |
| M3 | ✅ | 完全支持，原生 ARM64 运行 |
| M4 | ✅ | 完全支持，原生 ARM64 运行 |
| Intel | ✅ | 完全支持 |

此方案不涉及代码注入，仅为文件复制 + 元数据修改，**无需 Rosetta 2**。

## SIP 与安全性

### 是否需要禁用 SIP？

**不需要。** 此方案的核心操作是：
- 文件复制（`cp`）——普通文件操作
- 修改 Info.plist（`PlistBuddy`）——应用元数据
- Ad-hoc 签名（`codesign`）——macOS 原生工具

以上所有操作均在 SIP 允许范围内，**无需进入恢复模式或修改系统安全设置**。

### 安全评估

| 维度 | 评估 |
|------|------|
| 代码修改 | ❌ 无——仅复制官方微信，不修改任何二进制代码 |
| 网络通信 | ❌ 无——分身与原版使用相同的官方服务器 |
| 数据隔离 | ✅ 是——两个实例各自独立运行，消息数据互不干扰 |
| 封号风险 | 🟢 极低——此方案不注入、不 Hook、不修改微信逻辑 |
| 隐私泄露 | 🟢 无——不涉及第三方代码 |

> **结论**：这是目前最安全的微信多开方案，比第三方修改版或注入插件方案安全得多。

## 与其他方案的比较

| 方案 | 安全性 | 简便度 | 微信 4.x 支持 | 防撤回 | 维护状态 |
|------|:------:|:------:|:-----------:|:------:|:------:|
| **本方案（复制+重签名）** | 🟢 最安全 | ⭐⭐⭐ | ✅ | ❌ | 永久有效 |
| WeChatTweak-macOS | 🟡 注入插件 | ⭐⭐ | 需验证 | ✅ | 较慢 |
| X1a0HeWeChatPlugin | 🟡 注入插件 | ⭐⭐⭐ | ✅ | ✅ | 活跃 |
| 旧版 open -n 命令 | N/A | ⭐ | ❌ 已失效 | ❌ | 已失效 |

> 💡 **最佳组合**：本方案（安全多开）+ X1a0HeWeChatPlugin（防撤回），详见 `mac-wechat-anti-recall` skill。

## 扩展：命令行快捷启动

创建别名，一键启动所有微信实例：

```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
alias wechat2='open -a WeChat2'
alias wechat3='open -a WeChat3'
alias wechat-all='open -a WeChat && open -a WeChat2'

# 重新加载配置
source ~/.zshrc
```

## 卸载

```bash
# 删除所有分身
sudo rm -rf /Applications/WeChat2.app
sudo rm -rf /Applications/WeChat3.app
# 原版微信不受影响
```
