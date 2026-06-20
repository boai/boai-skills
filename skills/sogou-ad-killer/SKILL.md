---
name: sogou-ad-killer
description: 扫描系统上所有搜狗旗下软件，让用户手动选择要关闭哪些软件的广告，支持一键全禁搜狗输入法
triggers:
  - 搜狗广告
  - 关闭搜狗广告
  - sogou ad
  - 搜狗输入法广告
  - 搜狗弹窗
  - sogou ad killer
  - 去搜狗广告
  - 搜狗去广告
  - 管理搜狗
platform: windows
verified: Windows 11 + 搜狗拼音 15.9.0.2525
---

# Sogou Ad Killer（搜狗广告管理器）

扫描系统上所有搜狗旗下软件，由用户**手动勾选**要关闭广告的产品。

## 工作流程

```
扫描发现 → 分类展示 → 用户勾选 → 执行禁用 → 验证结果
```

### 第 1 步：扫描发现

扫描系统中所有搜狗产品：

```bash
# 主安装目录
find "/c/Program Files" "/c/Program Files (x86)" -maxdepth 3 -iname "*sogou*" -type d 2>/dev/null

# 用户数据目录
find "/c/Users/$USER/AppData" -maxdepth 5 -iname "*sogou*" -type d 2>/dev/null

# 搜狗相关进程
tasklist 2>/dev/null | grep -i sogou

# 搜狗相关服务
sc query state= all 2>/dev/null | grep -i sogou
```

### 第 2 步：分类展示

根据扫描结果，列出搜狗旗下产品。每个产品标注**广告组件数量**和**预计释放内存**。

#### 搜狗产品广告清单

| 产品 | 目录标识 | 广告形式 | 广告组件数 | 预计释放 |
|------|----------|----------|:--------:|:--------:|
| ⌨️ 搜狗拼音输入法 | `SogouInput` | 弹窗/候选框/皮肤/游戏/商业推广 | 31+ | ~200MB |
| ✒️ 搜狗五笔输入法 | `SogouWBInput` | 弹窗/候选框广告 | 15+ | ~80MB |
| 🌐 搜狗浏览器 | `SogouExplorer` | 首页推广/信息流广告 | 8+ | ~50MB |
| 📄 搜狗PDF | `sogoupdf` | 升级弹窗/推广 | 3+ | ~10MB |
| 💾 搜狗磁盘管理 | `kdiskmgr_sogou` | 推广横幅 | 2+ | ~5MB |
| ✂️ 搜狗截图 | `SogouScreenshot` | 分享页广告 | 2+ | ~5MB |

### 第 3 步：用户勾选

使用 `AskUserQuestion` 让用户勾选要关闭广告的产品。

预设快捷选项：

| 预设名称 | 说明 |
|----------|------|
| ⚡ 一键全禁搜狗输入法 | 禁用搜狗拼音输入法全部31+广告组件（最常见需求） |
| 🔥 全部禁用 | 禁用所有已安装搜狗产品的广告 |
| ✏️ 手动挑选 | 逐个勾选要禁用广告的产品 |

**重要**：默认选中「一键全禁搜狗输入法」作为推荐预设。

### 第 4 步：执行禁用

#### 4A. 搜狗拼音输入法广告禁用

采用 `.bak` 重命名方式禁用（可逆，不删除文件）。

##### 需终止的进程

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

##### Components 目录广告组件（18个）

```bash
SOGOU_DIR="C:\Program Files (x86)\SogouInput\<version>"

# 商业推广中心
mv "$SOGOU_DIR/Components/biz_center/<ver>/biz_bundle.dll" "*.bak"
# 游戏中心
mv "$SOGOU_DIR/Components/game_center/<ver>/game_center.dll" "*.bak"
# 桌面弹窗
mv "$SOGOU_DIR/Components/SGDeskControl/<ver>/SGDeskControl.dll" "*.bak"
# CEF 广告渲染引擎（最占内存 ~200MB）
mv "$SOGOU_DIR/Components/SGRender/<ver>/SGRender.exe" "*.bak"
mv "$SOGOU_DIR/Components/SGRender/<ver>/SGRender.dll" "*.bak"
mv "$SOGOU_DIR/Components/SGRender/<ver>/SGRender64.dll" "*.bak"
mv "$SOGOU_DIR/Components/SGRender/<ver>/SGRenderDll.dll" "*.bak"
mv "$SOGOU_DIR/Components/SGRender/<ver>/libcef.dll" "*.bak"
# 写作助手
mv "$SOGOU_DIR/Components/WriteSpirit/<ver>/write_spirit.exe" "*.bak"
mv "$SOGOU_DIR/Components/WriteSpirit/<ver>/spirit_bundle.dll" "*.bak"
mv "$SOGOU_DIR/Components/WriteSpirit/<ver>/browser_host.dll" "*.bak"
mv "$SOGOU_DIR/Components/WriteSpirit/<ver>/interceptor.dll" "*.bak"
# 其他组件
mv "$SOGOU_DIR/Components/AppBox/<ver>/"*.dll "*.bak"
mv "$SOGOU_DIR/Components/SkinBox/<ver>/"*.dll "*.bak"
mv "$SOGOU_DIR/Components/SogouFlash/<ver>/"*.dll "*.bak"
mv "$SOGOU_DIR/Components/Theme/<ver>/"*.dll "*.bak"
mv "$SOGOU_DIR/Components/SogouComMgr.exe" "*.bak"
```

##### 主安装目录广告文件（13个）

```bash
# 云服务（含推荐）
mv "$SOGOU_DIR/SogouCloud.exe" "*.bak"
# 广告定时拉取
mv "$SOGOU_DIR/userNetSchedule.exe" "*.bak"
# 工具集（含推广入口）
mv "$SOGOU_DIR/SogouToolkits.exe" "*.bak"
# 迷你广告浏览器
mv "$SOGOU_DIR/SGMiniBrowserHelperHost.dll" "*.bak"
# 广告配置面板
mv "$SOGOU_DIR/pandorabox.cupf" "*.bak"
mv "$SOGOU_DIR/skin_recommend.cupf" "*.bak"
mv "$SOGOU_DIR/SmartInfo.cupf" "*.bak"
mv "$SOGOU_DIR/RightPopmenu.cupf" "*.bak"
mv "$SOGOU_DIR/wangzai_guide.cupf" "*.bak"
mv "$SOGOU_DIR/skin_btn_tips.cupf" "*.bak"
mv "$SOGOU_DIR/screencapture.cupf" "*.bak"
mv "$SOGOU_DIR/richinput.cupf" "*.bak"
```

##### 权限处理

- **Components 目录**：通常无需管理员权限
- **主安装目录**：需管理员权限，使用自提权 PowerShell

```powershell
Start-Process powershell -Verb RunAs -Wait -ArgumentList '-NoProfile -Command "cd \"<sogou_path>\"; @(\"file1\",\"file2\",...) | % { if(Test-Path $_) { Rename-Item $_ \"$_.bak\" -Force } }"'
```

#### 4B. 搜狗五笔输入法广告禁用

结构类似搜狗拼音，路径为 `C:\Program Files (x86)\SogouWBInput\<version>\`。

```bash
# 进程终止
taskkill /F /IM SogouWB*.exe 2>/dev/null
taskkill /F /IM wb_toolkit.exe 2>/dev/null

# 广告组件（路径结构与拼音类似，组件名可能不同）
# 扫描 Components 目录，对所有 .dll/.exe 执行 .bak 重命名
```

#### 4C. 其他搜狗产品广告禁用

##### 搜狗浏览器

```bash
# 路径：C:\Program Files (x86)\SogouExplorer\
# 禁用推广组件
taskkill /F /IM SogouExplorer.exe 2>/dev/null
mv "C:\Program Files (x86)\SogouExplorer\<ver>\sgspromo.dll" "*.bak"
mv "C:\Program Files (x86)\SogouExplorer\<ver>\sebundle.dll" "*.bak"
```

##### 搜狗PDF / 搜狗磁盘管理

```bash
# 主要关闭自启动和服务
sc stop sogoupdfsvc 2>/dev/null
sc config sogoupdfsvc start=disabled 2>/dev/null
sc stop kdiskmgr_svc 2>/dev/null
sc config kdiskmgr_svc start=disabled 2>/dev/null
```

### 第 5 步：验证

```bash
# 统计禁用的广告文件数
find "/c/Program Files (x86)/SogouInput" -name "*.bak" -type f 2>/dev/null | wc -l
find "/c/Program Files (x86)/SogouWBInput" -name "*.bak" -type f 2>/dev/null | wc -l

# 确认关键广告进程未运行
tasklist 2>/dev/null | grep -iE "SGRender|SogouCloud|write_spirit|userNetSchedule"

# 确认内存释放
# 重启后 SGRender.exe 不再驻留，释放 ~200MB
```

---

## 内置预设方案

### 预设 1：一键全禁搜狗输入法（推荐）

```
禁用：搜狗拼音输入法全部 31+ 广告组件
```

触发词：`去搜狗广告` `关闭搜狗广告` `sogou ad killer`

### 预设 2：全部禁用

```
禁用：所有已安装搜狗产品的广告
```

触发词：`彻底关闭搜狗广告` `禁用所有搜狗广告`

### 预设 3：手动模式（默认）

扫描 → 展示 → 用户勾选各产品。无特定触发词，默认行为。

---

## 关键陷阱

### 权限
- **Components 目录**：通常无需管理员权限
- **主安装目录** (`Program Files (x86)/SogouInput/<ver>/`)：需要管理员权限
- 使用 `Start-Process -Verb RunAs` 触发 UAC 提权

### 自动更新
- 搜狗输入法更新时会重新下载组件，可能恢复广告
- **务必提醒用户关闭自动更新**：右键输入法状态栏 → 属性设置 → 高级 → 取消「自动升级」

### 兼容性
| 产品 | 已验证版本 | 说明 |
|------|-----------|------|
| 搜狗拼音 | 15.9.0.2525 | 完整支持 |
| 搜狗五笔 | 理论兼容 | 目录结构相似，组件名可能不同 |
| 其他搜狗产品 | 理论兼容 | 需实际测试验证 |

### 恢复方法
```powershell
# 恢复所有禁用的广告组件（搜狗拼音）
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
0.0.0.0 ad.sogou.com
0.0.0.0 push.sogou.com
```

---

## 验证标准

- ✅ 用户选择禁用的产品：广告组件全部 `.bak` 重命名
- ✅ 重启后输入法正常使用，无弹窗/推广
- ✅ 候选框无「搜狗搜索」或推广内容
- ✅ 任务管理器中无 `SGRender.exe` / `SogouCloud.exe`
- ✅ 内存占用下降（禁用前 SGRender 常驻 ~200MB）
- ✅ 未选择的产品不受影响
- ✅ 所有操作可逆（`.bak` 重命名，不删除文件）
