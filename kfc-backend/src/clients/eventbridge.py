"""Cliente EventBridge para publicar eventos"""
import boto3
import json
import os
from typing import Dict, Any
from datetime import datetime
from ..utils.logger import logger

# Inicializar cliente EventBridge
events_client = boto3.client('events')


def publish_event(
    source: str,
    detail_type: str,
    detail: Dict[str, Any],
    event_bus_name: str = None
) -> Dict[str, Any]:
    """
    Publicar evento al EventBridge bus
    
    Args:
        source: Fuente del evento (ej: 'kfc.orders')
        detail_type: Tipo de evento (ej: 'order.created')
        detail: Datos del evento
        event_bus_name: Nombre del bus (opcional, usa env var por defecto)
    
    Returns:
        Respuesta de EventBridge
    """
    if not event_bus_name:
        event_bus_name = os.getenv('EVENT_BUS_NAME')
    
    try:
        # Agregar timestamp si no existe
        if 'timestamp' not in detail:
            detail['timestamp'] = datetime.utcnow().isoformat()
        
        response = events_client.put_events(
            Entries=[
                {
                    'Source': source,
                    'DetailType': detail_type,
                    'Detail': json.dumps(detail),
                    'EventBusName': event_bus_name
                }
            ]
        )
        
        # Verificar si hubo errores
        if response.get('FailedEntryCount', 0) > 0:
            logger.error(
                "Failed to publish event",
                source=source,
                detail_type=detail_type,
                errors=response.get('Entries', [])
            )
            raise Exception(f"Failed to publish event: {response}")
        
        logger.info(
            "Event published successfully",
            source=source,
            detail_type=detail_type,
            event_id=response['Entries'][0].get('EventId')
        )
        
        return response
    except Exception as e:
        logger.exception(
            f"Error publishing event: {str(e)}",
            source=source,
            detail_type=detail_type
        )
        raise


# Helper functions para eventos específicos
def publish_order_created(tenant_id: str, order_id: str, order_data: Dict[str, Any]):
    """Publicar evento de orden creada"""
    return publish_event(
        source='kfc.orders',
        detail_type='order.created',
        detail={
            'tenantId': tenant_id,
            'orderId': order_id,
            **order_data
        }
    )


def publish_order_stage_started(tenant_id: str, order_id: str, stage: str):
    """Publicar evento de inicio de etapa"""
    return publish_event(
        source='kfc.orders',
        detail_type=f'order.{stage}.started',
        detail={
            'tenantId': tenant_id,
            'orderId': order_id,
            'stage': stage
        }
    )


def publish_order_stage_completed(tenant_id: str, order_id: str, stage: str):
    """Publicar evento de completado de etapa"""
    return publish_event(
        source='kfc.orders',
        detail_type=f'order.{stage}.completed',
        detail={
            'tenantId': tenant_id,
            'orderId': order_id,
            'stage': stage
        }
    )


def publish_order_delivered(tenant_id: str, order_id: str):
    """Publicar evento de orden entregada"""
    return publish_event(
        source='kfc.orders',
        detail_type='order.delivered',
        detail={
            'tenantId': tenant_id,
            'orderId': order_id
        }
    )


def publish_order_failed(tenant_id: str, order_id: str, error: str):
    """Publicar evento de orden fallida"""
    return publish_event(
        source='kfc.orders',
        detail_type='order.failed',
        detail={
            'tenantId': tenant_id,
            'orderId': order_id,
            'error': error
        }
    )
