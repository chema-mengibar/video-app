param(
    [switch]$SkipFfmpeg
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Frontend = Join-Path $Root "frontend"
$Venv = Join-Path $Root ".venv"
$Python = Join-Path $Venv "Scripts\python.exe"

function Test-Command($Name) {
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

Set-Location $Root

if (-not (Test-Command "python")) {
    throw "Python was not found. Install Python 3.12+ and run this script again."
}

if (-not (Test-Command "npm")) {
    throw "npm was not found. Install Node.js LTS and run this script again."
}

if (-not (Test-Path $Python)) {
    python -m venv $Venv
}

& $Python -m pip install --upgrade pip
& $Python -m pip install -r (Join-Path $Root "requirements.txt")

Push-Location $Frontend
npm install
npm run build
Pop-Location

if (-not $SkipFfmpeg) {
    $LocalFfmpeg = Join-Path $Root "tools\ffmpeg\bin\ffmpeg.exe"
    $HasFfmpeg = (Test-Command "ffmpeg") -or (Test-Path $LocalFfmpeg)
    if (-not $HasFfmpeg) {
        if (Test-Command "winget") {
            winget install --id Gyan.FFmpeg --source winget --accept-package-agreements --accept-source-agreements
        } else {
            Write-Warning "ffmpeg was not found. Install ffmpeg or place ffmpeg.exe and ffprobe.exe in tools\ffmpeg\bin."
        }
    }
}

Write-Host ""
Write-Host "Install complete."
Write-Host "Run the app with: .\scripts\run.ps1"
