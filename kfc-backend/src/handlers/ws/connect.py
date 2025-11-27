"""Handler para conexiones WebSocket"""
import os
from datetime import datetime, timedelta
from ...clients.dynamodb import put_item
from ...utils.logger import logger


def handler(event, context):
    """
    Registra una nueva conexión WebSocket
    
    Query params esperados:
    - tenantId: ID del tenant
    - userId: ID del usuario (opcional)
    - role: Rol del usuario (kitchen, cashier, delivery, etc)
    """
    connection_id = event['requestContext']['connectionId']
    
    # Extraer query params
    query_params = event.get('queryStringParameters') or {}
    tenant_id = query_params.get('tenantId')
    user_id = query_params.get('userId', 'anonymous')
    role = query_params.get('role', 'customer')
    
    logger.info(
        f"WebSocket connection",
        connection_id=connection_id,
        tenant_id=tenant_id,
        user_id=user_id,
        role=role
    )
    
    # Validar que tenantId esté presente
    if not tenant_id:
        logger.error("Missing tenantId in connection request")
        return {
            'statusCode': 400,
            'body': 'Missing tenantId parameter'
        }
    
    # Calcular TTL (1 hora por defecto)
    ttl_seconds = int(os.getenv('CONNECTION_TTL_SECONDS', '3600'))
    expires_at = int((datetime.utcnow() + timedelta(seconds=ttl_seconds)).timestamp())
    
    # Guardar conexión en DynamoDB
    connection = {
        'tenantId': tenant_id,
        'connectionId': connection_id,
        'userId': user_id,
        'role': role,
        'connectedAt': datetime.utcnow().isoformat(),
        'expiresAt': expires_at
    }
    
    try:
        table_name = os.getenv('CONNECTIONS_TABLE')
        put_item(table_name, connection)
        
        logger.info(
            f"Connection registered",
            connection_id=connection_id,
            tenant_id=tenant_id
        )
        
        return {'statusCode': 200}
    
    except Exception as e:
        logger.exception(f"Error registering connection: {str(e)}")
        return {
            'statusCode': 500,
            'body': 'Failed to register connection'
        }
