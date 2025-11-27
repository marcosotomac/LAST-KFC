"""Utilidades para respuestas HTTP estandarizadas"""
import json
from typing import Any, Dict, Optional


def success_response(
    data: Any,
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Respuesta exitosa estandarizada"""
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true'
    }
    
    if headers:
        default_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps({
            'success': True,
            'data': data
        })
    }


def error_response(
    message: str,
    status_code: int = 400,
    error_code: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Respuesta de error estandarizada"""
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true'
    }
    
    if headers:
        default_headers.update(headers)
    
    error_body = {
        'success': False,
        'error': {
            'message': message,
            'code': error_code or f'ERROR_{status_code}'
        }
    }
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(error_body)
    }


def created_response(data: Any) -> Dict[str, Any]:
    """Respuesta para recursos creados (201)"""
    return success_response(data, status_code=201)


def not_found_response(message: str = "Resource not found") -> Dict[str, Any]:
    """Respuesta para recursos no encontrados (404)"""
    return error_response(message, status_code=404, error_code='NOT_FOUND')


def unauthorized_response(message: str = "Unauthorized") -> Dict[str, Any]:
    """Respuesta para errores de autenticación (401)"""
    return error_response(message, status_code=401, error_code='UNAUTHORIZED')


def forbidden_response(message: str = "Forbidden") -> Dict[str, Any]:
    """Respuesta para errores de autorización (403)"""
    return error_response(message, status_code=403, error_code='FORBIDDEN')


def validation_error_response(errors: Any) -> Dict[str, Any]:
    """Respuesta para errores de validación (422)"""
    return {
        'statusCode': 422,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': False,
            'error': {
                'message': 'Validation error',
                'code': 'VALIDATION_ERROR',
                'details': errors
            }
        })
    }
