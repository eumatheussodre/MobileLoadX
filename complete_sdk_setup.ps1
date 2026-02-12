#!/usr/bin/env powershell
# Script para completar o setup do Android SDK apos download
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

$SdkPath = "C:\Android\Sdk"
$SdkManagerPath = "$SdkPath\cmdline-tools\latest\bin\sdkmanager.bat"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  COMPLETANDO SETUP DO ANDROID SDK" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Verificar se sdkmanager existe
Write-Host "`n1. Verificando sdkmanager..." -ForegroundColor Magenta
if (Test-Path $SdkManagerPath) {
    Write-Success "sdkmanager encontrado em: $SdkManagerPath"
} else {
    Write-Error-Custom "sdkmanager nao encontrado em: $SdkManagerPath"
    Write-Info "Certifique-se de que o download completou com sucesso"
    exit 1
}

# 2. Aceitar licencas
Write-Host "`n2. Aceitando licencas do Android..." -ForegroundColor Magenta
Write-Info "Isso pode levar alguns minutos..."

try {
    # Usar yes para aceitar todas as licencas
    $licensesFile = "$env:TEMP\accept_licenses.txt"
    @"
y
y
y
y
y
y
y
y
"@ | Out-File -FilePath $licensesFile -Encoding ASCII -Force
    
    # Executar sdkmanager com as respostas
    Get-Content $licensesFile | & $SdkManagerPath --licenses 2>&1 | Out-Null
    
    Remove-Item $licensesFile -Force -ErrorAction SilentlyContinue
    Write-Success "Licencas aceitas"
}
catch {
    Write-Error-Custom "Erro ao aceitar licencas: $_"
    exit 1
}

# 3. Instalar platform-tools
Write-Host "`n3. Instalando platform-tools..." -ForegroundColor Magenta
Write-Info "Tamanho: ~80MB, por favor aguarde..."

try {
    & $SdkManagerPath "platform-tools" 2>&1 | Select-String -Pattern "Installed|installed|Preparing|Done" | Out-Null
    Write-Success "platform-tools instalado"
}
catch {
    Write-Error-Custom "Erro ao instalar platform-tools: $_"
}

# 4. Instalar build-tools
Write-Host "`n4. Instalando build-tools..." -ForegroundColor Magenta
Write-Info "Versao: 34.0.0, tamanho: ~200MB..."

try {
    & $SdkManagerPath "build-tools;34.0.0" 2>&1 | Select-String -Pattern "Installed|installed|Preparing|Done" | Out-Null
    Write-Success "build-tools instalado"
}
catch {
    Write-Error-Custom "Erro ao instalar build-tools: $_"
}

# 5. Instalar Android API Platform
Write-Host "`n5. Instalando Android SDK Platform..." -ForegroundColor Magenta
Write-Info "API Level 34, tamanho: ~100MB..."

try {
    & $SdkManagerPath "platforms;android-34" 2>&1 | Select-String -Pattern "Installed|installed|Preparing|Done" | Out-Null
    Write-Success "android-34 SDK platform instalado"
}
catch {
    Write-Error-Custom "Erro ao instalar android-34: $_"
}

# 6. Instalar emulator (opcional)
Write-Host "`n6. Instalando emulator..." -ForegroundColor Magenta
Write-Info "Tamanho: ~200MB..."

try {
    & $SdkManagerPath "emulator" 2>&1 | Select-String -Pattern "Installed|installed|Preparing|Done" | Out-Null
    Write-Success "emulator instalado"
}
catch {
    Write-Error-Custom "Erro ao instalar emulator: $_"
}

# 7. Configurar PATH
Write-Host "`n7. Configurando PATH..." -ForegroundColor Magenta

$platformToolsPath = "$SdkPath\platform-tools"
$currentUserPath = [Environment]::GetEnvironmentVariable("Path", "User")

if ($currentUserPath -notlike "*$platformToolsPath*") {
    Write-Info "Adicionando $platformToolsPath ao PATH..."
    
    try {
        [Environment]::SetEnvironmentVariable(
            "Path",
            "$currentUserPath;$platformToolsPath",
            "User"
        )
        $env:Path = "$env:Path;$platformToolsPath"
        Write-Success "PATH configurado permanentemente"
    }
    catch {
        Write-Error-Custom "Erro ao configurar PATH: $_"
    }
} else {
    Write-Success "platform-tools ja esta no PATH"
}

# 8. Verificar instalacao
Write-Host "`n8. Verificando instalacao..." -ForegroundColor Magenta

try {
    $adbPath = "$platformToolsPath\adb.exe"
    
    if (Test-Path $adbPath) {
        $version = & $adbPath version
        Write-Success "ADB funcionando!"
        Write-Host "   $($version[0])"
        
        # Verificar devices
        Write-Host "`n9. Listando devices conectados..." -ForegroundColor Magenta
        $devices = & $adbPath devices
        Write-Host ($devices -join "`n")
    } else {
        Write-Error-Custom "adb.exe nao encontrado"
    }
}
catch {
    Write-Error-Custom "Erro ao verificar: $_"
}

# Resumo Final
Write-Host "`n" + "="*50 -ForegroundColor Green
Write-Host "OK: SETUP COMPLETO!" -ForegroundColor Green
Write-Host "="*50 -ForegroundColor Green

Write-Host "`nINFORMAÇOES:" -ForegroundColor Cyan
Write-Host "  SDK Path: $SdkPath"
Write-Host "  Platform Tools: $platformToolsPath"
Write-Host "  ADB Path: $adbPath"

Write-Host "`nPROXIMOS PASSOS:" -ForegroundColor Magenta
Write-Host "1. Feche e reabra o PowerShell para carregar o novo PATH"
Write-Host "2. Conecte um device Android via USB"
Write-Host "3. Execute: adb devices (deve listar seu device)"
Write-Host "4. Comece a testar APKs!"

Write-Host "`nCOMANDOS UTEIS:" -ForegroundColor Magenta
Write-Host "  adb devices              # Listar devices"
Write-Host "  adb install app.apk     # Instalar APK"
Write-Host "  adb shell                # Acessar shell do device"
Write-Host "  emulator -list-avds     # Listar emuladores"

exit 0
