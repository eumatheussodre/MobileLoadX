# 🚀 MobileLoadX - Getting Started

Parabéns! Você acabou de criar um framework completo de teste de performance mobile.

## ✅ O que foi criado?

### 🎯 Framework Core
- ✨ **LoadTest Engine**: Orquestrador de testes com suporte a múltiplos usuários
- ✨ **Virtual Users**: Simulação de usuários simultâneos
- ✨ **Scenarios & Actions**: DSL para definir workflows de teste
- ✨ **Metrics Collector**: Coleta de CPU, memória, bateria, rede, FPS
- ✨ **Report Generator**: Relatórios HTML, JSON e CSV

### 📚 Documentação Completa
- 📖 README com exemplos e guias
- 📖 Análise de gaps do mercado
- 📖 Guia de instalação
- 📖 Quick start (5 minutos)
- 📖 Arquitetura técnica
- 📖 Comparação com concorrentes
- 📖 Guia de contribuição

### 🎨 Diagramas
- 🔷 Diagrama de arquitetura (Mermaid)
- 🔷 Diagrama de fluxo de execução (Sequence)

### 💻 Exemplos Práticos
- 📝 Configuração YAML completa (e-commerce)
- 📝 API Python básica
- 📝 Multi-device test

## 🎬 Próximos Passos

### 1. Instale as Dependências

```bash
cd c:\Projetos\ProjetoPerformanceApp
pip install -r requirements.txt
```

### 2. Instale o Appium

```bash
npm install -g appium
appium driver install uiautomator2
appium driver install xcuitest
```

### 3. Inicie o Appium Server

```bash
appium
```

### 4. Configure seu Primeiro Teste

Edite o arquivo `examples/ecommerce_test.yaml` com:
- Caminho do seu app (`.apk` ou `.app`)
- ID do seu device/emulador
- IDs dos elementos da UI

### 5. Execute um Teste de Exemplo

```bash
# Via CLI (quando instalado)
python -m mobileloadx.cli run examples/ecommerce_test.yaml

# Ou via Python
python examples/basic_test.py
```

## 📖 Leia a Documentação

### Para Usuários
1. [README.md](README.md) - Comece aqui!
2. [docs/QUICKSTART.md](docs/QUICKSTART.md) - Tutorial de 5 minutos
3. [docs/INSTALLATION.md](docs/INSTALLATION.md) - Setup detalhado

### Para Desenvolvedores
1. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Entenda a arquitetura
2. [CONTRIBUTING.md](CONTRIBUTING.md) - Como contribuir
3. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Resumo executivo

### Análise de Mercado
1. [MARKET_GAPS.md](MARKET_GAPS.md) - Gaps do mercado
2. [docs/COMPARISON.md](docs/COMPARISON.md) - Comparação com concorrentes

## 🎯 Casos de Uso Comuns

### Teste de Login com 10 Usuários

```python
from mobileloadx import LoadTest, Scenario

scenario = Scenario("Login")
scenario.tap(id="username")
scenario.input("user@test.com")
scenario.tap(id="password")
scenario.input("senha123")
scenario.tap(id="loginBtn")

test = LoadTest(
    name="Login Performance",
    duration=60,
    virtual_users=10,
    ramp_up_time=10
)

test.add_platform(
    platform="android",
    app="./app.apk",
    device="emulator-5554"
)

test.add_scenario(scenario)

results = test.run()
print(f"Taxa de sucesso: {results.success_rate:.1f}%")
print(f"P95: {results.response_time_p95:.0f}ms")
```

### Teste com YAML

```yaml
test:
  name: "My Test"
  duration: 120

virtual_users:
  max: 20
  ramp_up_time: 30

platforms:
  - android:
      app: "./app.apk"
      device: "emulator-5554"

scenarios:
  - name: "Main Flow"
    weight: 100
    actions:
      - tap: {id: "button"}
      - wait: {timeout: 2}
      - scroll: {direction: "down", duration: 1}

thresholds:
  cpu_max: 80
  response_time_p95: 2000
```

Execute:
```bash
python -m mobileloadx.cli run config.yaml
```

## 🛠️ Desenvolvimento

### Instalar em modo desenvolvimento

```bash
pip install -e .
```

### Executar testes (quando implementados)

```bash
pytest
pytest --cov=mobileloadx
```

### Code formatting

```bash
black mobileloadx/
flake8 mobileloadx/
```

## 🌟 Recursos-Chave

### ✅ Diferenciais
- **Múltiplos usuários simultâneos** (1 a 1000+)
- **Cross-platform** (mesmo código Android/iOS)
- **Métricas detalhadas** (CPU, RAM, bateria, rede, FPS)
- **Configuração simples** (YAML declarativo)
- **Relatórios profissionais** (HTML interativo)
- **CI/CD ready** (thresholds automáticos)

### 📊 Métricas Coletadas
- CPU usage (app + sistema)
- Memória (RAM, Heap, Native, Graphics)
- Bateria (nível, temperatura, voltage)
- Rede (bytes in/out, latência)
- FPS e frame drops
- Tempo de resposta (min, max, média, P50, P95, P99)
- Taxa de sucesso/erro

### 🎨 Formatos de Saída
- **HTML**: Relatório interativo com gráficos Chart.js
- **JSON**: Dados estruturados para integração
- **CSV**: Análise em Excel/Python/Pandas

## 🔧 Troubleshooting

### Erro: "Module not found"
```bash
pip install -r requirements.txt
```

### Erro: "Appium not running"
```bash
# Verificar
curl http://localhost:4723/status

# Reiniciar
appium
```

### Erro: "Device not found"
```bash
# Android
adb devices

# iOS
xcrun simctl list devices
```

## 🤝 Contribuindo

Contributions são bem-vindas! Veja [CONTRIBUTING.md](CONTRIBUTING.md).

### Áreas que precisam de ajuda:
- 📊 Dashboard em tempo real
- 🤖 Mais integrações CI/CD
- 📱 Suporte a mais plataformas
- 🧪 Mais tipos de ações
- 📈 Visualizações avançadas
- ✅ Testes unitários

## 📞 Suporte

- 📧 Email: team@mobileloadx.dev
- 🐛 Issues: GitHub Issues
- 💬 Discussões: GitHub Discussions

## 📜 Licença

MIT License - use livremente em projetos comerciais e open source!

---

## 🎉 Parabéns!

Você tem em mãos um framework completo e profissional de teste de performance mobile!

**Próximos passos sugeridos:**
1. ✅ Instale as dependências
2. ✅ Leia o [README.md](README.md)
3. ✅ Execute um exemplo
4. ✅ Adapte para seu app
5. ✅ Compartilhe nos resultados!

**Happy Testing! 🚀📱**
