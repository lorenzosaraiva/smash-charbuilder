param(
    [switch]$Setup,
    [switch]$Init,
    [ValidateRange(1, 128)][int]$Jobs = 4,
    [string]$Distribution = 'Ubuntu'
)
$ErrorActionPreference = 'Stop'
$labRoot = Split-Path -Parent $PSScriptRoot
& (Join-Path $labRoot 'ssb-decomp-re\tools\build-character-lab.ps1') `
    -Setup:$Setup -Init:$Init -Jobs $Jobs -Distribution $Distribution
$labDist = Join-Path $labRoot 'dist'
New-Item -ItemType Directory -Path $labDist -Force | Out-Null
foreach ($labName in @('character-lab.z64','character-lab.zip','build-info.json',
                       'SHA256SUMS.txt','PLAY.md','release-notes.md')) {
    Copy-Item -LiteralPath (Join-Path $labRoot "ssb-decomp-re\dist\$labName") -Destination $labDist
}
Write-Output 'Checked files ready in root dist/.'
