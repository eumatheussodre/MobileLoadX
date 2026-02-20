"""
Validação de schema para configurações YAML
"""

import json
from typing import Dict, Any, List, Union, Optional
from pathlib import Path


class SchemaValidator:
    """Valida esquema de configuração YAML"""
    
    # Schema padrão (formato README: test, virtual_users objeto, platforms com android/ios)
    DEFAULT_SCHEMA = {
        'type': 'object',
        'properties': {
            'test': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'duration': {'type': 'integer', 'minimum': 1},
                },
                'required': ['name', 'duration']
            },
            'virtual_users': {
                'type': 'object',
                'properties': {
                    'initial': {'type': 'integer', 'minimum': 0},
                    'max': {'type': 'integer', 'minimum': 1},
                    'ramp_up_time': {'type': 'integer', 'minimum': 0},
                },
                'required': ['max']
            },
            'platforms': {
                'type': 'array',
                'minItems': 1,
                'items': {
                    'type': 'object',
                    'additionalProperties': {
                        'type': 'object',
                        'properties': {
                            'app': {'type': 'string'},
                            'device': {'type': 'string'},
                            'devices': {'type': 'array', 'items': {'type': 'string'}},
                            'capabilities': {'type': 'object'},
                            'distribute': {'type': 'string'},
                        }
                    }
                }
            },
            'scenarios': {
                'type': 'array',
                'minItems': 1,
                'items': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'weight': {'type': 'integer', 'minimum': 1},
                        'actions': {
                            'type': 'array',
                            'items': {'type': 'object'}
                        }
                    },
                    'required': ['name', 'actions']
                }
            },
            'thresholds': {
                'type': 'object',
                'properties': {
                    'response_time_p95': {'type': 'number'},
                    'response_time_p99': {'type': 'number'},
                    'error_rate_max': {'type': 'number'},
                    'cpu_max': {'type': 'number'},
                    'memory_max': {'type': 'number'}
                }
            },
            'metrics': {
                'type': 'object',
                'properties': {
                    'collect': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    },
                    'interval': {'type': 'number', 'minimum': 0.1}
                }
            }
        },
        'required': ['test', 'virtual_users', 'platforms', 'scenarios']
    }
    
    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        """
        Inicializa validador
        
        Args:
            schema: Schema customizado (usa DEFAULT_SCHEMA se None)
        """
        self.schema = schema or self.DEFAULT_SCHEMA
    
    def validate(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Valida dados contra schema
        
        Args:
            data: Dados a validar
        
        Returns:
            Tupla (válido, lista de erros)
        """
        errors = []
        
        # Validações básicas
        if not isinstance(data, dict):
            errors.append("Configuração deve ser um dicionário")
            return False, errors
        
        # Validar campos obrigatórios
        schema_required = self.schema.get('required', [])
        for field in schema_required:
            if field not in data:
                errors.append(f"Campo obrigatório ausente: {field}")
        
        # Validar tipos
        for field, value in data.items():
            field_schema = self.schema.get('properties', {}).get(field)
            if field_schema:
                field_errors = self._validate_field(field, value, field_schema)
                errors.extend(field_errors)
        
        # Validação customizada: platforms deve ter itens { android: {...} } ou { ios: {...} }
        if 'platforms' in data and isinstance(data['platforms'], list):
            for i, item in enumerate(data['platforms']):
                if not isinstance(item, dict) or len(item) != 1:
                    errors.append(f"platforms[{i}]: cada item deve ser um objeto com uma chave 'android' ou 'ios'")
                else:
                    key = list(item.keys())[0]
                    if key not in ('android', 'ios'):
                        errors.append(f"platforms[{i}]: chave deve ser 'android' ou 'ios', recebeu '{key}'")
                    elif not item[key].get('app'):
                        errors.append(f"platforms[{i}].{key}: campo 'app' é obrigatório")
        
        return len(errors) == 0, errors
    
    def _validate_field(self, name: str, value: Any, schema: Dict[str, Any]) -> List[str]:
        """Valida um campo específico"""
        errors = []
        
        # Verificar tipo
        field_type = schema.get('type')
        if field_type and not self._check_type(value, field_type):
            errors.append(f"Campo '{name}' deve ser {field_type}, recebeu {type(value).__name__}")
            return errors
        
        # Validações específicas por tipo
        if field_type == 'integer':
            minimum = schema.get('minimum')
            if minimum is not None and value < minimum:
                errors.append(f"Campo '{name}' deve ser >= {minimum}")
        
        elif field_type == 'number':
            minimum = schema.get('minimum')
            if minimum is not None and value < minimum:
                errors.append(f"Campo '{name}' deve ser >= {minimum}")
        
        elif field_type == 'string':
            enum_values = schema.get('enum')
            if enum_values and value not in enum_values:
                errors.append(f"Campo '{name}' deve ser um de {enum_values}")
        
        elif field_type == 'array':
            min_items = schema.get('minItems', 0)
            if len(value) < min_items:
                errors.append(f"Campo '{name}' deve ter no mínimo {min_items} item(ns), tem {len(value)}")
            items_schema = schema.get('items', {})
            for i, item in enumerate(value):
                item_errors = self._validate_field(f"{name}[{i}]", item, items_schema)
                errors.extend(item_errors)
        
        elif field_type == 'object':
            if isinstance(value, dict):
                # Campos obrigatórios do objeto
                for req in schema.get('required', []):
                    if req not in value:
                        errors.append(f"Campo obrigatório ausente: '{name}.{req}'")
                properties = schema.get('properties', {})
                for prop_name, prop_schema in properties.items():
                    if prop_name in value:
                        prop_errors = self._validate_field(
                            f"{name}.{prop_name}",
                            value[prop_name],
                            prop_schema
                        )
                        errors.extend(prop_errors)
        
        return errors
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Verifica se tipo está correto"""
        type_mapping = {
            'string': str,
            'number': (int, float),
            'integer': int,
            'boolean': bool,
            'array': list,
            'object': dict,
            'null': type(None)
        }
        
        expected_py_type = type_mapping.get(expected_type)
        if expected_py_type is None:
            return True
        
        return isinstance(value, expected_py_type)
    
    def validate_file(self, filepath: str) -> tuple[bool, List[str]]:
        """
        Valida arquivo YAML/JSON
        
        Args:
            filepath: Caminho do arquivo
        
        Returns:
            Tupla (válido, lista de erros)
        """
        from .config.loader import ConfigLoader
        
        try:
            config = ConfigLoader.load(filepath)
            return self.validate(config)
        except Exception as e:
            return False, [str(e)]


def validate_config(config_file: str) -> bool:
    """Helper para validar configuração"""
    validator = SchemaValidator()
    valid, errors = validator.validate_file(config_file)
    
    if not valid:
        print("❌ Configuração inválida:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✅ Configuração válida!")
    return True
