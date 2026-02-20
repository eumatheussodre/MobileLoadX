# Como testar se as melhorias surtiram efeito

Este guia traz **passos práticos** para conferir, no seu ambiente, se cada melhoria implementada está funcionando. Execute os comandos **na raiz do projeto** (`d:\Projetos\MobileLoadX` ou onde estiver o `pyproject.toml`).

---

## Pré-requisito: ambiente

Na raiz do projeto:

```powershell
cd d:\Projetos\MobileLoadX
```

### Opção A: Usar ambiente virtual (venv)

**1. Criar o venv (só na primeira vez):**
```powershell
python -m venv .venv
```

**2. Ativar o venv:**

- **No PowerShell:** use o operador `&` para executar o script:
  ```powershell
  & .\.venv\Scripts\Activate.ps1
  ```
  Se der erro de política de execução, rode **uma vez** (pode ser em outro terminal):
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

- **No CMD (Prompt de Comando):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

**3. Garantir pip no venv (se der "No module named pip" na instalação):**
```powershell
python -m ensurepip --upgrade
```

**4. Instalar o pacote:**
```powershell
pip install -e ".[dev]"
```

Se der erro *"No module named pip"* na etapa de *Running setup.py develop*, use **instalação normal** (sem editável):
```powershell
pip install ".[dev]"
```
Assim o pacote é instalado e você pode rodar `mobileloadx` e `pytest`. Para aplicar mudanças no código, execute `pip install ".[dev]"` de novo.

### Opção B: Sem venv (usar o Python do sistema)

Se a ativação do venv falhar ou preferir não usar:

```powershell
cd d:\Projetos\MobileLoadX
pip install -e ".[dev]"
```

---

**Sucesso:** ao rodar `mobileloadx --version` e ver a versão (ex.: 1.0.0), o **empacotamento** (melhoria 2) está ok.

---

## 1. Schema e formato YAML (melhoria 1)

### 1.1 Validar config no formato novo (test + virtual_users)

Use um config que já esteja no formato oficial, por exemplo o do e-commerce:

```powershell
mobileloadx validate examples\ecommerce_test.yaml
```

**Efeito esperado:** saída com `✅ Configuração válida!` e um resumo com **Nome**, **Duração**, **Usuários máx**, **Plataformas**, **Cenários**.

Se aparecer algo como “Campo obrigatório ausente: test” ou “virtual_users”, o schema ainda está no formato antigo.

### 1.2 Validar config gerado por `init`

```powershell
mobileloadx init
# Quando perguntar se pode sobrescrever, pode responder N se já existir config.yaml

mobileloadx validate config.yaml
```

**Efeito esperado:** `✅ Configuração válida!` e o resumo mostrando nome “My Performance Test”, duração e usuários a partir de `test` e `virtual_users`.

### 1.3 Rejeição de config inválido

Crie um YAML que **não** tenha o bloco `test`:

```powershell
# Criar um arquivo de teste inválido
@"
virtual_users:
  max: 5
platforms:
  - android:
      app: "./app.apk"
scenarios:
  - name: "X"
    actions: []
"@ | Out-File -Encoding utf8 invalid.yaml

mobileloadx validate invalid.yaml
```

**Efeito esperado:** `❌ Erros encontrados` e mensagem indicando ausência de `test` (ou campo obrigatório). Depois pode apagar: `del invalid.yaml`.

---

## 2. Empacotamento (melhoria 2)

### 2.1 Imports de todos os subpacotes

```powershell
python -c "
from mobileloadx import LoadTest, Scenario, VirtualUser, Action, MetricsCollector, ReportGenerator
from mobileloadx.core.load_test import LoadTest as L2
from mobileloadx.metrics.collector import MetricsCollector as M2
from mobileloadx.config.loader import ConfigLoader
from mobileloadx.schema_validator import SchemaValidator
print('OK: todos os subpacotes importáveis')
"
```

**Efeito esperado:** `OK: todos os subpacotes importáveis`. Se der `ModuleNotFoundError` para `mobileloadx.core` ou `mobileloadx.metrics`, o `pyproject.toml` pode não estar com `setuptools.packages.find` configurado.

### 2.2 Pytest não está em dependências de produção

```powershell
pip show mobileloadx
```

**Efeito esperado:** na lista de “Requires” **não** deve aparecer `pytest`. (Pytest deve vir só de `pip install -e ".[dev]"`.)

---

## 3. Métricas no YAML (melhoria 3)

### 3.1 LoadTest lê `metrics.interval` e `metrics.collect`

```powershell
python -c "
from mobileloadx.core.load_test import LoadTest
from pathlib import Path
# Usar um config que tenha bloco metrics (ex.: ecommerce_test.yaml)
cfg = 'examples/ecommerce_test.yaml'
if Path(cfg).exists():
    t = LoadTest('X', config_file=cfg)
    c = t.metrics_collector
    print('interval:', c.interval)
    print('collect:', c.collect)
    print('OK: metrics do YAML aplicados' if c.interval and c.collect else 'FALHA')
else:
    print('Arquivo não encontrado, use outro config com metrics')
"
```

**Efeito esperado:** impressão de `interval` (ex.: 2) e `collect` (ex.: lista com `cpu`, `memory`, etc.) e `OK: metrics do YAML aplicados`. Se `interval` for sempre 1 e `collect` não refletir o YAML, a melhoria 3 não está ativa.

---

## 4. Documentação (melhoria 4)

Confira se os arquivos existem e têm conteúdo:

```powershell
Get-ChildItem docs\GUIDE.md, docs\API.md, docs\TROUBLESHOOTING.md | ForEach-Object { "$($_.Name): $($_.Length) bytes" }
```

**Efeito esperado:** os três arquivos listados com tamanho > 0. Abra um deles no editor e confira se o conteúdo faz sentido.

---

## 5. CLI report e verify (melhoria 5)

### 5.1 Ajuda dos comandos

```powershell
mobileloadx report --help
mobileloadx verify --help
```

**Efeito esperado:**  
- `report`: opção `--open` e `--results-dir`.  
- `verify`: opção `--fail-on-threshold` e `--results-dir`.

### 5.2 Report --open (após um run que gera resultados)

Só faz sentido depois de ter executado um teste e gerado `results/report.html`:

```powershell
# Opcional: rodar um teste (precisa de Appium/device) e depois:
# mobileloadx report --results-dir ./results --open
```

Se você já tiver uma pasta `results` com `report.html`, use `mobileloadx report --results-dir ./results --open` e confira se o navegador abre o HTML.

---

## 6. Testes automatizados (melhorias 6 e 8)

### 6.1 Rodar todos os testes

```powershell
pytest tests\ -v --tb=short
```

**Efeito esperado:** todos os testes passando (incluindo `test_config_loader`, `test_load_test`, `test_schema_validator`). Falhas em `test_load_from_config_full` ou `test_validate_accepts_new_format` indicariam regressão nas melhorias 1 ou 8.

### 6.2 Rodar só os testes do schema e do config

```powershell
pytest tests\test_schema_validator.py tests\test_config_loader.py tests\test_load_test.py -v --tb=short
```

**Efeito esperado:** todos passando. O teste `test_validate_file_example_config` pode ser ignorado (skip) se o arquivo `examples/example_load_test/config.yaml` não existir; os outros devem passar.

### 6.3 Coverage (opcional)

```powershell
pytest tests\ -v --cov=mobileloadx --cov-report=term-missing
```

**Efeito esperado:** relatório de cobertura; módulos como `schema_validator`, `config.loader`, `core.load_test`, `metrics.collector` aparecem cobertos.

---

## 7. Resumo rápido (checklist)

| O que testar | Comando / ação | Sucesso se… |
|--------------|----------------|-------------|
| Schema (formato novo) | `mobileloadx validate examples\ecommerce_test.yaml` | ✅ Configuração válida + resumo com Nome/Duração/Usuários |
| Config do init | `mobileloadx init` e `mobileloadx validate config.yaml` | ✅ Configuração válida |
| Empacotamento | `pip install -e ".[dev]"` e `python -c "from mobileloadx.core.load_test import LoadTest"` | Sem ModuleNotFoundError |
| Métricas no YAML | Script Python que cria LoadTest com config_file e lê metrics_collector.interval/collect | interval e collect batem com o YAML |
| Docs | Existência de `docs\GUIDE.md`, `API.md`, `TROUBLESHOOTING.md` | Arquivos existem e têm conteúdo |
| CLI | `mobileloadx report --help` e `mobileloadx verify --help` | Opções `--open` e `--fail-on-threshold` aparecem |
| Testes | `pytest tests\ -v` | Todos passam |

Se todos os itens acima derem o resultado esperado, as melhorias implementadas **estão surtindo efeito** no seu ambiente.
