"""Worker para procesar pedidos en cocina"""
import json
import os
from datetime import datetime
from ...utils.logger import logger
from ...clients.dynamodb import update_item
from ...clients.eventbridge import publish_order_stage_started


def handler(event, context):
    """
    Procesa mensajes SQS de la cola de cocina
    
    El mensaje contiene:
    - taskToken: Token para responder a Step Functions
    - orderId: ID del pedido
    - tenantId: ID del tenant
    - stage: 'kitchen'
    
    IMPORTANTE: Este worker NO envía task_success a Step Functions.
    El task_success lo envía el endpoint complete_stage cuando
    el usuario marca la etapa como completada en la UI.
    """
    logger.info(f"Kitchen worker processing {len(event['Records'])} messages")
    
    for record in event['Records']:
        try:
            # Parsear mensaje SQS
            message_body = json.loads(record['body'])
            
            # El cuerpo del mensaje contiene los datos enviados por Step Functions
            task_token = message_body.get('taskToken')
            order_id = message_body.get('orderId')
            tenant_id = message_body.get('tenantId')
            stage = message_body.get('stage', 'kitchen')
            
            logger.info(
                f"Processing kitchen task",
                order_id=order_id,
                tenant_id=tenant_id,
                task_token=task_token[:50] if task_token else None
            )
            
            # Actualizar orden a estado 'kitchen'
            table_name = os.getenv('ORDERS_TABLE')
            
            # Agregar evento al trace
            trace_event = {
                'timestamp': datetime.utcnow().isoformat(),
                'event': 'kitchen_started',
                'status': 'kitchen',
                'taskToken': task_token[:20] + '...' if task_token else None
            }
            
            # Obtener trace actual y agregar nuevo evento
            from ...clients.dynamodb import get_order
            order = get_order(tenant_id, order_id)
            
            if not order:
                logger.error(f"Order not found", order_id=order_id)
                continue
            
            current_trace = order.get('trace', [])
            current_trace.append(trace_event)
            
            # Actualizar orden
            update_item(
                table_name,
                {'tenantId': tenant_id, 'orderId': order_id},
                {
                    'status': 'kitchen',
                    'updatedAt': datetime.utcnow().isoformat(),
                    'trace': current_trace,
                    'kitchenTaskToken': task_token  # Guardar para usar después
                }
            )
            
            logger.info(f"Order moved to kitchen", order_id=order_id)
            
            # Publicar evento de inicio de cocina
            publish_order_stage_started(tenant_id, order_id, 'kitchen')
            
            logger.info(f"Kitchen processing initiated", order_id=order_id)
            
            # NOTA: NO enviamos task_success aquí
            # El workflow quedará en espera hasta que el endpoint
            # /orders/{orderId}/stages/kitchen/complete sea llamado
            
        except Exception as e:
            logger.exception(f"Error processing kitchen message: {str(e)}")
            # La excepción hará que el mensaje sea reintentado o enviado a DLQ
            raise
    
    return {
        'statusCode': 200,
        'body': f'Processed {len(event["Records"])} messages'
    }
