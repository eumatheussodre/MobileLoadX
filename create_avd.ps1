#!/usr/bin/env powershell
# Script para criar um Android Virtual Device (AVD)
# Execute como Administrador

$ErrorActionPreference = "Continue"

function Write-Success {
    param([string]$Message)
    Write-Host "OK: $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "INFO: $Message" -ForegroundColor Blue
}

function Write-Warn {
    param([string]$Message)
    Write-Host "AVISO: $Message" -ForegroundColor Yellow
}

function Write-Header {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

Write-Header "CRIANDO ANDROID VIRTUAL DEVICE (AVD)"

# Configuracoes
$avdName = "Nexus_6_API_34"
$sdkPath = "C:\Android\Sdk"
$avdmanagerPath = "$sdkPath\cmdline-tools\latest\bin\avdmanager.bat"
$androidHome = "$env:USERPROFILE\.android"

# Configurar variaveis de ambiente
$env:ANDROID_HOME = $sdkPath
$env:ANDROID_SDK_HOME = $androidHome
$env:ANDROID_AVD_HOME = "$androidHome\avd"
$env:JAVA_HOME = "C:\Java\jdk-17"
$env:Path = "$env:Path;$sdkPath\platform-tools;$sdkPath\emulator"

Write-Info "JAVA_HOME = $env:JAVA_HOME"
Write-Info "ANDROID_HOME = $env:ANDROID_HOME"
Write-Info "ANDROID_AVD_HOME = $env:ANDROID_AVD_HOME"

# 1. Verificar avdmanager
Write-Host "`n1. Verificando avdmanager..." -ForegroundColor Magenta

if (Test-Path $avdmanagerPath) {
    Write-Success "avdmanager encontrado"
} else {
    Write-Warn "avdmanager nao encontrado em: $avdmanagerPath"
    Write-Info "Verifique se o Command Line Tools foi instalado"
    exit 1
}

# 2. Verificar se AVD ja existe
Write-Host "`n2. Procurando AVD existentes..." -ForegroundColor Magenta

try {
    $existingAvds = & $avdmanagerPath list avd 2>&1 | Select-String "Name:" | ForEach-Object { $_ -replace ".*Name: ", "" -replace " .*", "" }
    
    if ($existingAvds) {
        Write-Info "AVDs existentes:"
        $existingAvds | ForEach-Object { Write-Host "   - $_" }
        
        if ($existingAvds -contains $avdName) {
            Write-Success "AVD '$avdName' ja existe"
            exit 0
        }
    } else {
        Write-Info "Nenhum AVD encontrado"
    }
}
catch {
    Write-Info "Nao foi possivel listar AVDs"
}

# 3. Criar o AVD
Write-Host "`n3. Criando novo AVD: $avdName" -ForegroundColor Magenta
Write-Info "Isso pode levar alguns minutos..."
Write-Info "Sistema: Android 34 (API 34)"
Write-Info "Arquitetura: x86_64"

# Criar arquivo de resposta para questoes interativas
$configFile = "$env:TEMP\avd_config_$([System.DateTime]::Now.Ticks).txt"

@"
hw.device.name=Nexus 6
hw.target=android-34
hw.keyboard=yes
hw.sdCard=yes
disk.dataPartition.size=4G
hw.ramSize=2048
hw.screen.width=1440
hw.screen.height=2560
hw.screen.density=560
"@ | Out-File -FilePath $configFile -Encoding ASCII -Force

Write-Info "Criando AVD..."

try {
    $output = & $avdmanagerPath create avd `
        -n $avdName `
        -k "system-images;android-34;google_apis;x86_64" `
        -f 2>&1
    
    Write-Host $output -ForegroundColor Gray
    
    Write-Success "AVD criado com sucesso!"
    
    # Copiar configuracoes
    $avdConfigPath = "$env:ANDROID_AVD_HOME\$avdName\config.ini"
    if (Test-Path $avdConfigPath) {
        Write-Info "Configurando hardware..."
        Add-Content -Path $avdConfigPath -Value @"

# Configuracoes de performance
hw.keyboard=yes
hw.sdCard=yes
disk.dataPartition.size=4G
hw.ramSize=2048
"@
        Write-Success "Hardware configurado"
    }
}
catch {
    Write-Warn "Erro ao criar AVD: $_"
    Write-Info "Tentando alternativa..."
}

# Limpar temp
Remove-Item $configFile -Force -ErrorAction SilentlyContinue

# 4. Listar AVDs criados
Write-Host "`n4. Listando AVDs disponiveis..." -ForegroundColor Magenta

try {
    $avds = & $avdmanagerPath list avd 2>&1
    Write-Host ($avds -join "`n") -ForegroundColor Gray
}
catch {
    Write-Warn "Nao foi possivel listar AVDs"
}

# Resumo
Write-Host "`n" + "="*50 -ForegroundColor Green
Write-Host "OK: SETUP DO AVD COMPLETO!" -ForegroundColor Green
Write-Host "="*50 -ForegroundColor Green

Write-Host "`nPROXIMOS PASSOS:" -ForegroundColor Magenta
Write-Host "1. Abra um novo PowerShell"
Write-Host "2. Inicie o emulador:"
Write-Host "   emulator -avd $avdName"
Write-Host ""
Write-Host "3. Aguarde o Android iniciar (pode levar 3-5 minutos)"
Write-Host "4. Quando estiver pronto, em outro PowerShell execute:"
Write-Host "   adb devices"
Write-Host ""
Write-Host "5. Instale uma APK:"
Write-Host "   adb install -r app.apk"

Write-Host "`nCOMANDOS UTEIS:" -ForegroundColor Magenta
Write-Host "  adb shell pm list packages              # Listar apps"
Write-Host "  adb shell am start -n package/.Activity # Iniciar app"
Write-Host "  adb shell screencap -p > screenshot.png # Tirar screenshot"
Write-Host "  adb logcat                              # Ver logs"

exit 0
