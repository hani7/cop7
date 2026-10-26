$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$admin = Join-Path $projectRoot '.runtime/mysql-8.4.11-winx64/bin/mysqladmin.exe'
$config = Join-Path $projectRoot '.runtime/mysql-admin.cnf'
if (-not (Test-Path -LiteralPath $config)) { throw 'Local administrator configuration is missing.' }
& $admin "--defaults-file=$config" shutdown
if ($LASTEXITCODE -ne 0) { throw 'MySQL shutdown failed. No other process was stopped.' }
Write-Output 'Copet MySQL stopped safely. XAMPP was not changed.'
