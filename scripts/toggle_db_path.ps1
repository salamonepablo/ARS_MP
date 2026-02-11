# toggle_db_path.ps1
# Quick PowerShell script to toggle between local and remote database paths
# Usage:
#   .\toggle_db_path.ps1 show      # Show current path
#   .\toggle_db_path.ps1 local     # Switch to local path
#   .\toggle_db_path.ps1 remote    # Switch to remote path (G: drive)

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("show", "local", "remote")]
    [string]$Action = "show"
)

$ENV_FILE = ".env"
$LOCAL_DB = "docs/legacy_bd/Accdb/DB_CCEE_Programación 1.1.accdb"
$REMOTE_DB = "g:\Material Rodante\1-Servicio Eléctrico\DB\Base de Dato Prog\DB_CCEE_Programación 1.1.accdb"

if (-not (Test-Path $ENV_FILE)) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    exit 1
}

$content = Get-Content $ENV_FILE -Raw

function Show-Current {
    $lines = $content -split "`n"
    foreach ($line in $lines) {
        if ($line -like "LEGACY_ACCESS_DB_PATH=*") {
            Write-Host "📌 Current DB path:" -ForegroundColor Cyan
            Write-Host "   $line" -ForegroundColor Yellow
            break
        }
    }
}

function Switch-ToLocal {
    $content = Get-Content $ENV_FILE -Raw
    $updated = $content -replace 'LEGACY_ACCESS_DB_PATH=.*', "LEGACY_ACCESS_DB_PATH=$LOCAL_DB"
    
    if ($updated -ne $content) {
        Set-Content $ENV_FILE -Value $updated
        Write-Host "✅ Switched to LOCAL database" -ForegroundColor Green
        Write-Host "   Path: $LOCAL_DB" -ForegroundColor Yellow
        return $true
    } else {
        Write-Host "⚠️  LEGACY_ACCESS_DB_PATH not found in .env" -ForegroundColor Yellow
        return $false
    }
}

function Switch-ToRemote {
    $content = Get-Content $ENV_FILE -Raw
    $updated = $content -replace 'LEGACY_ACCESS_DB_PATH=.*', "LEGACY_ACCESS_DB_PATH=`"$REMOTE_DB`""
    
    if ($updated -ne $content) {
        Set-Content $ENV_FILE -Value $updated
        Write-Host "✅ Switched to REMOTE database (G:)" -ForegroundColor Green
        Write-Host "   Path: $REMOTE_DB" -ForegroundColor Yellow
        return $true
    } else {
        Write-Host "⚠️  LEGACY_ACCESS_DB_PATH not found in .env" -ForegroundColor Yellow
        return $false
    }
}

switch ($Action) {
    "show" { Show-Current }
    "local" { Switch-ToLocal }
    "remote" { Switch-ToRemote }
}
