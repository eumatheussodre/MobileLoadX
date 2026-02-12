# Guia de Teste de APK Real com MobileLoadX

## 1️⃣ Pré-requisitos

### Instalar ferramentas necessárias:

```bash
# Android SDK (já inclui adb)
# Baixar em: https://developer.android.com/studio

# Node.js (para Appium)
# https://nodejs.org/

# Appium (servidor que controla o APK)
npm install -g appium
npm install -g appium-doctor

# Verificar que tudo está instalado
appium-doctor --android
```

### Configurar variáveis de ambiente:

**Windows (adicione ao PATH):**
```
C:\Android\Sdk\platform-tools
C:\Android\Sdk\tools
```

**Verificar instalação:**
```bash
adb version
adb devices
```

---

## 2️⃣ Preparar Dispositivo/Emulador

### Opção A: Usar Emulador Android

```bash
# Listar emuladores disponíveis
emulator -list-avds

# Iniciar emulador
emulator -avd Pixel_5_API_33

# Verificar que está conectado
adb devices
# Output: emulator-5554	device
```

### Opção B: Usar Dispositivo Real

```bash
# Conectar USB
# Ativar USB Debugging em Settings > Developer Options

# Verificar conexão
adb devices
# Output: ZY123ABC123	device
```

### Instalar seu APK:

```bash
adb install -r path/to/your-app.apk

# Ou com adb direto no emulador específico
adb -s emulator-5554 install -r app.apk
```

---

## 3️⃣ Iniciar Appium Server

```bash
# Terminal 1: Iniciar Appium
appium

# Output:
# [Appium] Welcome to Appium v2.x.x
# [Appium] Server running on http://127.0.0.1:4723
```

---

## 4️⃣ Criar Arquivo de Configuração

**Criar arquivo: `android_test.yaml`**

```yaml
name: "APK Real Load Test"
duration: 300         # Duração em segundos
virtual_users: 3      # Número de usuários simultâneos
ramp_up_time: 30      # Tempo para rampar

platforms:
  - platform: android
    app: "/path/to/your-app.apk"
    devices:
      - emulator-5554    # ou seu device ID do adb
    capabilities:
      appium_server_url: "http://localhost:4723"
      automationName: "UiAutomator2"
      platformVersion: "13"               # Version do Android
      deviceName: "Pixel 5"               # Nome do device
      newCommandTimeout: 300
      autoGrantPermissions: true
      autoWebview: false

scenarios:
  - name: "Login & Browse"
    weight: 100
    actions:
      # Esperar a app carregar
      - type: wait
        timeout: 3
      
      # Clicar no campo de email (substitua pelo seu ID/xpath)
      - type: tap
        id: "com.example.app:id/email_input"
      
      # Digitar email
      - type: input
        text: "testuser@example.com"
      
      # Clicar senha
      - type: tap
        xpath: "//android.widget.EditText[@password='true']"
      
      # Digitar senha
      - type: input
        text: "password123"
      
      # Clicar botão login
      - type: tap
        xpath: "//android.widget.Button[@text='Login']"
      
      # Esperar carregar
      - type: wait
        timeout: 2
      
      # Scroll na página
      - type: scroll
        direction: "down"
        duration: 1
      
      # Esperar mais
      - type: wait
        timeout: 1
      
      # Scroll para cima
      - type: scroll
        direction: "up"
        duration: 1

thresholds:
  response_time_p95: 3000      # 3s
  response_time_p99: 5000      # 5s
  error_rate: 0.10             # 10%
  cpu_max: 80                  # CPU %
  memory_max: 500              # MB

metrics:
  collect:
    - cpu
    - memory
    - battery
    - network
  interval: 1
```

---

## 5️⃣ Encontrar IDs e XPath dos Elementos

### Método 1: Usar Appium Inspector

```bash
# Instalar
npm install -g appium-inspector

# Abrir
appium-inspector
```

**UI do Inspector:**
1. Conectar ao Appium (http://localhost:4723)
2. Adicionar capabilities (platform, app, etc)
3. Conectar
4. Inspecionar elementos interativamente

### Método 2: Usar adb + Espresso

```bash
# Dump UI hierarchy
adb shell uiautomator dump /sdcard/ui.xml

# Baixar arquivo
adb pull /sdcard/ui.xml

# Abrir em editor e procurar por IDs/labels
```

### Método 3: Código Python para Debug

```python
from mobileloadx.core.virtual_user import VirtualUser
from mobileloadx.core.scenario import Scenario

# Iniciar usuário virtual
user = VirtualUser(
    user_id=1,
    platform='android',
    app='/path/to/app.apk',
    device='emulator-5554',
    capabilities={
        'appium_server_url': 'http://localhost:4723',
        'automationName': 'UiAutomator2'
    }
)

user.start()

# Explorar app
driver = user.driver

# Pegar dump da tela
from selenium.webdriver.common.by import By

# Procurar por elementos
buttons = driver.find_elements(By.XPATH, "//android.widget.Button")
for btn in buttons:
    print(f"Button: {btn.get_attribute('text')}")

user.stop()
```

---

## 6️⃣ Executar Teste

### Opção A: Linha de Comando

```bash
# Validar configuração primeiro
mobileloadx validate android_test.yaml --strict

# Executar teste
mobileloadx run android_test.yaml --output-dir ./results --verbose

# Ver resultados
mobileloadx report ./results --open
```

### Opção B: Código Python

```python
from mobileloadx.core.load_test import LoadTest

# Criar teste
test = LoadTest(
    name="Android APK Test",
    config_file="android_test.yaml"
)

# Executar
results = test.run()

# Processar resultados
print(f"Total ações: {results.total_actions}")
print(f"Taxa de sucesso: {results.success_rate:.1f}%")
print(f"Tempo médio resposta: {results.response_time_avg:.0f}ms")
print(f"P95: {results.response_time_p95:.0f}ms")
print(f"P99: {results.response_time_p99:.0f}ms")
print(f"CPU médio: {results.avg_cpu:.1f}%")
print(f"Pico memória: {results.peak_memory:.1f}MB")

# Verificar thresholds
if results.passed_thresholds:
    print("✅ Teste passou!")
else:
    print("❌ Teste falhou")
```

---

## 7️⃣ Troubleshooting

### Problema: "Connection refused"
```bash
# Verificar se Appium está rodando
curl http://localhost:4723/status

# Reiniciar Appium
appium --base-path /wd/hub
```

### Problema: "Device not found"
```bash
# Verificar dispositivos
adb devices

# Matar e reiniciar adb
adb kill-server
adb start-server
```

### Problema: "App not installed"
```bash
# Instalar novamente
adb install -r app.apk

# Ou forçar reinstalação
adb uninstall com.example.app
adb install app.apk
```

### Problema: "Element not found"
```bash
# Inspecionar elemento interativamente com Appium Inspector
appium-inspector

# Ou verificar dump:
adb shell uiautomator dump /sdcard/ui.xml
adb pull /sdcard/ui.xml
```

### Problema: "Timeout"
```yaml
# Aumentar timeout na configuração
capabilities:
  newCommandTimeout: 600    # 10 minutos
  implicitWaitMs: 10000     # 10 segundos
```

---

## 8️⃣ Análise de Resultados

### Relatório HTML:
```bash
# Gerar e abrir
mobileloadx report ./results --open
```

### Relatório JSON:
```bash
# Analisar programaticamente
import json

with open('./results/report.json', 'r') as f:
    data = json.load(f)

print(f"Taxa de erro: {data['error_rate']:.2%}")
print(f"Upload: {data.get('network', {}).get('upload', 0)} KB/s")
print(f"Download: {data.get('network', {}).get('download', 0)} KB/s")
```

### Relatório CSV:
```bash
# Abrir em Excel/Google Sheets
./results/report.csv
```

---

## 9️⃣ Otimizações para Teste Real

### Performance:
```yaml
# Reduzir interval de coleta para menos overhead
metrics:
  interval: 5    # A cada 5 segundos (não a cada 1)

# Usar menos usuários virtuais para teste inicial
virtual_users: 1

# Reduzir duração
duration: 120    # 2 minutos
```

### Estabilidade:
```yaml
# Aumentar timeouts
capabilities:
  newCommandTimeout: 600
  implicitWaitMs: 15000
  implicitWaitMs: 15000

# Adicionar waits entre ações
actions:
  - type: wait
    timeout: 2
  - type: tap
    ...
  - type: wait
    timeout: 1
```

### Detalhes:
```bash
# Modo verbose para debug
mobileloadx run android_test.yaml --verbose -v

# Com logging estruturado
mobileloadx configure-logging --log-level DEBUG --log-file debug.log --json-logs
```

---

## 🔟 Exemplo Prático Completo

### 1. Instalar Appium
```bash
npm install -g appium
appium
```

### 2. Conectar Device
```bash
adb devices
adb install myapp.apk
```

### 3. Criar config
```bash
cat > test_config.yaml << 'EOF'
name: "MyApp Load Test"
duration: 120
virtual_users: 2
ramp_up_time: 10

platforms:
  - platform: android
    app: "./myapp.apk"
    devices:
      - emulator-5554

scenarios:
  - name: "Main Flow"
    weight: 100
    actions:
      - type: wait
        timeout: 2
      - type: tap
        xpath: "//android.widget.Button[@text='Start']"
      - type: wait
        timeout: 3

thresholds:
  response_time_p95: 3000
  error_rate: 0.05
EOF
```

### 4. Validar e Executar
```bash
mobileloadx validate test_config.yaml
mobileloadx run test_config.yaml --output-dir ./results --verbose
mobileloadx report ./results --open
```

---

## 📚 Recursos Adicionais

- [Appium Docs](http://appium.io/)
- [UIAutomator2 Docs](https://github.com/appium/appium-uiautomator2-driver)
- [XPath Tutorial](https://www.w3schools.com/xml/xpath_intro.asp)
- [MobileLoadX Docs](../README.md)
