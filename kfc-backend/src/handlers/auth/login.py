"""Handler para login de usuarios"""
import bcrypt
from datetime import datetime, timedelta
from jose import jwt
from ...utils.responses import success_response, error_response, unauthorized_response
from ...utils.decorators import with_logging, with_error_handling, parse_json_body, validate_tenant
from ...utils.validators import LoginRequest
from ...clients.dynamodb import get_user_by_email
from ...utils.logger import logger


# Secret para JWT (en producción debería estar en Parameter Store o Secrets Manager)
JWT_SECRET = "kfc-orders-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"


@with_logging
@with_error_handling
@parse_json_body
@validate_tenant
def handler(event, context):
    """
    Login de usuario
    
    POST /tenants/{tenantId}/auth/login
    Body: {
        "email": "juan@kfc.com",
        "password": "secret123"
    }
    """
    tenant_id = event['pathParameters']['tenantId']
    
    # Validar request
    try:
        body = event.get('parsedBody', {})
        login_request = LoginRequest(**body)
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return error_response(f"Validation error: {str(e)}", status_code=422)
    
    # Buscar usuario por email
    user = get_user_by_email(tenant_id, login_request.email)
    
    if not user:
        logger.warning(f"User not found", email=login_request.email)
        return unauthorized_response("Invalid email or password")
    
    # Verificar que el usuario esté activo
    if not user.get('active', True):
        return unauthorized_response("User account is inactive")
    
    # Verificar password
    password_hash = user.get('passwordHash')
    if not password_hash:
        logger.error(f"User missing password hash", user_id=user.get('userId'))
        return unauthorized_response("Invalid email or password")
    
    try:
        password_matches = bcrypt.checkpw(
            login_request.password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return unauthorized_response("Invalid email or password")
    
    if not password_matches:
        logger.warning(f"Invalid password for user", email=login_request.email)
        return unauthorized_response("Invalid email or password")
    
    # Generar JWT token
    expiration = datetime.utcnow() + timedelta(days=7)
    
    token_payload = {
        'sub': user.get('userId'),
        'email': user.get('email'),
        'name': user.get('name'),
        'role': user.get('role'),
        'tenantId': tenant_id,
        'exp': expiration,
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    logger.info(
        f"User logged in successfully",
        user_id=user.get('userId'),
        email=login_request.email
    )
    
    # Preparar respuesta sin password
    user_data = {k: v for k, v in user.items() if k != 'passwordHash'}
    
    return success_response({
        'token': token,
        'user': user_data,
        'expiresAt': expiration.isoformat()
    })
