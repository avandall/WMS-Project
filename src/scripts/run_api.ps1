# Runs the API with the project's .venv interpreter, avoiding VIRTUAL_ENV mismatch warnings.
# Usage (PowerShell):
#   cd D:\Hoc\First_Project\WMS
#   .\scripts\run_api.ps1

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$venvPython = Join-Path $projectRoot ".venv" | Join-Path "Scripts" | Join-Path "python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Error "Project venv not found at $venvPython. Create it with 'uv venv' or 'python -m venv .venv' and install deps."; exit 1
}

# Run main.py via uv run using the project interpreter
uv run --python $venvPython python main.py
