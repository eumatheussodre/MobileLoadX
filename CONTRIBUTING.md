# 🤝 Contribuindo para MobileLoadX

Obrigado por considerar contribuir para o MobileLoadX! Este documento fornece orientações para diferentes tipos de contribuições.

## 📋 Código de Conduta

- Seja respeitoso e inclusivo
- Aceite críticas construtivas
- Foque no que é melhor para a comunidade
- Mostre empatia com outros membros

## 🚀 Como Contribuir

### Reportar Bugs

Abra uma issue com:
- Descrição clara do bug
- Passos para reproduzir
- Comportamento esperado vs atual
- Ambiente (OS, Python version, Appium version)
- Logs relevantes (use `--verbose`)

### Sugerir Features

Abra uma issue de feature request com:
- Descrição clara da funcionalidade
- Casos de uso
- Exemplos de como seria usado
- Por que é importante

### Contribuir com Código

1. **Fork o repositório**

2. **Clone seu fork**
   ```bash
   git clone https://github.com/seu-usuario/mobileloadx.git
   cd mobileloadx
   ```

3. **Crie um branch**
   ```bash
   git checkout -b feature/minha-feature
   ```

4. **Configure ambiente de desenvolvimento**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

5. **Faça suas alterações**
   - Siga o estilo de código existente
   - Adicione testes
   - Atualize documentação

6. **Execute testes**
   ```bash
   pytest
   pytest --cov=mobileloadx  # Com coverage
   ```

7. **Execute linters**
   ```bash
   black .
   flake8 mobileloadx
   mypy mobileloadx
   ```

8. **Commit suas mudanças**
   ```bash
   git add .
   git commit -m "feat: adiciona suporte para X"
   ```

   Formato de commit:
   - `feat:` Nova funcionalidade
   - `fix:` Correção de bug
   - `docs:` Documentação
   - `test:` Testes
   - `refactor:` Refatoração
   - `perf:` Melhoria de performance
   - `chore:` Tarefas diversas

9. **Push e abra Pull Request**
   ```bash
   git push origin feature/minha-feature
   ```

## 📝 Guia de Estilo

### Python

- Siga PEP 8
- Use type hints
- Docstrings para classes e funções públicas
- Máximo 100 caracteres por linha

```python
def my_function(param: str, count: int = 10) -> List[str]:
    """
    Descrição breve da função.
    
    Args:
        param: Descrição do parâmetro
        count: Descrição com valor padrão
    
    Returns:
        Lista de strings resultantes
    
    Raises:
        ValueError: Quando param é inválido
    """
    pass
```

### Testes

- Use `pytest`
- Coverage mínimo de 80%
- Nomeação: `test_<funcao>_<cenario>_<resultado_esperado>`

```python
def test_load_test_run_success():
    """Testa execução bem-sucedida de LoadTest"""
    # Arrange
    test = LoadTest(name="Test", duration=10)
    
    # Act
    result = test.run()
    
    # Assert
    assert result.success_rate > 0
```

### Documentação

- README.md para overview
- Docstrings para código
- Markdown para docs/
- Exemplos práticos

## 🎯 Áreas Prioritárias

### Alto Impacto
- 🔴 Suporte a distributed testing
- 🔴 Dashboard em tempo real
- 🔴 Melhoria de performance

### Média Prioridade
- 🟡 Mais integrações CI/CD
- 🟡 Suporte a mais plataformas
- 🟡 Análises avançadas

### Melhorias Contínuas
- 🟢 Documentação
- 🟢 Exemplos
- 🟢 Testes

## 🏗️ Estrutura do Projeto

```
mobileloadx/
├── mobileloadx/           # Código-fonte
│   ├── core/             # Engine core
│   ├── metrics/          # Coleta de métricas
│   ├── config/           # Configuração
│   ├── reporting/        # Geração de relatórios
│   ├── plugins/          # Sistema de plugins
│   └── cli.py            # Interface CLI
├── tests/                # Testes unitários
├── examples/             # Exemplos de uso
├── docs/                 # Documentação
└── setup.py              # Setup do pacote
```

## 📚 Recursos

- [Documentação Appium](https://appium.io/docs/en/latest/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)
- [PEP 8 Style Guide](https://pep8.org/)

## ❓ Dúvidas

Abra uma issue com a tag `question` ou entre em contato:
- Email: team@mobileloadx.dev
- Discord: [Link]

## 📜 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a MIT License.
