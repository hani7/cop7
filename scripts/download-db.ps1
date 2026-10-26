$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$projectRoot = Split-Path -Parent $PSScriptRoot
$runtime = Join-Path $projectRoot '.runtime'
New-Item -ItemType Directory -Force -Path $runtime | Out-Null
$archive = Join-Path $runtime 'mysql-8.4.11-winx64.zip'
if (-not (Test-Path -LiteralPath $archive)) {
    Invoke-WebRequest -UseBasicParsing -Uri 'https://cdn.mysql.com/Downloads/MySQL-8.4/mysql-8.4.11-winx64.zip' -OutFile $archive
}
# Published on https://dev.mysql.com/downloads/mysql/8.4.html for this ZIP.
$expected = '2e833921898a9a030ea6bfe81bd811bc'
$actual = (Get-FileHash -LiteralPath $archive -Algorithm MD5).Hash
if ($expected -ne $actual) { throw 'Archive checksum mismatch. No binary was executed.' }
Write-Output "Official MySQL archive integrity verified: $actual"
$binary = Join-Path $runtime 'mysql-8.4.11-winx64/bin/mysqld.exe'
if (-not (Test-Path -LiteralPath $binary)) {
    Expand-Archive -LiteralPath $archive -DestinationPath $runtime
}
Write-Output 'MySQL binaries are ready in .runtime.'
