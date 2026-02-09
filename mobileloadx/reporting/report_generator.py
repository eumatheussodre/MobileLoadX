"""
Gerador de relatórios de performance
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from .results import TestResults

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Gera relatórios de resultados de testes"""
    
    def __init__(self, results: TestResults):
        self.results = results
    
    def generate_json(self, output_path: str = None) -> str:
        """
        Gera relatório em formato JSON
        
        Args:
            output_path: Caminho do arquivo de saída (opcional)
        
        Returns:
            JSON string do relatório
        """
        report_data = self.results.to_dict()
        json_str = json.dumps(report_data, indent=2, ensure_ascii=False)
        
        if output_path:
            Path(output_path).write_text(json_str, encoding='utf-8')
            logger.info(f"Relatório JSON gerado: {output_path}")
        
        return json_str
    
    def generate_html(self, output_path: str = "report.html"):
        """
        Gera relatório em formato HTML com gráficos
        
        Args:
            output_path: Caminho do arquivo de saída
        """
        html_content = self._create_html_report()
        
        Path(output_path).write_text(html_content, encoding='utf-8')
        logger.info(f"Relatório HTML gerado: {output_path}")
    
    def _create_html_report(self) -> str:
        """Cria conteúdo HTML do relatório"""
        results = self.results
        
        # Status do teste
        status = "✅ PASSOU" if results.passed_thresholds else "❌ FALHOU"
        status_color = "#28a745" if results.passed_thresholds else "#dc3545"
        
        # Thresholds
        threshold_rows = ""
        for metric, passed in results.check_thresholds().items():
            icon = "✅" if passed else "❌"
            threshold_value = results.thresholds.get(metric, "N/A")
            threshold_rows += f"""
                <tr>
                    <td>{icon}</td>
                    <td>{metric}</td>
                    <td>{threshold_value}</td>
                </tr>
            """
        
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Performance - {results.test_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
        }}
        
        h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .status {{
            display: inline-block;
            padding: 8px 16px;
            background: {status_color};
            border-radius: 5px;
            font-weight: bold;
            margin-top: 10px;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .metric-card {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 5px;
        }}
        
        .metric-card h3 {{
            font-size: 14px;
            color: #6c757d;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .metric-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .metric-card .unit {{
            font-size: 16px;
            color: #6c757d;
            margin-left: 5px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }}
        
        th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        
        .chart-container {{
            margin: 40px 0;
            height: 300px;
        }}
        
        section {{
            margin: 40px 0;
        }}
        
        h2 {{
            font-size: 24px;
            margin-bottom: 20px;
            color: #2c3e50;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 {results.test_name}</h1>
            <p>Início: {datetime.fromtimestamp(results.start_time).strftime('%d/%m/%Y %H:%M:%S')}</p>
            <p>Duração: {results.duration:.1f}s</p>
            <div class="status">{status}</div>
        </header>
        
        <div class="content">
            <!-- Métricas Principais -->
            <section>
                <h2>📈 Métricas Principais</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>Usuários Simultâneos</h3>
                        <div class="value">{results.max_concurrent_users}</div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>Total de Ações</h3>
                        <div class="value">{results.total_actions}</div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>Taxa de Sucesso</h3>
                        <div class="value">{results.success_rate:.1f}<span class="unit">%</span></div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>Taxa de Erro</h3>
                        <div class="value">{results.error_rate:.1f}<span class="unit">%</span></div>
                    </div>
                </div>
            </section>
            
            <!-- Tempos de Resposta -->
            <section>
                <h2>⏱️ Tempos de Resposta</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>Média</h3>
                        <div class="value">{results.response_time_avg:.0f}<span class="unit">ms</span></div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>Mediana (P50)</h3>
                        <div class="value">{results.response_time_p50:.0f}<span class="unit">ms</span></div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>P95</h3>
                        <div class="value">{results.response_time_p95:.0f}<span class="unit">ms</span></div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>P99</h3>
                        <div class="value">{results.response_time_p99:.0f}<span class="unit">ms</span></div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <canvas id="responseTimeChart"></canvas>
                </div>
            </section>
            
            <!-- Recursos do Device -->
            <section>
                <h2>📱 Recursos do Device</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>CPU Média</h3>
                        <div class="value">{results.avg_cpu:.1f}<span class="unit">%</span></div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>Memória Média</h3>
                        <div class="value">{results.avg_memory:.1f}<span class="unit">MB</span></div>
                    </div>
                    
                    <div class="metric-card">
                        <h3>Memória Pico</h3>
                        <div class="value">{results.peak_memory:.1f}<span class="unit">MB</span></div>
                    </div>
                </div>
            </section>
            
            <!-- Thresholds -->
            <section>
                <h2>🎯 Thresholds</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Status</th>
                            <th>Métrica</th>
                            <th>Threshold</th>
                        </tr>
                    </thead>
                    <tbody>
                        {threshold_rows}
                    </tbody>
                </table>
            </section>
        </div>
    </div>
    
    <script>
        // Gráfico de Tempo de Resposta
        const ctx = document.getElementById('responseTimeChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: ['Mínimo', 'Média', 'Mediana', 'P95', 'P99', 'Máximo'],
                datasets: [{{
                    label: 'Tempo de Resposta (ms)',
                    data: [
                        {results.response_time_min:.0f},
                        {results.response_time_avg:.0f},
                        {results.response_time_p50:.0f},
                        {results.response_time_p95:.0f},
                        {results.response_time_p99:.0f},
                        {results.response_time_max:.0f}
                    ],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(255, 159, 64, 0.7)',
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(153, 102, 255, 0.7)'
                    ],
                    borderColor: [
                        'rgba(75, 192, 192, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(255, 159, 64, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(153, 102, 255, 1)'
                    ],
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Tempo (ms)'
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
        """
        
        return html
    
    def generate_csv(self, output_path: str = "report.csv"):
        """
        Gera relatório em formato CSV com métricas de ações
        
        Args:
            output_path: Caminho do arquivo de saída
        """
        import csv
        
        action_metrics = self.results.metrics.get('action_metrics', [])
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if not action_metrics:
                return
            
            fieldnames = action_metrics[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(action_metrics)
        
        logger.info(f"Relatório CSV gerado: {output_path}")
