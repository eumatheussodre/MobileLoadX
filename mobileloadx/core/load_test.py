"""
Classe principal do LoadTest que orquestra toda a execução do teste
"""

import time
import threading
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from .virtual_user import VirtualUser
from .scenario import Scenario
from ..metrics.collector import MetricsCollector
from ..reporting.results import TestResults
from ..config.loader import ConfigLoader

logger = logging.getLogger(__name__)


@dataclass
class PlatformConfig:
    """Configuração de plataforma (Android/iOS)"""
    platform: str  # "android" or "ios"
    app: str
    devices: List[str]
    capabilities: Dict[str, Any]


class LoadTest:
    """
    Classe principal para executar testes de carga em aplicativos mobile
    """
    
    def __init__(
        self,
        name: str,
        duration: int = 300,
        virtual_users: int = 1,
        ramp_up_time: int = 0,
        config_file: Optional[str] = None
    ):
        """
        Inicializa um teste de carga
        
        Args:
            name: Nome do teste
            duration: Duração do teste em segundos
            virtual_users: Número máximo de usuários virtuais
            ramp_up_time: Tempo para aumentar gradualmente os usuários
            config_file: Arquivo de configuração YAML (opcional)
        """
        self.name = name
        self.duration = duration
        self.max_virtual_users = virtual_users
        self.ramp_up_time = ramp_up_time
        
        self.platforms: List[PlatformConfig] = []
        self.scenarios: List[tuple[Scenario, int]] = []  # (scenario, weight)
        self.thresholds: Dict[str, float] = {}
        
        self.virtual_users_pool: List[VirtualUser] = []
        self.metrics_collector = MetricsCollector()
        self.is_running = False
        self.start_time = None
        self.results = None
        
        if config_file:
            self._load_from_config(config_file)
    
    def add_platform(
        self,
        platform: str,
        app: str,
        device: str = None,
        devices: List[str] = None,
        **capabilities
    ):
        """Adiciona configuração de plataforma (Android ou iOS)"""
        device_list = devices if devices else ([device] if device else [])
        
        platform_config = PlatformConfig(
            platform=platform.lower(),
            app=app,
            devices=device_list,
            capabilities=capabilities
        )
        self.platforms.append(platform_config)
        logger.info(f"Plataforma adicionada: {platform} com {len(device_list)} device(s)")
    
    def add_scenario(self, scenario: Scenario, weight: int = 100):
        """
        Adiciona um cenário de teste
        
        Args:
            scenario: Cenário a ser executado
            weight: Peso relativo do cenário (0-100)
        """
        self.scenarios.append((scenario, weight))
        logger.info(f"Cenário adicionado: {scenario.name} (weight: {weight})")
    
    def set_threshold(self, metric: str, value: float):
        """Define um threshold para uma métrica"""
        self.thresholds[metric] = value
    
    def _load_from_config(self, config_file: str):
        """Carrega configuração de arquivo YAML/JSON"""
        config = ConfigLoader.load(config_file)
        
        # Configurações do teste
        test_config = config.get('test', {})
        self.name = test_config.get('name', self.name)
        self.duration = test_config.get('duration', self.duration)
        
        # Usuários virtuais
        vu_config = config.get('virtual_users', {})
        self.max_virtual_users = vu_config.get('max', self.max_virtual_users)
        self.ramp_up_time = vu_config.get('ramp_up_time', self.ramp_up_time)
        
        # Plataformas
        for platform_data in config.get('platforms', []):
            for platform, details in platform_data.items():
                self.add_platform(
                    platform=platform,
                    app=details.get('app'),
                    device=details.get('device'),
                    devices=details.get('devices'),
                    **details.get('capabilities', {})
                )
        
        # Cenários
        for scenario_data in config.get('scenarios', []):
            scenario = Scenario.from_dict(scenario_data)
            weight = scenario_data.get('weight', 100)
            self.add_scenario(scenario, weight)
        
        # Thresholds
        for metric, value in config.get('thresholds', {}).items():
            self.set_threshold(metric, value)
    
    def _calculate_users_at_time(self, elapsed_time: float) -> int:
        """Calcula quantos usuários devem estar ativos em um dado momento"""
        if elapsed_time >= self.ramp_up_time:
            return self.max_virtual_users
        
        if self.ramp_up_time == 0:
            return self.max_virtual_users
        
        # Ramp-up linear
        progress = elapsed_time / self.ramp_up_time
        return int(progress * self.max_virtual_users)
    
    def _create_virtual_user(self, user_id: int, platform_config: PlatformConfig) -> VirtualUser:
        """Cria um usuário virtual"""
        device = platform_config.devices[user_id % len(platform_config.devices)] if platform_config.devices else None
        
        return VirtualUser(
            user_id=user_id,
            platform=platform_config.platform,
            app=platform_config.app,
            device=device,
            capabilities=platform_config.capabilities,
            scenarios=self.scenarios,
            metrics_collector=self.metrics_collector
        )
    
    def _spawn_users(self, target_users: int, current_users: int, platform_config: PlatformConfig):
        """Cria novos usuários virtuais quando necessário"""
        users_to_spawn = target_users - current_users
        
        if users_to_spawn <= 0:
            return []
        
        new_users = []
        for i in range(users_to_spawn):
            user_id = current_users + i
            user = self._create_virtual_user(user_id, platform_config)
            new_users.append(user)
            logger.debug(f"Usuário virtual {user_id} criado")
        
        return new_users
    
    def _user_lifecycle(self, user: VirtualUser, end_time: float):
        """Executa o lifecycle de um usuário virtual"""
        try:
            user.start()
            
            while time.time() < end_time and self.is_running:
                user.execute_scenario()
            
            user.stop()
        except Exception as e:
            logger.error(f"Erro no usuário {user.user_id}: {e}")
            user.stop()
    
    def run(self) -> TestResults:
        """
        Executa o teste de carga
        
        Returns:
            TestResults com os resultados do teste
        """
        if not self.platforms:
            raise ValueError("Nenhuma plataforma configurada")
        
        if not self.scenarios:
            raise ValueError("Nenhum cenário configurado")
        
        logger.info(f"Iniciando teste: {self.name}")
        logger.info(f"Duração: {self.duration}s | Usuários: {self.max_virtual_users} | Ramp-up: {self.ramp_up_time}s")
        
        self.is_running = True
        self.start_time = time.time()
        end_time = self.start_time + self.duration
        
        # Iniciar coletor de métricas
        self.metrics_collector.start()
        
        # Usar primeira plataforma (pode ser expandido para múltiplas)
        platform_config = self.platforms[0]
        
        active_users = []
        executor = ThreadPoolExecutor(max_workers=self.max_virtual_users)
        futures = []
        
        try:
            # Loop principal de controle de carga
            while time.time() < end_time and self.is_running:
                elapsed_time = time.time() - self.start_time
                target_users = self._calculate_users_at_time(elapsed_time)
                current_users = len(active_users)
                
                # Spawn novos usuários se necessário
                if target_users > current_users:
                    new_users = self._spawn_users(target_users, current_users, platform_config)
                    
                    for user in new_users:
                        active_users.append(user)
                        future = executor.submit(self._user_lifecycle, user, end_time)
                        futures.append(future)
                    
                    logger.info(f"Usuários ativos: {len(active_users)}/{target_users}")
                
                time.sleep(1)  # Check a cada segundo
            
            # Aguardar conclusão de todos os usuários
            logger.info("Aguardando conclusão dos usuários virtuais...")
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Erro na thread do usuário: {e}")
        
        finally:
            self.is_running = False
            executor.shutdown(wait=True)
            self.metrics_collector.stop()
        
        # Coletar e analisar resultados
        logger.info("Processando resultados...")
        self.results = self._generate_results()
        
        logger.info(f"Teste concluído: {self.name}")
        return self.results
    
    def _generate_results(self) -> TestResults:
        """Gera os resultados do teste"""
        metrics_data = self.metrics_collector.get_metrics()
        
        results = TestResults(
            test_name=self.name,
            start_time=self.start_time,
            duration=time.time() - self.start_time,
            max_virtual_users=self.max_virtual_users,
            metrics=metrics_data,
            thresholds=self.thresholds
        )
        
        return results
    
    def stop(self):
        """Para o teste prematuramente"""
        logger.warning("Parando teste...")
        self.is_running = False
