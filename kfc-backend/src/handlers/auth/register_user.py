"""Handler para registrar usuarios"""
import uuid
import os
import bcrypt
from datetime import datetime
from ...utils.responses import created_response, error_response
from ...utils.decorators import with_logging, with_error_handling, parse_json_body, validate_tenant
from ...utils.validators import RegisterUserRequest
from ...clients.dynamodb import put_item, get_user_by_email
from ...utils.logger import logger


@with_logging
@with_error_handling
@parse_json_body
@validate_tenant
def handler(event, context):
    """
    Registra un nuevo usuario para un tenant
    
    POST /tenants/{tenantId}/auth/register
    Body: {
        "email": "juan@kfc.com",
        "password": "secret123",
        "name": "Juan Pérez",
        "role": "cashier"
    }
    """
    tenant_id = event['pathParameters']['tenantId']
    
    # Validar request
    try:
        body = event.get('parsedBody', {})
        user_request = RegisterUserRequest(**body)
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return error_response(f"Validation error: {str(e)}", status_code=422)
    
    # Verificar que el email no esté ya registrado
    existing_user = get_user_by_email(tenant_id, user_request.email)
    if existing_user:
        return error_response(
            "Email already registered",
            status_code=409,
            error_code='EMAIL_EXISTS'
        )
    
    # Hash de password
    password_hash = bcrypt.hashpw(
        user_request.password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    # Generar ID único para el usuario
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    
    # Crear usuario
    user = {
        'tenantId': tenant_id,
        'userId': user_id,
        'email': user_request.email,
        'passwordHash': password_hash,
        'name': user_request.name,
        'role': user_request.role.value,
        'active': True,
        'createdAt': datetime.utcnow().isoformat(),
        'updatedAt': datetime.utcnow().isoformat()
    }
    
    # Guardar en DynamoDB
    table_name = os.getenv('USERS_TABLE')
    put_item(table_name, user)
    
    logger.info(
        f"User registered successfully",
        tenant_id=tenant_id,
        user_id=user_id,
        email=user_request.email
    )
    
    # Retornar usuario sin password
    user_response = {k: v for k, v in user.items() if k != 'passwordHash'}
    
    return created_response(user_response)
