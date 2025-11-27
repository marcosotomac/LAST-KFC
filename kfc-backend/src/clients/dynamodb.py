"""Cliente DynamoDB con métodos helper"""
import boto3
import os
from typing import Dict, List, Optional, Any
from boto3.dynamodb.conditions import Key, Attr
from ..utils.logger import logger

# Inicializar cliente DynamoDB
dynamodb = boto3.resource('dynamodb')


def get_table(table_name: str):
    """Obtener referencia a tabla DynamoDB"""
    return dynamodb.Table(table_name)


def get_item(table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Obtener un item de DynamoDB"""
    try:
        table = get_table(table_name)
        response = table.get_item(Key=key)
        return response.get('Item')
    except Exception as e:
        logger.error(f"Error getting item from {table_name}: {str(e)}", key=key)
        raise


def put_item(table_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
    """Guardar un item en DynamoDB"""
    try:
        table = get_table(table_name)
        table.put_item(Item=item)
        return item
    except Exception as e:
        logger.error(f"Error putting item to {table_name}: {str(e)}", item=item)
        raise


def update_item(
    table_name: str,
    key: Dict[str, Any],
    updates: Dict[str, Any],
    condition_expression: Optional[str] = None
) -> Dict[str, Any]:
    """Actualizar un item en DynamoDB"""
    try:
        table = get_table(table_name)
        
        # Construir UpdateExpression
        update_expression_parts = []
        expression_attribute_values = {}
        expression_attribute_names = {}
        
        for field, value in updates.items():
            placeholder = f":{field}"
            name_placeholder = f"#{field}"
            update_expression_parts.append(f"{name_placeholder} = {placeholder}")
            expression_attribute_values[placeholder] = value
            expression_attribute_names[name_placeholder] = field
        
        update_expression = "SET " + ", ".join(update_expression_parts)
        
        kwargs = {
            'Key': key,
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expression_attribute_values,
            'ExpressionAttributeNames': expression_attribute_names,
            'ReturnValues': 'ALL_NEW'
        }
        
        if condition_expression:
            kwargs['ConditionExpression'] = condition_expression
        
        response = table.update_item(**kwargs)
        return response.get('Attributes', {})
    except Exception as e:
        logger.error(f"Error updating item in {table_name}: {str(e)}", key=key, updates=updates)
        raise


def query_items(
    table_name: str,
    key_condition_expression: Any,
    filter_expression: Optional[Any] = None,
    index_name: Optional[str] = None,
    limit: Optional[int] = None,
    scan_index_forward: bool = True
) -> List[Dict[str, Any]]:
    """Query items de DynamoDB"""
    try:
        table = get_table(table_name)
        
        kwargs = {
            'KeyConditionExpression': key_condition_expression,
            'ScanIndexForward': scan_index_forward
        }
        
        if filter_expression:
            kwargs['FilterExpression'] = filter_expression
        
        if index_name:
            kwargs['IndexName'] = index_name
        
        if limit:
            kwargs['Limit'] = limit
        
        response = table.query(**kwargs)
        return response.get('Items', [])
    except Exception as e:
        logger.error(f"Error querying {table_name}: {str(e)}")
        raise


def delete_item(table_name: str, key: Dict[str, Any]) -> None:
    """Eliminar un item de DynamoDB"""
    try:
        table = get_table(table_name)
        table.delete_item(Key=key)
    except Exception as e:
        logger.error(f"Error deleting item from {table_name}: {str(e)}", key=key)
        raise


# Helper functions específicas para cada tabla
def get_tenant(tenant_id: str) -> Optional[Dict[str, Any]]:
    """Obtener tenant por ID"""
    table_name = os.getenv('TENANTS_TABLE')
    return get_item(table_name, {'tenantId': tenant_id})


def get_order(tenant_id: str, order_id: str) -> Optional[Dict[str, Any]]:
    """Obtener orden por ID"""
    table_name = os.getenv('ORDERS_TABLE')
    return get_item(table_name, {'tenantId': tenant_id, 'orderId': order_id})


def list_orders_by_tenant(
    tenant_id: str,
    status: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Listar órdenes de un tenant"""
    table_name = os.getenv('ORDERS_TABLE')
    
    if status:
        # Query usando el índice status-index
        return query_items(
            table_name,
            key_condition_expression=Key('tenantId').eq(tenant_id) & Key('status').eq(status),
            index_name='status-index',
            limit=limit,
            scan_index_forward=False  # Orden descendente por fecha
        )
    else:
        # Query por tenantId solamente
        return query_items(
            table_name,
            key_condition_expression=Key('tenantId').eq(tenant_id),
            limit=limit,
            scan_index_forward=False
        )


def get_user_by_email(tenant_id: str, email: str) -> Optional[Dict[str, Any]]:
    """Obtener usuario por email"""
    table_name = os.getenv('USERS_TABLE')
    results = query_items(
        table_name,
        key_condition_expression=Key('tenantId').eq(tenant_id) & Key('email').eq(email),
        index_name='tenant-email-index',
        limit=1
    )
    return results[0] if results else None
