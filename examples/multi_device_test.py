"""
Exemplo de teste com múltiplos devices
"""

from mobileloadx import LoadTest, Scenario

# Criar cenários
scenario = Scenario("Main Flow")
scenario.tap(id="startButton")
scenario.wait(3)
scenario.scroll(direction="down", duration=2)

# Configurar teste
test = LoadTest(
    name="Multi-Device Test",
    duration=180,
    virtual_users=10,
    ramp_up_time=30
)

# Adicionar múltiplos devices Android
test.add_platform(
    platform="android",
    app="./app-release.apk",
    devices=[
        "emulator-5554",
        "emulator-5556",
        "real-device-serial-123"
    ],
    distribute="round-robin",  # Distribui usuários entre devices
    appium_server_url="http://localhost:4723"
)

test.add_scenario(scenario, weight=100)

# Executar
results = test.run()

print(f"Teste concluído!")
print(f"Taxa de sucesso: {results.success_rate:.1f}%")
