"""
Exemplo de plugin para MobileLoadX
"""

from typing import Dict, Any
from .base import Plugin, PluginInfo


class ExamplePlugin(Plugin):
    """Plugin de exemplo"""
    
    def get_info(self) -> PluginInfo:
        """Informações do plugin"""
        return PluginInfo(
            name='Example Plugin',
            version='1.0.0',
            description='Plugin de exemplo para demonstrar o sistema de plugins',
            author='MobileLoadX Team',
            dependencies=['requests']
        )
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Inicializa plugin"""
        self.logger.info("Inicializando Example Plugin")
        self.config = config
        return True
    
    def execute(self, **kwargs) -> Any:
        """Executa plugin"""
        self.logger.info(f"Executando Example Plugin com kwargs: {kwargs}")
        return {"status": "executed", "result": kwargs}


class CustomMetricsPlugin(Plugin):
    """Plugin para coletar métricas customizadas"""
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name='Custom Metrics',
            version='1.0.0',
            description='Coleta métricas customizadas adicionais',
            author='MobileLoadX Team'
        )
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Inicializa coletor"""
        self.logger.info("Inicializando Custom Metrics Plugin")
        self.metrics_config = config.get('metrics', {})
        return True
    
    def execute(self, **kwargs) -> Any:
        """Coleta e retorna métricas"""
        # Aqui você pode adicionar lógica para coletar métricas customizadas
        metrics = {
            'fps': 60,
            'frame_drops': 12,
            'lag_spikes': 3,
            'custom_metric_1': kwargs.get('value1', 0),
        }
        return metrics


class DataExportPlugin(Plugin):
    """Plugin para exportar dados """
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name='Data Export',
            version='1.0.0',
            description='Exporta dados de teste em múltiplos formatos',
            author='MobileLoadX Team',
            dependencies=['pandas', 'openpyxl']
        )
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Inicializa exportador"""
        self.logger.info("Inicializando Data Export Plugin")
        self.export_config = config.get('export', {})
        return True
    
    def execute(self, **kwargs) -> Any:
        """Exporta dados"""
        format_type = kwargs.get('format', 'csv')
        output_path = kwargs.get('output_path', './export')
        
        self.logger.info(f"Exportando dados em formato {format_type} para {output_path}")
        
        if format_type == 'csv':
            return self._export_csv(output_path)
        elif format_type == 'json':
            return self._export_json(output_path)
        elif format_type == 'excel':
            return self._export_excel(output_path)
        else:
            return {"status": "error", "message": f"Formato desconhecido: {format_type}"}
    
    def _export_csv(self, path: str) -> Dict[str, Any]:
        """Exporta em CSV"""
        self.logger.debug(f"Exportando CSV para {path}")
        return {"status": "exported", "format": "csv", "path": path}
    
    def _export_json(self, path: str) -> Dict[str, Any]:
        """Exporta em JSON"""
        self.logger.debug(f"Exportando JSON para {path}")
        return {"status": "exported", "format": "json", "path": path}
    
    def _export_excel(self, path: str) -> Dict[str, Any]:
        """Exporta em Excel"""
        self.logger.debug(f"Exportando Excel para {path}")
        return {"status": "exported", "format": "excel", "path": path}
