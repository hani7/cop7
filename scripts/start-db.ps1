$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$runtime = Join-Path $projectRoot '.runtime'
$binary = Join-Path $runtime 'mysql-8.4.11-winx64/bin/mysqld.exe'
$config = Join-Path $runtime 'mysql.ini'
$pidFile = Join-Path $runtime 'mysql-data/copet.pid'
if (-not (Test-Path -LiteralPath $binary) -or -not (Test-Path -LiteralPath $config)) {
    throw 'Local MySQL is not initialized. Follow README.md.'
}
if (Test-Path -LiteralPath $pidFile) {
    $databasePid = [int](Get-Content -LiteralPath $pidFile -Raw).Trim()
    $existing = Get-Process -Id $databasePid -ErrorAction SilentlyContinue
    if ($existing -and $existing.Path -eq $binary) {
        Write-Output "Copet MySQL is already running (PID $databasePid, port 3308)."
        exit 0
    }
}
$listener = [System.Net.Sockets.TcpClient]::new()
try {
    $listener.Connect('127.0.0.1', 3308)
    throw 'Port 3308 is occupied by another process. It was not stopped or changed.'
} catch [System.Net.Sockets.SocketException] {
    # The port is free.
} finally {
    $listener.Dispose()
}
$process = Start-Process -FilePath $binary -ArgumentList "--defaults-file=`"$config`"" -WorkingDirectory $runtime -WindowStyle Hidden -PassThru
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    Start-Sleep -Milliseconds 500
    $process.Refresh()
    if ($process.HasExited) { throw 'MySQL stopped. Check .runtime/mysql-data/copet.err.' }
    if (Test-Path -LiteralPath $pidFile) {
        Write-Output "Copet MySQL started on 127.0.0.1:3308 (PID $($process.Id))."
        exit 0
    }
}
throw 'Startup timed out. Check .runtime/mysql-data/copet.err.'
