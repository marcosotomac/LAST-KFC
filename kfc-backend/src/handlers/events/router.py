"""Handler para enrutar eventos del bus a WebSocket y SNS"""
from ...utils.decorators import with_logging, with_error_handling
from ...clients.websocket import broadcast_to_tenant
from ...utils.logger import logger


@with_logging
@with_error_handling
def handler(event, context):
    """
    Enruta eventos de EventBridge a WebSocket y otros destinos
    
    Recibe eventos del EventBridge bus y los distribuye a:
    - Conexiones WebSocket del tenant
    - SNS (configurado en las reglas de EventBridge)
    """
    # El evento viene con esta estructura desde EventBridge
    detail = event.get('detail', {})
    detail_type = event.get('detail-type', '')
    source = event.get('source', '')
    
    tenant_id = detail.get('tenantId')
    order_id = detail.get('orderId')
    
    logger.info(
        f"Routing event",
        source=source,
        detail_type=detail_type,
        tenant_id=tenant_id,
        order_id=order_id
    )
    
    if not tenant_id:
        logger.warning("Event missing tenantId, skipping WebSocket broadcast")
        return
    
    # Preparar mensaje para WebSocket
    ws_message = {
        'type': 'order_update',
        'eventType': detail_type,
        'data': detail
    }
    
    # Broadcast a todas las conexiones del tenant
    try:
        stats = broadcast_to_tenant(tenant_id, ws_message)
        logger.info(
            f"Broadcast completed",
            tenant_id=tenant_id,
            stats=stats
        )
    except Exception as e:
        logger.error(f"Failed to broadcast to WebSocket: {str(e)}")
        # No fallar el handler si el broadcast falla
    
    # El SNS se maneja automáticamente por las reglas de EventBridge
    # que tienen el topic como target
    
    logger.info("Event routing completed", event_type=detail_type)
