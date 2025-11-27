"""Handler para listar productos"""
from boto3.dynamodb.conditions import Key
from ...utils.responses import success_response
from ...utils.decorators import with_logging, with_error_handling, validate_tenant
from ...clients.dynamodb import query_items
from ...utils.logger import logger
import os


@with_logging
@with_error_handling
@validate_tenant
def handler(event, context):
    """
    Lista productos de un tenant
    
    GET /tenants/{tenantId}/products?category=Buckets&available=true
    """
    tenant_id = event['pathParameters']['tenantId']
    
    # Obtener query parameters
    query_params = event.get('queryStringParameters') or {}
    category = query_params.get('category')
    available_str = query_params.get('available')
    
    logger.info(
        f"Listing products for tenant",
        tenant_id=tenant_id,
        category=category
    )
    
    # Query productos del tenant
    table_name = os.getenv('PRODUCTS_TABLE')
    products = query_items(
        table_name,
        key_condition_expression=Key('tenantId').eq(tenant_id)
    )
    
    # Filtrar por categoría si se especifica
    if category:
        products = [p for p in products if p.get('category') == category]
    
    # Filtrar por disponibilidad si se especifica
    if available_str:
        available = available_str.lower() == 'true'
        products = [p for p in products if p.get('available') == available]
    
    logger.info(
        f"Found {len(products)} products",
        tenant_id=tenant_id,
        count=len(products)
    )
    
    return success_response({
        'products': products,
        'count': len(products)
    })
