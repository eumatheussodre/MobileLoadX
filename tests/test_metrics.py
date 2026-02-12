"""
Testes para o coletor de métricas
"""

import pytest
import time
from unittest.mock import Mock, patch
from mobileloadx.metrics.collector import MetricsCollector


class TestMetricsCollector:
    """Testes para a classe MetricsCollector"""
    
    def test_initialization(self):
        """Testa inicialização do coletor"""
        collector = MetricsCollector(interval=0.5)
        
        assert collector.interval == 0.5
        assert collector.is_collecting is False
        assert len(collector.device_metrics) == 0
        assert len(collector.action_metrics) == 0
    
    def test_default_interval(self):
        """Testa intervalo padrão"""
        collector = MetricsCollector()
        
        assert collector.interval == 1.0
    
    def test_start_collection(self):
        """Testa início da coleta"""
        collector = MetricsCollector()
        collector.start()
        
        assert collector.is_collecting is True
        assert collector.collection_thread is not None
        
        # Cleanup
        collector.stop()
    
    def test_stop_collection(self):
        """Testa parada da coleta"""
        collector = MetricsCollector()
        collector.start()
        
        assert collector.is_collecting is True
        
        collector.stop()
        
        assert collector.is_collecting is False
    
    def test_start_twice_warning(self, caplog):
        """Testa se não inicia coleta duas vezes"""
        import logging
        caplog.set_level(logging.WARNING)
        
        collector = MetricsCollector()
        collector.start()
        collector.start()  # Segunda vez
        
        collector.stop()
        
        # Verificar se há aviso
        assert 'já está ativo' in caplog.text or collector.is_collecting
    
    def test_metrics_collection_loop(self):
        """Testa se métricas são coletadas"""
        collector = MetricsCollector(interval=0.1)
        
        with patch.object(collector, '_collect_device_metrics') as mock_collect:
            mock_collect.return_value = {
                'timestamp': '2024-01-01T00:00:00',
                'cpu': 45.5,
                'memory': {'total': 250, 'heap': 150}
            }
            
            collector.start()
            time.sleep(0.3)  # Dar tempo para coletar
            collector.stop()
            
            # Deve ter coletado pelo menos uma vez
            assert collector._collect_device_metrics.called
    
    def test_collect_device_metrics_structure(self):
        """Testa estrutura das métricas coletadas"""
        collector = MetricsCollector()
        
        with patch.object(collector, '_get_cpu_usage', return_value=45.5):
            with patch.object(collector, '_get_memory_usage', return_value={'total': 250}):
                with patch.object(collector, '_get_battery_info', return_value={'level': 85}):
                    with patch.object(collector, '_get_network_stats', return_value={}):
                        metrics = collector._collect_device_metrics()
        
        assert 'timestamp' in metrics
        assert 'cpu' in metrics
        assert 'memory' in metrics
        assert 'battery' in metrics
        assert 'network' in metrics
    
    def test_thread_safety(self):
        """Testa thread-safety do lock"""
        collector = MetricsCollector()
        
        # Verificar se lock foi inicializado
        assert collector.lock is not None
    
    def test_cpu_usage_collection(self):
        """Testa coleta de CPU (mock)"""
        collector = MetricsCollector()
        
        cpu = collector._get_cpu_usage()
        
        # Com adb pode falhar, mas não deve lançar erro crítico
        assert cpu is None or isinstance(cpu, (int, float))
    
    def test_memory_usage_collection(self):
        """Testa coleta de memória (mock)"""
        collector = MetricsCollector()
        
        memory = collector._get_memory_usage()
        
        assert memory is None or isinstance(memory, dict)
        if memory:
            assert 'total' in memory
            assert 'heap' in memory
    
    def test_battery_info_collection(self):
        """Testa coleta de bateria (mock)"""
        collector = MetricsCollector()
        
        battery = collector._get_battery_info()
        
        assert battery is None or isinstance(battery, dict)
        if battery:
            assert 'level' in battery or 'temperature' in battery
    
    def test_metrics_storage(self):
        """Testa armazenamento de métricas"""
        collector = MetricsCollector()
        
        metric1 = {'timestamp': '2024-01-01T00:00:00', 'cpu': 45}
        metric2 = {'timestamp': '2024-01-01T00:00:01', 'cpu': 50}
        
        with collector.lock:
            collector.device_metrics.append(metric1)
            collector.device_metrics.append(metric2)
        
        assert len(collector.device_metrics) == 2
        assert collector.device_metrics[0]['cpu'] == 45
        assert collector.device_metrics[1]['cpu'] == 50
