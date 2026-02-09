# Projeto: Performance App

## Visão geral
Este projeto fornece uma estrutura leve para testes de carga focada em cenários para aplicações móveis e APIs. Ele reúne componentes para definir cenários, executar usuários virtuais, coletar métricas e gerar relatórios.

## Por que este projeto foi criado
- Demandas reais por testes de carga reproduzíveis e fáceis de configurar para equipes de QA e engenharia.
- Necessidade de uma ferramenta que combine simplicidade para começar com capacidade de extensão para cenários complexos.
- Facilitar experimentos comparativos entre diferentes arquiteturas e pontos de infraestrutura (ex.: mobile vs web backends).

## Objetivos
- Oferecer um fluxo claro para definir cenários de carga e executar testes locais ou em CI.
- Coletar métricas importantes (latência, throughput, erros) e gerar relatórios legíveis.
- Permitir que engenheiros expandam ações e coletores sem modificar o core.

## Público-alvo
- Engenheiros de performance e QA
- Desenvolvedores backend/mobile que precisam validar escalabilidade
- Equipes pequenas que queiram iniciar testes de carga sem ferramentas complexas

## Principais funcionalidades
- Definição de cenários e usuários virtuais (`core/scenario.py`, `core/virtual_user.py`)
- Execução de testes e orquestração (`core/load_test.py`)
- Coleta de métricas configurável (`metrics/collector.py`)
- Geração de relatórios e resultados (`reporting/report_generator.py`, `reporting/results.py`)
- CLI básica e exemplos em `examples/`

## Arquitetura resumida
- `mobileloadx/` — pacote principal e CLI
- `core/` — lógica do teste e modelagem de cenários
- `metrics/` — coletores e agregação de métricas
- `reporting/` — geração de relatórios e exportação de resultados
- `examples/` — scripts demonstrativos e arquivos de configuração

## Como usar (rápido)
1. Instale dependências:

```bash
pip install -r requirements.txt
```

2. Rode um exemplo rápido:

```bash
python examples/basic_test.py
```

3. Verifique os relatórios gerados em `reporting/` ou no diretório de saída configurado.

> Observação: adapte os exemplos em `examples/` para suas rotas/endpoints e credenciais.

## Como contribuir
- Leia `CONTRIBUTING.md` para regras de contribuição.
- Para novas funcionalidades, prefira criar módulos em `core/`, `metrics/` ou `reporting/` e adicionar testes mínimos.

## Licença
Consulte o arquivo `LICENSE` na raiz do repositório.

---

Se quiser, eu atualizo o `README.md` para apontar para esta documentação e adiciono um sumário resumido.
