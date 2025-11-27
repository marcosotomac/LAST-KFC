"""Handler para crear pedidos"""
import uuid
import os
from datetime import datetime
from ...utils.responses import created_response, error_response
from ...utils.decorators import with_logging, with_error_handling, parse_json_body, validate_tenant
from ...utils.validators import CreateOrderRequest
from ...clients.dynamodb import put_item
from ...clients.eventbridge import publish_order_created
from ...models.order import Order
from ...utils.logger import logger


@with_logging
@with_error_handling
@parse_json_body
@validate_tenant
def handler(event, context):
    """
    Crea un pedido y dispara el workflow
    
    POST /tenants/{tenantId}/orders
    Body: {
        "items": [
            {
                "productId": "prod_123",
                "quantity": 2,
                "price": 15.99,
                "name": "Bucket Original"
            }
        ],
        "customerName": "Juan Pérez",
        "customerPhone": "+51999888777",
        "deliveryAddress": "Av. Larco 123",
        "notes": "Sin picante"
    }
    """
    tenant_id = event['pathParameters']['tenantId']
    
    # Validar request
    try:
        body = event.get('parsedBody', {})
        order_request = CreateOrderRequest(**body)
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return error_response(f"Validation error: {str(e)}", status_code=422)
    
    # Generar ID único para la order
    order_id = f"order_{uuid.uuid4().hex[:16]}"
    
    # Crear objeto Order
    order_data = {
        'tenantId': tenant_id,
        'orderId': order_id,
        'status': 'pending',
        'items': [item.dict() for item in order_request.items],
        'customerName': order_request.customerName,
        'customerPhone': order_request.customerPhone,
        'deliveryAddress': order_request.deliveryAddress,
        'notes': order_request.notes,
        'createdAt': datetime.utcnow().isoformat(),
        'updatedAt': datetime.utcnow().isoformat(),
        'trace': []
    }
    
    order = Order(order_data)
    
    # Calcular total
    total = order.calculate_total()
    
    # Agregar evento de creación al trace
    order.add_trace_event('order_created', f'Order created by {order_request.customerName}')
    
    # Guardar en DynamoDB
    table_name = os.getenv('ORDERS_TABLE')
    put_item(table_name, order.to_dict())
    
    logger.info(
        f"Order created successfully",
        tenant_id=tenant_id,
        order_id=order_id,
        total=total
    )
    
    # Publicar evento a EventBridge para iniciar workflow
    try:
        publish_order_created(
            tenant_id=tenant_id,
            order_id=order_id,
            order_data={
                'customerName': order_request.customerName,
                'totalAmount': total,
                'itemCount': len(order_request.items)
            }
        )
        logger.info(f"Order created event published", order_id=order_id)
    except Exception as e:
        logger.error(f"Failed to publish order created event: {str(e)}")
        # No fallar la creación si el evento falla
    
    return created_response(order.to_dict())
