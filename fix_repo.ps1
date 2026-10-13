<#
fix_repo.ps1 — 一次性修复"虚拟环境被 Git 跟踪"的问题

※ 编码警告（这不是废话，是真实事故）：
  本文件必须保存为「UTF-8 with BOM」。因为 Windows PowerShell 5.1 读取无 BOM 的
  .ps1 文件时会按系统 ANSI 代码页（中文系统 = GBK）解码，里面的中文会全乱码，
  脚本连语法都过不了。用 VS Code 改这个文件时，右下角要选 "UTF-8 with BOM"。
  （对比：.py 文件不需要 BOM，Python 3 默认就按 UTF-8 读源码。）

背景：你的 D:\mycode 仓库里，.venv 的 1473 个文件已经被提交进 Git，
而且 .gitignore 是个 0 字节空文件（等于没写）。

脚本做的事（每步都打印验证结果）：
  1. 备份现有 .gitignore（如果是空的就跳过，直接重写）
  2. 写入正确的 .gitignore（UTF-8 无 BOM）
  3. 把已跟踪的 .venv 从版本控制移出（--cached = 只删索引，**不碰硬盘文件**）
  4. 验证：被跟踪的 .venv 文件数、硬盘上 .venv 是否完好、.gitignore 是否真的生效

脚本不会自动 commit —— 提交前自己看一眼 git status，这是习惯。

用法：
    cd D:\mycode
    powershell -ExecutionPolicy Bypass -File .\fix_repo.ps1
#>

# 原生程序(git)往 stderr 写东西时，不要让 PowerShell 把它当成致命错误
$ErrorActionPreference = 'Continue'

function Assert-Ok {
    param([string]$What)
    if ($LASTEXITCODE -ne 0) { throw "$What 失败（退出码 $LASTEXITCODE），已中止。" }
}

# ---------- 0. 安全检查：必须在"项目根目录且含 .git"的地方运行 ----------
$root = (Get-Location).Path
if (-not (Test-Path (Join-Path $root '.git'))) {
    throw "当前目录不是 Git 仓库根目录：$root   请先 cd D:\mycode"
}
if ($root -match '^[A-Za-z]:\\?$') {
    throw "拒绝在盘符根目录执行：$root"
}
Write-Host "[0] 项目根目录：$root" -ForegroundColor Cyan

$trackedBefore = @(git ls-files 2>$null | Select-String -Pattern '^\.venv/').Count
Assert-Ok 'git ls-files'
Write-Host "    当前被 Git 跟踪的 .venv 文件数：$trackedBefore" -ForegroundColor Yellow

# ---------- 1. 备份旧 .gitignore ----------
if (Test-Path '.gitignore') {
    $size = (Get-Item '.gitignore').Length
    if ($size -eq 0) {
        Write-Host "[1] 现有 .gitignore 是空的（0 字节）—— 这就是坑的根源，不备份，直接重写。" -ForegroundColor Yellow
    } else {
        Copy-Item '.gitignore' '.gitignore.bak' -Force
        Write-Host "[1] 已备份到 .gitignore.bak（原文件 $size 字节）" -ForegroundColor Green
    }
} else {
    Write-Host "[1] 没有 .gitignore，直接新建。" -ForegroundColor Green
}

# ---------- 2. 写入 .gitignore（UTF-8 无 BOM！） ----------
# 注意：PowerShell 5.1 的 `Set-Content -Encoding utf8` 会写入 BOM，
# 而带 BOM 的 .gitignore 第一条规则可能失效。所以用 .NET 显式指定"无 BOM"。
$gitignore = @'
# ==================== Python 垃圾文件 ====================
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
build/
dist/
*.bak

# ==================== 虚拟环境：绝对不要入库 ====================
.venv/
venv/
env/
ENV/

# ==================== 密钥 / 私有配置：安全红线 ====================
.env
.env.*
!.env.example
config.py
secrets.json
*.pem

# ==================== 编辑器与系统 ====================
.vscode/
.idea/
Thumbs.db
desktop.ini

# ==================== 运行产物 ====================
plan.txt
'@
$gitignorePath = Join-Path $root '.gitignore'
[System.IO.File]::WriteAllText($gitignorePath, $gitignore, (New-Object System.Text.UTF8Encoding $false))
$newSize = (Get-Item $gitignorePath).Length
Write-Host "[2] .gitignore 已写入：$newSize 字节，$((Get-Content $gitignorePath).Count) 行，UTF-8 无 BOM" -ForegroundColor Green

# ---------- 3. 从索引移除 .venv ----------
if ($trackedBefore -gt 0) {
    git rm -r --cached .venv --quiet 2>$null
    Assert-Ok 'git rm -r --cached .venv'
    Write-Host "[3] 已执行 git rm -r --cached .venv（只动索引；你的 .venv 文件夹还在硬盘上）" -ForegroundColor Green
} else {
    Write-Host "[3] .venv 本来就没被跟踪，跳过。" -ForegroundColor Green
}

# ---------- 3.5 密钥安全自检（比 .venv 更严重的问题） ----------
$trackedSecrets = @(
    git ls-files 2>$null |
    Select-String -Pattern '^(\.env|\.env\..*|config\.py|secrets\.json|.*\.pem)$' |
    ForEach-Object { $_.Line }
)
if ($trackedSecrets.Count -gt 0) {
    Write-Host "[!] 警告：以下「可能含密钥」的文件已经被 Git 跟踪：" -ForegroundColor Red
    $trackedSecrets | ForEach-Object { Write-Host "      $_" -ForegroundColor Red }
    Write-Host "    先打开确认内容，再自己执行（--cached 不会删硬盘文件）：" -ForegroundColor Yellow
    $trackedSecrets | ForEach-Object { Write-Host "      git rm --cached `"$_`"" -ForegroundColor White }
    Write-Host "    记住：只要提交过，密钥就永远留在 Git 历史里能翻出来。" -ForegroundColor Yellow
    Write-Host "    如果那是真实密钥 —— 立刻去平台作废重发一个，这是标准操作。" -ForegroundColor Yellow
} else {
    Write-Host "[3.5] 密钥自检：没有密钥类文件被跟踪 ✓" -ForegroundColor Green
}

# ---------- 4. 验证 ----------
$trackedAfter = @(git ls-files 2>$null | Select-String -Pattern '^\.venv/').Count
$venvPython = Test-Path (Join-Path $root '.venv\Scripts\python.exe')

git check-ignore -q .venv 2>$null
$isIgnored = ($LASTEXITCODE -eq 0)

Write-Host ""
Write-Host "==================== 验 证 结 果 ====================" -ForegroundColor Cyan
Write-Host "  .venv 被跟踪文件数 : $trackedBefore -> $trackedAfter   （目标 0）"
Write-Host "  硬盘上的 .venv 完好 : $venvPython   （必须是 True）"
Write-Host "  .gitignore 生效     : $isIgnored   （必须是 True）"
Write-Host "====================================================" -ForegroundColor Cyan

if ($trackedAfter -ne 0 -or -not $venvPython -or -not $isIgnored) {
    Write-Host "有检查项没过，先别提交，把上面的输出发给你的 AI 导师。" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "三条全过。接下来你自己敲这两条命令：" -ForegroundColor Yellow
Write-Host "  git status     # 看清楚这次改动删掉了哪些文件（应该是 1473 个 D 和 1 个 M）" -ForegroundColor White
Write-Host "  git commit -m `"chore: 补上 .gitignore，将 .venv 移出版本控制`"" -ForegroundColor White
if ($trackedSecrets.Count -gt 0) {
    Write-Host ""
    Write-Host "但上面那条「密钥警告」还没处理完，先把它处理掉再提交。" -ForegroundColor Red
}
