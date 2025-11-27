"""Decoradores para handlers de Lambda"""
import json
import functools
from typing import Callable, Any
from .logger import logger
from .responses import error_response, validation_error_response


def with_logging(func: Callable) -> Callable:
    """Decorador para logging automático"""
    @functools.wraps(func)
    def wrapper(event: dict, context: Any) -> dict:
        # Establecer contexto de request
        logger.set_request_context(context.request_id if hasattr(context, 'request_id') else 'unknown')
        
        # Log de entrada
        logger.info(
            f"Handler {func.__name__} invoked",
            event_type=event.get('requestContext', {}).get('routeKey', 'unknown'),
            function=func.__name__
        )
        
        try:
            result = func(event, context)
            
            # Log de salida exitosa
            logger.info(
                f"Handler {func.__name__} completed successfully",
                status_code=result.get('statusCode', 200)
            )
            
            return result
        except Exception as e:
            # Log de error
            logger.exception(
                f"Handler {func.__name__} failed",
                error=str(e),
                function=func.__name__
            )
            raise
    
    return wrapper


def with_error_handling(func: Callable) -> Callable:
    """Decorador para manejo centralizado de errores"""
    @functools.wraps(func)
    def wrapper(event: dict, context: Any) -> dict:
        try:
            return func(event, context)
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            return error_response(str(e), status_code=400, error_code='VALIDATION_ERROR')
        except KeyError as e:
            logger.error(f"Missing required field: {str(e)}")
            return error_response(
                f"Missing required field: {str(e)}",
                status_code=400,
                error_code='MISSING_FIELD'
            )
        except PermissionError as e:
            logger.error(f"Permission denied: {str(e)}")
            return error_response(str(e), status_code=403, error_code='FORBIDDEN')
        except Exception as e:
            logger.exception(f"Unexpected error: {str(e)}")
            return error_response(
                "Internal server error",
                status_code=500,
                error_code='INTERNAL_ERROR'
            )
    
    return wrapper


def validate_tenant(func: Callable) -> Callable:
    """Decorador para validar que el tenant existe"""
    @functools.wraps(func)
    def wrapper(event: dict, context: Any) -> dict:
        from ..clients.dynamodb import get_tenant
        
        # Extraer tenantId del path
        tenant_id = event.get('pathParameters', {}).get('tenantId')
        
        if not tenant_id:
            return error_response(
                "Tenant ID is required",
                status_code=400,
                error_code='MISSING_TENANT_ID'
            )
        
        # Verificar que el tenant existe
        tenant = get_tenant(tenant_id)
        if not tenant:
            return error_response(
                f"Tenant {tenant_id} not found",
                status_code=404,
                error_code='TENANT_NOT_FOUND'
            )
        
        # Agregar tenant al event para uso posterior
        event['tenant'] = tenant
        
        return func(event, context)
    
    return wrapper


def parse_json_body(func: Callable) -> Callable:
    """Decorador para parsear el body JSON automáticamente"""
    @functools.wraps(func)
    def wrapper(event: dict, context: Any) -> dict:
        if 'body' in event and isinstance(event['body'], str):
            try:
                event['parsedBody'] = json.loads(event['body'])
            except json.JSONDecodeError:
                return error_response(
                    "Invalid JSON in request body",
                    status_code=400,
                    error_code='INVALID_JSON'
                )
        
        return func(event, context)
    
    return wrapper


def cors_headers(func: Callable) -> Callable:
    """Decorador para agregar headers CORS"""
    @functools.wraps(func)
    def wrapper(event: dict, context: Any) -> dict:
        result = func(event, context)
        
        if 'headers' not in result:
            result['headers'] = {}
        
        result['headers'].update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization,x-tenant-id,x-user-id,x-role',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        })
        
        return result
    
    return wrapper
