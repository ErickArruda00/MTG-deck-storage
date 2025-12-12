$ErrorActionPreference = "Stop"

Write-Host "Reconstruindo e reiniciando API..."

$backendPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendPath

docker-compose up -d --build api

Write-Host "API updated and running"

