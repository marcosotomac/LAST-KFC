"""Logger estructurado para Lambda"""
import logging
import json
import os
from typing import Any, Dict


class StructuredLogger:
    """Logger con formato estructurado para CloudWatch"""
    
    def __init__(self, name: str = None):
        self.logger = logging.getLogger(name or __name__)
        self.logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))
        
        # Configurar handler si no existe
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(handler)
    
    def _log(self, level: str, message: str, **kwargs):
        """Log estructurado en formato JSON"""
        log_entry = {
            'level': level,
            'message': message,
            'service': os.getenv('SERVICE_NAME', 'kfc-orders-cloud'),
            'function': os.getenv('FUNCTION_NAME', 'unknown'),
            'stage': os.getenv('STAGE', 'dev'),
            **kwargs
        }
        
        # Agregar context de Lambda si está disponible
        if hasattr(self, 'request_id'):
            log_entry['request_id'] = self.request_id
        
        self.logger.log(
            getattr(logging, level.upper()),
            json.dumps(log_entry)
        )
    
    def debug(self, message: str, **kwargs):
        """Log de debug"""
        self._log('DEBUG', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log de información"""
        self._log('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log de advertencia"""
        self._log('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log de error"""
        self._log('ERROR', message, **kwargs)
    
    def exception(self, message: str, exc_info=True, **kwargs):
        """Log de excepción con traceback"""
        import traceback
        if exc_info:
            kwargs['traceback'] = traceback.format_exc()
        self._log('ERROR', message, **kwargs)
    
    def set_request_context(self, request_id: str):
        """Establecer contexto de la request"""
        self.request_id = request_id


# Instancia global del logger
logger = StructuredLogger()
