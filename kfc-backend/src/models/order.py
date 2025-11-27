"""Modelo de datos para Orders"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..utils.validators import OrderStatus


class Order:
    """Clase para gestionar órdenes"""
    
    def __init__(self, order_data: Dict[str, Any]):
        self.tenant_id = order_data.get('tenantId')
        self.order_id = order_data.get('orderId')
        self.status = order_data.get('status', OrderStatus.PENDING.value)
        self.items = order_data.get('items', [])
        self.customer_name = order_data.get('customerName')
        self.customer_phone = order_data.get('customerPhone')
        self.delivery_address = order_data.get('deliveryAddress')
        self.notes = order_data.get('notes')
        self.total_amount = order_data.get('totalAmount', 0.0)
        self.created_at = order_data.get('createdAt', datetime.utcnow().isoformat())
        self.updated_at = order_data.get('updatedAt', datetime.utcnow().isoformat())
        self.trace = order_data.get('trace', [])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para DynamoDB"""
        return {
            'tenantId': self.tenant_id,
            'orderId': self.order_id,
            'status': self.status,
            'items': self.items,
            'customerName': self.customer_name,
            'customerPhone': self.customer_phone,
            'deliveryAddress': self.delivery_address,
            'notes': self.notes,
            'totalAmount': self.total_amount,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
            'trace': self.trace
        }
    
    def add_trace_event(self, event_type: str, details: str = None) -> None:
        """Agregar evento al historial de trazabilidad"""
        trace_event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': event_type,
            'status': self.status
        }
        if details:
            trace_event['details'] = details
        
        self.trace.append(trace_event)
        self.updated_at = datetime.utcnow().isoformat()
    
    def update_status(self, new_status: str, details: str = None) -> None:
        """Actualizar estado de la orden"""
        old_status = self.status
        self.status = new_status
        self.add_trace_event(
            f'status_changed_{old_status}_to_{new_status}',
            details
        )
    
    def calculate_total(self) -> float:
        """Calcular total de la orden"""
        total = sum(
            item.get('price', 0) * item.get('quantity', 1)
            for item in self.items
        )
        self.total_amount = round(total, 2)
        return self.total_amount
