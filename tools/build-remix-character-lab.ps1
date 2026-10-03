param(
    [switch]$Setup,
    [switch]$Incremental,
    [switch]$PackageOnly,
    [string]$Distribution = 'Ubuntu',
    [string]$RomDirectory = 'C:\Users\Lorenzo\Desktop\Smash 64\roms'
)
$ErrorActionPreference = 'Stop'
$remixProject = Join-Path (Split-Path -Parent $PSScriptRoot) 'remix'
$previousDistribution = $env:SMASH_WSL_DISTRO
Push-Location $remixProject
try {
    $env:SMASH_WSL_DISTRO = $Distribution
    if ($Setup) {
        $env:PIPENV_VENV_IN_PROJECT = '1'
        python -m pip install pipenv
        if ($LASTEXITCODE -ne 0) { throw 'Pipenv installation failed.' }
        python -m pipenv sync
        if ($LASTEXITCODE -ne 0) { throw 'Remix dependency installation failed.' }
        python -m pipenv run python -m pip install -r scripts/requirements-test.txt
        if ($LASTEXITCODE -ne 0) { throw 'ROM verifier dependency installation failed.' }
    }
    $remixArgs = @('scripts/build_charlab.py', '--desktop', $RomDirectory)
    if ($Incremental) { $remixArgs += '--incremental' }
    if ($PackageOnly) { $remixArgs += '--package-only' }
    $remixPython = Join-Path $remixProject '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $remixPython) {
        & $remixPython @remixArgs
    } else {
        python -m pipenv run python @remixArgs
    }
    if ($LASTEXITCODE -ne 0) { throw 'Remix build/check failed. See remix/charlab-*.log.' }
} finally {
    $env:SMASH_WSL_DISTRO = $previousDistribution
    Pop-Location
}
