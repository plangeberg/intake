# Set up Windows Task Scheduler to run intake every 5 minutes
# Run this in PowerShell as Admin

$appDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$taskName = "Intake Pipeline"
$runnerScript = Join-Path $appDir "run-intake.ps1"

Write-Host ""
Write-Host "Intake Pipeline — Scheduled Task Setup"
Write-Host "======================================="
Write-Host ""
Write-Host "Do you want intake to pull files from another folder (e.g. Google Drive)?"
Write-Host "If so, files will be moved from that folder into the local _intake folder before processing."
Write-Host ""
Write-Host "  Example: G:\My Drive\_intake"
Write-Host ""
Write-Host "Leave blank to skip — intake will only process files dropped directly into:"
Write-Host "  $appDir\data\_intake"
Write-Host ""

$sourcePath = Read-Host "Source folder (or press Enter to skip)"
$sourcePath = $sourcePath.Trim('"').Trim("'").Trim()

# If a source was provided, verify or create it
if ($sourcePath) {
    if (-not (Test-Path $sourcePath)) {
        $create = Read-Host "Folder '$sourcePath' doesn't exist. Create it? (y/n)"
        if ($create -eq 'y') {
            New-Item -ItemType Directory -Force -Path $sourcePath | Out-Null
            Write-Host "Created: $sourcePath"
        } else {
            Write-Host "Aborting — create the folder first, then re-run this script." -ForegroundColor Yellow
            exit 1
        }
    }
    $argString = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$runnerScript`" -SourcePath `"$sourcePath`""
    $sourceDisplay = $sourcePath
} else {
    $argString = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$runnerScript`""
    $sourceDisplay = "$appDir\data\_intake (local only)"
}

# Build the scheduled task action
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument $argString

# Trigger: every 5 minutes, repeat for 25 years (effectively forever)
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) `
    -RepetitionDuration (New-TimeSpan -Days 9000)

# Settings: don't start a new instance if already running, stop after 2 min
$settings = New-ScheduledTaskSettingsSet `
    -DontStopOnIdleEnd `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 2) `
    -MultipleInstances IgnoreNew `
    -StartWhenAvailable

# Register the task (runs as current user)
Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Extracts ideas from brainstorm files via AI and posts to GitLab Kanban board." `
    -Force

# Suppress the window popup: set "Run whether user is logged on or not"
$task = Get-ScheduledTask -TaskName $taskName
$task.Principal.LogonType = "S4U"
Set-ScheduledTask -InputObject $task | Out-Null

Write-Host ""
Write-Host "Scheduled task '$taskName' created." -ForegroundColor Green
Write-Host "  Source:  $sourceDisplay"
Write-Host "  Runner:  $runnerScript"
Write-Host "  Logs:    $appDir\data\_logs\scheduled-run.log"
Write-Host "  Runs every 5 minutes"
Write-Host ""
Write-Host "To check status:  Get-ScheduledTask -TaskName '$taskName'"
Write-Host "To run now:       Start-ScheduledTask -TaskName '$taskName'"
Write-Host "To disable:       Disable-ScheduledTask -TaskName '$taskName'"
Write-Host "To remove:        Unregister-ScheduledTask -TaskName '$taskName'"
