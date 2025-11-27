"""Handler para ping WebSocket (mantener conexión activa)"""
import os
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key
from ...clients.dynamodb import update_item, query_items
from ...utils.logger import logger


def handler(event, context):
    """
    Renueva el TTL de una conexión WebSocket activa
    """
    connection_id = event['requestContext']['connectionId']
    
    logger.debug(f"WebSocket ping", connection_id=connection_id)
    
    try:
        # Obtener la conexión actual
        table_name = os.getenv('CONNECTIONS_TABLE')
        
        results = query_items(
            table_name,
            key_condition_expression=Key('connectionId').eq(connection_id),
            index_name='connection-index',
            limit=1
        )
        
        if not results:
            logger.warning(f"Connection not found", connection_id=connection_id)
            return {'statusCode': 404}
        
        connection = results[0]
        tenant_id = connection.get('tenantId')
        
        # Renovar TTL
        ttl_seconds = int(os.getenv('CONNECTION_TTL_SECONDS', '3600'))
        new_expires_at = int((datetime.utcnow() + timedelta(seconds=ttl_seconds)).timestamp())
        
        update_item(
            table_name,
            {
                'tenantId': tenant_id,
                'connectionId': connection_id
            },
            {
                'expiresAt': new_expires_at,
                'lastPing': datetime.utcnow().isoformat()
            }
        )
        
        logger.debug(f"Connection TTL renewed", connection_id=connection_id)
        
        return {
            'statusCode': 200,
            'body': 'pong'
        }
    
    except Exception as e:
        logger.exception(f"Error handling ping: {str(e)}")
        return {'statusCode': 500}
