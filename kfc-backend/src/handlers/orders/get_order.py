"""Handler para obtener detalle de un pedido"""
from ...utils.responses import success_response, not_found_response
from ...utils.decorators import with_logging, with_error_handling, validate_tenant
from ...clients.dynamodb import get_order
from ...utils.logger import logger


@with_logging
@with_error_handling
@validate_tenant
def handler(event, context):
    """
    Obtiene el detalle completo de un pedido
    
    GET /tenants/{tenantId}/orders/{orderId}
    """
    tenant_id = event['pathParameters']['tenantId']
    order_id = event['pathParameters']['orderId']
    
    logger.info(f"Getting order details", tenant_id=tenant_id, order_id=order_id)
    
    # Obtener orden de DynamoDB
    order = get_order(tenant_id, order_id)
    
    if not order:
        logger.warning(f"Order not found", tenant_id=tenant_id, order_id=order_id)
        return not_found_response(f"Order {order_id} not found")
    
    logger.info(f"Order found", order_id=order_id, status=order.get('status'))
    
    return success_response(order)
