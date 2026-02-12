#!/usr/bin/env powershell
# Script de instalacao automatica do Android SDK no Windows
# Execute como Administrador

param(
    [string]$SdkPath = "$env:USERPROFILE\AppData\Local\Android\Sdk",
    [switch]$Force = $false
)

$ErrorActionPreference = "Stop"

function Write-Header {
    param([string]$Message)
    Write-Host "`n" + "="*60 -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "="*60 -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "OK: $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "ERRO: $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "AVISO: $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "INFO: $Message" -ForegroundColor Blue
}

# Verificar se e Admin
$isAdmin = [bool]([Security.Principal.WindowsIdentity]::GetCurrent().Groups -match "S-1-5-32-544")
if (-not $isAdmin) {
    Write-Error-Custom "Este script deve ser executado como Administrador"
    Write-Info "Abra PowerShell como Admin e tente novamente"
    exit 1
}

Write-Header "INSTALADOR DO ANDROID SDK PARA MOBILELOADX"

# 1. Verificar se ADB ja esta instalado
Write-Host "`n1. Verificando ADB..." -ForegroundColor Magenta

try {
    $adbVersion = & adb version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "ADB ja esta instalado!"
        Write-Host "   Versao: $($adbVersion[0])"
        
        if (-not $Force) {
            Write-Success "Instalacao nao necessaria. Saindo..."
            & adb version
            exit 0
        } else {
            Write-Warning-Custom "Force flag ativada, continuando..."
        }
    }
}
catch {
    Write-Info "ADB nao encontrado (normal na primeira vez)"
}

# 2. Verificar se Android SDK existe
Write-Host "`n2. Procurando Android SDK..." -ForegroundColor Magenta

# Tentar multiplos caminhos
$possiblePaths = @(
    $SdkPath,
    "C:\Android\Sdk",
    "$env:USERPROFILE\AppData\Local\Android\Sdk"
)

$SdkFound = $null
foreach ($path in $possiblePaths) {
    if (Test-Path "$path\platform-tools\adb.exe") {
        $SdkFound = $path
        Write-Success "Android SDK encontrado em: $path"
        break
    }
}

if ($SdkFound) {
    $SdkPath = $SdkFound
    
    # 3. Adicionar ao PATH
    
    $platformToolsPath = "$SdkPath\platform-tools"
    $toolsPath = "$SdkPath\tools"
    $pathsToAdd = @($platformToolsPath, $toolsPath)
    
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $pathsAdded = @()
    
    foreach ($path in $pathsToAdd) {
        if ($env:Path -notlike "*$path*") {
            $env:Path = "$env:Path;$path"
            $pathsAdded += $path
            Write-Success "Adicionado ao PATH temporariamente: $path"
        } else {
            Write-Success "Ja esta no PATH: $path"
        }
    }
    
    if ($pathsAdded.Count -gt 0) {
        # Tentar adicionar permanentemente
        Write-Info "Configurando PATH permanentemente..."
        
        try {
            $newUserPath = $currentPath
            foreach ($path in $pathsAdded) {
                if ($newUserPath -notlike "*$path*") {
                    $newUserPath = "$newUserPath;$path"
                }
            }
            
            [Environment]::SetEnvironmentVariable(
                "Path",
                $newUserPath,
                "User"
            )
            Write-Success "PATH configurado permanentemente!"
            Write-Host "   - $platformToolsPath" -ForegroundColor Green
            Write-Host "   - $toolsPath" -ForegroundColor Green
        }
        catch {
            Write-Warning-Custom "Nao foi possivel configurar PATH permanentemente"
            Write-Info "Execute estas linhas manualmente no PowerShell como Admin:"
            Write-Host "   `[Environment]`::SetEnvironmentVariable(`"Path`", `$env:Path, `"User`")" -ForegroundColor Yellow
        }
    } else {
        Write-Success "Todos os caminhos ja estao configurados no PATH"
    }
    
    # 4. Verificar instalacao
    Write-Host "`n4. Verificando instalacao..." -ForegroundColor Magenta
    
    try {
        & adb version
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "ADB funcionando corretamente!"
            Write-Host "`n" + "="*60
            Write-Host "OK: INSTALACAO COMPLETA!" -ForegroundColor Green
            Write-Host "="*60
            
            # Proximos passos
            Write-Host "`n PROXIMOS PASSOS:" -ForegroundColor Magenta
            Write-Host "1. Conecte um device via USB ou inicie um emulador"
            Write-Host "2. Execute: adb devices"
            Write-Host "3. Voce esta pronto para testar com MobileLoadX!"
            
            Write-Host "`n COMANDOS UTEIS:" -ForegroundColor Magenta
            Write-Host "   adb devices              # Listar devices"
            Write-Host "   adb install app.apk     # Instalar APK"
            Write-Host "   adb push local remote    # Enviar arquivo"
            Write-Host "   adb shell                # Acessar terminal do device"
            
            exit 0
        }
    }
    catch {
        Write-Error-Custom "Erro ao verificar ADB: $_"
        exit 1
    }
} else {
    Write-Error-Custom "Android SDK nao encontrado nos caminhos esperados"
    Write-Host "`n CAMINHOS PROCURADOS:" -ForegroundColor Yellow
    foreach ($path in $possiblePaths) {
        Write-Host "   - $path"
    }
    Write-Host "`n OPCOES DE INSTALACAO:" -ForegroundColor Yellow
    Write-Host "1. Opcao A: Instalar Android Studio (RECOMENDADO)"
    Write-Host "   - Acesse: https://developer.android.com/studio"
    Write-Host "   - Download e instale"
    Write-Host "   - Deixe completar o setup automatico"
    Write-Host "   - Execute este script novamente"
    
    Write-Host "`n2. Opcao B: Instalar apenas Command Line Tools"
    Write-Host "   - Acesse: https://developer.android.com/studio/releases/sdk-tools"
    Write-Host "   - Download Command Line Tools"
    Write-Host "   - Extraia em: C:\Android\Sdk (recomendado) ou outro local"
    Write-Host "   - Execute este script novamente"
    
    Write-Host "`n3. Opcao C: Instalar via Chocolatey (Windows)"
    Write-Host "   - Execute como Admin:"
    Write-Host "   - choco install android-sdk"
    Write-Host "   - Execute este script novamente"
    
    exit 1
}
