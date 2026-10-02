param(
    [switch]$Setup,
    [switch]$Init,
    [ValidateRange(1, 128)][int]$Jobs = 4,
    [string]$Distribution = 'Ubuntu'
)

$ErrorActionPreference = 'Stop'
$labRoot = Split-Path -Parent $PSScriptRoot
$labArguments = @('tools/build-character-lab.sh', '--jobs', "$Jobs")
if ($Setup) { $labArguments += '--setup' }
if ($Init) { $labArguments += '--init' }
Push-Location -LiteralPath $labRoot
try {
    & wsl.exe -d $Distribution -- bash @labArguments
    if ($LASTEXITCODE -ne 0) { throw "Character Lab build failed (exit $LASTEXITCODE)." }
} finally {
    Pop-Location
}
