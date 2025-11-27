"""Handler para mensajes WebSocket no soportados"""
from ...utils.logger import logger


def handler(event, context):
    """
    Maneja mensajes WebSocket que no coinciden con ninguna ruta
    """
    connection_id = event['requestContext']['connectionId']
    
    logger.warning(
        f"Unsupported WebSocket message",
        connection_id=connection_id
    )
    
    return {
        'statusCode': 400,
        'body': 'Unsupported message type'
    }
