"""Cliente WebSocket API Gateway"""
import boto3
import json
import os
from typing import Dict, Any, List, Optional
from boto3.dynamodb.conditions import Key
from ..utils.logger import logger

# Inicializar cliente API Gateway Management
def get_api_client():
    """Obtener cliente de API Gateway Management API"""
    endpoint_url = os.getenv('WEBSOCKET_API_ENDPOINT')
    if not endpoint_url:
        raise ValueError("WEBSOCKET_API_ENDPOINT environment variable not set")
    
    return boto3.client(
        'apigatewaymanagementapi',
        endpoint_url=endpoint_url
    )


def post_to_connection(connection_id: str, data: Dict[str, Any]) -> bool:
    """
    Enviar mensaje a una conexión WebSocket específica
    
    Args:
        connection_id: ID de la conexión
        data: Datos a enviar
    
    Returns:
        True si exitoso, False si la conexión está cerrada
    """
    try:
        client = get_api_client()
        
        client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(data).encode('utf-8')
        )
        
        logger.debug(f"Message sent to connection {connection_id}")
        return True
    
    except client.exceptions.GoneException:
        logger.warning(f"Connection {connection_id} is gone, cleaning up")
        # La conexión está cerrada, se debería limpiar de la tabla
        _cleanup_connection(connection_id)
        return False
    
    except Exception as e:
        logger.error(
            f"Error posting to connection {connection_id}: {str(e)}",
            connection_id=connection_id
        )
        raise


def broadcast_to_tenant(
    tenant_id: str,
    data: Dict[str, Any],
    role: Optional[str] = None
) -> Dict[str, int]:
    """
    Enviar mensaje a todas las conexiones de un tenant
    
    Args:
        tenant_id: ID del tenant
        data: Datos a enviar
        role: Filtrar por rol específico (opcional)
    
    Returns:
        Dict con estadísticas de envío
    """
    from ..clients.dynamodb import query_items, get_table
    
    connections_table = os.getenv('CONNECTIONS_TABLE')
    
    try:
        # Query conexiones del tenant
        if role:
            # Usar índice tenant-role-index
            connections = query_items(
                connections_table,
                key_condition_expression=Key('tenantId').eq(tenant_id) & Key('role').eq(role),
                index_name='tenant-role-index'
            )
        else:
            # Query por tenantId
            connections = query_items(
                connections_table,
                key_condition_expression=Key('tenantId').eq(tenant_id)
            )
        
        stats = {
            'total': len(connections),
            'sent': 0,
            'failed': 0
        }
        
        # Enviar a cada conexión
        for conn in connections:
            connection_id = conn.get('connectionId')
            if connection_id:
                success = post_to_connection(connection_id, data)
                if success:
                    stats['sent'] += 1
                else:
                    stats['failed'] += 1
        
        logger.info(
            f"Broadcast to tenant {tenant_id}",
            tenant_id=tenant_id,
            role=role,
            stats=stats
        )
        
        return stats
    
    except Exception as e:
        logger.exception(
            f"Error broadcasting to tenant {tenant_id}: {str(e)}",
            tenant_id=tenant_id
        )
        raise


def _cleanup_connection(connection_id: str):
    """Limpiar conexión cerrada de la tabla"""
    from ..clients.dynamodb import delete_item, query_items
    
    connections_table = os.getenv('CONNECTIONS_TABLE')
    
    try:
        # Query para obtener la conexión completa (necesitamos tenantId)
        results = query_items(
            connections_table,
            key_condition_expression=Key('connectionId').eq(connection_id),
            index_name='connection-index',
            limit=1
        )
        
        if results:
            conn = results[0]
            delete_item(
                connections_table,
                {
                    'tenantId': conn['tenantId'],
                    'connectionId': connection_id
                }
            )
            logger.info(f"Cleaned up stale connection {connection_id}")
    
    except Exception as e:
        logger.warning(f"Error cleaning up connection {connection_id}: {str(e)}")
