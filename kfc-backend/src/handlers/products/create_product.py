"""Handler para crear productos"""
import uuid
import os
from datetime import datetime
from ...utils.responses import created_response, error_response
from ...utils.decorators import with_logging, with_error_handling, parse_json_body, validate_tenant
from ...utils.validators import CreateProductRequest
from ...clients.dynamodb import put_item
from ...utils.logger import logger


@with_logging
@with_error_handling
@parse_json_body
@validate_tenant
def handler(event, context):
    """
    Crea un producto para un tenant
    
    POST /tenants/{tenantId}/products
    Body: {
        "name": "Bucket Original 8 piezas",
        "description": "8 piezas de pollo...",
        "price": 45.90,
        "category": "Buckets",
        "imageUrl": "https://...",
        "available": true
    }
    """
    tenant_id = event['pathParameters']['tenantId']
    
    # Validar request
    try:
        body = event.get('parsedBody', {})
        product_request = CreateProductRequest(**body)
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return error_response(f"Validation error: {str(e)}", status_code=422)
    
    # Generar ID único para el producto
    product_id = f"prod_{uuid.uuid4().hex[:12]}"
    
    # Crear producto
    product = {
        'tenantId': tenant_id,
        'productId': product_id,
        'name': product_request.name,
        'description': product_request.description,
        'price': product_request.price,
        'category': product_request.category,
        'imageUrl': product_request.imageUrl,
        'available': product_request.available,
        'createdAt': datetime.utcnow().isoformat(),
        'updatedAt': datetime.utcnow().isoformat()
    }
    
    # Guardar en DynamoDB
    table_name = os.getenv('PRODUCTS_TABLE')
    put_item(table_name, product)
    
    logger.info(
        f"Product created successfully",
        tenant_id=tenant_id,
        product_id=product_id,
        name=product_request.name
    )
    
    return created_response(product)
