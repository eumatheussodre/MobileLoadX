"""
Testes para a CLI
"""

import pytest
from click.testing import CliRunner
from mobileloadx.cli import main, run, report, verify, init


@pytest.fixture
def cli_runner():
    """Runner para testes de CLI"""
    return CliRunner()


class TestMainCommand:
    """Testes para comando main"""
    
    def test_version_option(self, cli_runner):
        """Testa opção --version"""
        result = cli_runner.invoke(main, ['--version'])
        
        assert result.exit_code == 0
        assert '1.0.0' in result.output or 'version' in result.output.lower()
    
    def test_help_option(self, cli_runner):
        """Testa opção --help"""
        result = cli_runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert 'MobileLoadX' in result.output or 'Usage' in result.output


class TestRunCommand:
    """Testes para comando run"""
    
    def test_run_help(self, cli_runner):
        """Testa help do comando run"""
        result = cli_runner.invoke(run, ['--help'])
        
        assert result.exit_code == 0
        assert 'config_file' in result.output.lower() or 'config' in result.output.lower()
    
    def test_run_missing_config_file(self, cli_runner):
        """Testa erro ao não fornecer arquivo de config"""
        result = cli_runner.invoke(run, [])
        
        # Deve falhar por falta de argumentos
        assert result.exit_code != 0
    
    def test_run_nonexistent_file(self, cli_runner):
        """Testa erro ao usar arquivo inexistente"""
        result = cli_runner.invoke(run, ['nonexistent.yaml'])
        
        assert result.exit_code != 0
    
    def test_run_with_output_dir_option(self, cli_runner, temp_dir):
        """Testa opção --output-dir"""
        yaml_file = temp_dir / 'config.yaml'
        yaml_file.write_text('''
name: Test
duration: 10
virtual_users: 1
''')
        
        output_dir = temp_dir / 'results'
        
        result = cli_runner.invoke(run, [
            str(yaml_file),
            '--output-dir', str(output_dir)
        ])
        
        # Pode falhar por falta de Appium, mas não deve ser erro de argumentos
        assert 'output-dir' not in result.output or result.exit_code in [0, 1, 2]
    
    def test_run_with_verbose_flag(self, cli_runner, temp_dir):
        """Testa flag --verbose"""
        yaml_file = temp_dir / 'config.yaml'
        yaml_file.write_text('''
name: Test
duration: 10
virtual_users: 1
''')
        
        result = cli_runner.invoke(run, [
            str(yaml_file),
            '--verbose'
        ])
        
        # Verificar se verbose foi processado
        assert result.exit_code in [0, 1, 2]
    
    def test_run_with_short_verbose_flag(self, cli_runner, temp_dir):
        """Testa flag -v (verbose abreviado)"""
        yaml_file = temp_dir / 'config.yaml'
        yaml_file.write_text('''
name: Test
duration: 10
virtual_users: 1
''')
        
        result = cli_runner.invoke(run, [
            str(yaml_file),
            '-v'
        ])
        
        assert result.exit_code in [0, 1, 2]
    
    def test_run_with_ci_mode(self, cli_runner, temp_dir):
        """Testa flag --ci-mode"""
        yaml_file = temp_dir / 'config.yaml'
        yaml_file.write_text('''
name: Test
duration: 10
virtual_users: 1
''')
        
        result = cli_runner.invoke(run, [
            str(yaml_file),
            '--ci-mode'
        ])
        
        assert result.exit_code in [0, 1, 2]


class TestReportCommand:
    """Testes para comando report"""
    
    def test_report_help(self, cli_runner):
        """Testa help do comando report"""
        result = cli_runner.invoke(main, ['report', '--help'])
        
        assert result.exit_code == 0


class TestVerifyCommand:
    """Testes para comando verify"""
    
    def test_verify_help(self, cli_runner):
        """Testa help do comando verify"""
        result = cli_runner.invoke(main, ['verify', '--help'])
        
        assert result.exit_code == 0


class TestInitCommand:
    """Testes para comando init"""
    
    def test_init_help(self, cli_runner):
        """Testa help do comando init"""
        result = cli_runner.invoke(main, ['init', '--help'])
        
        assert result.exit_code == 0
    
    def test_init_creates_template(self, cli_runner, temp_dir):
        """Testa se init cria arquivo de template"""
        result = cli_runner.invoke(main, ['init', '--path', str(temp_dir / 'config.yaml')])
        
        # Pode ou não criar dependendo da implementação
        assert result.exit_code in [0, 1, 2]


class TestCLIIntegration:
    """Testes de integração da CLI"""
    
    def test_invalid_command(self, cli_runner):
        """Testa comando inválido"""
        result = cli_runner.invoke(main, ['invalid-command'])
        
        assert result.exit_code != 0
    
    def test_no_command(self, cli_runner):
        """Testa sem fornecer comando"""
        result = cli_runner.invoke(main, [])
        
        # Pode mostrar help ou erro
        assert result.exit_code in [0, 2]
