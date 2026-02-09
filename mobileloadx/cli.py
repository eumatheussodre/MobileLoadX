"""
Interface de linha de comando para MobileLoadX
"""

import click
import logging
import sys
from pathlib import Path

from .core.load_test import LoadTest
from .reporting.report_generator import ReportGenerator


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


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


if __name__ == '__main__':
    main()
