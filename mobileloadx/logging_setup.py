"""
Sistema de logging estruturado para MobileLoadX
"""

import logging
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class JSONFormatter(logging.Formatter):
    """Formata logs em JSON para melhor análise"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata record em JSON"""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Adicionar exceção se houver
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Adicionar campos customizados
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'action_type'):
            log_data['action_type'] = record.action_type
        
        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Formata logs com cores para terminal"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata record com cores"""
        levelname = record.levelname
        color = self.COLORS.get(levelname, self.RESET)
        
        record.levelname = f"{color}{levelname}{self.RESET}"
        
        # Usar formato padrão com cores
        return super().format(record)


def setup_logging(
    level: str = 'INFO',
    log_file: Optional[str] = None,
    json_format: bool = False,
    log_dir: str = './logs'
) -> logging.Logger:
    """
    Configura sistema de logging estruturado
    
    Args:
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Arquivo para salvar logs (opcional)
        json_format: Se True, usa formato JSON
        log_dir: Diretório para arquivos de log
    
    Returns:
        Logger configurado
    """
    # Criar diretório de logs se não existir
    if log_file:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
    
    # Logger raiz
    logger = logging.getLogger('mobileloadx')
    logger.setLevel(getattr(logging, level))
    
    # Limpar handlers existentes
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    
    # Escolher formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = ColoredFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (se especificado)
    if log_file:
        log_file_path = Path(log_dir) / log_file
        
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Sempre usar JSON para arquivo
        file_formatter = JSONFormatter()
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Obtém logger para um módulo específico"""
    return logging.getLogger(f'mobileloadx.{name}')


class ContextualLogger:
    """Logger com contexto (usuário, ação, etc)"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.context = {}
    
    def set_context(self, **kwargs):
        """Define contexto"""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Limpa contexto"""
        self.context = {}
    
    def _log(self, level: int, msg: str, **kwargs):
        """Log com contexto"""
        # Adicionar contexto à mensagem
        if self.context:
            context_str = ' | '.join(f'{k}={v}' for k, v in self.context.items())
            msg = f"[{context_str}] {msg}"
        
        # Criar record com contexto
        record = self.logger.makeRecord(
            self.logger.name,
            level,
            None,
            0,
            msg,
            (),
            None,
            None
        )
        
        # Adicionar campos customizados
        for key, value in self.context.items():
            setattr(record, key, value)
        
        self.logger.handle(record)
    
    def debug(self, msg: str, **kwargs):
        self.set_context(**kwargs)
        self._log(logging.DEBUG, msg)
    
    def info(self, msg: str, **kwargs):
        self.set_context(**kwargs)
        self._log(logging.INFO, msg)
    
    def warning(self, msg: str, **kwargs):
        self.set_context(**kwargs)
        self._log(logging.WARNING, msg)
    
    def error(self, msg: str, **kwargs):
        self.set_context(**kwargs)
        self._log(logging.ERROR, msg)
    
    def critical(self, msg: str, **kwargs):
        self.set_context(**kwargs)
        self._log(logging.CRITICAL, msg)
