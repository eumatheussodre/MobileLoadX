"""
Interface de linha de comando para MobileLoadX
"""

import click
import logging
import sys
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from .core.load_test import LoadTest
from .reporting.report_generator import ReportGenerator
from .schema_validator import SchemaValidator
from .logging_setup import setup_logging, get_logger
from .plugins.base import get_plugin_manager
from .config.loader import ConfigLoader


# Configurar logging
logger = get_logger('cli')


@click.group()
@click.version_option(version='1.0.0')
def main():
    """
    MobileLoadX - Framework de Performance Testing para Apps Mobile
    
    Simule múltiplos usuários simultâneos e colete métricas detalhadas
    de performance em aplicativos Android e iOS.
    """
    pass


@main.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--ci-mode', is_flag=True, help='Modo CI/CD (sem saída interativa)')
@click.option('--output-dir', type=click.Path(), default='./results', 
              help='Diretório para salvar resultados')
@click.option('--verbose', '-v', is_flag=True, help='Modo verbose')
def run(config_file, ci_mode, output_dir, verbose):
    """
    Executa um teste de carga a partir de arquivo de configuração
    
    \b
    Exemplo:
        mobileloadx run config.yaml
        mobileloadx run config.yaml --output-dir ./my-results --verbose
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        click.echo(f"🚀 Carregando configuração: {config_file}")
        
        # Criar teste a partir do arquivo de configuração
        test = LoadTest(name="CLI Test", config_file=config_file)
        
        click.echo(f"▶️  Iniciando teste: {test.name}")
        click.echo(f"   Usuários: {test.max_virtual_users} | Duração: {test.duration}s")
        
        # Executar teste
        results = test.run()
        
        # Criar diretório de saída
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Gerar relatórios
        click.echo("\n📄 Gerando relatórios...")
        generator = ReportGenerator(results)
        
        html_file = output_path / "report.html"
        json_file = output_path / "report.json"
        csv_file = output_path / "report.csv"
        
        generator.generate_html(str(html_file))
        generator.generate_json(str(json_file))
        generator.generate_csv(str(csv_file))
        
        # Exibir resumo
        click.echo("\n" + "="*60)
        click.echo("📊 RESULTADOS DO TESTE")
        click.echo("="*60)
        click.echo(f"Teste: {results.test_name}")
        click.echo(f"Duração: {results.duration:.1f}s")
        click.echo(f"Usuários simultâneos: {results.max_concurrent_users}")
        
        click.echo(f"\n📈 AÇÕES")
        click.echo(f"  Total: {results.total_actions}")
        click.echo(f"  Sucesso: {results.successful_actions} ({results.success_rate:.1f}%)")
        click.echo(f"  Falhas: {results.failed_actions} ({results.error_rate:.1f}%)")
        
        click.echo(f"\n⏱️  TEMPO DE RESPOSTA")
        click.echo(f"  Média: {results.response_time_avg:.0f}ms")
        click.echo(f"  P95: {results.response_time_p95:.0f}ms")
        click.echo(f"  P99: {results.response_time_p99:.0f}ms")
        
        click.echo(f"\n📱 DEVICE")
        click.echo(f"  CPU média: {results.avg_cpu:.1f}%")
        click.echo(f"  Memória pico: {results.peak_memory:.1f}MB")
        
        # Thresholds
        if results.thresholds:
            click.echo(f"\n🎯 THRESHOLDS")
            threshold_results = results.check_thresholds()
            for metric, passed in threshold_results.items():
                status = "✅" if passed else "❌"
                click.echo(f"  {status} {metric}")
        
        click.echo(f"\n📁 Relatórios salvos em: {output_path.absolute()}")
        click.echo(f"  - {html_file.name}")
        click.echo(f"  - {json_file.name}")
        click.echo(f"  - {csv_file.name}")
        
        # Status final
        if results.passed_thresholds:
            click.secho("\n✅ TESTE PASSOU", fg='green', bold=True)
            sys.exit(0)
        else:
            click.secho("\n❌ TESTE FALHOU", fg='red', bold=True)
            sys.exit(1)
    
    except Exception as e:
        click.secho(f"\n❌ Erro: {e}", fg='red', bold=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option('--open', 'open_browser', is_flag=True, 
              help='Abrir relatório no navegador')
@click.option('--results-dir', type=click.Path(exists=True), default='./results',
              help='Diretório com os resultados')
def report(open_browser, results_dir):
    """
    Visualiza relatórios de testes anteriores
    
    \b
    Exemplo:
        mobileloadx report --open
        mobileloadx report --results-dir ./my-results --open
    """
    results_path = Path(results_dir)
    html_file = results_path / "report.html"
    
    if not html_file.exists():
        click.secho(f"❌ Relatório não encontrado: {html_file}", fg='red')
        sys.exit(1)
    
    click.echo(f"📊 Relatório: {html_file.absolute()}")
    
    if open_browser:
        import webbrowser
        webbrowser.open(f"file://{html_file.absolute()}")
        click.echo("🌐 Abrindo no navegador...")
    else:
        click.echo("Use --open para abrir no navegador")


@main.command()
@click.option('--fail-on-threshold', is_flag=True,
              help='Falhar se algum threshold não for atingido')
@click.option('--results-dir', type=click.Path(exists=True), default='./results',
              help='Diretório com os resultados')
def verify(fail_on_threshold, results_dir):
    """
    Verifica se os thresholds foram atingidos (útil para CI/CD)
    
    \b
    Exemplo:
        mobileloadx verify --fail-on-threshold
    """
    import json
    
    results_path = Path(results_dir)
    json_file = results_path / "report.json"
    
    if not json_file.exists():
        click.secho(f"❌ Resultados não encontrados: {json_file}", fg='red')
        sys.exit(1)
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    passed = data.get('passed', False)
    threshold_results = data.get('threshold_results', {})
    
    click.echo("🎯 VERIFICAÇÃO DE THRESHOLDS")
    click.echo("="*40)
    
    for metric, result in threshold_results.items():
        status = "✅" if result else "❌"
        click.echo(f"{status} {metric}")
    
    click.echo("="*40)
    
    if passed:
        click.secho("✅ Todos os thresholds foram atingidos", fg='green')
        sys.exit(0)
    else:
        msg = "❌ Alguns thresholds não foram atingidos"
        click.secho(msg, fg='red')
        
        if fail_on_threshold:
            sys.exit(1)
        else:
            sys.exit(0)


@main.command()
def init():
    """
    Cria um arquivo de configuração de exemplo
    
    \b
    Exemplo:
        mobileloadx init
    """
    config_template = """test:
  name: "My Performance Test"
  duration: 300

virtual_users:
  initial: 1
  max: 10
  ramp_up_time: 30

platforms:
  - android:
      app: "./app-release.apk"
      device: "emulator-5554"
      capabilities:
        appium_server_url: "http://localhost:4723"

scenarios:
  - name: "Main Flow"
    weight: 100
    actions:
      - tap: {id: "buttonId"}
      - wait: {timeout: 2}
      - scroll: {direction: "down", duration: 1}

metrics:
  collect:
    - cpu
    - memory
    - battery
    - network
  interval: 1

thresholds:
  cpu_max: 80
  memory_max: 300
  response_time_p95: 2000
  error_rate_max: 5
"""
    
    config_file = Path("config.yaml")
    
    if config_file.exists():
        click.secho(f"⚠️  Arquivo já existe: {config_file}", fg='yellow')
        if not click.confirm("Sobrescrever?"):
            return
    
    config_file.write_text(config_template, encoding='utf-8')
    click.secho(f"✅ Arquivo criado: {config_file}", fg='green')
    click.echo("\nEdite o arquivo e execute:")
    click.echo(f"  mobileloadx run {config_file}")


@main.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--strict', is_flag=True, help='Modo strict (falha em qualquer erro)')
def validate(config_file, strict):
    """
    Valida configuração de teste
    
    \b
    Exemplo:
        mobileloadx validate config.yaml
        mobileloadx validate config.yaml --strict
    """
    try:
        click.echo(f"🔍 Validando: {config_file}")
        
        validator = SchemaValidator()
        valid, errors = validator.validate_file(config_file)
        
        if valid:
            # Carregar para validações adicionais
            config = ConfigLoader.load(config_file)
            
            click.secho("✅ Configuração válida!", fg='green')
            test_cfg = config.get('test', {})
            vu_cfg = config.get('virtual_users', {})
            name = test_cfg.get('name', config.get('name', 'N/A'))
            duration = test_cfg.get('duration', config.get('duration', 'N/A'))
            users = vu_cfg.get('max', config.get('virtual_users', 'N/A'))
            click.echo(f"\n📋 RESUMO DA CONFIGURAÇÃO")
            click.echo(f"  Nome: {name}")
            click.echo(f"  Duração: {duration}s")
            click.echo(f"  Usuários máx: {users}")
            click.echo(f"  Plataformas: {len(config.get('platforms', []))}")
            click.echo(f"  Cenários: {len(config.get('scenarios', []))}")
            
            sys.exit(0)
        else:
            click.secho("❌ Erros encontrados:", fg='red')
            for error in errors:
                click.echo(f"  • {error}")
            
            if strict:
                sys.exit(1)
            else:
                click.echo("\nUse --strict para falhar em erros de validação")
                sys.exit(0)
    
    except Exception as e:
        click.secho(f"❌ Erro ao validar: {e}", fg='red')
        sys.exit(1)


@main.command()
@click.option('--plugin', type=str, help='Carregar plugin específico')
def plugins(plugin):
    """
    Gerencia plugins do MobileLoadX
    
    \b
    Exemplo:
        mobileloadx plugins
        mobileloadx plugins --plugin CustomMetrics
    """
    try:
        manager = get_plugin_manager()
        
        if plugin:
            # Mostrar informações de um plugin específico
            p = manager.get_plugin(plugin)
            if not p:
                click.secho(f"❌ Plugin não encontrado: {plugin}", fg='red')
                sys.exit(1)
            
            info = p.get_info()
            click.echo(f"📦 {info.name}")
            click.echo(f"  Versão: {info.version}")
            click.echo(f"  Descrição: {info.description}")
            click.echo(f"  Autor: {info.author}")
            if info.dependencies:
                click.echo(f"  Dependências: {', '.join(info.dependencies)}")
        else:
            # Listar todos os plugins
            plugins_list = manager.list_plugins()
            
            if not plugins_list:
                click.echo("📦 Nenhum plugin registrado")
            else:
                click.echo("📦 PLUGINS REGISTRADOS")
                for info in plugins_list:
                    click.echo(f"  • {info.name} v{info.version}")
                    click.echo(f"    {info.description}")
    
    except Exception as e:
        click.secho(f"❌ Erro: {e}", fg='red')
        sys.exit(1)


@main.command()
@click.argument('report1', type=click.Path(exists=True))
@click.argument('report2', type=click.Path(exists=True))
@click.option('--format', type=click.Choice(['text', 'json']), default='text',
              help='Formato de saída')
def compare(report1, report2, format):
    """
    Compara dois testes
    
    \b
    Exemplo:
        mobileloadx compare ./test1/report.json ./test2/report.json
        mobileloadx compare report1.json report2.json --format json
    """
    try:
        with open(report1, 'r') as f:
            data1 = json.load(f)
        with open(report2, 'r') as f:
            data2 = json.load(f)
        
        comparison = {
            'report1': Path(report1).name,
            'report2': Path(report2).name,
            'metrics': {}
        }
        
        # Comparar métricas principais
        metrics = [
            'response_time_avg',
            'response_time_p95',
            'error_rate',
            'success_rate',
            'avg_cpu',
            'peak_memory'
        ]
        
        for metric in metrics:
            v1 = data1.get(metric, 0)
            v2 = data2.get(metric, 0)
            
            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                diff = v2 - v1
                percentage = (diff / v1 * 100) if v1 != 0 else 0
                
                comparison['metrics'][metric] = {
                    'test1': v1,
                    'test2': v2,
                    'difference': diff,
                    'percentage': percentage
                }
        
        if format == 'json':
            click.echo(json.dumps(comparison, indent=2))
        else:
            click.echo("📊 COMPARAÇÃO DE TESTES")
            click.echo("="*60)
            click.echo(f"Test 1: {comparison['report1']}")
            click.echo(f"Test 2: {comparison['report2']}")
            click.echo("="*60)
            
            for metric, values in comparison['metrics'].items():
                v1 = values['test1']
                v2 = values['test2']
                p = values['percentage']
                
                direction = "📈" if p > 0 else "📉" if p < 0 else "↔️ "
                click.echo(f"\n{metric}:")
                click.echo(f"  Test 1: {v1:.2f}")
                click.echo(f"  Test 2: {v2:.2f}")
                click.echo(f"  {direction} Mudança: {p:+.1f}%")
    
    except json.JSONDecodeError:
        click.secho("❌ Erro ao ler arquivo JSON", fg='red')
        sys.exit(1)
    except Exception as e:
        click.secho(f"❌ Erro ao comparar: {e}", fg='red')
        sys.exit(1)


@main.command()
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='INFO', help='Nível de log')
@click.option('--log-file', type=str, help='Arquivo para salvar logs')
@click.option('--json-logs', is_flag=True, help='Usar formato JSON para logs')
def configure_logging(log_level, log_file, json_logs):
    """
    Configura sistema de logging
    
    \b
    Exemplo:
        mobileloadx configure-logging --log-level DEBUG
        mobileloadx configure-logging --log-file app.log --json-logs
    """
    try:
        setup_logging(
            level=log_level,
            log_file=log_file,
            json_format=json_logs,
            log_dir='./logs'
        )
        
        click.secho("✅ Logging configurado!", fg='green')
        click.echo(f"  Nível: {log_level}")
        if log_file:
            click.echo(f"  Arquivo: {log_file}")
        click.echo(f"  Formato: {'JSON' if json_logs else 'Texto'}")
    
    except Exception as e:
        click.secho(f"❌ Erro ao configurar logging: {e}", fg='red')
        sys.exit(1)


if __name__ == '__main__':
    main()
