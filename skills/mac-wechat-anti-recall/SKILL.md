---
name: mac-wechat-anti-recall
description: 防止 Mac 微信消息被撤回，支持文字/图片/视频/语音/表情/文件/小程序/拍一拍等全部消息类型，同时提供多开和禁用更新功能。支持微信 4.x 最新版，Apple Silicon 和 Intel
triggers:
  - 微信防撤回
  - 防撤回
  - WeChat anti recall
  - 微信撤回拦截
  - Mac微信防撤回
  - 微信消息防撤回
  - 阻止撤回
  - anti revoke
  - wechat tweak
  - wechat plugin
  - 微信插件
platform: darwin
verified: macOS 26 + 微信 4.1.10 (build 268851) + Apple Silicon (M1 Pro) 实测；macOS 15 + 微信 4.1.x 亦可用
---

# Mac 微信防撤回

防止 Mac 微信中的消息被撤回，支持全类型消息（文字、图片、视频、语音、表情、文件、小程序、拍一拍、合并转发、引用消息、名片、位置、音乐等），同时提供多开和禁用更新等辅助功能。

## 可选方案总览

| 方案 | 微信版本支持 | Apple Silicon | Intel | 活跃度 | 防撤回范围 | 安装难度 |
|------|:----------:|:-----------:|:----:|:----:|:--------:|:------:|
| **X1a0HeWeChatPlugin** | ✅ 4.1.9.x | ✅ ARM64 | ❌ | 🟢 活跃 (2026) | **全类型** | ⭐ |
| **WeChatTweak-macOS** | ⚠️ ~4.0 | ✅ | ✅ | 🟡 较慢 | 基本覆盖 | ⭐⭐ |
| WeChatIntercept | ⚠️ 3.7.x | ✅ | ✅ | 🔴 停更 | 基本覆盖 | ⭐⭐ |

> **推荐**：微信版本 ≥ 4.1 首选 **X1a0HeWeChatPlugin**（更新最勤、适配最新版）；微信版本 ≤ 4.0 且为 Intel Mac 可选 **WeChatTweak-macOS**。

---

## 方案一：X1a0HeWeChatPlugin（推荐，微信 4.x 最新版）

### 项目信息

- **GitHub**: [X1a0He/X1a0HeWeChatPlugin](https://github.com/X1a0He/X1a0HeWeChatPlugin)
- **最新版本**: v2.3.1 (2026年4月)
- **支持架构**: Apple Silicon ARM64（不支持 Intel）
- **微信兼容**: 4.0.x ~ 4.1.9.x

### 安装方式

#### 一键安装（推荐）

```bash
git clone https://github.com/X1a0He/X1a0HeWeChatPlugin.git
cd X1a0HeWeChatPlugin
sudo sh install.sh
```

#### pkg 安装包

从 GitHub Releases 下载 `.pkg` 文件，双击安装（需要允许来自"任何来源"的应用）。

### 功能清单

| 功能 | 说明 |
|------|------|
| 🔒 **全类型防撤回** | 文字、图片、视频、语音、表情、文件、小程序、拍一拍、合并转发、引用消息、名片、位置、音乐等 |
| 📱 **微信多开** | 支持同时运行多个微信实例（⚠️ 慎用，多开有封号风险） |
| 🚫 **禁用日志上报** | 阻断微信的日志/数据上报，保护隐私 |
| 🛡️ **安全模式** | 可选择开启安全模式，降低检测风险 |
| 🔄 **禁用更新检测** | 阻止微信自动检查/下载更新 |
| ✏️ **自定义撤回提示** | 修改撤回提示短语（如改为 "XXX 撤回了一条消息"） |
| 🔍 **插件版本自检** | 自动检查插件是否有新版本 |

### 使用说明

安装后，插件会在微信菜单栏添加设置入口：
- 微信 → 菜单栏 → 插件设置 → 开启/关闭各项功能
- 防撤回开启后，对方撤回的消息会保留在聊天窗口并带有提示标记
- 多开功能通过右键 Dock 图标 → 登录新账号 使用

---

## 方案二：WeChatTweak-macOS（经典方案，Intel 可用）

### 项目信息

- **GitHub**: [sunnyyoung/WeChatTweak-macOS](https://github.com/sunnyyoung/WeChatTweak-macOS)
- **最新版本**: v1.5.0 (2024年3月)
- **支持架构**: Apple Silicon + Intel（通用）
- **微信兼容**: ≤ 4.0.x（4.1 以上未经充分测试）

> **4.1+ 用户请看这里**：上游停在 ≤ 4.0 已久，4.1 及以上请用社区维护的 fork [naizhao/WeChatTweak](https://github.com/naizhao/WeChatTweak)（持续更新 config.json 里的字节补丁偏移）。它是**字节补丁**而非 dylib 注入，原理、验证方法与实测踩坑见下文「字节补丁方案实操与踩坑」。

### 安装方式

#### brew 安装（推荐）

```bash
# 安装 CLI 工具
brew install sunnyyoung/repo/wechattweak-cli

# 安装 Tweak
sudo wechattweak-cli install

# 更新
sudo wechattweak-cli install

# 卸载
sudo wechattweak-cli uninstall
```

#### 手动安装

从 GitHub Releases 下载 `WeChatTweak-macOS-x.x.x.zip`，解压后将 `WeChatTweak.framework` 放入微信的 `Contents/MacOS/` 目录。

### 功能清单

| 功能 | 说明 |
|------|------|
| 🔒 **消息防撤回** | 阻止消息撤回（消息列表通知 + 系统通知） |
| 📱 **无限多开** | 右键 Dock 图标 → 登录新账号 |
| 😊 **表情导出** | 导出微信表情包 |
| 🔗 **二维码识别** | 聊天窗口中识别二维码 |
| 📋 **右键复制链接** | 消息右键菜单中复制链接 |
| ⚙️ **UI 设置面板** | 可视化开关各项功能 |

---

## 方案三：WeChatIntercept（备选，轻量）

- **项目**: [WeChatIntercept](https://gitcode.com/gh_mirrors/we/WeChatIntercept)
- **特点**: 一键安装脚本、免认证登录、自定义拦截提示
- **限制**: 仅支持微信 v3.7.0+，已停更，不推荐新用户使用

---

## 进阶：字节补丁方案实操与踩坑（naizhao/WeChatTweak fork · 2026-09 实测）

方案一/二是「注入 framework / dylib」；4.x 上还有一类**字节补丁**方案：社区 fork [naizhao/WeChatTweak](https://github.com/naizhao/WeChatTweak)（上游 sunnyyoung 停在 4.0，此 fork 持续维护 4.x 的偏移配置）。下文全部在 macOS 26 + 微信 4.1.10（build 268851）+ Apple Silicon 上实测过。

### 原理（读源码确认）

- `wechattweak patch` 把 config.json 里每个 build 的 `asm` 字节写到 `addr` 指定的虚拟地址；**目标是 `Contents/Resources/wechat.dylib`（300 MB+），不是主程序**（主程序只有几 MB —— 这是腾讯自己的布局，不是插件挪的）
- arm64 的防撤回补丁是 `20008052c0035fd6`（`mov w0, #1; ret`，让某个判断恒为真）；x86_64 另有一条多开补丁（6 × NOP）
- 同一地址写同一字节 → **重复执行是幂等的**，不会打坏；前提是 build 号在 config 支持列表里：

```bash
~/tools/WeChatTweak/wechattweak versions --app /Applications/WeChat.app
```

### 装完先验证（不必真找人撤回一次）

`scripts/check_patch.py` 反向解析 config 的 `addr`，按 Mach-O segment 换算出文件偏移，读实际字节比对：

```bash
python3 scripts/check_patch.py 268851                                  # 参数 = CFBundleVersion
python3 scripts/check_patch.py 268851 --app /Applications/微信1.app     # 多开副本同理
```

期望两处 `✅ 补丁在`。**「字节在」≠「功能生效」**：字节正确 + 载荷确实被进程加载（`lsof -p <pid> | grep Resources/wechat.dylib`）只是必要条件，最终仍需一次真实撤回事件验证。

### 三个实测踩坑

**1. 签名顺序：先重签嵌套载荷，再封 bundle**

先 `codesign --force --deep --sign -` 封完整个 bundle、**之后**才单独重签 `Contents/Resources/wechat.dylib`（naizhao 工具当前就是这个顺序），会让 `CodeResources` 与最终签名不一致 —— 验证时报 `a sealed resource is missing or invalid`。后果不止是报错：macOS 每次重启都会重新校验敏感权限签名，**反复作废屏幕录制授权、反复弹框**。补完之后必须再来一次 `codesign --force --deep --sign -` 把 bundle 封正。

**2. 任何重签之后，必须重置屏幕录制授权**

TCC 按 **cdhash** 记录授权，重签即失效。典型症状：**微信截图提示「没有权限」，但系统设置里的开关明明是开的**（开关指向的是旧 cdhash 那条记录）。

```bash
tccutil reset ScreenCapture com.tencent.xinWeChat
# 然后回微信截一次图 → 系统弹框 → 允许（一次干净授权）
```

多次重签会累积重复授权行，reset 会一并清掉（对每条旧记录各报一次 Successfully reset）。

**3. 不要下意识用 sudo**

`/Applications` 下的微信通常就归你所有，patch 与重签都**不需要 root**。用 sudo 跑反而会把 `_CodeSignature/CodeResources` 变成 root 属主，导致之后无法正常重签（真遇到才需要 `sudo chown -R "$(whoami):admin" /Applications/WeChat.app`）。

同理：若机器上 `xattr` 被 Python 版包覆盖（`~/Library/Python/*/bin/xattr`，且只有 x86_64），`xattr -cr` 会因架构不兼容报 ImportError —— 用系统原版 `/usr/bin/xattr -cr /Applications/WeChat.app` 收尾。

### 多开副本能不能也带上防撤回？

能：把它从**已打补丁的主 App 复制**过去（字节副本自带补丁），再改 Bundle ID + 重签即可；容器按 Bundle ID 走，登录数据不受影响。但反向不成立 —— 副本若停在旧版本、且其 build 不在 config 支持列表里，**没法单独给它打补丁**（工具直接拒绝），只能靠复制刷新。

### 关于「禁用更新」的真相

微信 macOS 版内置 **Sparkle 自动更新**（`Info.plist` 里有 `SUPublicEDKey`，缓存目录 `~/Library/Caches/com.tencent.xinWeChat/org.sparkle-project.Sparkle`），而且**升级是静默的、不询问用户**：实测 2026-06-09 微信在无人操作的情况下把自己从 4.1.9 升到 4.1.10，插件随之失效、需要重打（更新后的 App 带着全新载荷和签名）。

想真正拦住得阻断更新域名或替换更新机制；本 skill 目前**没有**经完整验证的拦截方案 —— 别轻信"勾个开关就行"。

---

## SIP（系统完整性保护）详解

### 什么是 SIP？

系统完整性保护（System Integrity Protection，SIP）是 macOS 的安全机制，限制对系统文件和 `/Applications` 下应用的修改，防止恶意软件注入。

### 是否需要禁用 SIP？

| 方案 | SIP 要求 | 说明 |
|------|:------:|------|
| X1a0HeWeChatPlugin | 🟢 **通常不需要** | 安装脚本已做适配，大多数情况下无需关闭 SIP |
| WeChatTweak-macOS | 🟡 **可能需要** | 部分 macOS 版本上 framework 注入会失败，需临时关闭 SIP |

### 如果遇到安装失败（framework 注入被阻止）

**常见症状**：
- `WeChatTweak.framework` 无法复制到 `/Applications/WeChat.app/Contents/MacOS/`
- 微信启动后功能未生效
- 安装脚本报错 "Operation not permitted"

**解决方法（按顺序尝试）**：

```
第 1 步：完全退出微信 → 重启 Mac → 重试安装
第 2 步：手动删除残留的 WeChatTweak.framework 目录 → 重试
第 3 步：临时关闭 SIP → 安装插件 → 立即重新开启 SIP
```

### 如何临时关闭 SIP（最后手段）

> ⚠️ **仅在安装阶段临时关闭，安装完必须立即重新开启！**

#### Apple Silicon (M1/M2/M3/M4)

1. **关机**
2. **长按电源按钮**直到出现「启动选项」→ 点击「选项」→「继续」
3. 进入恢复模式后，顶部菜单栏 →「实用工具」→「终端」
4. 输入 `csrutil disable` 并回车
5. 输入 `reboot` 重启
6. **安装插件**（不要做其他操作）
7. **重复步骤 1-3 进入恢复模式**
8. 输入 `csrutil enable` 并回车
9. 输入 `reboot` 重启

#### Intel Mac

1. **重启**，启动时按住 **Command+R** 进入恢复模式
2. 顶部菜单栏 →「实用工具」→「终端」
3. 输入 `csrutil disable` 并回车
4. 重启 → 安装插件
5. **重新进入恢复模式** → 终端输入 `csrutil enable` → 重启

### 检查 SIP 状态

```bash
csrutil status
# 正常输出：System Integrity Protection status: enabled.
```

---

## 安全与风险评估

### 封号风险

| 风险等级 | 说明 |
|:------:|------|
| 🟢 **极低** | 只使用防撤回功能，无已知大规模封号案例 |
| 🟡 **低** | 同时使用多开功能，理论上有风控可能 |
| 🔴 **中** | 使用自动化脚本（群发、抢红包等），曾有封号报告 |

> **建议**：
> - 大号仅使用防撤回，不使用多开
> - 多开功能建议仅在工作号/小号上使用
> - 避免与自动化工具（抢红包、自动回复、群发）同时使用
> - 使用 X1a0HeWeChatPlugin 的"安全模式"功能

### 隐私与数据安全

| 维度 | 说明 |
|------|------|
| **插件权限** | 插件以 dylib 形式注入微信进程，拥有微信全部权限（读取聊天记录、文件等） |
| **网络通信** | 两个主流插件均为**开源**，代码可审计，未发现后门报告 |
| **数据上传** | 插件理论上可以访问你的所有聊天数据，务必从官方 GitHub 下载 |
| **供应链风险** | ⚠️ 不要从第三方/百度网盘下载，务必从 GitHub Releases 获取 |

### 安全最佳实践

1. **从官方 GitHub 下载**——永远不要使用来源不明的 .pkg 或 .dmg
2. **查看 Star/Issue**——确认项目活跃、社区信任
3. **代码审计**——如有能力，审查 install.sh 脚本内容
4. **安装完立即重启 SIP**——如果你临时关闭了它
5. **大号慎用多开**——防撤回相对安全，多开有额外风控
6. **禁用自动更新**——避免插件与新版本微信不兼容

---

## 自动化执行流程

当触发此 skill 时，按以下步骤执行：

### 第 1 步：检测环境

```bash
# 确认是 macOS
uname -a

# 确认微信已安装并获取版本
/usr/libexec/PlistBuddy -c "Print :CFBundleShortVersionString" /Applications/WeChat.app/Contents/Info.plist 2>/dev/null

# 确认芯片架构
uname -m
# arm64 = Apple Silicon, x86_64 = Intel

# 检查 SIP 状态
csrutil status
```

### 第 2 步：根据环境推荐方案

| 条件 | 推荐方案 |
|------|----------|
| arm64 + 微信 ≥ 4.1 | X1a0HeWeChatPlugin |
| arm64 + 微信 ≤ 4.0 | WeChatTweak-macOS 或 X1a0He |
| x86_64 + 任意版本 | WeChatTweak-macOS |

### 第 3 步：执行安装

根据推荐方案执行对应的安装命令（见上方各方案安装方式）。

### 第 4 步：验证安装

```bash
# 检查 framework/plugin 是否存在
ls /Applications/WeChat.app/Contents/MacOS/WeChatTweak.framework 2>/dev/null && echo "WeChatTweak installed" || echo "WeChatTweak not found"

# 或检查 X1a0He 的安装标记
ls /Applications/WeChat.app/Contents/MacOS/WeChatPlugin.framework 2>/dev/null && echo "X1a0He installed" || echo "X1a0He not found"

# 字节补丁类（naizhao fork）：直接验补丁字节，比找文件可靠
python3 scripts/check_patch.py "$(/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' /Applications/WeChat.app/Contents/Info.plist)" 2>/dev/null
```

### 第 5 步：提示用户

完成后告知用户：
1. ✅ 插件已安装/未安装（如实反馈）
2. 🔄 需要**完全退出微信并重新打开**才能生效
3. ⚙️ 设置入口：微信菜单栏 → 插件设置
4. ⚠️ 建议关闭微信自动更新
5. 🛡️ 如曾关闭 SIP，务必重新开启：`csrutil enable`（需进入恢复模式）

---

## 常见问题

### 安装后防撤回不生效

1. 确认微信**完全退出**（Cmd+Q，不是关闭窗口）
2. 重新打开微信
3. 检查插件设置面板中防撤回功能是否开启
4. 如果仍不生效，尝试重启 Mac

### 装完 / 重装后，微信截图提示「没有权限」，但系统设置里明明是开的

重签导致的 TCC 授权漂移（授权按 cdhash 记录，重签后旧授权作废）：

```bash
tccutil reset ScreenCapture com.tencent.xinWeChat
# 回微信截一次图 → 弹框 → 允许
```

详见上文「字节补丁方案实操与踩坑」第 2 条。

### 怎么确认防撤回真的生效了（不想麻烦别人撤回消息）

1. 字节补丁类方案先验字节：`python3 scripts/check_patch.py <CFBundleVersion>`，两处都 `✅ 补丁在`
2. 再验功能，最省事的是**双开自测**：小号发一条消息给主号 → 小号撤回 → 看主号窗口里那条是否还在（还在 = 生效）
3. 「字节在」不等于「功能生效」—— 别只看安装脚本打印的成功提示

### 微信更新后插件失效

**原因**：微信更新可能覆盖或移除注入的 framework，或新版本微信改变了内部结构导致插件不兼容。

**解决**：
1. 重新运行插件的安装脚本
2. 如果重新安装后仍不生效，等待插件作者适配新版本
3. 建议关闭微信自动更新

### "无法验证开发者" 或 "已损坏"

针对 WeChatTweak CLI 或安装脚本：
```bash
# 移除隔离标记
sudo xattr -d com.apple.quarantine /path/to/file
# 或在「系统设置 → 隐私与安全性」中点击「仍要打开」
```

### 是否支持 App Store 版微信？

- **WeChatTweak-macOS**：理论上支持，但 App Store 版的沙盒限制可能更严格
- **X1a0HeWeChatPlugin**：官方说明支持官网版和 App Store 版
- **建议**：优先使用官网下载的微信（非 App Store 版），兼容性更好

### 卸载插件

**X1a0HeWeChatPlugin**：
```bash
sudo sh uninstall.sh
```

**WeChatTweak-macOS**：
```bash
sudo wechattweak-cli uninstall
# 或手动删除
sudo rm -rf /Applications/WeChat.app/Contents/MacOS/WeChatTweak.framework
```

### Apple Silicon 上 WeChat 运行在 Rosetta 模式

如果 WeChat 以 Rosetta (Intel) 模式运行，右键 `/Applications/WeChat.app` → 显示简介 → 确保**未勾选**「使用 Rosetta 打开」。

---

## 版本兼容性参考

| 微信版本 | X1a0HeWeChatPlugin | WeChatTweak-macOS | WeChatIntercept |
|----------|:-----------------:|:-----------------:|:---------------:|
| 4.1.9.x | ✅ v2.3.1 | ❓ 未测试 | ❌ |
| 4.1.x | ✅ | ❓ 未测试 | ❌ |
| 4.0.x | ✅ | ✅ v1.5.0 | ❌ |
| 3.7.x ~ 3.9.x | ❌ | ✅ | ✅ |
| 3.6.x 及更早 | ❌ | ⚠️ 部分 | ✅ |

> 4.1.x 上另有 **naizhao/WeChatTweak** fork（字节补丁方案，实测 4.1.10 / build 268851 可用）；「安装成功」别只看脚本提示，用 `scripts/check_patch.py` 验字节 + 一次真实撤回验功能。
