# Intake Pipeline runner — called by Windows Task Scheduler or manually
#
# Usage:
#   .\run-intake.ps1 -SourcePath "G:\My Drive\_intake"  # moves from Google Drive, then processes
#   .\run-intake.ps1                                     # no source — just processes local _intake

param(
    [string]$SourcePath
)

$appDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$localIntake = Join-Path $appDir "data\_intake"
$logFile = Join-Path $appDir "data\_logs\scheduled-run.log"

# Ensure directories exist
New-Item -ItemType Directory -Force -Path (Join-Path $appDir "data\_intake") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $appDir "data\_logs") | Out-Null

# Step 1: Move files from source to local intake (only if a source was specified)
if ($SourcePath) {
    $resolvedSource = (Resolve-Path $SourcePath -ErrorAction SilentlyContinue).Path
    $resolvedLocal = (Resolve-Path $localIntake -ErrorAction SilentlyContinue).Path

    if (-not $resolvedSource) {
        Add-Content -Path $logFile -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Source folder not found: $SourcePath (skipping move)"
    } elseif ($resolvedSource -ne $resolvedLocal) {
        $files = Get-ChildItem -Path "$SourcePath\*" -File -Include "*.txt","*.md" -ErrorAction SilentlyContinue
        foreach ($f in $files) {
            $dest = Join-Path $localIntake $f.Name
            try {
                Move-Item -Path $f.FullName -Destination $dest -Force
                Add-Content -Path $logFile -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Moved from source: $($f.Name)"
            } catch {
                Add-Content -Path $logFile -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ERROR moving $($f.Name): $_"
            }
        }
    }
}

# Step 2: Run intake processor via WSL
# Convert Windows app path to WSL path (E:\intake → /mnt/e/intake)
$driveLetter = $appDir.Substring(0,1).ToLower()
$remainder = $appDir.Substring(2) -replace '\\','/'
$wslAppDir = "/mnt/$driveLetter$remainder"
$wslLog = "$wslAppDir/data/_logs/scheduled-run.log"
$wslCmd = "cd $wslAppDir && python3 intake.py >> $wslLog 2>&1"
wsl.exe -e bash -c $wslCmd
