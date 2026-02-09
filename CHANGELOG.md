# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2026-02-09

### 🎉 Lançamento Inicial

#### Adicionado
- ✨ Framework core de teste de carga mobile
- ✨ Suporte cross-platform (Android/iOS)
- ✨ Simulação de múltiplos usuários simultâneos
- ✨ Sistema de cenários com ações configuráveis
- ✨ Coleta de métricas:
  - CPU usage
  - Memory (RAM, Heap, Native, Graphics)
  - Battery (level, temperature)
  - Network (bytes in/out)
  - FPS e frame drops
- ✨ Geração de relatórios:
  - HTML interativo com gráficos
  - JSON estruturado
  - CSV para análise
- ✨ Sistema de thresholds configuráveis
- ✨ CLI completa (`mobileloadx`)
- ✨ Python API fluente
- ✨ Configuração via YAML/JSON
- ✨ Suporte a ramp-up/ramp-down de usuários
- ✨ Múltiplos devices por teste
- ✨ Distribuição de carga round-robin
- ✨ Logging estruturado
- ✨ Integração CI/CD ready

#### Documentação
- 📚 README completo com exemplos
- 📚 Análise de gaps do mercado
- 📚 Guia de instalação
- 📚 Quick start
- 📚 Arquitetura técnica
- 📚 Guia de contribuição
- 📚 Exemplos práticos

#### Ações Suportadas
- `tap`: Click em elementos
- `input`: Entrada de texto
- `scroll`: Scroll vertical/horizontal
- `swipe`: Gestures customizados
- `wait`: Esperas explícitas
- `back`: Navegação reversa

#### Locators Suportados
- `id`: Resource ID / Accessibility ID
- `xpath`: XPath expressions
- `accessibility_id`: Accessibility identifiers
- `class_name`: Class name selectors

### Roadmap Futuro

#### [1.1.0] - Planejado
- [ ] Suporte a gestures avançados (pinch, long-press)
- [ ] Network throttling simulation
- [ ] Screenshot on error
- [ ] Video recording
- [ ] Memory leak detection

#### [1.5.0] - Planejado
- [ ] Real-time dashboard
- [ ] Visual regression testing
- [ ] AI-powered analysis
- [ ] Cloud device integration

#### [2.0.0] - Futuro
- [ ] Distributed testing
- [ ] Selenium Grid integration
- [ ] Flutter/React Native native support
- [ ] Session replay
- [ ] Advanced ML analytics

---

## Convenções

### Tipos de Mudanças
- `Adicionado` para novas funcionalidades
- `Modificado` para mudanças em funcionalidades existentes
- `Descontinuado` para funcionalidades que serão removidas
- `Removido` para funcionalidades removidas
- `Corrigido` para correções de bugs
- `Segurança` para vulnerabilidades

### Formato de Versão
- **Major (X.0.0)**: Mudanças incompatíveis na API
- **Minor (0.X.0)**: Novas funcionalidades compatíveis
- **Patch (0.0.X)**: Correções de bugs compatíveis
