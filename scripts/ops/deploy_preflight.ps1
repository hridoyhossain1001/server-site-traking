param(
    [ValidateSet("backend", "client", "admin", "marketing", "all")]
    [string]$Target = "all"
)

$ErrorActionPreference = "Stop"
$workspace = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

$targets = [ordered]@{
    backend = @{
        Path = $workspace
        Delivery = "Direct server deploy only. Do not push backend code to GitHub."
    }
    client = @{
        Path = Join-Path $workspace "client-portal"
        Delivery = "GitHub: buykori-client-portal -> Vercel"
    }
    admin = @{
        Path = Join-Path $workspace "admin-portal"
        Delivery = "GitHub: buykori-admin-portal -> Vercel"
    }
    marketing = @{
        Path = Join-Path $workspace "marketing-site"
        Delivery = "GitHub: buykori-marketing-site -> Vercel"
    }
}

function Get-RepoStatus {
    param(
        [string]$RepoPath,
        [string[]]$IgnoredStatusLines = @()
    )

    if (-not (Test-Path (Join-Path $RepoPath ".git"))) {
        return [pscustomobject]@{
            IsRepo = $false
            Branch = "-"
            Dirty = $true
            Status = "Missing .git directory"
        }
    }

    $branch = (git -C $RepoPath branch --show-current).Trim()
    $statusLines = @(
        git -C $RepoPath status --short |
            Where-Object { $_ -and ($IgnoredStatusLines -notcontains $_) }
    )
    return [pscustomobject]@{
        IsRepo = $true
        Branch = $branch
        Dirty = $statusLines.Count -gt 0
        Status = if ($statusLines.Count) { $statusLines -join "`n" } else { "clean" }
    }
}

$selected = if ($Target -eq "all") { @($targets.Keys) } else { @($Target) }
$hasWarnings = $false

Write-Host "Buykori deployment preflight (read-only)" -ForegroundColor Cyan
Write-Host "Workspace: $workspace"
Write-Host ""

foreach ($name in $selected) {
    $config = $targets[$name]
    $ignoredLines = if ($name -eq "backend") { @(" M client-portal") } else { @() }
    $status = Get-RepoStatus -RepoPath $config.Path -IgnoredStatusLines $ignoredLines

    Write-Host "[$name]" -ForegroundColor Yellow
    Write-Host "Path: $($config.Path)"
    Write-Host "Delivery: $($config.Delivery)"
    Write-Host "Branch: $($status.Branch)"
    Write-Host "Status:"
    Write-Host $status.Status
    if ($name -eq "backend") {
        Write-Host "Note: root client-portal pointer marker is ignored because the client repo is checked separately."
    }
    Write-Host ""

    if (-not $status.IsRepo -or $status.Dirty) {
        $hasWarnings = $true
    }
}

if ($Target -eq "backend") {
    Write-Host "BLOCK: Backend GitHub push is intentionally outside the approved release flow." -ForegroundColor Red
    Write-Host "Use a reviewed direct server deployment only after explicit approval." -ForegroundColor Red
}

if ($hasWarnings) {
    Write-Host "Preflight completed with warnings. Review dirty or missing repos before release." -ForegroundColor Yellow
    exit 1
}

Write-Host "Preflight passed: selected repos are clean." -ForegroundColor Green
