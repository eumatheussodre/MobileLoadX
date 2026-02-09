"""
Classe que representa um usuário virtual executando ações no app
"""

import random
import time
import logging
from typing import List, Dict, Any, Optional
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions

from .scenario import Scenario

logger = logging.getLogger(__name__)


class VirtualUser:
    """
    Representa um usuário virtual que executa cenários no aplicativo
    """
    
    def __init__(
        self,
        user_id: int,
        platform: str,
        app: str,
        device: Optional[str] = None,
        capabilities: Dict[str, Any] = None,
        scenarios: List[tuple] = None,
        metrics_collector = None
    ):
        """
        Inicializa um usuário virtual
        
        Args:
            user_id: ID único do usuário
            platform: "android" ou "ios"
            app: Caminho do app
            device: Device ID (opcional)
            capabilities: Capabilities extras do Appium
            scenarios: Lista de (Scenario, weight)
            metrics_collector: Coletor de métricas
        """
        self.user_id = user_id
        self.platform = platform.lower()
        self.app = app
        self.device = device
        self.capabilities = capabilities or {}
        self.scenarios = scenarios or []
        self.metrics_collector = metrics_collector
        
        self.driver = None
        self.is_active = False
        self.actions_executed = 0
        self.errors = 0
        self.start_time = None
    
    def start(self):
        """Inicia a sessão do Appium"""
        try:
            logger.debug(f"Usuário {self.user_id}: Iniciando sessão Appium")
            
            if self.platform == "android":
                options = UiAutomator2Options()
                options.app = self.app
                if self.device:
                    options.udid = self.device
                options.automation_name = "UiAutomator2"
            elif self.platform == "ios":
                options = XCUITestOptions()
                options.app = self.app
                if self.device:
                    options.udid = self.device
                options.automation_name = "XCUITest"
            else:
                raise ValueError(f"Plataforma não suportada: {self.platform}")
            
            # Adicionar capabilities customizadas
            for key, value in self.capabilities.items():
                setattr(options, key, value)
            
            # Conectar ao Appium server
            appium_server_url = self.capabilities.get('appium_server_url', 'http://localhost:4723')
            self.driver = webdriver.Remote(appium_server_url, options=options)
            
            self.is_active = True
            self.start_time = time.time()
            
            logger.info(f"Usuário {self.user_id}: Sessão iniciada com sucesso")
            
        except Exception as e:
            logger.error(f"Usuário {self.user_id}: Erro ao iniciar sessão: {e}")
            self.errors += 1
            raise
    
    def stop(self):
        """Encerra a sessão do Appium"""
        if self.driver:
            try:
                self.driver.quit()
                logger.debug(f"Usuário {self.user_id}: Sessão encerrada")
            except Exception as e:
                logger.error(f"Usuário {self.user_id}: Erro ao encerrar: {e}")
        
        self.is_active = False
    
    def _select_scenario(self) -> Scenario:
        """Seleciona um cenário baseado nos pesos"""
        if not self.scenarios:
            raise ValueError("Nenhum cenário configurado")
        
        # Seleção ponderada
        scenarios_list = [s[0] for s in self.scenarios]
        weights = [s[1] for s in self.scenarios]
        
        return random.choices(scenarios_list, weights=weights)[0]
    
    def execute_scenario(self):
        """
        Executa um cenário aleatório (baseado em pesos)
        """
        if not self.is_active or not self.driver:
            logger.warning(f"Usuário {self.user_id}: Tentativa de executar sem sessão ativa")
            return
        
        scenario = self._select_scenario()
        
        try:
            logger.debug(f"Usuário {self.user_id}: Executando cenário '{scenario.name}'")
            start_time = time.time()
            
            scenario.execute(self.driver, self.platform)
            
            elapsed_time = time.time() - start_time
            self.actions_executed += 1
            
            # Coletar métrica de tempo de execução
            if self.metrics_collector:
                self.metrics_collector.record_action(
                    user_id=self.user_id,
                    scenario=scenario.name,
                    duration=elapsed_time,
                    success=True
                )
            
            logger.debug(f"Usuário {self.user_id}: Cenário '{scenario.name}' executado em {elapsed_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Usuário {self.user_id}: Erro ao executar cenário '{scenario.name}': {e}")
            self.errors += 1
            
            if self.metrics_collector:
                self.metrics_collector.record_action(
                    user_id=self.user_id,
                    scenario=scenario.name,
                    duration=0,
                    success=False,
                    error=str(e)
                )
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do usuário"""
        uptime = time.time() - self.start_time if self.start_time else 0
        
        return {
            "user_id": self.user_id,
            "platform": self.platform,
            "device": self.device,
            "is_active": self.is_active,
            "uptime": uptime,
            "actions_executed": self.actions_executed,
            "errors": self.errors,
            "success_rate": (self.actions_executed - self.errors) / self.actions_executed * 100 if self.actions_executed > 0 else 0
        }
