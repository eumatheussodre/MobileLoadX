"""
Testes para a classe LoadTest
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from mobileloadx.core.load_test import LoadTest, PlatformConfig
from mobileloadx.core.scenario import Scenario, Action


class TestPlatformConfig:
    """Testes para PlatformConfig"""
    
    def test_platform_config_android(self):
        """Testa configuração de plataforma Android"""
        config = PlatformConfig(
            platform='android',
            app='/path/to/app.apk',
            devices=['emulator-5554'],
            capabilities={'timeout': 30}
        )
        
        assert config.platform == 'android'
        assert config.app == '/path/to/app.apk'
        assert len(config.devices) == 1
        assert config.capabilities['timeout'] == 30
    
    def test_platform_config_ios(self):
        """Testa configuração de plataforma iOS"""
        config = PlatformConfig(
            platform='iOS',
            app='/path/to/app.ipa',
            devices=['iPhone-12'],
            capabilities={'automation': 'XCUITest'}
        )
        
        assert config.platform == 'iOS'
        assert config.app == '/path/to/app.ipa'


class TestLoadTest:
    """Testes para a classe LoadTest"""
    
    def test_load_test_initialization(self):
        """Testa inicialização de LoadTest"""
        test = LoadTest(
            name='My Test',
            duration=300,
            virtual_users=10,
            ramp_up_time=60
        )
        
        assert test.name == 'My Test'
        assert test.duration == 300
        assert test.max_virtual_users == 10
        assert test.ramp_up_time == 60
        assert test.is_running is False
        assert len(test.platforms) == 0
        assert len(test.scenarios) == 0
    
    def test_add_platform_single_device(self):
        """Testa adição de plataforma com um device"""
        test = LoadTest('Test')
        test.add_platform('android', '/path/to/app.apk', device='emulator-5554')
        
        assert len(test.platforms) == 1
        assert test.platforms[0].platform == 'android'
        assert len(test.platforms[0].devices) == 1
    
    def test_add_platform_multiple_devices(self):
        """Testa adição de plataforma com múltiplos devices"""
        test = LoadTest('Test')
        devices = ['device-1', 'device-2', 'device-3']
        test.add_platform('android', '/path/to/app.apk', devices=devices)
        
        assert len(test.platforms) == 1
        assert len(test.platforms[0].devices) == 3
    
    def test_add_platform_case_insensitive(self):
        """Testa se plataforma é case-insensitive"""
        test = LoadTest('Test')
        test.add_platform('ANDROID', '/path/to/app.apk')
        
        assert test.platforms[0].platform == 'android'
    
    def test_add_platform_with_capabilities(self):
        """Testa adição de plataforma com capabilities"""
        test = LoadTest('Test')
        test.add_platform(
            'ios',
            '/path/to/app.ipa',
            device='iphone-12',
            automationName='XCUITest',
            platformVersion='15.0'
        )
        
        platform = test.platforms[0]
        assert platform.capabilities['automationName'] == 'XCUITest'
        assert platform.capabilities['platformVersion'] == '15.0'
    
    def test_add_scenario_with_weight(self):
        """Testa adição de cenário com peso"""
        test = LoadTest('Test')
        scenario = Scenario('Login Flow')
        scenario.tap(xpath='//login')
        
        test.add_scenario(scenario, weight=100)
        
        assert len(test.scenarios) == 1
        assert test.scenarios[0][0] == scenario
        assert test.scenarios[0][1] == 100
    
    def test_add_multiple_scenarios(self):
        """Testa adição de múltiplos cenários"""
        test = LoadTest('Test')
        
        scenario1 = Scenario('Login')
        scenario2 = Scenario('Purchase')
        scenario3 = Scenario('Logout')
        
        test.add_scenario(scenario1, weight=80)
        test.add_scenario(scenario2, weight=15)
        test.add_scenario(scenario3, weight=5)
        
        assert len(test.scenarios) == 3
        assert sum(weight for _, weight in test.scenarios) == 100
    
    def test_default_values(self):
        """Testa valores padrão"""
        test = LoadTest('Test')
        
        assert test.duration == 300
        assert test.max_virtual_users == 1
        assert test.ramp_up_time == 0
    
    def test_metrics_collector_initialized(self):
        """Testa se coletor de métricas foi inicializado"""
        test = LoadTest('Test')
        
        assert test.metrics_collector is not None
    
    def test_set_threshold(self):
        """Testa definição de limiar"""
        test = LoadTest('Test')
        test.thresholds['response_time_p95'] = 2000
        test.thresholds['error_rate'] = 0.05
        
        assert test.thresholds['response_time_p95'] == 2000
        assert test.thresholds['error_rate'] == 0.05
    
    def test_load_from_empty_config(self, temp_dir):
        """Testa carregamento de arquivo vazio"""
        import yaml
        
        config_file = temp_dir / 'empty.yaml'
        with open(config_file, 'w') as f:
            yaml.dump({}, f)
        
        # Não deve lançar erro
        test = LoadTest('Test', config_file=str(config_file))
    
    def test_multiple_platforms(self):
        """Testa adição de múltiplas plataformas"""
        test = LoadTest('Test')
        
        test.add_platform('android', '/path/to/android.apk', device='android-1')
        test.add_platform('ios', '/path/to/ios.ipa', device='ios-1')
        
        assert len(test.platforms) == 2
        assert test.platforms[0].platform == 'android'
        assert test.platforms[1].platform == 'ios'
