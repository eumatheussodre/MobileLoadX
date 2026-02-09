"""
Classe que representa um cenário de teste (sequência de ações)
"""

import time
import logging
from typing import List, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)


class Action:
    """Representa uma ação individual no cenário"""
    
    def __init__(self, action_type: str, **params):
        self.action_type = action_type
        self.params = params
    
    def execute(self, driver, platform: str):
        """Executa a ação no driver"""
        if self.action_type == "tap":
            self._tap(driver, platform)
        elif self.action_type == "input":
            self._input(driver)
        elif self.action_type == "wait":
            self._wait()
        elif self.action_type == "scroll":
            self._scroll(driver, platform)
        elif self.action_type == "swipe":
            self._swipe(driver)
        elif self.action_type == "back":
            self._back(driver)
        else:
            raise ValueError(f"Tipo de ação desconhecido: {self.action_type}")
    
    def _find_element(self, driver, platform: str):
        """Encontra elemento baseado em diferentes locators"""
        wait = WebDriverWait(driver, self.params.get('timeout', 10))
        
        if 'id' in self.params:
            if platform == "android":
                locator = (By.ID, self.params['id'])
            else:  # iOS
                locator = (By.ID, self.params['id'])
        elif 'xpath' in self.params:
            locator = (By.XPATH, self.params['xpath'])
        elif 'accessibility_id' in self.params:
            locator = (By.ACCESSIBILITY_ID, self.params['accessibility_id'])
        elif 'class_name' in self.params:
            locator = (By.CLASS_NAME, self.params['class_name'])
        else:
            raise ValueError("Nenhum locator válido fornecido")
        
        element = wait.until(EC.presence_of_element_located(locator))
        return element
    
    def _tap(self, driver, platform: str):
        """Ação de tap/click em elemento"""
        element = self._find_element(driver, platform)
        element.click()
    
    def _input(self, driver):
        """Ação de input de texto"""
        text = self.params.get('text', '')
        
        # Se há um elemento específico, usa ele, senão busca o elemento ativo
        if any(k in self.params for k in ['id', 'xpath', 'accessibility_id', 'class_name']):
            element = self._find_element(driver, 'android')  # Plataforma não importa aqui
            element.send_keys(text)
        else:
            # Envia para o elemento ativo
            driver.switch_to.active_element.send_keys(text)
    
    def _wait(self):
        """Ação de espera"""
        timeout = self.params.get('timeout', 1)
        time.sleep(timeout)
    
    def _scroll(self, driver, platform: str):
        """Ação de scroll"""
        direction = self.params.get('direction', 'down')
        duration = self.params.get('duration', 1)
        
        size = driver.get_window_size()
        start_x = size['width'] // 2
        
        if direction == 'down':
            start_y = size['height'] * 0.8
            end_y = size['height'] * 0.2
        elif direction == 'up':
            start_y = size['height'] * 0.2
            end_y = size['height'] * 0.8
        else:
            raise ValueError(f"Direção inválida: {direction}")
        
        driver.swipe(start_x, start_y, start_x, end_y, int(duration * 1000))
    
    def _swipe(self, driver):
        """Ação de swipe customizado"""
        start_x = self.params.get('start_x')
        start_y = self.params.get('start_y')
        end_x = self.params.get('end_x')
        end_y = self.params.get('end_y')
        duration = self.params.get('duration', 1)
        
        driver.swipe(start_x, start_y, end_x, end_y, int(duration * 1000))
    
    def _back(self, driver):
        """Ação de voltar (Android back button ou iOS navigation)"""
        driver.back()


class Scenario:
    """
    Representa um cenário de teste (conjunto de ações)
    """
    
    def __init__(self, name: str):
        self.name = name
        self.actions: List[Action] = []
    
    def add_action(self, action: Action):
        """Adiciona uma ação ao cenário"""
        self.actions.append(action)
    
    def tap(self, **locator):
        """Helper: Adiciona ação de tap"""
        self.add_action(Action("tap", **locator))
        return self
    
    def input(self, text: str, **locator):
        """Helper: Adiciona ação de input"""
        params = {"text": text}
        params.update(locator)
        self.add_action(Action("input", **params))
        return self
    
    def wait(self, timeout: float = 1):
        """Helper: Adiciona ação de wait"""
        self.add_action(Action("wait", timeout=timeout))
        return self
    
    def scroll(self, direction: str = "down", duration: float = 1):
        """Helper: Adiciona ação de scroll"""
        self.add_action(Action("scroll", direction=direction, duration=duration))
        return self
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1):
        """Helper: Adiciona ação de swipe"""
        self.add_action(Action("swipe", start_x=start_x, start_y=start_y, 
                              end_x=end_x, end_y=end_y, duration=duration))
        return self
    
    def back(self):
        """Helper: Adiciona ação de back"""
        self.add_action(Action("back"))
        return self
    
    def execute(self, driver, platform: str):
        """
        Executa todas as ações do cenário
        
        Args:
            driver: Appium WebDriver
            platform: "android" ou "ios"
        """
        logger.debug(f"Executando cenário: {self.name} ({len(self.actions)} ações)")
        
        for idx, action in enumerate(self.actions):
            try:
                logger.debug(f"  Ação {idx + 1}/{len(self.actions)}: {action.action_type}")
                action.execute(driver, platform)
            except Exception as e:
                logger.error(f"Erro na ação {idx + 1} ({action.action_type}): {e}")
                raise
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Scenario':
        """
        Cria um cenário a partir de dicionário (usado para carregar de YAML)
        
        Args:
            data: Dicionário com 'name' e 'actions'
        
        Returns:
            Scenario configurado
        """
        scenario = cls(data['name'])
        
        for action_data in data.get('actions', []):
            # Cada ação é um dicionário com um único key (tipo da ação)
            action_type = list(action_data.keys())[0]
            action_params = action_data[action_type]
            
            scenario.add_action(Action(action_type, **action_params))
        
        return scenario
