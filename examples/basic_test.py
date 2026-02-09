"""
Exemplo de teste de performance usando Python API
"""

from mobileloadx import LoadTest, Scenario

# Criar cenário de login
login_scenario = Scenario("Login Flow")
login_scenario.wait(2)
login_scenario.tap(id="username")
login_scenario.input("user@example.com")
login_scenario.tap(id="password")
login_scenario.input("password123")
login_scenario.tap(id="loginButton")
login_scenario.wait(5)

# Criar cenário de navegação
browse_scenario = Scenario("Browse Products")
browse_scenario.tap(id="productsTab")
browse_scenario.wait(1)
browse_scenario.scroll(direction="down", duration=2)
browse_scenario.tap(xpath="//android.widget.TextView[@text='Product 1']")
browse_scenario.wait(2)

# Configurar teste de carga
test = LoadTest(
    name="App Performance Test",
    duration=300,  # 5 minutos
    virtual_users=50,
    ramp_up_time=60  # 1 minuto
)

# Adicionar plataforma Android
test.add_platform(
    platform="android",
    app="./app-release.apk",
    device="emulator-5554",
    appium_server_url="http://localhost:4723",
    platformVersion="13.0",
    automationName="UiAutomator2"
)

# Adicionar cenários com pesos
test.add_scenario(login_scenario, weight=70)  # 70% dos usuários
test.add_scenario(browse_scenario, weight=30)  # 30% dos usuários

# Definir thresholds
test.set_threshold('cpu_max', 80)
test.set_threshold('memory_max', 300)
test.set_threshold('response_time_p95', 2000)
test.set_threshold('error_rate_max', 5)

# Executar teste
print("🚀 Iniciando teste de performance...")
results = test.run()

# Exibir resultados
print("\n📊 RESULTADOS DO TESTE")
print("=" * 50)
print(f"Teste: {results.test_name}")
print(f"Duração: {results.duration:.1f}s")
print(f"Usuários simultâneos: {results.max_concurrent_users}")
print(f"\n📈 MÉTRICAS DE AÇÕES")
print(f"  Total de ações: {results.total_actions}")
print(f"  Bem-sucedidas: {results.successful_actions}")
print(f"  Falhas: {results.failed_actions}")
print(f"  Taxa de sucesso: {results.success_rate:.1f}%")
print(f"  Taxa de erro: {results.error_rate:.1f}%")
print(f"\n⏱️  TEMPO DE RESPOSTA")
print(f"  Mínimo: {results.response_time_min:.0f}ms")
print(f"  Média: {results.response_time_avg:.0f}ms")
print(f"  Mediana: {results.response_time_p50:.0f}ms")
print(f"  P95: {results.response_time_p95:.0f}ms")
print(f"  P99: {results.response_time_p99:.0f}ms")
print(f"  Máximo: {results.response_time_max:.0f}ms")
print(f"\n📱 RECURSOS DO DEVICE")
print(f"  CPU média: {results.avg_cpu:.1f}%")
print(f"  Memória média: {results.avg_memory:.1f}MB")
print(f"  Memória pico: {results.peak_memory:.1f}MB")

# Verificar thresholds
print(f"\n🎯 THRESHOLDS")
threshold_results = results.check_thresholds()
for metric, passed in threshold_results.items():
    status = "✅ PASSOU" if passed else "❌ FALHOU"
    print(f"  {metric}: {status}")

print(f"\n{'✅ TESTE PASSOU' if results.passed_thresholds else '❌ TESTE FALHOU'}")

# Gerar relatórios
from mobileloadx import ReportGenerator

generator = ReportGenerator(results)
generator.generate_html("report.html")
generator.generate_json("report.json")
generator.generate_csv("report.csv")

print("\n📄 Relatórios gerados:")
print("  - report.html")
print("  - report.json")
print("  - report.csv")
