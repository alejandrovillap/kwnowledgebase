# start_watcher.ps1 — Launch watcher.py with the API key loaded from .env

$ErrorActionPreference = "Stop"

$KBRoot = "C:\Users\villa\OneDrive\KnowledgeBase"
$EnvFile = Join-Path $KBRoot ".env"

Set-Location $KBRoot

# Load .env and export each key=value as an environment variable
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#")) {
            $parts = $line -split "=", 2
            if ($parts.Length -eq 2) {
                $name  = $parts[0].Trim()
                $value = $parts[1].Trim()
                [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
            }
        }
    }
    Write-Host "[watcher] .env loaded from $EnvFile"
} else {
    Write-Warning ".env not found at $EnvFile — ANTHROPIC_API_KEY may be unset."
}

Write-Host "[watcher] Starting watcher.py …"
python "$KBRoot\watcher.py"
