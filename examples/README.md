# Exemplos de Uso - MobileLoadX

Este diretório contém exemplos práticos de como usar MobileLoadX para testar aplicações mobile.

## 📂 Arquivos

### 1. `test_real_apk.py` - Script para testar APK real

Script Python prático para testar um APK real em emulador ou device.

#### Instalação de dependências

```bash
npm install -g appium
appium  # Em outro terminal
```

#### Uso básico

```bash
# Teste básico simples
python test_real_apk.py --apk ./myapp.apk --device emulator-5554

# Com múltiplos usuários
python test_real_apk.py --apk ./myapp.apk --device emulator-5554 --users 5 --duration 300

# Com modo verbose/debug
python test_real_apk.py --apk ./myapp.apk --device emulator-5554 --verbose
```

#### Criar arquivo de configuração

```bash
# Gerar template de configuração
python test_real_apk.py \
  --create-config mytest.yaml \
  --apk ./myapp.apk \
  --device emulator-5554 \
  --name "Meu Teste" \
  --duration 600 \
  --users 10
```

#### Executar com arquivo de configuração

```bash
# Usar configuração YAML
python test_real_apk.py \
  --config mytest.yaml \
  --output ./results
```

#### Opções disponíveis

```
--apk PATH              Caminho do APK a testar
--device ID             ID do device (default: emulator-5554)
--config FILE           Arquivo de configuração YAML
--create-config FILE    Criar arquivo de configuração
--name TEXT             Nome do teste
--duration SECONDS      Duração do teste (default: 120)
--users NUM             Número de usuários virtuais (default: 1)
--output DIR            Diretório de saída (default: ./results)
--verbose, -v           Modo verbose com logs detalhados
```

---

### 2. `find_elements.py` - Descobrir IDs e XPath

Script para inspecionar elementos do APK e gerar XPath/IDs para usar na configuração.

#### Uso básico

```bash
# Listar todos os botões
python find_elements.py --type Button

# Procurar por texto
python find_elements.py --text "Login"

# Procurar por tipo de input
python find_elements.py --type EditText

# Mostrar todos os elementos
python find_elements.py --show-all
```

#### Com device específico

```bash
# Usar device real
python find_elements.py --device ZY123ABC --text "Submit"

# Com emulador
python find_elements.py --device emulator-5554 --type Button
```

#### Salvar resultado

```bash
# Salvar em arquivo
python find_elements.py --type Button --output buttons.txt
python find_elements.py --text "Login" --output login_elements.txt
```

#### Opções disponíveis

```
--device ID         ID do device (usa o conectado se não especificado)
--text TEXT         Procurar por texto
--type CLASS        Procurar por tipo (Button, EditText, CheckBox, etc)
--output FILE       Salvar resultado em arquivo
--show-all          Mostrar todos os elementos interativos
```

---

### 3. `real_apk_config.yaml` - Configuração de exemplo

Arquivo de exemplo com configuração completa para testar um APK real.

#### Usar como template

```bash
# Copiar template
cp real_apk_config.yaml mytest.yaml

# Editar com seu editor favorito
nano mytest.yaml  # ou code, vim, etc

# Validar
mobileloadx validate mytest.yaml --strict

# Executar
mobileloadx run mytest.yaml --verbose
```

#### Estrutura

```yaml
name: "Teste"              # Nome do teste
duration: 300              # Duração em segundos
virtual_users: 3           # Usuários virtuais
ramp_up_time: 30           # Tempo para rampar

platforms:                 # Plataformas
  - platform: android
    app: "/path/app.apk"   # Caminho do APK
    devices:               # Devices
      - emulator-5554
    capabilities:          # Capabilities do Appium
      appium_server_url: "http://localhost:4723"
      automationName: "UiAutomator2"

scenarios:                 # Cenários de teste
  - name: "Login"
    weight: 100            # Peso relativo
    actions:               # Ações
      - type: wait
        timeout: 2
      - type: tap
        id: "com.app:id/button"
      - type: input
        text: "email@example.com"

thresholds:                # Limites de sucesso
  response_time_p95: 2500
  error_rate: 0.05

metrics:                   # Métricas a coletar
  collect:
    - cpu
    - memory
  interval: 2
```

---

## 🚀 Fluxo Típico de Uso

### 1. Preparar ambiente

```bash
# Instalar Appium
npm install -g appium
appium &

# Conectar device/iniciar emulador
adb devices

# Instalar APK
adb install -r myapp.apk
```

### 2. Descobrir elementos

```bash
# Inspecionar app
python find_elements.py --device emulator-5554 --show-all

# Procurar por textos específicos
python find_elements.py --text "Login"
python find_elements.py --text "Submit"

# Salvar resultado
python find_elements.py --type Button --output buttons.txt
```

### 3. Criar configuração

```bash
# Opção A: Usar template
cp real_apk_config.yaml mytest.yaml
# Editar com os IDs e XPath descobertos

# Opção B: Gerar com script
python test_real_apk.py \
  --create-config mytest.yaml \
  --apk ./myapp.apk \
  --device emulator-5554
```

### 4. Validar configuração

```bash
mobileloadx validate mytest.yaml --strict
```

### 5. Executar teste

```bash
# Opção A: Usar CLI
mobileloadx run mytest.yaml --output-dir ./results --verbose

# Opção B: Usar script Python
python test_real_apk.py --config mytest.yaml --output ./results
```

### 6. Analisar resultados

```bash
# Ver relatório
mobileloadx report ./results --open

# Ou analisar JSON direto
cat ./results/report.json | python -m json.tool
```

---

## 📊 Exemplos de Ações

### Tap (clique)

```yaml
# Pelo ID
- type: tap
  id: "com.example.app:id/button"

# Pelo XPath
- type: tap
  xpath: "//android.widget.Button[@text='Login']"

# Pelo accessibility ID
- type: tap
  accessibility_id: "submit_button"
```

### Input (digitar)

```yaml
# Digitar em campo focado
- type: input
  text: "meu_email@example.com"

# Limpar e digitar
- type: tap
  id: "email_field"
- type: input
  text: "novo_email@example.com"
```

### Wait (esperar)

```yaml
# Esperar 2 segundos
- type: wait
  timeout: 2

# Esperar 5 segundos (mais comum entre telas)
- type: wait
  timeout: 5
```

### Scroll (rolar)

```yaml
# Scroll para baixo
- type: scroll
  direction: "down"
  duration: 1

# Scroll para cima
- type: scroll
  direction: "up"
  duration: 1.5
```

### Back (voltar)

```yaml
# Voltar (botão Android back)
- type: back
```

---

## 🐛 Troubleshooting

### "Element not found"

```bash
# Verificar se elemento ainda existe
python find_elements.py --device emulator-5554 --text "Login"

# Pode ser necessário refazer inspect depois de ação anterior
# Adicione wait antes do tap
```

### "Connection refused"

```bash
# Verificar Appium
curl http://localhost:4723/status

# Reiniciar Appium
pkill -f appium
appium
```

### "Device not found"

```bash
# Listar devices
adb devices

# Reiniciar adb
adb kill-server
adb start-server
```

### Elemento aparece mas não clica

```yaml
# Tentar diferentes formas de localizador
# ID é preferido (mais rápido)
- type: tap
  id: "com.app:id/button"

# Se não funcionar, tentar XPath
- type: tap
  xpath: "//android.widget.Button[@resource-id='com.app:id/button']"

# Adicionar wait antes
- type: wait
  timeout: 1
- type: tap
  id: "com.app:id/button"
```

---

## 📚 Recursos

- [Documentação - TESTING_REAL_APK.md](../docs/TESTING_REAL_APK.md)
- [Documentação - Plugins](../docs/PLUGINS.md)
- [Appium Documentation](http://appium.io/)
- [XPath Tutorial](https://www.w3schools.com/xml/xpath_intro.asp)

---

## 💡 Dicas

1. **Sempre testar em emulador primeiro** - Mais fácil de debugar
2. **Usar IDs instead of XPath** - Mais rápido e confiável
3. **Adicionar waits entre ações** - Evita race conditions
4. **Manter testes simples inicialmente** - Depois complexificar
5. **Usar --verbose para debug** - Ajuda a entender erros
6. **Coletar métricas com interval adequado** - Não impactar performance

---

## 📝 Licença

MIT - Veja LICENSE para detalhes
