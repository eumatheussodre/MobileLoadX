#!/usr/bin/env powershell
# Script alternativo para instalar JDK via ZIP (sem MSI)
# Execute como Administrador

$ErrorActionPreference = "Stop"

function Write-Success {
    param([string]$Message)
    Write-Host "OK: $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "INFO: $Message" -ForegroundColor Blue
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "ERRO: $Message" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  INSTALANDO JAVA (OpenJDK via ZIP)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Criar diretorio Java
$javaDir = "C:\Java"
$javaHome = "$javaDir\jdk-17"

Write-Host "`n1. Preparando diretorio Java..." -ForegroundColor Magenta

if (-not (Test-Path $javaDir)) {
    New-Item -ItemType Directory -Path $javaDir -Force | Out-Null
    Write-Success "Diretorio criado: $javaDir"
}

# URL para download do OpenJDK 17 (Microsoft)
$downloadUrl = "https://aka.ms/download-jdk/microsoft-jdk-17.0.7-windows-x64.zip"
$zipPath = "$env:TEMP\jdk.zip"
$tempExtract = "$env:TEMP\jdk-extract"

Write-Host "`n2. Baixando OpenJDK 17..." -ForegroundColor Magenta
Write-Info "Tamanho: ~180MB, pode levar alguns minutos..."

try {
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($downloadUrl, $zipPath)
    Write-Success "Download completo"
}
catch {
    Write-Error-Custom "Erro ao baixar: $_"
    Write-Info "Tentando URL alternativa (Azul Zulu OpenJDK)..."
    
    $downloadUrl = "https://cdn.azul.com/zulu/bin/zulu17.42.19-ca-jdk17.0.6-win_x64.zip"
    
    try {
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($downloadUrl, $zipPath)
        Write-Success "Download completo (Azul Zulu)"
    }
    catch {
        Write-Error-Custom "Falha ao baixar JDK: $_"
        Write-Info "Por favor, instale manualmente Java de:"
        Write-Host "  - https://adoptium.net/" -ForegroundColor Yellow
        Write-Host "  - https://www.azul.com/downloads/" -ForegroundColor Yellow
        exit 1
    }
}

# Extrair
Write-Host "`n3. Extraindo OpenJDK..." -ForegroundColor Magenta
Write-Info "Isso pode levar alguns minutos..."

try {
    if (Test-Path $tempExtract) {
        Remove-Item $tempExtract -Recurse -Force
    }
    
    Expand-Archive -Path $zipPath -DestinationPath $tempExtract -Force
    Write-Success "Extracao completa"
    
    # Mover para destino final (pode estar em subpasta)
    $extractedJdk = Get-ChildItem $tempExtract -Filter "microsoft-jdk-*" -Directory | Select-Object -First 1
    
    if ($extractedJdk) {
        if (Test-Path $javaHome) {
            Remove-Item $javaHome -Recurse -Force
        }
        Move-Item -Path $extractedJdk.FullName -Destination $javaHome -Force
        Write-Success "OpenJDK movido para: $javaHome"
    } else {
        # Talvez esteja em uma estrutura diferente
        $allDirs = Get-ChildItem $tempExtract -Directory
        if ($allDirs.Count -eq 1) {
            if (Test-Path $javaHome) {
                Remove-Item $javaHome -Recurse -Force
            }
            Move-Item -Path $allDirs[0].FullName -Destination $javaHome -Force
            Write-Success "OpenJDK movido para: $javaHome"
        }
    }
}
catch {
    Write-Error-Custom "Erro ao extrair: $_"
    exit 1
}

# Limpar temp
Write-Host "`n4. Limpando arquivos temporarios..." -ForegroundColor Magenta

try {
    Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
    Remove-Item $tempExtract -Recurse -Force -ErrorAction SilentlyContinue
    Write-Success "Limpeza completa"
}
catch {
    Write-Warning "Nao foi possivel limpar alguns arquivos temporarios"
}

# Configurar JAVA_HOME
Write-Host "`n5. Configurando JAVA_HOME..." -ForegroundColor Magenta

try {
    [Environment]::SetEnvironmentVariable("JAVA_HOME", $javaHome, "User")
    $env:JAVA_HOME = $javaHome
    
    # Adicionar ao PATH tambem
    $binPath = "$javaHome\bin"
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    
    if ($currentPath -notlike "*$binPath*") {
        [Environment]::SetEnvironmentVariable(
            "Path",
            "$currentPath;$binPath",
            "User"
        )
        $env:Path = "$env:Path;$binPath"
    }
    
    Write-Success "JAVA_HOME: $javaHome"
    Write-Success "PATH atualizado com bin/java"
}
catch {
    Write-Error-Custom "Erro ao configurar: $_"
}

# Testar
Write-Host "`n6. Testando Java..." -ForegroundColor Magenta

try {
    $javaExe = "$javaHome\bin\java.exe"
    
    if (Test-Path $javaExe) {
        $version = & $javaExe -version 2>&1
        Write-Success "Java funcionando!"
        Write-Host "   $($version[0])"
    } else {
        Write-Error-Custom "java.exe nao encontrado em: $javaExe"
    }
}
catch {
    Write-Error-Custom "Erro ao testar Java: $_"
}

# Resumo
Write-Host "`n" + "="*50
Write-Host "OK: JAVA INSTALADO COM SUCESSO!" -ForegroundColor Green
Write-Host "="*50

Write-Host "`nINFORMAÇOES:" -ForegroundColor Cyan
Write-Host "  JAVA_HOME: $javaHome"
Write-Host "  Java Bin: $javaHome\bin"

Write-Host "`nPROXIMO PASSO:" -ForegroundColor Magenta
Write-Host "Feche e reabra o PowerShell, depois execute:" -ForegroundColor Yellow
Write-Host "  powershell -ExecutionPolicy Bypass -File complete_sdk_setup.ps1" -ForegroundColor Yellow

exit 0
