"""Handler para listar pedidos"""
from ...utils.responses import success_response
from ...utils.decorators import with_logging, with_error_handling, validate_tenant
from ...clients.dynamodb import list_orders_by_tenant
from ...utils.logger import logger


@with_logging
@with_error_handling
@validate_tenant
def handler(event, context):
    """
    Lista pedidos de un tenant con filtro opcional por estado
    
    GET /tenants/{tenantId}/orders?status=pending&limit=50
    """
    tenant_id = event['pathParameters']['tenantId']
    
    # Obtener query parameters
    query_params = event.get('queryStringParameters') or {}
    status = query_params.get('status')
    limit = int(query_params.get('limit', 100))
    
    # Limitar a máximo 100 resultados
    if limit > 100:
        limit = 100
    
    logger.info(
        f"Listing orders for tenant",
        tenant_id=tenant_id,
        status=status,
        limit=limit
    )
    
    # Obtener órdenes de DynamoDB
    orders = list_orders_by_tenant(
        tenant_id=tenant_id,
        status=status,
        limit=limit
    )
    
    logger.info(
        f"Found {len(orders)} orders",
        tenant_id=tenant_id,
        count=len(orders)
    )
    
    return success_response({
        'orders': orders,
        'count': len(orders),
        'limit': limit,
        'filters': {
            'status': status
        } if status else None
    })
