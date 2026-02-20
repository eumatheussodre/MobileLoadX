"""
Coletor de métricas do device (CPU, memória, bateria, etc)
"""

import time
import subprocess
import threading
import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Coleta métricas de performance do device durante o teste
    """
    
    def __init__(self, interval: float = 1.0):
        """
        Args:
            interval: Intervalo de coleta em segundos
        """
        self.interval = interval
        self.is_collecting = False
        self.collection_thread = None
        
        # Armazenamento de métricas
        self.device_metrics: List[Dict[str, Any]] = []
        self.action_metrics: List[Dict[str, Any]] = []
        
        # Lock para thread-safety
        self.lock = threading.Lock()
    
    def start(self):
        """Inicia a coleta de métricas"""
        if self.is_collecting:
            logger.warning("Coletor já está ativo")
            return
        
        logger.info("Iniciando coleta de métricas")
        self.is_collecting = True
        self.collection_thread = threading.Thread(target=self._collect_loop, daemon=True)
        self.collection_thread.start()
    
    def stop(self):
        """Para a coleta de métricas"""
        logger.info("Parando coleta de métricas")
        self.is_collecting = False
        
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
    
    def _collect_loop(self):
        """Loop principal de coleta"""
        while self.is_collecting:
            try:
                metrics = self._collect_device_metrics()
                
                with self.lock:
                    self.device_metrics.append(metrics)
                
            except Exception as e:
                logger.error(f"Erro ao coletar métricas: {e}")
            
            time.sleep(self.interval)
    
    def _collect_device_metrics(self) -> Dict[str, Any]:
        """
        Coleta métricas do device conforme configurado em self.collect.

        Nota: Implementação simplificada. Em produção, usar ferramentas
        específicas como adb para Android e Instruments para iOS.
        FPS está planejado (não implementado).
        """
        timestamp = datetime.now()
        metrics = {"timestamp": timestamp.isoformat()}

        if "cpu" in self.collect:
            metrics["cpu"] = self._get_cpu_usage()
        if "memory" in self.collect:
            metrics["memory"] = self._get_memory_usage()
        if "battery" in self.collect:
            metrics["battery"] = self._get_battery_info()
        if "network" in self.collect:
            metrics["network"] = self._get_network_stats()
        if "fps" in self.collect:
            # FPS: planejado (coleta via adb/iOS ainda não implementada)
            metrics["fps"] = None

        return metrics
    
    def _get_cpu_usage(self) -> Optional[float]:
        """
        Obtém uso de CPU do app
        
        Android: adb shell dumpsys cpuinfo | grep <package>
        iOS: instruments -t 'Time Profiler'
        """
        try:
            # Exemplo simplificado para Android
            # Em produção, precisa do package name e parsing adequado
            result = subprocess.run(
                ['adb', 'shell', 'dumpsys', 'cpuinfo'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            # Parse básico (precisa ser melhorado)
            # Retorna um valor simulado para demonstração
            return 45.5
            
        except Exception as e:
            logger.debug(f"Erro ao coletar CPU: {e}")
            return None
    
    def _get_memory_usage(self) -> Optional[Dict[str, float]]:
        """
        Obtém uso de memória do app
        
        Android: adb shell dumpsys meminfo <package>
        iOS: instruments -t 'Allocations'
        """
        try:
            # Exemplo simplificado
            return {
                "total": 250.5,  # MB
                "heap": 150.2,
                "native": 80.3,
                "graphics": 20.0
            }
        except Exception as e:
            logger.debug(f"Erro ao coletar memória: {e}")
            return None
    
    def _get_battery_info(self) -> Optional[Dict[str, Any]]:
        """
        Obtém informações de bateria
        
        Android: adb shell dumpsys battery
        iOS: Acesso via IOKit framework
        """
        try:
            # Exemplo simplificado
            return {
                "level": 85,  # %
                "temperature": 32.5,  # °C
                "voltage": 3850  # mV
            }
        except Exception as e:
            logger.debug(f"Erro ao coletar bateria: {e}")
            return None
    
    def _get_network_stats(self) -> Optional[Dict[str, int]]:
        """
        Obtém estatísticas de rede
        
        Android: adb shell cat /proc/net/xt_qtaguid/stats
        iOS: Network Link Conditioner
        """
        try:
            # Exemplo simplificado
            return {
                "rx_bytes": 1024000,  # bytes recebidos
                "tx_bytes": 512000,   # bytes enviados
                "rx_packets": 1500,
                "tx_packets": 800
            }
        except Exception as e:
            logger.debug(f"Erro ao coletar rede: {e}")
            return None
    
    def record_action(
        self,
        user_id: int,
        scenario: str,
        duration: float,
        success: bool,
        error: Optional[str] = None
    ):
        """
        Registra métrica de uma ação executada
        
        Args:
            user_id: ID do usuário virtual
            scenario: Nome do cenário
            duration: Duração da execução (segundos)
            success: Se foi bem-sucedida
            error: Mensagem de erro (se houver)
        """
        with self.lock:
            self.action_metrics.append({
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "scenario": scenario,
                "duration": duration,
                "success": success,
                "error": error
            })
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Retorna todas as métricas coletadas
        
        Returns:
            Dicionário com métricas de device e ações
        """
        with self.lock:
            return {
                "device_metrics": self.device_metrics.copy(),
                "action_metrics": self.action_metrics.copy(),
                "summary": self._calculate_summary()
            }
    
    def _calculate_summary(self) -> Dict[str, Any]:
        """Calcula estatísticas resumidas"""
        if not self.action_metrics:
            return {}
        
        # Calcular estatísticas de ações
        durations = [m['duration'] for m in self.action_metrics]
        successes = sum(1 for m in self.action_metrics if m['success'])
        total_actions = len(self.action_metrics)
        
        # Agrupar por cenário
        scenarios_stats = defaultdict(lambda: {'count': 0, 'durations': []})
        for metric in self.action_metrics:
            scenario = metric['scenario']
            scenarios_stats[scenario]['count'] += 1
            scenarios_stats[scenario]['durations'].append(metric['duration'])
        
        # Calcular percentis
        durations_sorted = sorted(durations)
        p50 = durations_sorted[len(durations_sorted) // 2] if durations_sorted else 0
        p95_idx = int(len(durations_sorted) * 0.95)
        p95 = durations_sorted[p95_idx] if durations_sorted else 0
        p99_idx = int(len(durations_sorted) * 0.99)
        p99 = durations_sorted[p99_idx] if durations_sorted else 0
        
        # Métricas de device (médias)
        cpu_values = [m['cpu'] for m in self.device_metrics if m.get('cpu') is not None]
        avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0
        
        memory_total_values = [
            m['memory']['total'] for m in self.device_metrics
            if m.get('memory') and isinstance(m.get('memory'), dict) and 'total' in m.get('memory', {})
        ]
        avg_memory = sum(memory_total_values) / len(memory_total_values) if memory_total_values else 0
        peak_memory = max(memory_total_values) if memory_total_values else 0
        
        return {
            "total_actions": total_actions,
            "successful_actions": successes,
            "failed_actions": total_actions - successes,
            "success_rate": (successes / total_actions * 100) if total_actions > 0 else 0,
            "error_rate": ((total_actions - successes) / total_actions * 100) if total_actions > 0 else 0,
            
            "response_time": {
                "min": min(durations) if durations else 0,
                "max": max(durations) if durations else 0,
                "mean": sum(durations) / len(durations) if durations else 0,
                "median": p50,
                "p95": p95,
                "p99": p99
            },
            
            "device": {
                "avg_cpu": avg_cpu,
                "avg_memory": avg_memory,
                "peak_memory": peak_memory
            },
            
            "scenarios": {
                name: {
                    "count": stats['count'],
                    "avg_duration": sum(stats['durations']) / len(stats['durations'])
                }
                for name, stats in scenarios_stats.items()
            }
        }
