# Instalação do Android SDK no Windows

## 🚀 Opção 1: Android Studio (Recomendada - Mais Fácil)

### Passo 1: Baixar Android Studio

1. Acesse: https://developer.android.com/studio
2. Clique em "Download Android Studio"
3. Aceite os termos
4. Download ~1GB (vai demorar um pouco)

### Passo 2: Instalar

```bash
# Executar o instalador (Android-Studio-2024.x.x-windows.exe)
# Next → Next → Install → Finish

# Ao abrir pela primeira vez:
# - Deixar fazer setup automático
# - Vai baixar SDK Components automaticamente (~2GB)
# - Aguarde completar (pode levar 10-20 min)
```

### Passo 3: Verificar Instalação

```bash
# Abrir PowerShell e testar
adb version

# Se der erro ainda, adicionar ao PATH (veja Passo 4)
```

### Passo 4: Configurar PATH (Se necessário)

```powershell
# Abrir PowerShell como Administrador

# Verificar onde Android SDK foi instalado
# Geralmente em: C:\Users\[seu-usuario]\AppData\Local\Android\Sdk

# Adicionar ao PATH:
$AndroidSdkPath = "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk\platform-tools"
$env:Path += ";$AndroidSdkPath"

# Ou configurar variável de ambiente permanente:
# Settings → Environment Variables → New User Variable
# Variable name: ANDROID_SDK_ROOT
# Variable value: C:\Users\[seu-usuario]\AppData\Local\Android\Sdk

# Depois reiniciar PowerShell

# Testar novamente
adb version
```

---

## ⚡ Opção 2: Download Mínimo (Sem Android Studio)

Se quer apenas o SDK mínimo (~500MB):

```bash
# 1. Download Command Line Tools
# https://developer.android.com/studio/releases/sdk-tools

# 2. Extrair em C:\Android\Sdk

# 3. Abrir PowerShell como Admin
$env:Path += ";C:\Android\Sdk\platform-tools"

# 4. Testar
adb version
```

---

## 🔧 Instalação Automática (PowerShell Script)

**Copie e execute este script no PowerShell (como Admin):**

```powershell
# Script de instalação do ADB
Write-Host "🔧 Instalando ADB..." -ForegroundColor Green

# Verificar se já existe
if (Get-Command adb -ErrorAction SilentlyContinue) {
    Write-Host "✅ ADB já está instalado!" -ForegroundColor Green
    adb version
    exit
}

# Caminho padrão do Android SDK
$AndroidSdkPath = "$env:USERPROFILE\AppData\Local\Android\Sdk"

# Verificar se Android Studio já instalou SDK
if (Test-Path "$AndroidSdkPath\platform-tools\adb.exe") {
    Write-Host "✅ Android SDK encontrado em: $AndroidSdkPath" -ForegroundColor Green
    
    # Adicionar ao PATH
    $platformToolsPath = "$AndroidSdkPath\platform-tools"
    if ($env:Path -notlike "*$platformToolsPath*") {
        $env:Path = "$env:Path;$platformToolsPath"
        Write-Host "✅ ADB adicionado ao PATH" -ForegroundColor Green
    }
    
    # Testar
    adb version
    Write-Host "✅ Instalação completa!" -ForegroundColor Green
} else {
    Write-Host "❌ Android SDK não encontrado" -ForegroundColor Red
    Write-Host "📥 Baixe Android Studio em: https://developer.android.com/studio" -ForegroundColor Yellow
    Write-Host "⏱️  Após instalar, execute este script novamente" -ForegroundColor Yellow
}
```

**Para salvar e executar:**

```powershell
# 1. Copiar script acima
# 2. Salvar em: install_adb.ps1
# 3. Executar no PowerShell (como Admin):

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\install_adb.ps1
```

---

## ✅ Verificar Instalação Completa

```powershell
# 1. Testar ADB
adb version
# Output: Android Debug Bridge version 1.0.x

# 2. Listar devices conectados
adb devices
# Output: List of attached devices
#         (nenhum device por enquanto é ok)

# 3. Se ambos funcionarem, você está pronto! ✅
```

---

## 📋 Checklist de Instalação

- [ ] Baixar Android Studio
- [ ] Instalar Android Studio
- [ ] Aguardar setup automático (pode levar tempo)
- [ ] Adicionar ao PATH (se necessário)
- [ ] Abrir PowerShell novo
- [ ] Testar `adb version` → funciona ✅
- [ ] Testar `adb devices` → funciona ✅

---

## 🚨 Troubleshooting

### Erro: "adb: not found"

```powershell
# Solução 1: Reiniciar PowerShell como Admin
# (após instalar Android Studio)

# Solução 2: Adicionar manualmente
$AndroidSdk = "$env:USERPROFILE\AppData\Local\Android\Sdk\platform-tools"
$env:Path = "$env:Path;$AndroidSdk"
adb version

# Solução 3: Verificar se Android Studio foi instalado
# Abrir Android Studio e deixar completar o setup

# Solução 4: Configurar PATH permanente
# Settings → Search "environment variables" → Edit → New
# Variable name: ANDROID_SDK_ROOT
# Variable value: C:\Users\[seu-usuario]\AppData\Local\Android\Sdk
# Depois reiniciar PowerShell completamente (fechar e abrir)
```

### Download muito lento

```bash
# Usar VPN ou baixar por partes
# Alternativamente, usar emulador online
```

### Muito grande (~2GB)?

```bash
# Usar apenas Command Line Tools
# https://developer.android.com/studio/releases/sdk-tools
# (~500MB ao invés de 2GB)
```

---

## ⚡ Quick Start Resumido

```powershell
# 1. Abrir PowerShell como Admin

# 2. Se Android Studio NÃO está instalado:
#    Baixar em: https://developer.android.com/studio
#    Instalar normalmente (Next → Next → Install)
#    Aguardar completar o setup automático (bem importante!)

# 3. Com Android Studio instalado, rodar:
$env:Path += ";$env:USERPROFILE\AppData\Local\Android\Sdk\platform-tools"
adb version

# 4. Se funcionou, você está 100% pronto! ✅
```

---

## 📞 Confirmação

Após instalar, execute:

```powershell
adb version
adb devices
```

Se ambas funcionarem, me avisa que a gente segue com o teste do APK! 🎉
