# Sogou Ad Killer - 搜狗输入法广告清理脚本
# 需要管理员权限运行
# Run: right-click → Run with PowerShell (Administrator)

param(
    [switch]$Restore,    # -Restore: 恢复所有禁用的组件
    [switch]$DryRun,     # -DryRun: 仅列出将执行的操作，不实际执行
    [switch]$BlockHosts  # -BlockHosts: 额外在 hosts 文件中屏蔽广告域名
)

$ErrorActionPreference = "Stop"
$ScriptName = "Sogou Ad Killer"
$Version = "1.0.0"

# ──────────────────────────────────────
# 配置
# ──────────────────────────────────────
$SogouRoot = "C:\Program Files (x86)\SogouInput"
$SogouMain = $null  # 动态检测版本号

# 广告组件清单: key=相对路径, value=广告描述
$AdComponents = [ordered]@{
    # Components 目录
    "Components\biz_center"           = @{ Files=@("biz_bundle.dll"); Desc="商业推广中心" }
    "Components\game_center"          = @{ Files=@("game_center.dll"); Desc="游戏中心广告" }
    "Components\SGDeskControl"        = @{ Files=@("SGDeskControl.dll"); Desc="桌面弹窗广告" }
    "Components\SGRender"             = @{ Files=@("SGRender.exe","SGRender.dll","SGRender64.dll","SGRenderDll.dll","libcef.dll"); Desc="Chromium广告渲染引擎(最占内存~200MB)" }
    "Components\WriteSpirit"          = @{ Files=@("write_spirit.exe","spirit_bundle.dll","browser_host.dll","interceptor.dll"); Desc="写作助手广告" }
    "Components\AppBox"               = @{ Files=@("AppBox.exe","appbox_bundle.dll"); Desc="应用盒子推广" }
    "Components\SkinBox"              = @{ Files=@("skinbox_bundle.dll"); Desc="皮肤推荐盒子" }
    "Components\SogouFlash"           = @{ Files=@("SogouFlash.dll"); Desc="Flash广告" }
    "Components\Theme"                = @{ Files=@("theme_bundle.dll"); Desc="主题推荐" }
    "Components\HandInput"            = @{ Files=@("handinput_bundle.dll"); Desc="手写输入(含推荐)" }
    "Components\biz_pdf"              = @{ Files=@("biz_pdf.dll"); Desc="PDF推广" }
    # 主目录文件
    "Main"                            = @{ Files=@(
        "SogouCloud.exe",
        "userNetSchedule.exe",
        "SogouToolkits.exe",
        "SGMiniBrowserHelperHost.dll",
        "pandorabox.cupf",
        "skin_recommend.cupf",
        "SmartInfo.cupf",
        "RightPopmenu.cupf",
        "wangzai_guide.cupf",
        "skin_btn_tips.cupf",
        "screencapture.cupf",
        "screencapture.exe",
        "richinput.cupf"
    ); Desc="主程序广告/推荐文件" }
}

# Hosts 屏蔽域名
$AdDomains = @(
    "0.0.0.0 pcbao.sogou.com",
    "0.0.0.0 pb.sogou.com",
    "0.0.0.0 get.sogou.com",
    "0.0.0.0 config.pinyin.sogou.com",
    "0.0.0.0 ping.pinyin.sogou.com",
    "0.0.0.0 img.shouji.sogou.com",
    "0.0.0.0 ie.sogou.com"
)

# ──────────────────────────────────────
# 工具函数
# ──────────────────────────────────────
function Write-Banner {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║   $(if($Restore){'🔄'}else{'🧹'})  Sogou Ad Killer v$Version" -ForegroundColor Cyan
    Write-Host "║   $(if($Restore){'恢复所有广告组件'}else{'永久关闭搜狗输入法所有广告'})" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Text, [string]$Color="Yellow")
    Write-Host "  [$((Get-Date).ToString('HH:mm:ss'))] $Text" -ForegroundColor $Color
}

function Find-SogouVersion {
    $dirs = Get-ChildItem $SogouRoot -Directory | Where-Object { $_.Name -match '^\d+\.\d+\.\d+\.\d+$' } | Sort-Object Name -Descending
    if ($dirs.Count -eq 0) {
        throw "未找到搜狗输入法安装目录: $SogouRoot"
    }
    $script:SogouMain = $dirs[0].FullName
    Write-Step "检测到版本: $($dirs[0].Name)" "Green"
    return $dirs[0].FullName
}

function Get-ComponentVersionDir {
    param([string]$ComponentPath)
    $full = Join-Path $SogouRoot $ComponentPath
    if (-not (Test-Path $full)) { return $null }
    $dirs = Get-ChildItem $full -Directory | Where-Object { $_.Name -match '^\d+\.\d+\.\d+\.\d+$' } | Sort-Object Name -Descending
    if ($dirs.Count -eq 0) { return $null }
    return $dirs[0].FullName
}

function Invoke-AdOperation {
    param(
        [string]$Path,
        [string]$File,
        [string]$Operation  # "disable" or "restore"
    )
    $src = Join-Path $Path $File
    $bak = "$src.bak"

    if ($Operation -eq "disable") {
        if (Test-Path $src) {
            if ($DryRun) {
                Write-Host "      [DRY-RUN] Would rename: $File → $File.bak" -ForegroundColor Gray
                return $true
            }
            try {
                Rename-Item -Path $src -NewName "$File.bak" -Force -ErrorAction Stop
                return $true
            } catch {
                # 尝试提权
                try {
                    takeown /F $src 2>&1 | Out-Null
                    icacls $src /grant "Administrators:F" 2>&1 | Out-Null
                    Rename-Item -Path $src -NewName "$File.bak" -Force -ErrorAction Stop
                    return $true
                } catch {
                    Write-Host "      ❌ 权限不足: $File (需要管理员权限)" -ForegroundColor Red
                    return $false
                }
            }
        }
    } elseif ($Operation -eq "restore") {
        if (Test-Path $bak) {
            if ($DryRun) {
                Write-Host "      [DRY-RUN] Would restore: $File.bak → $File" -ForegroundColor Gray
                return $true
            }
            try {
                Rename-Item -Path $bak -NewName $File -Force -ErrorAction Stop
                return $true
            } catch {
                Write-Host "      ❌ 恢复失败: $File" -ForegroundColor Red
                return $false
            }
        }
    }
    return $null  # 文件不存在
}

function Invoke-RestoreAll {
    Write-Step "恢复所有禁用的广告组件..." "Cyan"

    $bakFiles = Get-ChildItem $SogouRoot -Recurse -Filter "*.bak" -ErrorAction SilentlyContinue
    if ($bakFiles.Count -eq 0) {
        Write-Host "  没有找到被禁用的 .bak 文件，无需恢复" -ForegroundColor Gray
        return
    }

    Write-Host "  找到 $($bakFiles.Count) 个 .bak 文件" -ForegroundColor Yellow

    $restored = 0
    foreach ($f in $bakFiles) {
        $original = $f.FullName -replace '\.bak$', ''
        if ($DryRun) {
            Write-Host "  [DRY-RUN] Would restore: $($f.Name) → $(Split-Path $original -Leaf)" -ForegroundColor Gray
            $restored++
            continue
        }
        try {
            Rename-Item -Path $f.FullName -NewName (Split-Path $original -Leaf) -Force -ErrorAction Stop
            Write-Host "  ✅ 恢复: $(Split-Path $original -Leaf)" -ForegroundColor Green
            $restored++
        } catch {
            Write-Host "  ❌ 恢复失败: $($f.Name) - $_" -ForegroundColor Red
        }
    }
    Write-Host "  共恢复 $restored 个组件" -ForegroundColor Green
}

function Invoke-DisableAll {
    $mainPath = Find-SogouVersion
    $total = 0
    $success = 0
    $skipped = 0

    foreach ($compKey in $AdComponents.Keys) {
        $comp = $AdComponents[$compKey]
        $desc = $comp.Desc

        if ($compKey -eq "Main") {
            $compPath = $mainPath
        } else {
            $compPath = Get-ComponentVersionDir $compKey
        }

        if (-not $compPath) {
            Write-Host "  ⬜ $desc — 未安装" -ForegroundColor Gray
            continue
        }

        Write-Host "  📦 $desc" -ForegroundColor Yellow

        foreach ($file in $comp.Files) {
            $total++
            $result = Invoke-AdOperation -Path $compPath -File $file -Operation "disable"
            if ($result -eq $true) {
                Write-Host "      ✅ $file → $file.bak" -ForegroundColor Green
                $success++
            } elseif ($result -eq $false) {
                Write-Host "      ❌ $file 失败" -ForegroundColor Red
            } else {
                Write-Host "      ⬜ $file (已禁用或不存在)" -ForegroundColor Gray
                $skipped++
            }
        }
    }

    return @{ Total=$total; Success=$success; Skipped=$skipped }
}

function Invoke-BlockHosts {
    if (-not $BlockHosts) { return }
    Write-Step "屏蔽搜狗广告域名 (hosts)..." "Cyan"

    $hostsPath = "C:\Windows\System32\drivers\etc\hosts"
    $blockStart = "# === Sogou Ad Killer Block Start ==="
    $blockEnd = "# === Sogou Ad Killer Block End ==="

    try {
        if ($DryRun) {
            Write-Host "  [DRY-RUN] Would add $($AdDomains.Count) domains to hosts file" -ForegroundColor Gray
            return
        }

        attrib -R $hostsPath 2>&1 | Out-Null
        $content = Get-Content $hostsPath -Raw -ErrorAction Stop

        # 移除已有屏蔽
        if ($content -match [regex]::Escape($blockStart)) {
            $content = $content -replace "(?ms)$blockStart.*$blockEnd\r?\n?", ""
        }

        $newBlock = "`r`n$blockStart`r`n$($AdDomains -join \"`r`n\")`r`n$blockEnd`r`n"
        $content = $content.TrimEnd() + $newBlock
        Set-Content -Path $hostsPath -Value $content -Force

        attrib +R $hostsPath 2>&1 | Out-Null
        Write-Host "  ✅ Hosts 已添加 $($AdDomains.Count) 条屏蔽规则" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ Hosts 修改失败: $_" -ForegroundColor Red
    }
}

function Invoke-KillProcesses {
    Write-Step "终止搜狗进程..." "Cyan"
    $procs = @(
        "SogouImeBroker", "SogouCloud", "SogouExe", "SogouSvc",
        "SGRender", "write_spirit", "userNetSchedule", "SogouToolkits",
        "SogouImeRepair", "screencapture", "sgfeedbackhelper", "crashrpt"
    )
    foreach ($p in $procs) {
        $killed = Stop-Process -Name $p -Force -ErrorAction SilentlyContinue -PassThru
        if ($killed) {
            Write-Host "  🔪 Killed: $p" -ForegroundColor Gray
        }
    }
    Write-Host "  进程清理完毕" -ForegroundColor Green
}

# ──────────────────────────────────────
# 主流程
# ──────────────────────────────────────
Write-Banner

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin -and -not $DryRun) {
    Write-Host "⚠️  未以管理员身份运行！部分文件可能无法修改。" -ForegroundColor Yellow
    Write-Host "  建议: 右键 → 以管理员身份运行 PowerShell" -ForegroundColor Yellow
    Write-Host ""
}

if (-not (Test-Path $SogouRoot)) {
    Write-Host "❌ 未找到搜狗输入法安装目录: $SogouRoot" -ForegroundColor Red
    Write-Host "  如果安装在非标准路径，请手动修改脚本中的 `SogouRoot` 变量" -ForegroundColor Red
    exit 1
}

if ($Restore) {
    Invoke-KillProcesses
    Invoke-RestoreAll
    Write-Host ""
    Write-Host "🎉 恢复完成！请重新启动搜狗输入法。" -ForegroundColor Green
} else {
    Invoke-KillProcesses
    $result = Invoke-DisableAll
    Invoke-BlockHosts

    Write-Host ""
    Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  🎉 清理完成！                           " -ForegroundColor Green
    Write-Host "║                                          " -ForegroundColor Cyan
    Write-Host "║  共处理: $($result.Total) 个广告文件        " -ForegroundColor Cyan
    Write-Host "║  已禁用: $($result.Success) 个              " -ForegroundColor Green
    Write-Host "║  已跳过: $($result.Skipped) 个              " -ForegroundColor Gray
    Write-Host "║                                          " -ForegroundColor Cyan
    Write-Host "║  请重启电脑使改动生效                    " -ForegroundColor Yellow
    Write-Host "║  建议关闭搜狗自动更新防止广告复活        " -ForegroundColor Yellow
    Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
