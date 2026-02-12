"""
Base classes para sistema de plugins do MobileLoadX
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging


logger = logging.getLogger(__name__)


@dataclass
class PluginInfo:
    """Informações sobre um plugin"""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = None


class Plugin(ABC):
    """Classe base para plugins do MobileLoadX"""
    
    def __init__(self):
        """Inicializa plugin"""
        self.logger = logging.getLogger(f'mobileloadx.plugin.{self.__class__.__name__}')
        self.config = {}
    
    @abstractmethod
    def get_info(self) -> PluginInfo:
        """Retorna informações do plugin"""
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Inicializa plugin com configuração
        
        Args:
            config: Dicionário de configuração
        
        Returns:
            True se inicialização foi bem-sucedida
        """
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Executa funcionalidade principal do plugin
        
        Args:
            **kwargs: Argumentos específicos do plugin
        
        Returns:
            Resultado da execução
        """
        pass
    
    def cleanup(self):
        """Limpa recursos do plugin"""
        pass


class ReporterPlugin(Plugin):
    """Plugin para gerar relatórios"""
    
    @abstractmethod
    def generate_report(self, results: Dict[str, Any], output_path: str) -> bool:
        """
        Gera relatório
        
        Args:
            results: Resultados do teste
            output_path: Caminho para salvar relatório
        
        Returns:
            True se sucesso
        """
        pass


class MetricsPlugin(Plugin):
    """Plugin para coletar métricas"""
    
    @abstractmethod
    def collect_metrics(self) -> Dict[str, Any]:
        """
        Coleta métricas
        
        Returns:
            Dicionário com métricas coletadas
        """
        pass


class ActionPlugin(Plugin):
    """Plugin para ações customizadas"""
    
    @abstractmethod
    def execute_action(self, action_name: str, **params) -> bool:
        """
        Executa ação customizada
        
        Args:
            action_name: Nome da ação
            **params: Parâmetros da ação
        
        Returns:
            True se ação foi bem-sucedida
        """
        pass


class PluginManager:
    """Gerenciador de plugins"""
    
    def __init__(self):
        """Inicializa gerenciador"""
        self.plugins: Dict[str, Plugin] = {}
        self.logger = logging.getLogger('mobileloadx.plugin_manager')
    
    def register_plugin(self, name: str, plugin: Plugin) -> bool:
        """
        Registra um plugin
        
        Args:
            name: Nome do plugin
            plugin: Instância do plugin
        
        Returns:
            True se registro foi bem-sucedido
        """
        if name in self.plugins:
            self.logger.warning(f"Plugin '{name}' já está registrado")
            return False
        
        try:
            info = plugin.get_info()
            self.plugins[name] = plugin
            self.logger.info(f"Plugin registrado: {name} v{info.version}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao registrar plugin '{name}': {e}")
            return False
    
    def unregister_plugin(self, name: str) -> bool:
        """Remove plugin"""
        if name not in self.plugins:
            self.logger.warning(f"Plugin '{name}' não encontrado")
            return False
        
        plugin = self.plugins[name]
        plugin.cleanup()
        del self.plugins[name]
        self.logger.info(f"Plugin removido: {name}")
        return True
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Obtém plugin por nome"""
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[PluginInfo]:
        """Lista informações de todos os plugins registrados"""
        plugins_info = []
        for plugin in self.plugins.values():
            plugins_info.append(plugin.get_info())
        return plugins_info
    
    def execute_hook(self, hook_name: str, **kwargs) -> List[Any]:
        """
        Executa hook em todos os plugins registrados
        
        Args:
            hook_name: Nome do hook
            **kwargs: Argumentos do hook
        
        Returns:
            Lista de resultados
        """
        results = []
        for name, plugin in self.plugins.items():
            if hasattr(plugin, hook_name):
                try:
                    method = getattr(plugin, hook_name)
                    result = method(**kwargs)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Erro ao executar {hook_name} em {name}: {e}")
        
        return results


# Instância global do gerenciador
_plugin_manager = PluginManager()


def get_plugin_manager() -> PluginManager:
    """Obtém instância global do gerenciador de plugins"""
    return _plugin_manager
