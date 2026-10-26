$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$runtime = Join-Path $projectRoot '.runtime'
$base = Join-Path $runtime 'mysql-8.4.11-winx64'
$binary = Join-Path $base 'bin/mysqld.exe'
$data = Join-Path $runtime 'mysql-data'
$config = Join-Path $runtime 'mysql.ini'
if (-not (Test-Path -LiteralPath $binary)) { throw 'Run scripts/download-db.ps1 first.' }
if (Test-Path -LiteralPath $data) {
    throw 'The data directory already exists and will not be overwritten. Use start-db.ps1 if it is initialized.'
}
& $binary '--no-defaults' '--initialize-insecure' "--basedir=$base" "--datadir=$data" '--console'
if ($LASTEXITCODE -ne 0) { throw 'MySQL initialization failed. The directory was preserved for inspection.' }
$baseForward = $base.Replace('\', '/')
$dataForward = $data.Replace('\', '/')
@"
[mysqld]
basedir=$baseForward
datadir=$dataForward
bind-address=127.0.0.1
port=3308
mysqlx=0
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci
innodb-buffer-pool-size=64M
log-error=copet.err
pid-file=copet.pid

[client]
host=127.0.0.1
port=3308
"@ | Set-Content -LiteralPath $config -Encoding ASCII
Write-Output 'MySQL initialized. Start it, then run scripts/provision-db.py immediately to secure local accounts.'
