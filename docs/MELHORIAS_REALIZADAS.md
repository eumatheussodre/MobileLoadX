# Melhorias Realizadas - MobileLoadX

Documento que registra as melhorias implementadas no projeto, com foco em consistência do formato de configuração, documentação, empacotamento, métricas e exemplo de uso.

---

## 1. Alinhamento do schema ao formato YAML (README / loader)

### Problema
O **SchemaValidator** exigia campos na raiz (`name`, `duration`, `virtual_users` como número), enquanto o **ConfigLoader** e o exemplo do README usavam o formato com blocos `test` e `virtual_users` (objeto). Um config igual ao do README falhava na validação.

### O que foi feito
- **`mobileloadx/schema_validator.py`**
  - Schema atualizado para o formato oficial:
    - **test**: objeto com `name` e `duration` (obrigatórios).
    - **virtual_users**: objeto com `max` (obrigatório), `initial` e `ramp_up_time` (opcionais).
    - **platforms**: lista em que cada item é um objeto com uma única chave `android` ou `ios` (ex.: `{ android: { app, device, devices, capabilities } }`).
    - **scenarios**: lista com `name`, `weight` e `actions`.
    - **metrics** e **thresholds**: opcionais, com estrutura documentada.
  - Validação extra para garantir que cada item de `platforms` tenha exatamente uma chave `android` ou `ios` e que exista `app`.
  - Suporte a validação de campos obrigatórios em objetos aninhados (ex.: `test.name`, `test.duration`).

- **`mobileloadx/cli.py`**
  - Comando `validate` passou a exibir o resumo usando `config.get('test', {})` e `config.get('virtual_users', {})`, mostrando nome, duração e usuários máximos corretamente.

### Resultado
O arquivo de configuração do README e o gerado por `mobileloadx init` passam na validação sem alterações.

---

## 2. Correções em pyproject.toml e setup.py

### Problema
- **pyproject.toml**: `packages = ["mobileloadx"]` não incluía subpacotes (`mobileloadx.core`, `mobileloadx.metrics`, etc.), podendo quebrar a instalação.
- **setup.py**: `python_requires=">=3.8"` e inclusão de `pytest` em `install_requires`; dependências desalinhadas em relação ao pyproject.

### O que foi feito
- **`pyproject.toml`**
  - Substituído `[tool.setuptools] packages = ["mobileloadx"]` por:
    ```ini
    [tool.setuptools.packages.find]
    where = ["."]
    include = ["mobileloadx*"]
    ```
  - Mantido `requires-python = ">=3.9"`.

- **`setup.py`**
  - `python_requires=">=3.9"` (alinhado ao pyproject).
  - **pytest** removido de `install_requires` (permanece apenas em extras de desenvolvimento).
  - Inclusão em `install_requires` de: `requests`, `Jinja2`, `python-dotenv`.
  - Classifiers atualizados para Python 3.9–3.12.

### Resultado
Instalação via `pip install -e .` ou `pip install mobileloadx` inclui todos os módulos do pacote; dependências de produção e desenvolvimento estão consistentes.

---

## 3. Uso de `metrics.interval` e `metrics.collect` no YAML

### Problema
O exemplo do README definia `metrics.collect` e `metrics.interval`, mas o **LoadTest** e o **MetricsCollector** não utilizavam essa seção; o intervalo era fixo e não havia filtro por tipo de métrica.

### O que foi feito
- **`mobileloadx/metrics/collector.py`**
  - Novo parâmetro **collect** no construtor: lista de métricas a coletar (`cpu`, `memory`, `battery`, `network`, `fps`). Se `None` ou vazia, coleta todas as disponíveis.
  - Constante **AVAILABLE_METRICS** documentando métricas suportadas; `fps` tratado como planejado (ainda não implementado).
  - Em `_collect_device_metrics()`, apenas as chaves presentes em `self.collect` são preenchidas.
  - Ajuste em `_calculate_summary()` para não quebrar quando `memory` não for coletada.

- **`mobileloadx/core/load_test.py`**
  - Em `_load_from_config()`, leitura de `metrics.interval` e `metrics.collect` e criação do **MetricsCollector** com esses valores:
    ```python
    metrics_config = config.get('metrics', {})
    interval = metrics_config.get('interval', 1.0)
    collect = metrics_config.get('collect')
    self.metrics_collector = MetricsCollector(interval=interval, collect=collect)
    ```

### Resultado
O bloco `metrics` do YAML passa a controlar intervalo e quais métricas são coletadas, conforme documentado no README.

---

## 4. Documentação criada (GUIDE, API, TROUBLESHOOTING)

### Problema
O README referenciava `docs/GUIDE.md`, `docs/API.md` e `docs/TROUBLESHOOTING.md`, que não existiam.

### O que foi feito
- **`docs/GUIDE.md`**
  - Instalação e requisitos.
  - Estrutura do arquivo de configuração (test, virtual_users, platforms, scenarios, metrics, thresholds).
  - Comandos principais (run, validate, report, verify, init).
  - Uso em Python (LoadTest, Scenario).
  - Integração CI/CD e próximos passos.

- **`docs/API.md`**
  - Referência das classes e métodos: LoadTest, Scenario, VirtualUser, Action, MetricsCollector, TestResults, ReportGenerator, ConfigLoader, SchemaValidator, plugins.

- **`docs/TROUBLESHOOTING.md`**
  - Erros de validação (test, virtual_users, platforms).
  - Conexão Appium e device (Android/iOS).
  - Execução do teste (plataforma/cenário, timeout, métricas).
  - Relatórios e verify (paths, fail-on-threshold).
  - Instalação e ambiente.

- **README.md**
  - Links para GUIDE, API e TROUBLESHOOTING mantidos; adicionado link para o exemplo em `examples/example_load_test/`; adicionado link para este documento (Melhorias Realizadas).

### Resultado
Todos os links de documentação do README passam a apontar para arquivos existentes e úteis.

---

## 5. Comandos CLI (report --open e verify --fail-on-threshold)

### Verificação
Os comandos **`mobileloadx report --open`** e **`mobileloadx verify --fail-on-threshold`** já estavam implementados no CLI. Nenhuma alteração foi necessária; apenas confirmado o comportamento documentado.

---

## 6. CI (GitHub Actions)

### O que foi feito
- **`.github/workflows/tests.yml`**
  - Job principal de testes: instalação alterada de `pip install -r requirements.txt` para **`pip install -e ".[dev]"`**, garantindo instalação do pacote em modo editável com dependências de desenvolvimento.
  - Novo job **validate-config**:
    - Roda em Ubuntu com Python 3.11.
    - Instala o pacote com `pip install -e .`.
    - Executa **`mobileloadx validate examples/example_load_test/config.yaml`** para garantir que o config de exemplo continua válido a cada push/PR.

### Resultado
O pipeline passa a instalar o projeto corretamente e a validar o exemplo de configuração automaticamente.

---

## 7. Exemplo funcional (config + README)

### O que foi feito
- **`examples/example_load_test/config.yaml`**
  - Arquivo de configuração de exemplo no formato oficial:
    - test (name, duration).
    - virtual_users (initial, max, ramp_up_time).
    - platforms com um item android (app, device, capabilities).
    - Dois cenários (Login e Navegar) com ações no formato tap/input/wait/scroll.
    - metrics (collect, interval) e thresholds.

- **`examples/example_load_test/README.md`**
  - Explicação da estrutura do `config.yaml`.
  - Passos: validar (sem device), ajustar para o ambiente, executar teste, ver relatórios e verify.
  - Exemplo equivalente em Python (LoadTest + Scenario + add_platform/add_scenario/set_threshold e run).
  - Links para GUIDE, API e TROUBLESHOOTING.

### Resultado
Exemplo completo e reproduzível; usuários podem validar sem Appium e, com ambiente configurado, rodar o teste e seguir a documentação.

---

## 8. Testes atualizados e novos

### O que foi feito
- **`tests/conftest.py`**
  - Fixture **config_dict** atualizada para o formato oficial: `test`, `virtual_users` (objeto), `platforms` como lista de `{ android: { app, device, devices, capabilities } }`, `scenarios` com ações no formato `{ tap: { id: "..." } }`, `thresholds` com `error_rate_max`.

- **`tests/test_config_loader.py`**
  - Asserções alteradas para ler do novo formato: `config['test']['name']`, `config['test']['duration']`, `config['virtual_users']['max']`, e `config['test']['name']` nos testes de save.

- **`tests/test_load_test.py`**
  - Novo teste **test_load_from_config_full**: carrega config a partir de `yaml_config_file` (novo formato) e verifica name, duration, max_virtual_users, ramp_up_time, platforms, scenarios e metrics_collector (interval e collect).

- **`tests/test_schema_validator.py`** (novo arquivo)
  - **test_validate_accepts_new_format**: aceita config com test, virtual_users, platforms (android/ios), scenarios.
  - **test_validate_rejects_missing_test**: rejeita config sem bloco test.
  - **test_validate_rejects_missing_virtual_users_max**: rejeita virtual_users sem max.
  - **test_validate_rejects_invalid_platform_key**: rejeita chave que não seja android ou ios em platforms.
  - **test_validate_file_example_config**: valida o arquivo `examples/example_load_test/config.yaml`.

### Resultado
Todos os testes passam com o formato oficial de configuração; o schema é coberto por testes e o exemplo é validado automaticamente nos testes.

---

## Resumo

| Área              | Melhoria                                                                 |
|-------------------|--------------------------------------------------------------------------|
| Schema            | Alinhado ao formato README/loader (test, virtual_users, platforms)      |
| Empacotamento     | pyproject com find packages; setup.py sem pytest em install_requires     |
| Métricas          | metrics.interval e metrics.collect aplicados no LoadTest e Collector    |
| Documentação      | docs/GUIDE.md, API.md, TROUBLESHOOTING.md criados; README atualizado    |
| CLI               | report --open e verify --fail-on-threshold já existentes, confirmados  |
| CI                | pip install -e ".[dev]"; job validate-config para exemplo              |
| Exemplo           | examples/example_load_test/config.yaml + README com uso e Python         |
| Testes            | conftest e config_loader atualizados; load_test e schema_validator novos |

Essas melhorias foram realizadas para tornar o projeto mais consistente, documentado e fácil de usar e manter.

---

## Como verificar se as melhorias surtiram efeito

Para testar no seu ambiente se cada melhoria está realmente ativa, use o guia **[Como testar as melhorias](./COMO_TESTAR_MELHORIAS.md)**. Lá você encontra comandos e scripts (PowerShell e Python) para:

- Validar config no formato novo (`mobileloadx validate`)
- Confirmar empacotamento e imports dos subpacotes
- Verificar se `metrics.interval` e `metrics.collect` são aplicados
- Checar documentação e CLI
- Rodar os testes (`pytest`) e um checklist resumido
