"""
Testes para a classe VirtualUser
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from mobileloadx.core.virtual_user import VirtualUser
from mobileloadx.core.scenario import Scenario


class TestVirtualUser:
    """Testes para a classe VirtualUser"""
    
    def test_virtual_user_initialization(self):
        """Testa inicialização de usuário virtual"""
        user = VirtualUser(
            user_id=1,
            platform='android',
            app='/path/to/app.apk',
            device='emulator-5554'
        )
        
        assert user.user_id == 1
        assert user.platform == 'android'
        assert user.app == '/path/to/app.apk'
        assert user.device == 'emulator-5554'
        assert user.is_active is False
        assert user.actions_executed == 0
        assert user.errors == 0
    
    def test_platform_lowercase(self):
        """Testa se plataforma é convertida para minúsculas"""
        user = VirtualUser(user_id=1, platform='ANDROID', app='/app.apk')
        
        assert user.platform == 'android'
    
    def test_virtual_user_with_capabilities(self):
        """Testa usuário com capabilities customizadas"""
        capabilities = {
            'automationName': 'UiAutomator2',
            'platformVersion': '11',
            'appium_server_url': 'http://localhost:4723'
        }
        
        user = VirtualUser(
            user_id=1,
            platform='android',
            app='/app.apk',
            capabilities=capabilities
        )
        
        assert user.capabilities['automationName'] == 'UiAutomator2'
        assert user.capabilities['platformVersion'] == '11'
    
    def test_virtual_user_with_scenarios(self):
        """Testa usuário com cenários"""
        scenario = Scenario('Login')
        user = VirtualUser(
            user_id=1,
            platform='android',
            app='/app.apk',
            scenarios=[(scenario, 100)]
        )
        
        assert len(user.scenarios) == 1
        assert user.scenarios[0][0] == scenario
    
    def test_virtual_user_with_metrics_collector(self):
        """Testa usuário com coletor de métricas"""
        from mobileloadx.metrics.collector import MetricsCollector
        
        collector = MetricsCollector()
        user = VirtualUser(
            user_id=1,
            platform='ios',
            app='/app.ipa',
            metrics_collector=collector
        )
        
        assert user.metrics_collector is collector
    
    def test_default_device_none(self):
        """Testa device padrão como None"""
        user = VirtualUser(user_id=1, platform='android', app='/app.apk')
        
        assert user.device is None
    
    def test_default_capabilities_empty_dict(self):
        """Testa capabilities padrão como dict vazio"""
        user = VirtualUser(user_id=1, platform='android', app='/app.apk')
        
        assert user.capabilities == {}
    
    def test_default_scenarios_empty_list(self):
        """Testa scenarios padrão como lista vazia"""
        user = VirtualUser(user_id=1, platform='android', app='/app.apk')
        
        assert user.scenarios == []
    
    @patch('mobileloadx.core.virtual_user.webdriver.Remote')
    def test_start_session_android(self, mock_webdriver):
        """Testa início de sessão no Android"""
        mock_driver = MagicMock()
        mock_webdriver.return_value = mock_driver
        
        with patch('mobileloadx.core.virtual_user.UiAutomator2Options'):
            user = VirtualUser(
                user_id=1,
                platform='android',
                app='/path/to/app.apk',
                device='emulator-5554'
            )
            
            user.start()
            
            assert user.is_active
            assert user.driver is mock_driver
    
    @patch('mobileloadx.core.virtual_user.webdriver.Remote')
    def test_start_session_ios(self, mock_webdriver):
        """Testa início de sessão no iOS"""
        mock_driver = MagicMock()
        mock_webdriver.return_value = mock_driver
        
        with patch('mobileloadx.core.virtual_user.XCUITestOptions'):
            user = VirtualUser(
                user_id=1,
                platform='ios',
                app='/path/to/app.ipa'
            )
            
            user.start()
            
            assert user.is_active
            assert user.driver is mock_driver
    
    def test_start_session_invalid_platform(self):
        """Testa erro com plataforma inválida"""
        user = VirtualUser(
            user_id=1,
            platform='windows',
            app='/app.exe'
        )
        
        with patch('mobileloadx.core.virtual_user.webdriver.Remote'):
            with pytest.raises(ValueError, match='Plataforma não suportada'):
                user.start()
    
    def test_stop_session(self):
        """Testa parada de sessão"""
        user = VirtualUser(user_id=1, platform='android', app='/app.apk')
        user.driver = MagicMock()
        user.is_active = True
        
        user.stop()
        
        user.driver.quit.assert_called_once()
        assert user.is_active is False
    
    def test_stop_session_no_driver(self):
        """Testa parada quando não há driver"""
        user = VirtualUser(user_id=1, platform='android', app='/app.apk')
        user.driver = None
        
        # Não deve lançar erro
        user.stop()
    
    def test_error_count_increment(self):
        """Testa incremento de contagem de erros"""
        user = VirtualUser(user_id=1, platform='android', app='/app.apk')
        
        assert user.errors == 0
        
        user.errors += 1
        user.errors += 1
        
        assert user.errors == 2
    
    def test_actions_executed_increment(self):
        """Testa incremento de ações executadas"""
        user = VirtualUser(user_id=1, platform='android', app='/app.apk')
        
        assert user.actions_executed == 0
        
        user.actions_executed += 1
        user.actions_executed += 5
        
        assert user.actions_executed == 6
    
    def test_user_id_is_unique(self):
        """Testa se ID de usuário é mantido"""
        user1 = VirtualUser(user_id=1, platform='android', app='/app.apk')
        user2 = VirtualUser(user_id=2, platform='android', app='/app.apk')
        
        assert user1.user_id == 1
        assert user2.user_id == 2
        assert user1.user_id != user2.user_id
