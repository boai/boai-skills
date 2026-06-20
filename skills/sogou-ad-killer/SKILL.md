---
name: sogou-ad-killer
description: 彻底永久关闭搜狗输入法所有广告（商业推广、游戏中心、桌面弹窗、Chromium 广告渲染引擎、写作助手、云服务广告等），31+ 组件一键禁用，支持自动化和手动恢复
triggers:
  - 搜狗广告
  - 关闭搜狗广告
  - sogou ad
  - 搜狗输入法广告
  - 搜狗弹窗
  - sogou ad killer
  - 去搜狗广告
  - 搜狗去广告
platform: windows
verified: Windows 11 + 搜狗拼音 15.9.0.2525
---

# Sogou Ad Killer（搜狗输入法广告清理）

永久禁用搜狗输入法所有广告组件，通过将广告相关的可执行文件、DLL 和配置文件重命名为 `.bak` 后缀使其无法加载。

> ⚠️ 本工具仅重命名文件（可逆），不删除任何文件。如需恢复，将 `.bak` 改回原名即可。

## 原理

搜狗输入法的广告通过以下载体展示：

| 广告载体 | 组件/文件 | 广告形式 |
|----------|-----------|----------|
| **商业推广中心** | `biz_center/biz_bundle.dll` | 输入法内的商业推广卡片 |
| **游戏中心** | `game_center/game_center.dll` | 游戏推荐弹窗 |
| **桌面弹窗** | `SGDeskControl/SGDeskControl.dll` | 桌面右下角弹窗广告 |
| **Chromium 渲染引擎** | `SGRender/SGRender.exe` + `libcef.dll` (完整 CEF 浏览器) | 运行富媒体广告（最占内存，~200MB） |
| **写作助手** | `WriteSpirit/write_spirit.exe` | 写作辅助中的推荐/广告 |
| **云服务** | `SogouCloud.exe` | 云端词库/推荐 |
| **定时推送** | `userNetSchedule.exe` | 定时拉取广告素材 |
| **迷你浏览器** | `SGMiniBrowserHelperHost.dll` | 嵌入式广告弹窗 |
| **配置面板广告** | `pandorabox.cupf`, `SmartInfo.cupf`, `RightPopmenu.cupf` 等 | 候选框/右键菜单推荐 |

## 用法

### 自动模式（推荐）

直接对 Claude 说以下任意一句即可：

```
/oh-my-claudecode:sogou-ad-killer
```

或提及触发词：
- "帮我去掉搜狗广告"
- "关闭搜狗输入法所有广告"
- "sogou ad killer"

Claude 将自动执行：检测安装路径 → 杀进程 → 禁用组件 → 验证结果。

### 手动模式（如果自动执行权限不足）

当自动执行遇到管理员权限问题时，Claude 会生成一个 PowerShell 脚本，请右键以管理员身份运行：

```powershell
# 右键 → 以管理员身份运行 PowerShell
.\sogou_ad_cleanup.ps1
```

## 禁用的完整组件清单

### Components 目录（18 个广告组件）

| 组件目录 | 禁用文件 | 广告类型 |
|----------|----------|----------|
| `biz_center/` | `biz_bundle.dll` | 商业推广 |
| `biz_pdf/` | (整个组件) | PDF 推广 |
| `game_center/` | `game_center.dll` | 游戏推荐 |
| `SGDeskControl/` | `SGDeskControl.dll` | 桌面弹窗 |
| `SGRender/` | `SGRender.exe`, `SGRender.dll`, `SGRender64.dll`, `SGRenderDll.dll`, `libcef.dll` | CEF 广告渲染引擎 |
| `WriteSpirit/` | `write_spirit.exe`, `spirit_bundle.dll`, `browser_host.dll`, `interceptor.dll` | 写作助手广告 |
| `AppBox/` | (整个组件) | 应用盒子 |
| `SkinBox/` | (整个组件) | 皮肤推荐盒子 |
| `SogouFlash/` | (整个组件) | Flash 广告 |
| `Theme/` | (整个组件) | 主题推荐 |
| `SogouComMgr.exe` | (组件管理) | 组件下载/更新 |

### 主安装目录（13 个广告文件）

| 文件 | 功能 |
|------|------|
| `SogouCloud.exe` | 云服务（含推荐） |
| `userNetSchedule.exe` | 广告定时拉取 |
| `SogouToolkits.exe` | 工具集（含推广入口） |
| `SGMiniBrowserHelperHost.dll` | 迷你广告浏览器 |
| `pandorabox.cupf` | 潘多拉魔盒面板 |
| `skin_recommend.cupf` | 皮肤推荐配置 |
| `SmartInfo.cupf` | 智能信息（含广告） |
| `RightPopmenu.cupf` | 右键菜单推广 |
| `wangzai_guide.cupf` | 旺仔新手指引 |
| `skin_btn_tips.cupf` | 皮肤按钮提示 |
| `screencapture.cupf` | 截图工具配置 |
| `screencapture.exe` | 截图工具 |
| `richinput.cupf` | 富媒体输入配置 |

## 自动化执行流程

当触发此 skill 时，按以下步骤执行：

### 第 1 步：检测安装

```bash
# 查找搜狗输入法安装路径（支持多版本）
find "/c/Program Files" "/c/Program Files (x86)" -maxdepth 2 -type d -name "SogouInput" 2>/dev/null
ls "/c/Program Files (x86)/SogouInput/"  # 获取版本号
```

### 第 2 步：终止进程

```bash
taskkill /F /IM SogouImeBroker.exe 2>/dev/null
taskkill /F /IM SogouCloud.exe 2>/dev/null
taskkill /F /IM SogouExe.exe 2>/dev/null
taskkill /F /IM SogouSvc.exe 2>/dev/null
taskkill /F /IM SGRender.exe 2>/dev/null
taskkill /F /IM write_spirit.exe 2>/dev/null
taskkill /F /IM userNetSchedule.exe 2>/dev/null
taskkill /F /IM SogouToolkits.exe 2>/dev/null
```

### 第 3 步：禁用 Components 广告组件

对每个组件的核心文件执行 `mv <file> <file>.bak`：
- `Components/biz_center/<ver>/biz_bundle.dll`
- `Components/game_center/<ver>/game_center.dll`
- `Components/SGDeskControl/<ver>/SGDeskControl.dll`
- `Components/SGRender/<ver>/` — 全部 .exe 和核心 .dll
- `Components/WriteSpirit/<ver>/` — 全部 .exe 和核心 .dll

Component 目录的文件通常不需要管理员权限即可重命名。

### 第 4 步：禁用主目录广告文件（需管理员权限）

对主安装目录 `15.x.x.xxxx/` 下的文件执行 `mv <file> <file>.bak`。

如果遇到 `Permission denied`，使用提权 PowerShell：

```powershell
Start-Process powershell -Verb RunAs -Wait -ArgumentList '-NoProfile -Command "cd \"<sogou_path>\"; @(\"file1\",\"file2\",...) | % { if(Test-Path $_) { Rename-Item $_ \"$_.bak\" -Force } }"'
```

### 第 5 步：验证

```bash
# 统计禁用的文件数
find "/c/Program Files (x86)/SogouInput/" -name "*.bak" -type f | wc -l
# 应 ≥ 31
```

### 第 6 步：提示用户

完成后明确告知用户：
1. ✅ 已禁用 X 个广告组件
2. ⚠️ 需要**重启电脑**使改动生效
3. ⚠️ 建议在搜狗设置中关闭「自动升级」防止广告复活
4. 📝 如需恢复：将 .bak 文件改回原名

## 已知问题与注意事项

### 权限
- **Components 目录**：通常无需管理员权限
- **主安装目录** (`Program Files (x86)/SogouInput/<ver>/`)：需要管理员权限
- 写文件到 Program Files 需要提权，使用 `Start-Process -Verb RunAs` 触发 UAC

### 自动更新
- 搜狗输入法更新时会重新下载组件，可能恢复广告
- **务必提醒用户关闭自动更新**：右键输入法状态栏 → 属性设置 → 高级 → 取消勾选「自动升级」

### 兼容性
- **已验证版本**：搜狗拼音 15.9.0.2525（Windows 11）
- **理论兼容**：15.x 全系列（目录结构相似）
- **不兼容**：搜狗五笔（目录结构不同，需扩展）
- 搜狗可能在新版本中变更组件名称和目录结构

### 恢复方法
```powershell
# 恢复所有禁用的广告组件
Get-ChildItem "C:\Program Files (x86)\SogouInput" -Recurse -Filter "*.bak" |
    ForEach-Object { Rename-Item $_.FullName $_.FullName.Replace('.bak','') }
```

### hosts 域名屏蔽（可选增强）
如需额外防护，在 `C:\Windows\System32\drivers\etc\hosts` 中添加：
```
0.0.0.0 pcbao.sogou.com
0.0.0.0 pb.sogou.com
0.0.0.0 get.sogou.com
0.0.0.0 config.pinyin.sogou.com
```

## 验证标准

- `find ... -name "*.bak" | wc -l` ≥ 31
- 重启后输入法正常使用，无弹窗
- 候选框无「搜狗搜索」或推广内容
- 任务管理器中无 `SGRender.exe` / `SogouCloud.exe`
- 内存占用下降 100-300MB（禁用前 SGRender 常驻）

## 🤝 开源贡献

此 skill 可自由分享到 skill 市场。建议遵循以下规范：
- 保持 `.bak` 重命名方式（可逆、安全）
- 新版本搜狗发布后及时更新组件清单
- 欢迎提交 PR 补充更多版本兼容性
