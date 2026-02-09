"""
Classe para armazenar resultados dos testes
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime


@dataclass
class TestResults:
    """Armazena os resultados de um teste de carga"""
    
    test_name: str
    start_time: float
    duration: float
    max_virtual_users: int
    metrics: Dict[str, Any]
    thresholds: Dict[str, float]
    
    @property
    def end_time(self) -> float:
        """Timestamp de fim do teste"""
        return self.start_time + self.duration
    
    @property
    def summary(self) -> Dict[str, Any]:
        """Resumo das métricas"""
        return self.metrics.get('summary', {})
    
    @property
    def max_concurrent_users(self) -> int:
        """Número máximo de usuários concorrentes"""
        return self.max_virtual_users
    
    @property
    def total_actions(self) -> int:
        """Total de ações executadas"""
        return self.summary.get('total_actions', 0)
    
    @property
    def successful_actions(self) -> int:
        """Total de ações bem-sucedidas"""
        return self.summary.get('successful_actions', 0)
    
    @property
    def failed_actions(self) -> int:
        """Total de ações que falharam"""
        return self.summary.get('failed_actions', 0)
    
    @property
    def success_rate(self) -> float:
        """Taxa de sucesso (%)"""
        return self.summary.get('success_rate', 0.0)
    
    @property
    def error_rate(self) -> float:
        """Taxa de erro (%)"""
        return self.summary.get('error_rate', 0.0)
    
    @property
    def avg_cpu(self) -> float:
        """CPU média (%)"""
        return self.summary.get('device', {}).get('avg_cpu', 0.0)
    
    @property
    def avg_memory(self) -> float:
        """Memória média (MB)"""
        return self.summary.get('device', {}).get('avg_memory', 0.0)
    
    @property
    def peak_memory(self) -> float:
        """Memória pico (MB)"""
        return self.summary.get('device', {}).get('peak_memory', 0.0)
    
    @property
    def response_time_avg(self) -> float:
        """Tempo de resposta médio (ms)"""
        return self.summary.get('response_time', {}).get('mean', 0.0) * 1000
    
    @property
    def response_time_p50(self) -> float:
        """Tempo de resposta P50/mediana (ms)"""
        return self.summary.get('response_time', {}).get('median', 0.0) * 1000
    
    @property
    def response_time_p95(self) -> float:
        """Tempo de resposta P95 (ms)"""
        return self.summary.get('response_time', {}).get('p95', 0.0) * 1000
    
    @property
    def response_time_p99(self) -> float:
        """Tempo de resposta P99 (ms)"""
        return self.summary.get('response_time', {}).get('p99', 0.0) * 1000
    
    @property
    def response_time_min(self) -> float:
        """Tempo de resposta mínimo (ms)"""
        return self.summary.get('response_time', {}).get('min', 0.0) * 1000
    
    @property
    def response_time_max(self) -> float:
        """Tempo de resposta máximo (ms)"""
        return self.summary.get('response_time', {}).get('max', 0.0) * 1000
    
    def check_thresholds(self) -> Dict[str, bool]:
        """
        Verifica se os thresholds foram atingidos
        
        Returns:
            Dicionário com resultado de cada threshold
        """
        results = {}
        
        for metric, threshold in self.thresholds.items():
            if metric == 'cpu_max':
                results[metric] = self.avg_cpu <= threshold
            elif metric == 'memory_max':
                results[metric] = self.peak_memory <= threshold
            elif metric == 'response_time_p95':
                results[metric] = self.response_time_p95 <= threshold
            elif metric == 'error_rate_max':
                results[metric] = self.error_rate <= threshold
            else:
                results[metric] = None  # Threshold desconhecido
        
        return results
    
    @property
    def passed_thresholds(self) -> bool:
        """Verifica se todos os thresholds passaram"""
        threshold_results = self.check_thresholds()
        return all(v for v in threshold_results.values() if v is not None)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte resultados para dicionário"""
        return {
            "test_name": self.test_name,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(self.end_time).isoformat(),
            "duration": self.duration,
            "max_virtual_users": self.max_virtual_users,
            "summary": {
                "actions": {
                    "total": self.total_actions,
                    "successful": self.successful_actions,
                    "failed": self.failed_actions,
                    "success_rate": self.success_rate,
                    "error_rate": self.error_rate
                },
                "response_time": {
                    "min": self.response_time_min,
                    "max": self.response_time_max,
                    "avg": self.response_time_avg,
                    "p50": self.response_time_p50,
                    "p95": self.response_time_p95,
                    "p99": self.response_time_p99
                },
                "device": {
                    "avg_cpu": self.avg_cpu,
                    "avg_memory": self.avg_memory,
                    "peak_memory": self.peak_memory
                }
            },
            "thresholds": self.thresholds,
            "threshold_results": self.check_thresholds(),
            "passed": self.passed_thresholds,
            "metrics": self.metrics
        }
