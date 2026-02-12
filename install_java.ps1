#!/usr/bin/env powershell
# Script para instalar JDK necessario para o Android SDK
# Execute como Administrador

param(
    [switch]$UseChocolatey = $false
)

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

function Write-Header {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

Write-Header "VERIFICANDO/INSTALANDO JAVA PARA ANDROID SDK"

# 1. Procurar Java existente
Write-Host "`n1. Procurando Java instalado..." -ForegroundColor Magenta

$javaFound = $null

# Procurar em locais comuns
$commonJavaPaths = @(
    "C:\Program Files\Java\jdk-*\bin\java.exe",
    "C:\Program Files (x86)\Java\jdk-*\bin\java.exe",
    "$env:JAVA_HOME\bin\java.exe"
)

foreach ($pattern in $commonJavaPaths) {
    $matches = Get-Item $pattern -ErrorAction SilentlyContinue
    if ($matches) {
        $javaFound = $matches[0].FullName
        break
    }
}

# Tentar encontrar via where
if (-not $javaFound) {
    try {
        $javaFound = & where java 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Java encontrado: $javaFound"
        }
    }
    catch {
        # Java nao encontrado
    }
}

if ($javaFound) {
    Write-Success "Java ja esta instalado!"
    Write-Host "   Caminho: $javaFound"
    
    # Testar versao
    try {
        $version = & $javaFound -version 2>&1 | Select-Object -First 1
        Write-Host "   Versao: $version"
        
        # Configurar JAVA_HOME
        $javaHome = Split-Path (Split-Path $javaFound)
        [Environment]::SetEnvironmentVariable("JAVA_HOME", $javaHome, "User")
        $env:JAVA_HOME = $javaHome
        
        Write-Success "JAVA_HOME configurado: $javaHome"
    }
    catch {
        Write-Error-Custom "Erro ao obter versao do Java"
    }
} else {
    Write-Host "`n2. Java nao encontrado. Instalando..." -ForegroundColor Magenta
    
    # Opcoes de instalacao
    if ($UseChocolatey) {
        Write-Info "Tentando instalar via Chocolatey..."
        Write-Info "Executando: choco install openjdk -y"
        
        try {
            & choco install openjdk -y
            Write-Success "OpenJDK instalado via Chocolatey"
        }
        catch {
            Write-Error-Custom "Falha ao instalar via Chocolatey: $_"
            Write-Info "Instalando manualmente via download..."
        }
    }
    
    # Download manual (Microsoft OpenJDK)
    if (-not (Test-Path "C:\Program Files\Java\jdk-*\bin\java.exe")) {
        Write-Host "`nInstalando Microsoft OpenJDK 17..." -ForegroundColor Cyan
        
        $downloadUrl = "https://aka.ms/download-jdk/microsoft-jdk-17.0.7-windows-x64.msi"
        $installerPath = "$env:TEMP\jdk-installer.msi"
        
        Write-Info "Baixando OpenJDK..."
        try {
            $webClient = New-Object System.Net.WebClient
            $webClient.DownloadFile($downloadUrl, $installerPath)
            Write-Success "Download completo"
            
            Write-Info "Executando instalador..."
            Start-Process -FilePath "msiexec.exe" -ArgumentList "/i", $installerPath, "/qn" -Wait
            
            Write-Success "OpenJDK instalado"
            
            # Limpar
            Remove-Item $installerPath -Force
            
            # Configurar JAVA_HOME
            $jdkPath = Get-Item "C:\Program Files\Java\jdk-*" | Select-Object -Last 1
            if ($jdkPath) {
                [Environment]::SetEnvironmentVariable("JAVA_HOME", $jdkPath.FullName, "User")
                $env:JAVA_HOME = $jdkPath.FullName
                Write-Success "JAVA_HOME configurado: $($jdkPath.FullName)"
            }
        }
        catch {
            Write-Error-Custom "Erro ao instalar OpenJDK: $_"
            Write-Info "Por favor, instale manualmente:"
            Write-Host "  https://www.microsoft.com/openjdk" -ForegroundColor Yellow
            exit 1
        }
    }
}

# 3. Testar Java
Write-Host "`n3. Testando Java..." -ForegroundColor Magenta

try {
    $javaVersion = java -version 2>&1
    Write-Success "Java funcionando corretamente"
    Write-Host $javaVersion[0]
}
catch {
    Write-Error-Custom "Erro ao executar Java"
    exit 1
}

Write-Host "`n" + "="*50
Write-Host "OK: JAVA CONFIGURADO COM SUCESSO!" -ForegroundColor Green
Write-Host "="*50

Write-Host "`nProximo passo:" -ForegroundColor Magenta
Write-Host "Execute: powershell -ExecutionPolicy Bypass -File complete_sdk_setup.ps1" -ForegroundColor Yellow

exit 0
