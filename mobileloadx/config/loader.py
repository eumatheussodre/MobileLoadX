"""
Carregador de configuração de arquivos YAML/JSON
"""

import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Carrega configurações de arquivos YAML ou JSON"""
    
    @staticmethod
    def load(file_path: str) -> Dict[str, Any]:
        """
        Carrega configuração de arquivo
        
        Args:
            file_path: Caminho do arquivo (.yaml, .yml ou .json)
        
        Returns:
            Dicionário com a configuração
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        logger.info(f"Carregando configuração de: {file_path}")
        
        # Determinar formato pelo sufixo
        if path.suffix in ['.yaml', '.yml']:
            return ConfigLoader._load_yaml(path)
        elif path.suffix == '.json':
            return ConfigLoader._load_json(path)
        else:
            raise ValueError(f"Formato não suportado: {path.suffix}")
    
    @staticmethod
    def _load_yaml(path: Path) -> Dict[str, Any]:
        """Carrega arquivo YAML"""
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        logger.debug(f"Configuração YAML carregada: {len(config)} chaves principais")
        return config
    
    @staticmethod
    def _load_json(path: Path) -> Dict[str, Any]:
        """Carrega arquivo JSON"""
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logger.debug(f"Configuração JSON carregada: {len(config)} chaves principais")
        return config
    
    @staticmethod
    def save(config: Dict[str, Any], file_path: str, format: str = 'yaml'):
        """
        Salva configuração em arquivo
        
        Args:
            config: Dicionário de configuração
            file_path: Caminho do arquivo
            format: 'yaml' ou 'json'
        """
        path = Path(file_path)
        
        logger.info(f"Salvando configuração em: {file_path}")
        
        if format == 'yaml':
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        elif format == 'json':
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Formato não suportado: {format}")
