"""
Testes para a classe Scenario e Action
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from mobileloadx.core.scenario import Scenario, Action


class TestAction:
    """Testes para a classe Action"""
    
    def test_action_initialization(self):
        """Testa inicialização de ações"""
        action = Action('tap', xpath='//button', timeout=10)
        
        assert action.action_type == 'tap'
        assert action.params['xpath'] == '//button'
        assert action.params['timeout'] == 10
    
    def test_action_tap(self, mock_driver):
        """Testa ação de tap"""
        # Mock do WebDriverWait
        with patch('mobileloadx.core.scenario.WebDriverWait') as mock_wait_class:
            mock_wait = MagicMock()
            mock_wait_class.return_value = mock_wait
            
            mock_element = MagicMock()
            mock_wait.until.return_value = mock_element
            
            action = Action('tap', xpath='//button')
            action.execute(mock_driver, 'android')
            
            mock_element.click.assert_called_once()
    
    def test_action_input(self, mock_driver):
        """Testa ação de input de texto"""
        with patch('mobileloadx.core.scenario.WebDriverWait') as mock_wait_class:
            mock_wait = MagicMock()
            mock_wait_class.return_value = mock_wait
            
            mock_element = MagicMock()
            mock_wait.until.return_value = mock_element
            
            action = Action('input', text='hello', xpath='//input')
            action.execute(mock_driver, 'android')
            
            mock_element.send_keys.assert_called_once_with('hello')
    
    def test_action_wait(self):
        """Testa ação de wait"""
        import time
        
        action = Action('wait', timeout=0.1)
        
        start = time.time()
        action.execute(None, 'android')
        elapsed = time.time() - start
        
        assert elapsed >= 0.1
    
    def test_action_scroll(self, mock_driver):
        """Testa ação de scroll"""
        action = Action('scroll', direction='down', duration=1)
        action.execute(mock_driver, 'android')
        
        mock_driver.swipe.assert_called_once()
        args = mock_driver.swipe.call_args
        assert args[0][0] == 540  # width/2
    
    def test_action_back(self, mock_driver):
        """Testa ação de voltar"""
        action = Action('back')
        action.execute(mock_driver, 'android')
        
        mock_driver.back.assert_called_once()
    
    def test_invalid_action_type(self):
        """Testa erro com tipo de ação inválido"""
        action = Action('invalid', param='value')
        
        with pytest.raises(ValueError, match='Tipo de ação desconhecido'):
            action.execute(None, 'android')


class TestScenario:
    """Testes para a classe Scenario"""
    
    def test_scenario_initialization(self):
        """Testa inicialização de cenário"""
        scenario = Scenario('Login Flow')
        
        assert scenario.name == 'Login Flow'
        assert len(scenario.actions) == 0
    
    def test_add_action(self):
        """Testa adição de ações"""
        scenario = Scenario('Test Scenario')
        action = Action('tap', xpath='//button')
        
        scenario.add_action(action)
        
        assert len(scenario.actions) == 1
        assert scenario.actions[0] == action
    
    def test_tap_helper(self):
        """Testa helper de tap"""
        scenario = Scenario('Test').tap(xpath='//button')
        
        assert len(scenario.actions) == 1
        assert scenario.actions[0].action_type == 'tap'
    
    def test_input_helper(self):
        """Testa helper de input"""
        scenario = Scenario('Test').input('hello', xpath='//input')
        
        assert len(scenario.actions) == 1
        assert scenario.actions[0].action_type == 'input'
        assert scenario.actions[0].params['text'] == 'hello'
    
    def test_wait_helper(self):
        """Testa helper de wait"""
        scenario = Scenario('Test').wait(timeout=2.0)
        
        assert len(scenario.actions) == 1
        assert scenario.actions[0].action_type == 'wait'
    
    def test_scroll_helper(self):
        """Testa helper de scroll"""
        scenario = Scenario('Test').scroll(direction='up', duration=0.5)
        
        assert len(scenario.actions) == 1
        assert scenario.actions[0].action_type == 'scroll'
    
    def test_fluent_api(self):
        """Testa API fluente (method chaining)"""
        scenario = (Scenario('Login')
                   .tap(xpath='//login')
                   .input('user@test.com', xpath='//email')
                   .input('password', xpath='//pass')
                   .tap(xpath='//submit'))
        
        assert len(scenario.actions) == 4
        assert scenario.name == 'Login'
    
    def test_multiple_taps(self):
        """Testa múltiplas ações de tap"""
        scenario = Scenario('Test')
        scenario.tap(id='button1')
        scenario.tap(id='button2')
        scenario.tap(id='button3')
        
        assert len(scenario.actions) == 3
        for action in scenario.actions:
            assert action.action_type == 'tap'
