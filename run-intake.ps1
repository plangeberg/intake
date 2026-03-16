# Intake Pipeline runner — called by Windows Task Scheduler or manually
#
# Runtime data lives in D:\AppData\intake (outside Synology Drive / git).
# Source code lives in this repo (D:\SynologyDrive\czechito\intake).
#
# Usage:
#   .\run-intake.ps1          # normal scheduled or manual run

$codeDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# AppData paths (Windows)
$dataRoot = "D:\AppData\intake\data"
$envFile  = "D:\AppData\intake\.env"
$logFile  = Join-Path $dataRoot "_logs\scheduled-run.log"

# WSL equivalents
$wslCodeDir  = "/mnt/d/SynologyDrive/czechito/intake"
$wslDataRoot = "/mnt/d/AppData/intake/data"
$wslEnvFile  = "/mnt/d/AppData/intake/.env"
$wslLog      = "$wslDataRoot/_logs/scheduled-run.log"

# Ensure AppData directories exist
New-Item -ItemType Directory -Force -Path "$dataRoot\_intake" | Out-Null
New-Item -ItemType Directory -Force -Path "$dataRoot\_processed" | Out-Null
New-Item -ItemType Directory -Force -Path "$dataRoot\_failed" | Out-Null
New-Item -ItemType Directory -Force -Path "$dataRoot\_logs" | Out-Null

# Run intake processor via WSL with env vars pointing to AppData
$wslCmd = "cd $wslCodeDir && INTAKE_DATA_ROOT=$wslDataRoot INTAKE_ENV_FILE=$wslEnvFile python3 intake.py >> $wslLog 2>&1"
wsl.exe -e bash -c $wslCmd
