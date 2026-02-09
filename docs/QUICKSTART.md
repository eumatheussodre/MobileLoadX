# 🚀 Guia de Início Rápido - MobileLoadX

## Em 5 Minutos

### 1️⃣ Instale

```bash
pip install mobileloadx
```

### 2️⃣ Inicie o Appium

```bash
appium
```

### 3️⃣ Prepare seu device

**Android Emulador:**
```bash
emulator -avd Pixel_5_API_33 &
adb devices  # Verifique o device ID
```

**iOS Simulador:**
```bash
xcrun simctl boot "iPhone 14 Pro"
```

### 4️⃣ Crie configuração

```bash
mobileloadx init
```

Edite `config.yaml` e ajuste para seu app:

```yaml
test:
  name: "Meu Teste"
  duration: 60

virtual_users:
  max: 5
  ramp_up_time: 10

platforms:
  - android:
      app: "./seu-app.apk"
      device: "emulator-5554"  # Seu device ID

scenarios:
  - name: "Tap no botão"
    weight: 100
    actions:
      - tap: {id: "button_id"}  # ID do seu elemento
      - wait: {timeout: 2}
```

### 5️⃣ Execute

```bash
mobileloadx run config.yaml
```

### 6️⃣ Veja os resultados

```bash
mobileloadx report --open
```

## Exemplo Python

```python
from mobileloadx import LoadTest, Scenario

# Criar cenário
scenario = Scenario("Login")
scenario.tap(id="username")
scenario.input("user@test.com")
scenario.tap(id="password")
scenario.input("senha123")
scenario.tap(id="login_btn")

# Configurar teste
test = LoadTest(
    name="Login Test",
    duration=60,
    virtual_users=5
)

test.add_platform(
    platform="android",
    app="./app.apk",
    device="emulator-5554"
)

test.add_scenario(scenario)

# Executar
results = test.run()
print(f"Taxa de sucesso: {results.success_rate:.1f}%")
```

## Próximos Passos

✅ Explore mais [exemplos](../examples/)
✅ Configure [thresholds](../README.md#configuração-avançada)
✅ Integre com [CI/CD](../README.md#integração-cicd)
✅ Veja métricas detalhadas no [relatório HTML](../README.md#métricas-coletadas)

## Dicas

💡 Use `--verbose` para debug:
```bash
mobileloadx run config.yaml --verbose
```

💡 Descubra IDs de elementos com Appium Inspector

💡 Comece com poucos usuários (5-10) e aumente gradualmente

💡 Defina thresholds realistas baseados em testes iniciais
