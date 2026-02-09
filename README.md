# 🚀 MobileLoadX Framework

Framework profissional de teste de performance para aplicativos mobile (Android/iOS) com suporte a simulação de múltiplos usuários simultâneos.

## 📋 Características Principais

- ✅ **Cross-Platform**: Android e iOS com o mesmo código
- ✅ **Múltiplos Usuários**: Simule até milhares de usuários simultâneos
- ✅ **Métricas Detalhadas**: CPU, Memória, Bateria, Rede, FPS
- ✅ **Configuração Simples**: YAML/JSON para cenários de teste
- ✅ **Relatórios Completos**: HTML, JSON, CSV com gráficos
- ✅ **CI/CD Ready**: Integração fácil com pipelines
- ✅ **Extensível**: Sistema de plugins

## 🎯 Por que MobileLoadX?

Este framework preenche lacunas críticas dos frameworks existentes:
- Appium não suporta múltiplos usuários simultâneos
- JMeter não é feito para apps mobile
- Maestro foca em funcional, não performance
- XCUITest/Espresso não são cross-platform

Veja [MARKET_GAPS.md](MARKET_GAPS.md) para análise completa.

## 📦 Instalação

```bash
pip install mobileloadx
```

### Requisitos
- Python 3.8+
- Appium Server 2.0+
- Android SDK / Xcode (conforme plataforma)

## 🚀 Início Rápido

### 1. Configure seu teste (config.yaml)

```yaml
test:
  name: "Login Performance Test"
  duration: 300  # 5 minutos
  
virtual_users:
  initial: 1
  max: 50
  ramp_up_time: 60  # segundos
  
platforms:
  - android:
      app: "./app-release.apk"
      device: "emulator-5554"
  - ios:
      app: "./MyApp.app"
      device: "iPhone 14 Pro"
      
scenarios:
  - name: "Login Flow"
    weight: 70
    actions:
      - tap: {id: "username"}
      - input: {text: "user@example.com"}
      - tap: {id: "password"}
      - input: {text: "password123"}
      - tap: {id: "loginButton"}
      - wait: {timeout: 5}
      
  - name: "Browse Products"
    weight: 30
    actions:
      - tap: {id: "productsTab"}
      - scroll: {direction: "down", duration: 2}
      - tap: {xpath: "//android.widget.TextView[@text='Product 1']"}
      
metrics:
  collect:
    - cpu
    - memory
    - battery
    - network
    - fps
  interval: 1  # segundos
  
thresholds:
  cpu_max: 80  # %
  memory_max: 300  # MB
  response_time_p95: 2000  # ms
  error_rate_max: 5  # %
```

### 2. Execute o teste

```bash
mobileloadx run config.yaml
```

### 3. Veja os resultados

```bash
mobileloadx report --open
```

## 📊 Exemplo com Python API

```python
from mobileloadx import LoadTest, VirtualUser, Scenario

# Criar cenário
scenario = Scenario("Login Flow")
scenario.tap(id="username")
scenario.input("user@example.com")
scenario.tap(id="password")
scenario.input("password123")
scenario.tap(id="loginButton")
scenario.wait(5)

# Configurar teste
test = LoadTest(
    name="Login Performance",
    duration=300,
    virtual_users=50,
    ramp_up_time=60
)

# Adicionar plataforma
test.add_platform(
    platform="android",
    app="./app-release.apk",
    device="emulator-5554"
)

# Adicionar cenário
test.add_scenario(scenario, weight=100)

# Executar
results = test.run()

# Analisar
print(f"Usuários simultâneos: {results.max_concurrent_users}")
print(f"CPU média: {results.avg_cpu}%")
print(f"Memória pico: {results.peak_memory}MB")
print(f"Tempo resposta P95: {results.response_time_p95}ms")
print(f"Taxa de erro: {results.error_rate}%")
```

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────┐
│           Test Configuration (YAML/JSON)        │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│         MobileLoadX Test Engine                 │
│  ┌───────────────────────────────────────────┐  │
│  │     Virtual User Manager                  │  │
│  │  - Creates & manages virtual users        │  │
│  │  - Handles ramp-up/ramp-down             │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │     Scenario Orchestrator                 │  │
│  │  - Distributes scenarios by weight       │  │
│  │  - Manages action execution              │  │
│  └───────────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────┘
                  │
        ┌─────────┴──────────┐
        ▼                    ▼
┌──────────────┐      ┌──────────────┐
│   Android    │      │     iOS      │
│   Driver     │      │    Driver    │
└──────┬───────┘      └──────┬───────┘
       │                     │
       ▼                     ▼
┌──────────────┐      ┌──────────────┐
│   Appium     │      │   Appium     │
│  (Android)   │      │   (iOS)      │
└──────┬───────┘      └──────┬───────┘
       │                     │
       ▼                     ▼
┌──────────────┐      ┌──────────────┐
│   ADB        │      │  XCTest      │
│  Metrics     │      │  Metrics     │
└──────────────┘      └──────────────┘
       │                     │
       └──────────┬──────────┘
                  ▼
        ┌─────────────────────┐
        │  Metrics Collector  │
        │  - CPU, Memory      │
        │  - Battery, Network │
        │  - FPS, UI Metrics  │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │   Results Engine    │
        │  - Aggregation      │
        │  - Analysis         │
        │  - Thresholds       │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │  Report Generator   │
        │  - HTML, JSON, CSV  │
        │  - Charts, Graphs   │
        └─────────────────────┘
```

## 📈 Métricas Coletadas

### Device Metrics
- **CPU**: Uso por app e sistema
- **Memória**: RAM, Heap, Native, Graphics
- **Bateria**: Consumo e temperatura
- **Rede**: Bytes enviados/recebidos, latência

### Performance Metrics
- **FPS**: Frames per second (60fps target)
- **Frame Drops**: Quantidade de frames perdidos
- **Jank**: Frames com > 16ms render time
- **Response Time**: Tempo de resposta de ações

### Test Metrics
- **Throughput**: Ações/segundo
- **Concurrent Users**: Usuários simultâneos
- **Error Rate**: Taxa de erro
- **Success Rate**: Taxa de sucesso

## 🔧 Configuração Avançada

### Distribuição de Carga Customizada

```yaml
virtual_users:
  pattern: custom
  stages:
    - users: 10
      duration: 60
    - users: 50
      duration: 120
    - users: 100
      duration: 180
    - users: 50
      duration: 60
    - users: 0
      duration: 30
```

### Múltiplos Devices

```yaml
platforms:
  - android:
      devices:
        - "emulator-5554"
        - "emulator-5556"
        - "real-device-serial"
      app: "./app-release.apk"
      distribute: "round-robin"  # or "random", "load-balance"
```

### Plugins Customizados

```python
from mobileloadx.plugins import MetricsPlugin

class CustomMetricsPlugin(MetricsPlugin):
    def collect(self, context):
        # Sua lógica customizada
        return {
            "custom_metric": value
        }

test.add_plugin(CustomMetricsPlugin())
```

## 🎯 Integração CI/CD

### GitHub Actions

```yaml
- name: Run Performance Tests
  run: |
    mobileloadx run config.yaml --ci-mode
    
- name: Check Thresholds
  run: |
    mobileloadx verify --fail-on-threshold
    
- name: Upload Results
  uses: actions/upload-artifact@v3
  with:
    name: performance-results
    path: ./results/
```

## 📚 Documentação

- [Guia Completo](./docs/GUIDE.md)
- [API Reference](./docs/API.md)
- [Exemplos](./examples/)
- [Troubleshooting](./docs/TROUBLESHOOTING.md)
 - [Motivação do Projeto](./docs/PROJECT_MOTIVATION.md) — contexto e justificativa para a criação do framework

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

Construído sobre os ombros de gigantes:
- Appium
- Selenium
- adb (Android Debug Bridge)
- libimobiledevice
