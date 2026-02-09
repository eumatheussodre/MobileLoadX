# 📖 Guia de Instalação - MobileLoadX

## Pré-requisitos

### 1. Python 3.8+

```bash
python --version
# Deve retornar Python 3.8 ou superior
```

### 2. Appium Server 2.0+

```bash
npm install -g appium
appium --version
```

### 3. Drivers Appium

**Android (UiAutomator2):**
```bash
appium driver install uiautomator2
```

**iOS (XCUITest):**
```bash
appium driver install xcuitest
```

### 4. Android SDK (para testes Android)

- Instale o [Android Studio](https://developer.android.com/studio)
- Configure as variáveis de ambiente:
  ```bash
  export ANDROID_HOME=/path/to/android-sdk
  export PATH=$PATH:$ANDROID_HOME/platform-tools
  export PATH=$PATH:$ANDROID_HOME/tools
  ```
- Verifique:
  ```bash
  adb version
  ```

### 5. Xcode e Command Line Tools (para testes iOS - apenas macOS)

```bash
xcode-select --install
```

## Instalação do MobileLoadX

### Opção 1: Via pip (quando publicado)

```bash
pip install mobileloadx
```

### Opção 2: A partir do código fonte

```bash
# Clone o repositório
git clone https://github.com/your-org/mobileloadx.git
cd mobileloadx

# Instale em modo desenvolvimento
pip install -e .

# Ou instale as dependências manualmente
pip install -r requirements.txt
```

## Verificação da Instalação

```bash
# Verificar CLI
mobileloadx --version

# Criar config de exemplo
mobileloadx init

# Verificar Python API
python -c "from mobileloadx import LoadTest; print('OK')"
```

## Setup de Ambiente de Desenvolvimento

### Devices Android

**Emulador:**
```bash
# Listar emuladores disponíveis
emulator -list-avds

# Iniciar emulador
emulator -avd Pixel_5_API_33 &

# Verificar conexão
adb devices
```

**Device Físico:**
1. Habilite "Opções do Desenvolvedor" no device
2. Ative "Depuração USB"
3. Conecte via USB
4. Execute `adb devices` para verificar

### Devices iOS

**Simulador:**
```bash
# Listar simuladores
xcrun simctl list devices

# Iniciar simulador
open -a Simulator

# Ou específico
xcrun simctl boot "iPhone 14 Pro"
```

**Device Físico:**
1. Conecte o device via USB
2. Confie no computador no device
3. Configure certificados de desenvolvimento no Xcode

## Iniciar Appium Server

```bash
# Modo padrão
appium

# Modo verbose (para debug)
appium --log-level debug

# Porta customizada
appium --port 4724
```

## Primeiro Teste

### 1. Crie um arquivo de configuração

```bash
mobileloadx init
```

### 2. Edite `config.yaml`

Ajuste os valores para seu app e device:
- `app`: Caminho do .apk (Android) ou .app (iOS)
- `device`: ID do device/emulador
- `id` dos elementos: Inspecione com Appium Inspector

### 3. Execute o teste

```bash
mobileloadx run config.yaml
```

## Ferramentas Úteis

### Appium Inspector

Para inspecionar elementos da UI:

```bash
npm install -g appium-inspector
# Ou baixe: https://github.com/appium/appium-inspector/releases
```

### Android UI Automator Viewer

```bash
# Já vem com Android SDK
uiautomatorviewer
```

### Accessibility Inspector (iOS)

Incluso no Xcode:
1. Xcode → Open Developer Tool → Accessibility Inspector

## Troubleshooting

### Erro: "Could not connect to Appium server"

```bash
# Verificar se Appium está rodando
curl http://localhost:4723/status

# Reiniciar Appium
killall node
appium
```

### Erro: "Device not found"

```bash
# Android
adb devices
adb kill-server
adb start-server

# iOS
xcrun simctl list devices
```

### Erro: "App not installed"

```bash
# Android - Instalar manualmente
adb install /path/to/app.apk

# iOS
xcrun simctl install booted /path/to/app.app
```

### Performance lenta

- Use emuladores/simuladores com aceleração de hardware
- Aumente memória RAM do emulador
- Desative animações no device
- Use devices reais quando possível

## Próximos Passos

1. Leia o [README.md](../README.md) para overview do framework
2. Veja os [exemplos](../examples/) para diferentes casos de uso
3. Consulte a [análise de gaps](../MARKET_GAPS.md) para entender os diferenciais
4. Explore a API Python em [API Reference](./API.md)

## Recursos Adicionais

- [Documentação Appium](https://appium.io/docs/en/latest/)
- [Android Debug Bridge (adb)](https://developer.android.com/studio/command-line/adb)
- [iOS Simulator](https://developer.apple.com/documentation/xcode/running-your-app-in-simulator-or-on-a-device)
