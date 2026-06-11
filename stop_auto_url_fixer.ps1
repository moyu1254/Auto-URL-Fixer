param()

$runtimeDir = Join-Path $env:LOCALAPPDATA "AutoURLFixer"
$pidFile = Join-Path $runtimeDir "auto_url_fixer.pid"
$stopFile = Join-Path $runtimeDir "stop.flag"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$expectedExePath = Join-Path $scriptDir "Auto URL Fixer.exe"

New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null
New-Item -ItemType File -Force -Path $stopFile | Out-Null

$targetPids = [System.Collections.Generic.HashSet[int]]::new()

if (Test-Path $pidFile) {
    $pidText = (Get-Content $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
    $pidValue = 0
    if ([int]::TryParse($pidText, [ref]$pidValue)) {
        $null = $targetPids.Add($pidValue)
    }
}

$processes = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
    ($_.CommandLine -and $_.CommandLine -match '(?i)(^| )(-m +auto_url_fixer|auto_url_fixer[/\\]__main__\.py)') -or
    ($_.ExecutablePath -and [System.StringComparer]::OrdinalIgnoreCase.Equals($_.ExecutablePath, $expectedExePath)) -or
    $_.Name -match '^(?i:auto url fixer|auto-url-fixer|auto_url_fixer)\.exe$'
}

foreach ($process in $processes) {
    $null = $targetPids.Add([int]$process.ProcessId)
}

if ($targetPids.Count -eq 0) {
    Write-Output "Stop request sent, but no Auto URL Fixer process was found."
    exit 0
}

Start-Sleep -Seconds 2

$stillRunning = @()
foreach ($targetPid in $targetPids) {
    $process = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
    if ($process) {
        $stillRunning += $process
    }
}

if ($stillRunning.Count -eq 0) {
    Remove-Item $pidFile, $stopFile -Force -ErrorAction SilentlyContinue
    Write-Output "Auto URL Fixer has stopped."
    exit 0
}

foreach ($process in $stillRunning) {
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Milliseconds 500

$remaining = @()
foreach ($targetPid in $targetPids) {
    $process = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
    if ($process) {
        $remaining += $process.Id
    }
}

if ($remaining.Count -gt 0) {
    Write-Output ("Failed to stop PID(s): " + ($remaining -join ", "))
    exit 1
}

Remove-Item $pidFile, $stopFile -Force -ErrorAction SilentlyContinue
Write-Output ("Auto URL Fixer was stopped. PID(s): " + (($targetPids | Sort-Object) -join ", "))
