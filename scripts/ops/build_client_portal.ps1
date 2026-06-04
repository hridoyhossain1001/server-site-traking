param(
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"
$workspace = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$portal = Join-Path $workspace "client-portal"
$dist = Join-Path $portal "dist"
$target = Join-Path $workspace "app\static\client-portal"

if (-not $SkipInstall) {
    npm --prefix $portal install
}

npm --prefix $portal run build

$resolvedTarget = [System.IO.Path]::GetFullPath($target)
$resolvedStaticRoot = [System.IO.Path]::GetFullPath((Join-Path $workspace "app\static"))
if (-not $resolvedTarget.StartsWith($resolvedStaticRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to replace files outside app\static."
}

if (Test-Path $target) {
    Remove-Item -LiteralPath $target -Recurse -Force
}

New-Item -ItemType Directory -Path $target -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $dist "index.html") -Destination $target
Copy-Item -LiteralPath (Join-Path $dist "assets") -Destination $target -Recurse

$assetCount = (Get-ChildItem (Join-Path $target "assets") -File).Count
$sizeKb = [math]::Round(((Get-ChildItem $target -Recurse -File | Measure-Object Length -Sum).Sum) / 1KB, 2)
Write-Host "Client portal static bundle refreshed: $assetCount assets, $sizeKb KB."
