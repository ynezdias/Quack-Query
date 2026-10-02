param(
    [ValidateRange(1, 65535)]
    [int]$Port = 8502
)

$ErrorActionPreference = 'Stop'
$projectPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $projectPython)) {
    $projectPython = Join-Path $PSScriptRoot 'venv/Scripts/python.exe'
}
if (-not (Test-Path -LiteralPath $projectPython)) {
    throw 'Create .venv and install requirements.txt before running QuackQuery.'
}

$applicationExitCode = 0
Push-Location -LiteralPath $PSScriptRoot
try {
    & $projectPython -m src.serve --host 127.0.0.1 --port $Port
    $applicationExitCode = $LASTEXITCODE
} finally {
    Pop-Location
}
exit $applicationExitCode
