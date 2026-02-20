"""
Testes para o carregador de configuração
"""

import pytest
import json
from pathlib import Path
from mobileloadx.config.loader import ConfigLoader


class TestConfigLoader:
    """Testes para a classe ConfigLoader"""
    
    def test_load_yaml_file(self, yaml_config_file):
        """Testa carregamento de arquivo YAML"""
        config = ConfigLoader.load(str(yaml_config_file))
        
        assert config['name'] == 'Test Load Test'
        assert config['duration'] == 300
        assert config['virtual_users'] == 5
        assert len(config['platforms']) > 0
    
    def test_load_json_file(self, json_config_file):
        """Testa carregamento de arquivo JSON"""
        config = ConfigLoader.load(str(json_config_file))
        
        assert config['name'] == 'Test Load Test'
        assert config['duration'] == 300
        assert config['virtual_users'] == 5
    
    def test_load_nonexistent_file(self, temp_dir):
        """Testa erro ao carregar arquivo inexistente"""
        nonexistent_file = temp_dir / 'nonexistent.yaml'
        
        with pytest.raises(FileNotFoundError):
            ConfigLoader.load(str(nonexistent_file))
    
    def test_load_unsupported_format(self, temp_dir):
        """Testa erro com formato de arquivo não suportado"""
        unsupported_file = temp_dir / 'config.txt'
        unsupported_file.write_text('some content')
        
        with pytest.raises(ValueError, match='Formato não suportado'):
            ConfigLoader.load(str(unsupported_file))
    
    def test_save_yaml(self, temp_dir, config_dict):
        """Testa salvamento de configuração em YAML"""
        output_file = temp_dir / 'output.yaml'
        
        ConfigLoader.save(config_dict, str(output_file), format='yaml')
        
        assert output_file.exists()
        
        # Verificar se pode ser relido
        loaded_config = ConfigLoader.load(str(output_file))
        assert loaded_config['test']['name'] == config_dict['test']['name']
    
    def test_save_json(self, temp_dir, config_dict):
        """Testa salvamento de configuração em JSON"""
        output_file = temp_dir / 'output.json'
        
        ConfigLoader.save(config_dict, str(output_file), format='json')
        
        assert output_file.exists()
        
        # Verificar se pode ser relido
        loaded_config = ConfigLoader.load(str(output_file))
        assert loaded_config['test']['name'] == config_dict['test']['name']
    
    def test_save_unsupported_format(self, temp_dir, config_dict):
        """Testa erro ao salvar com formato não suportado"""
        output_file = temp_dir / 'output.txt'
        
        with pytest.raises(ValueError, match='Formato não suportado'):
            ConfigLoader.save(config_dict, str(output_file), format='txt')
    
    def test_load_yaml_with_yml_extension(self, temp_dir, config_dict):
        """Testa carregamento de arquivo .yml"""
        import yaml
        
        config_file = temp_dir / 'config.yml'
        with open(config_file, 'w') as f:
            yaml.dump(config_dict, f)
        
        config = ConfigLoader.load(str(config_file))
        assert config['test']['name'] == 'Test Load Test'
    
    def test_load_preserves_structure(self, yaml_config_file):
        """Testa se carregamento preserva estrutura aninhada"""
        config = ConfigLoader.load(str(yaml_config_file))
        
        assert 'platforms' in config
        assert isinstance(config['platforms'], list)
        assert 'scenarios' in config
        assert isinstance(config['scenarios'], list)
        assert 'thresholds' in config
        assert isinstance(config['thresholds'], dict)
