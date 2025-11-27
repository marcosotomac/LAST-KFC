"""Worker para procesar empaque de pedidos"""
import json
import os
from datetime import datetime
from ...utils.logger import logger
from ...clients.dynamodb import update_item, get_order
from ...clients.eventbridge import publish_order_stage_started


def handler(event, context):
    """
    Procesa mensajes SQS de la cola de empaque
    
    Similar a kitchen_worker, este worker inicia el procesamiento
    pero el task_success se envía desde el endpoint complete_stage
    """
    logger.info(f"Packaging worker processing {len(event['Records'])} messages")
    
    for record in event['Records']:
        try:
            message_body = json.loads(record['body'])
            
            task_token = message_body.get('taskToken')
            order_id = message_body.get('orderId')
            tenant_id = message_body.get('tenantId')
            stage = message_body.get('stage', 'packaging')
            
            logger.info(
                f"Processing packaging task",
                order_id=order_id,
                tenant_id=tenant_id
            )
            
            # Actualizar orden a estado 'packaging'
            table_name = os.getenv('ORDERS_TABLE')
            
            order = get_order(tenant_id, order_id)
            if not order:
                logger.error(f"Order not found", order_id=order_id)
                continue
            
            current_trace = order.get('trace', [])
            current_trace.append({
                'timestamp': datetime.utcnow().isoformat(),
                'event': 'packaging_started',
                'status': 'packaging'
            })
            
            update_item(
                table_name,
                {'tenantId': tenant_id, 'orderId': order_id},
                {
                    'status': 'packaging',
                    'updatedAt': datetime.utcnow().isoformat(),
                    'trace': current_trace,
                    'packagingTaskToken': task_token
                }
            )
            
            logger.info(f"Order moved to packaging", order_id=order_id)
            
            # Publicar evento
            publish_order_stage_started(tenant_id, order_id, 'packaging')
            
            logger.info(f"Packaging processing initiated", order_id=order_id)
            
        except Exception as e:
            logger.exception(f"Error processing packaging message: {str(e)}")
            raise
    
    return {
        'statusCode': 200,
        'body': f'Processed {len(event["Records"])} messages'
    }
