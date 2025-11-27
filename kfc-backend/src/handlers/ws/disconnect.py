"""Handler para desconexiones WebSocket"""
import os
from boto3.dynamodb.conditions import Key
from ...clients.dynamodb import delete_item, query_items
from ...utils.logger import logger


def handler(event, context):
    """
    Limpia una conexión WebSocket cuando se desconecta
    """
    connection_id = event['requestContext']['connectionId']
    
    logger.info(f"WebSocket disconnection", connection_id=connection_id)
    
    try:
        # Primero necesitamos obtener el tenantId para poder eliminar
        # (porque tenantId es la partition key)
        table_name = os.getenv('CONNECTIONS_TABLE')
        
        # Query usando el índice connection-index
        results = query_items(
            table_name,
            key_condition_expression=Key('connectionId').eq(connection_id),
            index_name='connection-index',
            limit=1
        )
        
        if not results:
            logger.warning(f"Connection not found in table", connection_id=connection_id)
            return {'statusCode': 200}
        
        connection = results[0]
        tenant_id = connection.get('tenantId')
        
        # Eliminar la conexión
        delete_item(
            table_name,
            {
                'tenantId': tenant_id,
                'connectionId': connection_id
            }
        )
        
        logger.info(
            f"Connection removed",
            connection_id=connection_id,
            tenant_id=tenant_id
        )
        
        return {'statusCode': 200}
    
    except Exception as e:
        logger.exception(f"Error removing connection: {str(e)}")
        # Retornar 200 de todas formas para no bloquear la desconexión
        return {'statusCode': 200}
