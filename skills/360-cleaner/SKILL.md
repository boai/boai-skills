---
name: 360-cleaner
description: 扫描系统上所有360旗下的软件，让用户手动选择要卸载/清理的软件，支持预设方案
triggers:
  - 清理360
  - 卸载360
  - 删除360
  - 360残留
  - 360卸载
  - clean 360
  - remove 360
  - 360清理
  - 管理360
platform: windows
verified: Windows 11 Pro
---

# 360 Cleaner（360 软件管理器）

扫描系统上已安装和残留的所有360产品，由用户**手动选择**要卸载/清理哪些。

## 工作流程

```
扫描发现 → 分类展示 → 用户勾选 → 执行清理 → 验证结果
```

### 第 1 步：扫描发现

扫描以下位置，找出所有360产品痕迹：

```bash
# 主安装目录
ls -d "/c/Program Files (x86)/360/"*/
ls -d "/c/Program Files/360/"*/ 2>/dev/null

# 开始菜单快捷方式
ls -d "/c/ProgramData/Microsoft/Windows/Start Menu/Programs/360"*/
ls -d "/c/Users/$USER/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/360"*/

# ProgramData 数据目录
ls -d "/c/ProgramData/360"*/

# 用户数据目录
ls -d "/c/Users/$USER/AppData/Roaming/360"*/
ls -d "/c/Users/$USER/AppData/Local/360"*/
ls -d "/c/Users/$USER/AppData/LocalLow/360"*/

# 内核驱动
ls /c/Windows/System32/drivers/360*

# 注册表
reg query "HKLM\SOFTWARE\WOW6432Node\360Safe" /s 2>/dev/null
reg query "HKCU\SOFTWARE\360" /s 2>/dev/null

# Windows 服务
sc query state= all 2>/dev/null | grep -i "360"
```

### 第 2 步：分类展示

根据扫描结果，按以下分类整理给用户。每个产品标注**完整路径**和**磁盘占用**。

#### 360 产品识别表

| 产品名 | 目录标识 | 常用路径 |
|--------|----------|----------|
| 🔧 360驱动大师 | `360DrvMgr` | `Program Files (x86)\360\360DrvMgr` |
| 🗜️ 360压缩 | `360zip` | `Program Files (x86)\360\360zip` |
| 🛡️ 360安全卫士 | `360safe` | `Program Files (x86)\360\360Safe` |
| 🦠 360杀毒 | `360sd` | `Program Files\360\360sd` |
| 🌐 360安全浏览器 | `360se` | `Program Files (x86)\360\360se` |
| 🧹 360清理大师 | `360CleanHelper` | `Program Files (x86)\360\360CleanHelper` |
| 📦 360软件管家 | `360SoftMgr` | `Program Files (x86)\360\360SoftMgr` |
| 📱 360手机助手 | `360MobileMgr` | `Program Files (x86)\360\360MobileMgr` |
| 🖼️ 360画报 | `360huabao` | `Program Files (x86)\360\360huabao` |
| 🩹 360系统急救箱 | `360reskit`(exe) | `Program Files (x86)\360\360reskit` |
| 🗑️ 360文件粉碎机 | `360FileShredder` | `Program Files (x86)\360\360FileShredder` |
| 💾 360文件恢复 | `360FileRecovery` | `Program Files (x86)\360\360FileRecovery` |
| 📡 360WiFi | `360WiFi` | `Program Files (x86)\360\360WiFi` |
| 🎮 360游戏大厅 | `360Game` | `Program Files (x86)\360\360Game` |
| 🔌 360漏洞修复 | `360leakfixer` | `Program Files (x86)\360\360leakfixer` |
| 📺 360影视 | `360vod` | `Program Files (x86)\360\360vod` |
| 🧑‍🔧 360专家服务 | `Expert` 缓存 | `AppData\Roaming\Expert` |

#### 残留物分类（无主程序的产品残留）

| 残留类型 | 标识 | 说明 |
|----------|------|------|
| 安装器临时文件 | `360Base.dll`, `360net.dll`, `360Inst.exe` | 曾安装/卸载某360产品的残留 |
| 图标/快捷方式缓存 | `*360safe*.png`, `*360se*.png` | 各类系统工具收录的360图标 |
| 监控日志 | `360TptMon*.log` | 搜狗输入法等软件记录的360监控日志 |
| IE缓存 | DOMStore `*360*` | IE浏览器访问360网站的DOM缓存 |
| 开始菜单空壳 | `360安全中心` 快捷方式 | 指向已卸载程序的死链 |

### 第 3 步：用户勾选

使用 `AskUserQuestion` 工具，以 **多选 + 分组** 方式让用户勾选要删除的软件。

预设快捷选项（作为第一个选项展示）：

| 预设名称 | 说明 |
|----------|------|
| ⚡ 仅保留驱动和压缩 | 删掉所有其他360产品，只留 `360DrvMgr` + `360zip` |
| 🔥 全部删除 | 删除所有360产品（包括驱动大师和压缩） |
| ✏️ 手动挑选 | 逐个勾选要删除的产品 |

**重要**：默认选中「仅保留驱动和压缩」作为推荐预设。

### 第 4 步：执行清理

根据用户选择，按以下策略清理每个产品：

#### 清理策略

对用户勾选的每个产品：

```
1. 终止相关进程（taskkill）
2. 删除主程序目录（Program Files 下的产品目录）
3. 删除用户数据目录（AppData\Roaming, AppData\Local 下的对应目录）
4. 删除 ProgramData 共享数据（仅当对应产品不存在 Program Files 主目录时）
5. 删除开始菜单快捷方式
6. 删除内核驱动文件（C:\Windows\System32\drivers\ 下对应的 .sys）
7. 清理注册表项
8. 删除 Windows 服务（sc delete）
```

#### 共享组件的处理

部分文件被多个产品共享时，采用以下规则：
- 安装在 `Program Files (x86)\360\` 下的子目录各自独立，按需删除
- `ProgramData\360zip\` 仅属于360压缩，勾选压缩才删除
- `AppData\Roaming\Expert\` 仅属于360专家服务，勾选才删除
- `C:\Windows\System32\drivers\360Sensor_DM64.sys` 仅属于驱动大师
- `C:\Windows\System32\drivers\360reskit64.sys` 属于360安全卫士

#### 顽固文件处理

对受系统保护的文件（如 `C:\Windows\System32\drivers\360reskit64.sys`），使用自提权 PowerShell：

```powershell
# 生成自提权脚本，用户右键 "使用 PowerShell 运行"
$admin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $admin) {
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}
# 对每个顽固文件：
#   1. attrib -r -h -s <file>     — 移除保护属性
#   2. sc stop <service>           — 停止关联服务
#   3. takeown /f <file>           — 夺取所有权
#   4. icacls <file> /grant Administrators:F — 授予权限
#   5. del /f /q <file>            — 删除
#   如果仍失败 → MoveFileEx MOVEFILE_DELAY_UNTIL_REBOOT 标记重启删除
```

### 第 5 步：验证结果

```bash
echo "=== 剩余360目录 ===" 
find "/c/Program Files (x86)/360" "/c/ProgramData/360"* "/c/Users/$USER/AppData/Roaming/360"* -maxdepth 1 -type d 2>/dev/null

echo "=== 驱动残留 ===" 
ls /c/Windows/System32/drivers/360* 2>/dev/null

echo "=== 注册表 ===" 
reg query "HKLM\SOFTWARE\WOW6432Node\360Safe" 2>&1
reg query "HKCU\SOFTWARE\360" 2>&1

echo "=== 服务 ===" 
sc query state= all 2>/dev/null | grep -i "360"
```

---

## 内置预设方案

### 预设 1：仅保留驱动和压缩

```
保留：360DrvMgr, 360zip
删除：其他所有360产品 + 所有残留物
```

触发词：`删除360保留驱动和压缩` `清理360只留驱动大师和360压缩`

### 预设 2：全部删除

```
删除：所有360产品，包括驱动大师和压缩
```

触发词：`彻底删除所有360` `完全卸载360`

### 预设 3：手动模式（默认）

扫描 → 展示 → 用户勾选。无特定触发词，默认行为。

---

## 关键陷阱

### 误判过滤

大量非360文件在其哈希/ID中碰巧包含数字"360"，**不得匹配**：

| 误判模式 | 示例 | 实际来源 |
|----------|------|----------|
| 随机哈希含360 | `rule360000v2.xml`, `*360*.js` | Office、VS Code 等 |
| 产品名含360 | `xbox_360_*.txt` | Steam |
| 版本号含360 | `dao360.dll` | Microsoft DAO |
| 纯数字ID | `1336085817`, `536096151` | 网易云歌词 |
| hex含360 | `dcc8d2360...` | AlibabaProtect |

**判断逻辑**：只有当文件**路径的目录部分**包含360且是360产品目录（如 `360Safe`、`360sd`、`360zip` 等）时，才认定是360产品。**不要匹配**路径中散列UUID碰巧含"360"的文件。

### 权限要求
- 普通文件/目录：大部分无需管理员
- `C:\Windows\System32\drivers\` 下的 `.sys` 文件：**必须管理员权限**
- 运行中的服务/进程：先 `taskkill` / `sc stop`，再删除

### 不完整卸载的常见残留
- 卸载程序可能留下 `AppData\Roaming\` 下的空目录
- 开始菜单快捷方式可能变成死链
- 内核驱动 `.sys` 文件可能不被卸载程序处理
- 注册表项可能残留

---

## 验证标准

- ✅ 用户选择保留的产品完整可用
- ✅ 用户选择删除的产品：主程序、用户数据、缓存、注册表、服务、驱动全部清理
- ✅ 无死链快捷方式残留
- ✅ 无注册表残留项
- ✅ 无误删（非360文件未受影响）
