#!/usr/bin/env powershell
# Script completo para finalizar Android SDK setup com Java configurado
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

function Write-Header {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

Write-Header "COMPLETANDO SETUP DO ANDROID SDK"

# 1. Configurar JAVA_HOME para esta sessao
Write-Host "`n1. Configurando Java..." -ForegroundColor Magenta

$javaHome = "C:\Java\jdk-17"
$env:JAVA_HOME = $javaHome
$env:Path = "$env:Path;$javaHome\bin"

Write-Info "JAVA_HOME = $javaHome"

# Verificar Java
$javaExe = "$javaHome\bin\java.exe"
if (Test-Path $javaExe) {
    Write-Success "Java encontrado em: $javaExe"
} else {
    Write-Error-Custom "java.exe nao encontrado em: $javaExe"
    exit 1
}

# 2. Verificar sdkmanager
Write-Host "`n2. Verificando SDK Manager..." -ForegroundColor Magenta

$sdkManagerPath = "C:\Android\Sdk\cmdline-tools\latest\bin\sdkmanager.bat"

if (Test-Path $sdkManagerPath) {
    Write-Success "SDK Manager encontrado"
} else {
    Write-Error-Custom "SDK Manager nao encontrado"
    exit 1
}

# 3. Aceitar licencas
Write-Host "`n3. Aceitando licencas (pode levar 1-2 minutos)..." -ForegroundColor Magenta

try {
    $licensesFile = "$env:TEMP\accept_licenses_$([System.DateTime]::Now.Ticks).txt"
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
    
    Write-Info "Processando licencas..."
    Get-Content $licensesFile | & $sdkManagerPath --licenses 2>&1 | Select-String -Pattern "Accepted|accepted|License|All licenses" | Write-Host
    
    Remove-Item $licensesFile -Force -ErrorAction SilentlyContinue
    Write-Success "Licencas aceitas"
}
catch {
    Write-Error-Custom "Erro ao aceitar licencas: $_"
    Write-Info "Continuando mesmo assim..."
}

# 4. Instalar packages essenciais
Write-Host "`n4. Instalando packages essenciais..." -ForegroundColor Magenta

$packages = @(
    @{name = "platform-tools"; display = "Platform Tools (~80MB)" },
    @{name = "build-tools;34.0.0"; display = "Build Tools 34.0.0 (~200MB)" },
    @{name = "platforms;android-34"; display = "Android SDK 34 (~100MB)" },
    @{name = "emulator"; display = "Android Emulator (~200MB)" }
)

foreach ($pkg in $packages) {
    Write-Info "Instalando $($pkg.display)..."
    
    try {
        $output = & $sdkManagerPath $pkg.name 2>&1
        
        # Procurar por mensagens de sucesso
        if ($output -match "Installed|installed|Done") {
            Write-Success "$($pkg.name) instalado"
        } else {
            Write-Success "$($pkg.name) processado"
        }
    }
    catch {
        Write-Error-Custom "Falha em $($pkg.name): $_"
    }
}

# 5. Configurar PATH
Write-Host "`n5. Configurando PATH para adb..." -ForegroundColor Magenta

$platformToolsPath = "C:\Android\Sdk\platform-tools"
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
        Write-Success "PATH configurado"
    }
    catch {
        Write-Error-Custom "Erro ao configurar PATH: $_"
    }
} else {
    Write-Success "PATH ja configurado"
}

# 6. Verificar instalacao
Write-Host "`n6. Verificando instalacao..." -ForegroundColor Magenta

# Aguardar um pouco para os arquivos serem criados
Start-Sleep -Seconds 2

$adbPath = "$platformToolsPath\adb.exe"

if (Test-Path $adbPath) {
    Write-Success "adb.exe encontrado!"
    
    try {
        $version = & $adbPath version 2>&1 | Select-Object -First 1
        Write-Host "   $version"
        Write-Success "ADB funcionando corretamente!"
    }
    catch {
        Write-Error-Custom "Erro ao testar adb: $_"
    }
} else {
    Write-Error-Custom "adb.exe ainda nao foi criado"
    Write-Info "Isso pode levar alguns minutos. Tente novamente em breve."
}

# 7. Listar devices
Write-Host "`n7. Procurando devices conectados..." -ForegroundColor Magenta

try {
    $devices = & $adbPath devices 2>&1
    Write-Host ($devices -join "`n")
}
catch {
    Write-Info "Nenhum device conectado ainda (normal)"
}

# Resumo Final
Write-Host "`n" + "="*60 -ForegroundColor Green
Write-Host "OK: SETUP DO ANDROID SDK COMPLETO!" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Green

Write-Host "`nINFORMAÇOES:" -ForegroundColor Cyan
Write-Host "  Java: $javaHome"
Write-Host "  SDK: C:\Android\Sdk"
Write-Host "  ADB: $adbPath"

Write-Host "`nPROXIMOS PASSOS:" -ForegroundColor Magenta
Write-Host "1. Feche e reabra o PowerShell (para carregar PATH novo)"
Write-Host "2. Conecte um device Android via USB (com modo developer ON)"
Write-Host "3. Execute: adb devices"
Write-Host "4. Se device aparecer, pode começar a testar APKs!"

Write-Host "`nCOMANDOS UTEIS:" -ForegroundColor Magenta
Write-Host "  adb devices              # Listar devices conectados"
Write-Host "  adb install app.apk     # Instalar APK"
Write-Host "  adb push file /sdcard/  # Enviar arquivo"
Write-Host "  adb shell                # Terminal do device"
Write-Host "  emulator -list-avds     # Listar emuladores"
Write-Host "  emulator -avd MyAVD     # Iniciar emulador"

Write-Host "`nCOMO TESTAR COM MOBILELOADX:" -ForegroundColor Magenta
Write-Host "  python examples/find_elements.py --apk app.apk"
Write-Host "  mobileloadx validate config.yaml"
Write-Host "  mobileloadx run config.yaml"

Write-Host "`n========================================" -ForegroundColor Green

exit 0
