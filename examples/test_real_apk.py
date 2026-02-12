#!/usr/bin/env python3
"""
Script prático para testar um APK real com MobileLoadX
Exemplo de uso:
    python test_real_apk.py --apk ./myapp.apk --device emulator-5554
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, Any

from mobileloadx.core.load_test import LoadTest
from mobileloadx.core.scenario import Scenario
from mobileloadx.core.action import Action
from mobileloadx.reporting.report_generator import ReportGenerator
from mobileloadx.config.loader import ConfigLoader
from mobileloadx.logging_setup import setup_logging, get_logger


logger = get_logger('test_real_apk')


def create_test_config(
    apk_path: str,
    device_id: str,
    test_name: str = "APK Load Test",
    duration: int = 120,
    virtual_users: int = 1,
    ramp_up_time: int = 10
) -> Dict[str, Any]:
    """
    Cria configuração de teste para APK real
    
    Args:
        apk_path: Caminho do APK
        device_id: ID do device (ex: emulator-5554)
        test_name: Nome do teste
        duration: Duração em segundos
        virtual_users: Número de usuários virtuais
        ramp_up_time: Tempo para rampar
    
    Returns:
        Dicionário com configuração
    """
    config = {
        'name': test_name,
        'duration': duration,
        'virtual_users': virtual_users,
        'ramp_up_time': ramp_up_time,
        'platforms': [
            {
                'platform': 'android',
                'app': apk_path,
                'devices': [device_id],
                'capabilities': {
                    'appium_server_url': 'http://localhost:4723',
                    'automationName': 'UiAutomator2',
                    'newCommandTimeout': 300,
                    'autoGrantPermissions': True,
                    'autoWebview': False
                }
            }
        ],
        'scenarios': [
            {
                'name': 'Basic Flow',
                'weight': 100,
                'actions': [
                    {'type': 'wait', 'timeout': 2},
                    {'type': 'scroll', 'direction': 'down', 'duration': 1},
                    {'type': 'wait', 'timeout': 1},
                    {'type': 'scroll', 'direction': 'up', 'duration': 1},
                    {'type': 'wait', 'timeout': 1}
                ]
            }
        ],
        'thresholds': {
            'response_time_p95': 3000,
            'error_rate': 0.10,
            'cpu_max': 85,
            'memory_max': 500
        },
        'metrics': {
            'collect': ['cpu', 'memory', 'battery'],
            'interval': 2
        }
    }
    
    return config


def test_basic_scenario(apk_path: str, device_id: str, test_name: str = "Basic APK Test"):
    """
    Testa cenário básico do APK
    
    Args:
        apk_path: Caminho do APK
        device_id: ID do device
        test_name: Nome do teste
    """
    logger.info(f"Iniciando teste básico: {test_name}")
    
    # Criar teste
    test = LoadTest(
        name=test_name,
        duration=60,
        virtual_users=1,
        ramp_up_time=5
    )
    
    # Adicionar plataforma
    test.add_platform(
        platform='android',
        app=apk_path,
        device=device_id,
        appium_server_url='http://localhost:4723',
        automationName='UiAutomator2',
        newCommandTimeout=300,
        autoGrantPermissions=True
    )
    
    # Criar cenário
    scenario = Scenario("Basic Navigation")
    scenario.wait(timeout=2)
    scenario.scroll(direction="down", duration=1)
    scenario.wait(timeout=1)
    scenario.scroll(direction="up", duration=1)
    
    test.add_scenario(scenario, weight=100)
    
    # Definir thresholds
    test.thresholds['response_time_p95'] = 3000
    test.thresholds['error_rate'] = 0.10
    
    logger.info("Executando teste...")
    
    try:
        # Executar teste
        results = test.run()
        
        # Exibir resultados
        print("\n" + "="*60)
        print("📊 RESULTADOS DO TESTE")
        print("="*60)
        print(f"Teste: {results.test_name}")
        print(f"Duração: {results.duration:.1f}s")
        print(f"Usuários: {results.max_concurrent_users}")
        
        print(f"\n📈 AÇÕES")
        print(f"  Total: {results.total_actions}")
        print(f"  Sucesso: {results.successful_actions}")
        print(f"  Taxa sucesso: {results.success_rate:.1f}%")
        print(f"  Falhas: {results.failed_actions}")
        
        print(f"\n⏱️  TEMPO DE RESPOSTA")
        print(f"  Média: {results.response_time_avg:.0f}ms")
        print(f"  P95: {results.response_time_p95:.0f}ms")
        print(f"  P99: {results.response_time_p99:.0f}ms")
        
        print(f"\n📱 DEVICE")
        print(f"  CPU médio: {results.avg_cpu:.1f}%")
        print(f"  Memória pico: {results.peak_memory:.1f}MB")
        
        if results.passed_thresholds:
            print("\n✅ TESTE PASSOU")
        else:
            print("\n❌ TESTE FALHOU")
        
        print("="*60 + "\n")
        
        return results
        
    except Exception as e:
        logger.error(f"Erro ao executar teste: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_with_config_file(config_path: str, output_dir: str = "./results"):
    """
    Executa teste a partir de arquivo de configuração
    
    Args:
        config_path: Caminho do arquivo de configuração
        output_dir: Diretório para salvar relatórios
    """
    logger.info(f"Carregando configuração: {config_path}")
    
    # Carregar configuração
    config = ConfigLoader.load(config_path)
    
    # Criar teste
    test = LoadTest(
        name=config.get('name', 'Test'),
        duration=config.get('duration', 300),
        virtual_users=config.get('virtual_users', 1),
        ramp_up_time=config.get('ramp_up_time', 0),
        config_file=config_path
    )
    
    logger.info(f"Executando teste: {test.name}")
    
    try:
        # Executar teste
        results = test.run()
        
        # Gerar relatórios
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Gerando relatórios em {output_path}")
        
        generator = ReportGenerator(results)
        generator.generate_html(str(output_path / "report.html"))
        generator.generate_json(str(output_path / "report.json"))
        generator.generate_csv(str(output_path / "report.csv"))
        
        print(f"\n✅ Relatórios salvos em: {output_path.absolute()}")
        
        return results
        
    except Exception as e:
        logger.error(f"Erro ao executar teste: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_config_file(
    output_path: str,
    apk_path: str,
    device_id: str,
    test_name: str = "APK Load Test",
    duration: int = 120,
    virtual_users: int = 1
):
    """
    Gera arquivo de configuração YAML
    
    Args:
        output_path: Caminho para salvar arquivo
        apk_path: Caminho do APK
        device_id: ID do device
        test_name: Nome do teste
        duration: Duração em segundos
        virtual_users: Número de usuários
    """
    config = create_test_config(
        apk_path=apk_path,
        device_id=device_id,
        test_name=test_name,
        duration=duration,
        virtual_users=virtual_users
    )
    
    ConfigLoader.save(config, output_path, format='yaml')
    logger.info(f"Arquivo de configuração gerado: {output_path}")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Teste um APK real com MobileLoadX',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Exemplos de uso:

  # Teste básico com emulador
  python test_real_apk.py --apk ./myapp.apk --device emulator-5554

  # Teste com device real
  python test_real_apk.py --apk ./myapp.apk --device ZY123ABC

  # Usando arquivo de configuração
  python test_real_apk.py --config test_config.yaml

  # Gerar arquivo de configuração
  python test_real_apk.py --create-config test_config.yaml --apk ./app.apk --device emulator-5554

  # Teste com debug
  python test_real_apk.py --apk ./app.apk --device emulator-5554 --verbose
        '''
    )
    
    parser.add_argument('--apk', type=str, help='Caminho do APK a testar')
    parser.add_argument('--device', type=str, default='emulator-5554', 
                       help='ID do device/emulador (default: emulator-5554)')
    parser.add_argument('--config', type=str, help='Arquivo de configuração YAML')
    parser.add_argument('--create-config', type=str, help='Criar arquivo de configuração')
    parser.add_argument('--name', type=str, default='APK Load Test', help='Nome do teste')
    parser.add_argument('--duration', type=int, default=120, help='Duração do teste em segundos')
    parser.add_argument('--users', type=int, default=1, help='Número de usuários virtuais')
    parser.add_argument('--output', type=str, default='./results', help='Diretório de saída')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verbose')
    
    args = parser.parse_args()
    
    # Configurar logging
    setup_logging(
        level='DEBUG' if args.verbose else 'INFO',
        log_file='test.log' if args.verbose else None,
        json_format=False,
        log_dir='./logs'
    )
    
    # Criar arquivo de configuração
    if args.create_config:
        if not args.apk:
            parser.error("--create-config requer --apk")
        
        generate_config_file(
            output_path=args.create_config,
            apk_path=args.apk,
            device_id=args.device,
            test_name=args.name,
            duration=args.duration,
            virtual_users=args.users
        )
        return
    
    # Executar teste
    if args.config:
        # Usar arquivo de configuração
        test_with_config_file(args.config, args.output)
    elif args.apk:
        # Teste básico
        test_basic_scenario(
            apk_path=args.apk,
            device_id=args.device,
            test_name=args.name
        )
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
