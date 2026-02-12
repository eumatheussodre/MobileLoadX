#!/usr/bin/env powershell
# Script para download e setup automatico do Android SDK Command Line Tools
# Execute como Administrador

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

Write-Header "DOWNLOAD E SETUP DO ANDROID SDK COMMAND LINE TOOLS"

# Configuracoes
$SdkPath = "C:\Android\Sdk"
$TempDir = "$env:TEMP\android-sdk-download"
$DownloadUrl = "https://dl.google.com/android/repository/commandlinetools-win-10406996_latest.zip"
$ZipFile = "$TempDir\commandlinetools-win.zip"

Write-Host "`n CONFIGURACOES:" -ForegroundColor Magenta
Write-Host "   Destino: $SdkPath"
Write-Host "   Download: $DownloadUrl"

# 1. Criar diretorio temporario
Write-Host "`n1. Preparando diretorio de download..." -ForegroundColor Magenta

if (Test-Path $TempDir) {
    Remove-Item $TempDir -Recurse -Force | Out-Null
}

New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
Write-Success "Diretorio criado: $TempDir"

# 2. Criar diretorio de destino
Write-Host "`n2. Preparando diretorio de instalacao..." -ForegroundColor Magenta

if (-not (Test-Path $SdkPath)) {
    New-Item -ItemType Directory -Path $SdkPath -Force | Out-Null
    Write-Success "Diretorio criado: $SdkPath"
} else {
    Write-Success "Diretorio ja existe: $SdkPath"
}

# 3. Download
Write-Host "`n3. Baixando Command Line Tools..." -ForegroundColor Magenta
Write-Info "Tamanho estimado: ~1.2GB (pode levar alguns minutos)"
Write-Info "Por favor, aguarde..."

try {
    # Usar ProgressPreference para mostrar progresso
    $ProgressPreference = 'Continue'
    
    # Usar WebClient para ter mais controle
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($DownloadUrl, $ZipFile)
    
    Write-Success "Download concluido!"
    
    $fileSize = (Get-Item $ZipFile).Length / 1GB
    Write-Info "Tamanho do arquivo: $([Math]::Round($fileSize, 2)) GB"
}
catch {
    Write-Error-Custom "Erro ao baixar: $_"
    Write-Info "Tente novamente ou baixe manualmente em:"
    Write-Host "   https://developer.android.com/studio/releases/sdk-tools" -ForegroundColor Yellow
    exit 1
}

# 4. Extrair
Write-Host "`n4. Extraindo Command Line Tools..." -ForegroundColor Magenta
Write-Info "Isso pode levar alguns minutos..."

try {
    # Expandindo arquivo zip
    Expand-Archive -Path $ZipFile -DestinationPath $SdkPath -Force
    Write-Success "Extracao concluida!"
}
catch {
    Write-Error-Custom "Erro ao extrair: $_"
    exit 1
}

# 5. Reorganizar estrutura (se necessario)
Write-Host "`n5. Ajustando estrutura de diretorios..." -ForegroundColor Magenta

$cmdlineToolsPath = "$SdkPath\cmdline-tools"

if (Test-Path "$cmdlineToolsPath\cmdline-tools") {
    # Pode estar em cmdline-tools/cmdline-tools - reorganizar
    $tempPath = "$cmdlineToolsPath\latest"
    if (Test-Path $tempPath) {
        Remove-Item $tempPath -Recurse -Force | Out-Null
    }
    
    Move-Item "$cmdlineToolsPath\cmdline-tools" $tempPath -Force
    Write-Success "Estrutura reorganizada"
} elseif (-not (Test-Path "$cmdlineToolsPath\bin\sdkmanager.bat")) {
    Write-Warning-Custom "Estrutura de diretorios nao esta como esperado"
    Write-Info "Verifique: $cmdlineToolsPath"
}

Write-Success "Command Line Tools extraidos em: $cmdlineToolsPath"

# 6. Aceitar licencas
Write-Host "`n6. Aceitando licencas do Android SDK..." -ForegroundColor Magenta
Write-Info "Isso pode levar alguns minutos na primeira vez..."

try {
    $sdkManagerPath = "$cmdlineToolsPath\latest\bin\sdkmanager.bat"
    
    if (Test-Path $sdkManagerPath) {
        # Criar script para aceitar licencas
        $licenseScript = @"
yes
yes
yes
yes
yes
yes
yes
yes
"@
        
        $licenseScript | & $sdkManagerPath --licenses
        Write-Success "Licencas aceitas"
    } else {
        Write-Warning-Custom "sdkmanager nao encontrado em: $sdkManagerPath"
        Write-Info "O setup pode exigir passos manuais adicionais"
    }
}
catch {
    Write-Warning-Custom "Erro ao aceitar licencas (pode ser necessario manualmente)"
}

# 7. Instalar ferramentas minimas
Write-Host "`n7. Instalando ferramentas essenciais..." -ForegroundColor Magenta
Write-Info "Instalando: SDK Platforms, Build Tools, Emulator..."

try {
    $sdkManagerPath = "$cmdlineToolsPath\latest\bin\sdkmanager.bat"
    
    if (Test-Path $sdkManagerPath) {
        # Instalar ferramentas essenciais
        & $sdkManagerPath "platform-tools"
        & $sdkManagerPath "build-tools;33.0.0"
        & $sdkManagerPath "platforms;android-33"
        
        Write-Success "Ferramentas essenciais instaladas"
    }
}
catch {
    Write-Warning-Custom "Erro ao instalar ferramentas: $_"
}

# 8. Limpar temporary files
Write-Host "`n8. Limpando arquivos temporarios..." -ForegroundColor Magenta

try {
    Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Success "Arquivos temporarios removidos"
}
catch {
    Write-Warning-Custom "Nao foi possivel remover alguns arquivos temporarios"
}

# 9. Executar script de configuracao de PATH
Write-Host "`n9. Configurando PATH..." -ForegroundColor Magenta

$configScript = "$PSScriptRoot\install_android_sdk.ps1"

if (Test-Path $configScript) {
    Write-Info "Executando script de configuracao de PATH..."
    & $configScript
} else {
    Write-Warning-Custom "Script de configuracao nao encontrado: $configScript"
    Write-Info "Adicione manualmente ao PATH:"
    Write-Host "   - $SdkPath\platform-tools" -ForegroundColor Yellow
    Write-Host "   - $SdkPath\tools" -ForegroundColor Yellow
}

# Resultado final
Write-Host "`n" + "="*60
Write-Host "OK: INSTALACAO CONCLUIDA!" -ForegroundColor Green
Write-Host "="*60

Write-Host "`n PROXIMOS PASSOS:" -ForegroundColor Magenta
Write-Host "1. Feche e reabra o PowerShell para carregar o novo PATH"
Write-Host "2. Conecte um device via USB ou inicie um emulador"
Write-Host "3. Execute: adb devices"
Write-Host "4. Voce esta pronto para testar com MobileLoadX!"

Write-Host "`n COMANDOS UTEIS:" -ForegroundColor Magenta
Write-Host "   adb devices              # Listar devices conectados"
Write-Host "   adb install app.apk     # Instalar APK"
Write-Host "   adb push local remote    # Enviar arquivo"
Write-Host "   adb shell                # Acessar terminal do device"

Write-Host "`n SDK INSTALADO EM: $SdkPath" -ForegroundColor Cyan

exit 0
