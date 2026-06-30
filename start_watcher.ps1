# start_watcher.ps1 - Launch watcher.py with API key from .env
# Designed to run from Task Scheduler (no user profile loaded)

$KBRoot  = 'C:\Users\villa\OneDrive\KnowledgeBase'
$EnvFile = Join-Path $KBRoot '.env'
$LogFile = Join-Path $KBRoot 'watcher.log'

Set-Location $KBRoot

# Redirect stdout+stderr to log file with timestamp header
$ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
Add-Content $LogFile "`n[$ts] start_watcher.ps1 launched"

# Load .env into process environment
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith('#')) {
            $parts = $line -split '=', 2
            if ($parts.Length -eq 2) {
                [System.Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), 'Process')
            }
        }
    }
    Add-Content $LogFile "[$ts] .env loaded"
} else {
    Add-Content $LogFile "[$ts] WARNING: .env not found at $EnvFile"
}

# Force UTF-8 output so watcher/agent logs handle Unicode correctly
$env:PYTHONUTF8 = '1'

# Resolve python - try common locations so Task Scheduler finds it
$PythonCandidates = @(
    (Get-Command python -ErrorAction SilentlyContinue).Source,
    "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:APPDATA\Local\Programs\Python\Python313\python.exe",
    'C:\Python313\python.exe',
    'C:\Python312\python.exe'
)
$PythonExe = $PythonCandidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1

if (-not $PythonExe) {
    Add-Content $LogFile "[$ts] ERROR: python executable not found. Candidates tried: $($PythonCandidates -join ', ')"
    exit 1
}

Add-Content $LogFile "[$ts] Using python: $PythonExe"
Add-Content $LogFile "[$ts] Starting watcher.py ..."

# Run watcher, append all output to log
& $PythonExe "$KBRoot\watcher.py" >> $LogFile 2>&1
