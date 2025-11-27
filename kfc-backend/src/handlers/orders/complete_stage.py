"""Handler para completar una etapa del workflow"""
import os
from datetime import datetime
from ...utils.responses import success_response, not_found_response, error_response
from ...utils.decorators import with_logging, with_error_handling, parse_json_body, validate_tenant
from ...clients.dynamodb import get_order, update_item
from ...clients.stepfunctions import send_task_success
from ...clients.eventbridge import publish_order_stage_completed
from ...utils.logger import logger


@with_logging
@with_error_handling
@parse_json_body
@validate_tenant
def handler(event, context):
    """
    Completa una etapa del workflow y notifica a Step Functions
    
    POST /tenants/{tenantId}/orders/{orderId}/stages/{stage}/complete
    Body: {
        "taskToken": "...",
        "notes": "Completed successfully"
    }
    """
    tenant_id = event['pathParameters']['tenantId']
    order_id = event['pathParameters']['orderId']
    stage = event['pathParameters']['stage']
    
    body = event.get('parsedBody', {})
    task_token = body.get('taskToken')
    notes = body.get('notes', '')
    
    logger.info(
        f"Completing stage for order",
        tenant_id=tenant_id,
        order_id=order_id,
        stage=stage
    )
    
    # Verificar que la orden existe
    order = get_order(tenant_id, order_id)
    if not order:
        return not_found_response(f"Order {order_id} not found")
    
    # Validar que el stage es válido
    valid_stages = ['kitchen', 'packaging', 'delivery']
    if stage not in valid_stages:
        return error_response(
            f"Invalid stage. Must be one of: {', '.join(valid_stages)}",
            status_code=400
        )
    
    # Actualizar estado en DynamoDB
    try:
        # Agregar evento al trace
        new_trace_event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': f'{stage}_completed',
            'status': stage,
            'notes': notes
        }
        
        current_trace = order.get('trace', [])
        current_trace.append(new_trace_event)
        
        updates = {
            'status': stage,
            'updatedAt': datetime.utcnow().isoformat(),
            'trace': current_trace
        }
        
        updated_order = update_item(
            os.getenv('ORDERS_TABLE'),
            {'tenantId': tenant_id, 'orderId': order_id},
            updates
        )
        
        logger.info(f"Order status updated", order_id=order_id, status=stage)
    except Exception as e:
        logger.error(f"Failed to update order: {str(e)}")
        return error_response("Failed to update order", status_code=500)
    
    # Publicar evento de stage completado
    try:
        publish_order_stage_completed(tenant_id, order_id, stage)
        logger.info(f"Stage completed event published", order_id=order_id, stage=stage)
    except Exception as e:
        logger.error(f"Failed to publish event: {str(e)}")
    
    # Si hay taskToken, notificar a Step Functions
    if task_token:
        try:
            send_task_success(
                task_token=task_token,
                output={
                    'orderId': order_id,
                    'tenantId': tenant_id,
                    'stage': stage,
                    'completedAt': datetime.utcnow().isoformat()
                }
            )
            logger.info(f"Task success sent to Step Functions", order_id=order_id)
        except Exception as e:
            logger.error(f"Failed to send task success: {str(e)}")
            # No fallar si esto falla
    
    return success_response({
        'message': f'Stage {stage} completed successfully',
        'order': updated_order
    })
