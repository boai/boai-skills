---
name: 360-cleaner
description: 清理360软件残留，只保留360驱动大师和360压缩，删除其他所有360相关的文件、缓存、注册表和驱动
triggers:
  - 清理360
  - 卸载360
  - 删除360
  - 360残留
  - 360卸载
  - clean 360
  - remove 360
  - 360清理
platform: windows
verified: Windows 11 Pro + 360驱动大师 + 360压缩
---

# 360 Cleaner（360 残留清理器）

清理系统上除「360驱动大师」和「360压缩」之外的所有360相关残留（安全卫士、杀毒、浏览器、专家服务等）。

> ⚠️ 本工具仅删除残留文件和缓存，不影响360驱动大师和360压缩的正常使用。

## 保留 vs 删除

| 产品 | 标识 | 处理 |
|------|------|------|
| 🔧 360驱动大师 | `360DrvMgr`, `360Sensor_DM` | ✅ 保留 |
| 🗜️ 360压缩 | `360zip`, `360Zip` | ✅ 保留 |
| 🛡️ 360安全卫士 | `360safe`, `360reskit` | ❌ 删除 |
| 🦠 360杀毒 | `360sd` | ❌ 删除 |
| 🌐 360浏览器 | `360se` | ❌ 删除 |
| 📡 360传输监控 | `360TptMon` | ❌ 删除 |
| 🧑‍🔧 360专家服务 | `helpton.360.cn`, `opplat.jishi.360.cn` 缓存 | ❌ 删除 |
| 📦 360安装器残留 | `360Base.dll`, `360net.dll`, `360Inst.exe` | ❌ 删除 |

## 用法

### 自动模式（推荐）

直接对 Claude 说以下任意一句即可：

```
/oh-my-claudecode:360-cleaner
```

或提及触发词：
- "清理360残留"
- "卸载360"
- "删除360，保留驱动和压缩"

Claude 将自动执行：全面扫描 → 识别保留/删除 → 执行删除 → 处理顽固驱动 → 验证结果。

### 手动模式（如果自动执行权限不足）

当遇到 `360reskit64.sys` 驱动文件无法删除时，Claude 会生成一个自提权 PowerShell 脚本，请右键以管理员身份运行：

```powershell
# 右键 → 使用 PowerShell 运行
.\del360.ps1
```

## 自动化执行流程

### 第 1 步：全面扫描

```bash
# 扫描所有常见位置
find /c/Program Files /c/Program Files (x86) /c/ProgramData \
  /c/Users -maxdepth 6 -iname "*360*" -type d 2>/dev/null

# 检查驱动文件
ls /c/Windows/System32/drivers/*360*
```

### 第 2 步：检查注册表

```bash
reg query "HKLM\SOFTWARE\WOW6432Node\360Safe" /s 2>/dev/null
reg query "HKCU\SOFTWARE\360" /s 2>/dev/null
```

### 第 3 步：删除已知残留

```bash
# 开始菜单残留
rm -rf "/c/ProgramData/Microsoft/Windows/Start Menu/Programs/360安全中心"
rm -rf "/c/Users/<用户名>/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/360安全中心"

# 360安装器临时文件（含360Base.dll, 360net.dll, 360Inst.exe）
find "/c/Users/<用户名>/AppData/Local/Temp" -maxdepth 2 -path "*360*" -delete 2>/dev/null

# 360专家服务缓存
rm -rf "/c/Users/<用户名>/AppData/Roaming/Expert/cache"

# 360TptMon 日志
find "/c/Users/<用户名>/AppData/LocalLow/SogouPY/LOG/IME" -name "360TptMon*.log" -delete 2>/dev/null

# 360图标缓存（Windows Master / 其他软件收录的360图标）
find "/c/ProgramData/Windows Master" \( -name "*360safe*" -o -name "*360se*" -o -name "*360_safe_browser*" \) -delete 2>/dev/null
find "/c/Users/<用户名>/AppData/Local/Windows Master" -name "*360se*" -delete 2>/dev/null

# IE浏览器360网站缓存
find "/c/Users/<用户名>/AppData/Local/Microsoft/Internet Explorer/DOMStore" -name "*360*" -delete 2>/dev/null

# 注册表清理
reg delete "HKLM\SOFTWARE\WOW6432Node\360Safe" /f 2>/dev/null
reg delete "HKCU\SOFTWARE\360" /f 2>/dev/null
```

### 第 4 步：处理顽固驱动文件

`C:\Windows\System32\drivers\360reskit64.sys` 是360安全卫士的内核驱动残留，普通权限无法删除。

**注意区分**：
- `360reskit64.sys` → 360安全卫士的 rescue kit 驱动（**删除**）
- `360Sensor_DM64.sys` → 360驱动大师的内核驱动（**保留**，DM = Driver Master）

```powershell
# 自提权 PowerShell 脚本
$admin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $admin) {
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}
$f = "C:\Windows\System32\drivers\360reskit64.sys"
if (-not (Test-Path $f)) { Write-Host "Already gone!"; exit }

# 移除文件保护属性
attrib -r -h -s $f 2>$null
# 停止关联服务（如有）
sc stop 360reskit64 2>$null
# 夺取所有权
cmd /c "takeown /f `"$f`""
# 授予完全控制
cmd /c "icacls `"$f`" /grant Administrators:F"
# 删除
cmd /c "del /f /q `"$f`""

# 如果仍失败，标记重启后删除
if (Test-Path $f) {
    $def = @'
[DllImport("kernel32.dll", SetLastError=true, CharSet=CharSet.Auto)]
public static extern bool MoveFileEx(string lpExistingFileName, string lpNewFileName, int dwFlags);
'@
    Add-Type -Name MF -Namespace W32 -MemberDefinition $def
    $r = [W32.MF]::MoveFileEx($f, $null, 4)
    if ($r) { Write-Host "[OK] Marked for delete on reboot. Please restart." }
}
```

### 第 5 步：验证结果

```bash
# 确认只有驱动大师和压缩残留
find /c/ProgramData /c/Users /c/Program Files -maxdepth 6 -iname "*360*" 2>/dev/null | grep -iv "360zip\|360drvmgr\|360Drv"

# 确认360reskit已删除，360Sensor仍保留
ls /c/Windows/System32/drivers/360*

# 确认注册表已清
reg query "HKLM\SOFTWARE\WOW6432Node\360Safe" 2>&1
reg query "HKCU\SOFTWARE\360" 2>&1

# 确认无360服务
sc query state= all | grep -i "360"
```

## 关键陷阱

### 误判风险
大量非360文件在哈希/ID中包含数字"360"（如 `rule360000v2.xml`、`xbox_360_*.txt`、`dao360.dll`、Office包里的 `*360*.js` 等）。**必须通过目录上下文判断**，不能单纯按文件名匹配。

**过滤这些正常文件**：
- `*.dartServer/*` — Dart 编译缓存
- `*JianyingPro*` — 剪映缓存
- `*Corsair*` — 海盗船驱动缓存
- `*Netease*` — 网易云音乐歌词/缓存
- `*Tencent*` — 腾讯QQ缓存
- `*Steam*` — Steam Xbox 360手柄配置
- `*NVIDIA*` — 显卡驱动缓存
- `*Microsoft/Office*` — Office 规则文件
- `*Microsoft/Windows/ClipSVC*` — Windows 系统文件

### 权限问题
- 大部分残留文件无需管理员权限即可删除
- `C:\Windows\System32\drivers\360reskit64.sys` 需要管理员权限并可能需要 `takeown` + `icacls`
- 如果 `takeown` 也失败，使用 `MoveFileEx(MOVEFILE_DELAY_UNTIL_REBOOT)` 标记重启删除

### 压缩更新缓存保护
`AppData\Roaming\360zip\v3update\` 目录下的 `.exe` 安装包属于360压缩的正常更新缓存文件，**不应删除**。

## 验证标准

- ✅ 无360安全卫士相关目录和文件
- ✅ 无360杀毒残留
- ✅ 无360浏览器残留
- ✅ 注册表无360Safe相关项
- ✅ 系统服务中无360广告/安全服务
- ✅ `360reskit64.sys` 已删除
- ✅ `360Sensor_DM64.sys` 仍保留（驱动大师）
- ✅ `C:\Program Files (x86)\360\360DrvMgr\` 完整保留
- ✅ `C:\Program Files (x86)\360\360zip\` 完整保留
- ✅ 360驱动大师和360压缩正常使用

## 适用版本

- Windows 10 / Windows 11 所有版本
- 适用于360安全卫士、360杀毒、360浏览器、360WiFi等360全系产品的残留清理
- 非破坏性：不会影响360驱动大师和360压缩的正常使用

## 恢复方法

本工具执行的是**直接删除**（非重命名），删除后无法恢复。如需使用已删除的360产品（安全卫士/杀毒等），请重新安装。
