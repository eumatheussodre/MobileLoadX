# ⚡ Guia Rápido de Instalação do Android SDK

## 🚀 OPÇÃO RECOMENDADA: Android Studio

### Passo 1: Baixar
```
Acesse: https://developer.android.com/studio
Clique: "Download Android Studio"
Arquivo: ~1GB (vai demorar)
```

### Passo 2: Instalar
```
1. Execute o instalador
2. Clique Next → Next → Install → Finish
3. AGUARDE o primeiro launch (vai baixar ~2GB extras)
   ⚠️  NÃO FECHE! Deixe completar (10-20 minutos)
4. Feche Android Studio
```

### Passo 3: Configurar PATH (Como Admin)
```powershell
# Abrir PowerShell como ADMINISTRADOR

$env:Path += ";$env:USERPROFILE\AppData\Local\Android\Sdk\platform-tools"

# Testar
adb version

# Se funcionou, você está 100% pronto! ✅
```

### Passo 4: Verificar
```powershell
adb version      # Deve mostrar versão
adb devices      # Deve funcionar
```

---

## ⚡ OPÇÃO RAPIDA: Apenas Command Line Tools (~500MB)

```powershell
# 1. Baixar de:
#    https://developer.android.com/studio/releases/sdk-tools

# 2. Extrair em:
#    C:\Android\Sdk

# 3. Adicionar ao PATH como Admin:
$env:Path += ";C:\Android\Sdk\platform-tools"

# 4. Testar:
adb version
```

---

## 🔧 Script Automático

```powershell
# Abrir PowerShell como ADMINISTRADOR

cd D:\Projetos\MobileLoadX

powershell -ExecutionPolicy Bypass -File install_android_sdk.ps1
```

O script vai:
- ✅ Verificar se Android SDK está instalado
- ✅ Adicionar ao PATH automaticamente
- ✅ Testar se ADB funciona
- ✅ Mostrar próximos passos

---

## ✅ Próximos Passos Após Instalação

```powershell
# 1. Verifique
adb version
adb devices

# 2. Se houver device listado:
adb install seu-app.apk

# 3. Pronto para testar! 🎉
mobileloadx run test_config.yaml
```

---

## 📋 Checklist

- [ ] Baixar Android Studio
- [ ] Instalar (Next → Finish)
- [ ] Aguardar setup automático (~20 min)
- [ ] Abrir PowerShell como Admin
- [ ] Executar script ou adicionar PATH
- [ ] Testar: `adb version` ✅
- [ ] Testar: `adb devices` ✅
- [ ] Pronto para usar MobileLoadX! 🚀

---

## 🆘 Problemas?

**"adb: not found"**
→ Reinicie PowerShell completamente (feche todas as janelas)
→ Ou execute como Admin novamente

**Android Studio está demorando muito**
→ Normal! Deixe baixar (SDK ~2GB)
→ Pode levar 15-30 minutos

**Não consegue adicionar ao PATH**
→ Execute o script com admin
→ Ou adicione manualmente em Settings → Environment Variables

---

## 💡 Dica Extra

Se tem **device real**:
```
1. Conecte via USB
2. Ative USB Debugging (Settings → Developer → USB Debugging)
3. Autorize no device
4. adb devices (vai listar)
5. adb install seu-app.apk
```

**Nenhuma instalação extra necessária!** 👍

---

**Quando terminar, entre em contato que vamos prosseguir com o teste do APK! 🎉**
