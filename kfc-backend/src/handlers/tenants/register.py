"""Handler para registrar tenants (franquicias)"""
import uuid
from datetime import datetime
from ...utils.responses import created_response, error_response
from ...utils.decorators import with_logging, with_error_handling, parse_json_body
from ...utils.validators import CreateTenantRequest
from ...clients.dynamodb import put_item, get_tenant
from ...utils.logger import logger
import os


@with_logging
@with_error_handling
@parse_json_body
def handler(event, context):
    """
    Registra un nuevo tenant (franquicia KFC)
    
    POST /tenants
    Body: {
        "name": "KFC Miraflores",
        "email": "miraflores@kfc.com.pe",
        "phone": "+51999888777",
        "address": "Av. Larco 123",
        "city": "Lima",
        "country": "PE"
    }
    """
    # Parsear y validar datos
    try:
        body = event.get('parsedBody', {})
        tenant_request = CreateTenantRequest(**body)
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return error_response(f"Validation error: {str(e)}", status_code=422)
    
    # Generar ID único para el tenant
    tenant_id = f"tenant_{uuid.uuid4().hex[:12]}"
    
    # Verificar que no exista un tenant con el mismo email
    # (Esto requeriría un GSI en producción real)
    
    # Crear tenant
    tenant = {
        'tenantId': tenant_id,
        'name': tenant_request.name,
        'email': tenant_request.email,
        'phone': tenant_request.phone,
        'address': tenant_request.address,
        'city': tenant_request.city,
        'country': tenant_request.country,
        'active': True,
        'createdAt': datetime.utcnow().isoformat(),
        'updatedAt': datetime.utcnow().isoformat()
    }
    
    # Guardar en DynamoDB
    table_name = os.getenv('TENANTS_TABLE')
    put_item(table_name, tenant)
    
    logger.info(f"Tenant created successfully", tenant_id=tenant_id, name=tenant_request.name)
    
    return created_response(tenant)
