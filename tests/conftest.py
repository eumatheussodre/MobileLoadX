"""
Configurações compartilhadas para testes
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock


@pytest.fixture
def temp_dir():
    """Diretório temporário para testes"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_driver():
    """Mock do webdriver do Appium"""
    driver = MagicMock()
    driver.get_window_size.return_value = {'width': 1080, 'height': 1920}
    driver.swipe = Mock()
    driver.click = Mock()
    driver.back = Mock()
    return driver


@pytest.fixture
def config_dict():
    """Configuração básica para testes"""
    return {
        'name': 'Test Load Test',
        'duration': 300,
        'virtual_users': 5,
        'ramp_up_time': 60,
        'platforms': [
            {
                'platform': 'android',
                'app': '/path/to/app.apk',
                'devices': ['emulator-5554'],
                'capabilities': {}
            }
        ],
        'scenarios': [
            {
                'name': 'Login Flow',
                'weight': 100,
                'actions': [
                    {'type': 'tap', 'xpath': '//login_button'},
                    {'type': 'input', 'text': 'user@example.com'},
                    {'type': 'tap', 'xpath': '//password_field'},
                    {'type': 'input', 'text': 'password123'}
                ]
            }
        ],
        'thresholds': {
            'response_time_p95': 2000,
            'error_rate': 0.05
        }
    }


@pytest.fixture
def yaml_config_file(temp_dir, config_dict):
    """Cria arquivo YAML de configuração"""
    import yaml
    
    config_file = temp_dir / 'config.yaml'
    with open(config_file, 'w') as f:
        yaml.dump(config_dict, f)
    
    return config_file


@pytest.fixture
def json_config_file(temp_dir, config_dict):
    """Cria arquivo JSON de configuração"""
    import json
    
    config_file = temp_dir / 'config.json'
    with open(config_file, 'w') as f:
        json.dump(config_dict, f)
    
    return config_file
