# register_task.ps1 - Register KnowledgeBase-Watcher as a Task Scheduler job.
# Run once (no elevation required for AtLogon tasks scoped to your own account).
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File "C:\Users\villa\OneDrive\KnowledgeBase\register_task.ps1"

$TaskName   = 'KnowledgeBase-Watcher'
$KBRoot     = 'C:\Users\villa\OneDrive\KnowledgeBase'
$ScriptPath = Join-Path $KBRoot 'start_watcher.ps1'

# Build the -Argument string via concatenation to avoid nested-quote escaping
$TaskArg = '-ExecutionPolicy Bypass -WindowStyle Hidden -File "' + $ScriptPath + '"'

# Resolve the python executable currently on PATH
$PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PythonExe) {
    Write-Error 'python not found in PATH. Activate your virtual environment first.'
    exit 1
}

# Remove existing task with the same name if present
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed existing task: $TaskName"
}

# Action: run PowerShell with start_watcher.ps1
$Action = New-ScheduledTaskAction `
    -Execute 'powershell.exe' `
    -Argument $TaskArg `
    -WorkingDirectory $KBRoot

# Trigger: at user logon (current user only)
$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

# Settings: no time limit, restart on failure, run even if missed
$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable `
    -DontStopIfGoingOnBatteries `
    -RunOnlyIfNetworkAvailable:$false

# Principal: interactive logon, no elevation
$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName    $TaskName `
    -Action      $Action `
    -Trigger     $Trigger `
    -Settings    $Settings `
    -Principal   $Principal `
    -Description 'Auto-starts the KnowledgeBase watcher on user login.' `
    -Force | Out-Null

Write-Host ''
Write-Host "[OK] Task registered: $TaskName"
Write-Host "     Trigger : At logon ($env:USERNAME)"
Write-Host "     Script  : $ScriptPath"
Write-Host "     Python  : $PythonExe"
Write-Host ''
Write-Host 'To start it right now without logging out:'
Write-Host "    Start-ScheduledTask -TaskName '$TaskName'"
Write-Host ''
Write-Host 'To check status:'
Write-Host "    Get-ScheduledTask -TaskName '$TaskName' | Get-ScheduledTaskInfo"
Write-Host ''
Write-Host 'To remove it later:'
Write-Host '    Unregister-ScheduledTask -TaskName KnowledgeBase-Watcher -Confirm:$false'
