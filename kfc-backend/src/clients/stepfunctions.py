"""Cliente Step Functions"""
import boto3
import json
from typing import Dict, Any
from ..utils.logger import logger

# Inicializar cliente Step Functions
sfn_client = boto3.client('stepfunctions')


def start_execution(
    state_machine_arn: str,
    input_data: Dict[str, Any],
    name: str = None
) -> Dict[str, Any]:
    """
    Iniciar ejecución de Step Function
    
    Args:
        state_machine_arn: ARN de la State Machine
        input_data: Datos de entrada para la ejecución
        name: Nombre único para la ejecución (opcional)
    
    Returns:
        Respuesta de Step Functions
    """
    try:
        kwargs = {
            'stateMachineArn': state_machine_arn,
            'input': json.dumps(input_data)
        }
        
        if name:
            kwargs['name'] = name
        
        response = sfn_client.start_execution(**kwargs)
        
        logger.info(
            "Step Function execution started",
            execution_arn=response['executionArn'],
            state_machine=state_machine_arn
        )
        
        return response
    except Exception as e:
        logger.exception(
            f"Error starting Step Function execution: {str(e)}",
            state_machine=state_machine_arn
        )
        raise


def send_task_success(task_token: str, output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enviar éxito de tarea a Step Functions
    
    Args:
        task_token: Token de la tarea (recibido en el mensaje SQS)
        output: Resultado de la tarea
    
    Returns:
        Respuesta de Step Functions
    """
    try:
        response = sfn_client.send_task_success(
            taskToken=task_token,
            output=json.dumps(output)
        )
        
        logger.info("Task success sent to Step Functions", task_token=task_token[:50])
        
        return response
    except Exception as e:
        logger.exception(
            f"Error sending task success: {str(e)}",
            task_token=task_token[:50]
        )
        raise


def send_task_failure(task_token: str, error: str, cause: str = None) -> Dict[str, Any]:
    """
    Enviar fallo de tarea a Step Functions
    
    Args:
        task_token: Token de la tarea
        error: Código de error
        cause: Descripción detallada del error (opcional)
    
    Returns:
        Respuesta de Step Functions
    """
    try:
        kwargs = {
            'taskToken': task_token,
            'error': error
        }
        
        if cause:
            kwargs['cause'] = cause
        
        response = sfn_client.send_task_failure(**kwargs)
        
        logger.warning(
            "Task failure sent to Step Functions",
            task_token=task_token[:50],
            error=error
        )
        
        return response
    except Exception as e:
        logger.exception(
            f"Error sending task failure: {str(e)}",
            task_token=task_token[:50]
        )
        raise


def send_task_heartbeat(task_token: str) -> Dict[str, Any]:
    """
    Enviar heartbeat para mantener la tarea activa
    
    Args:
        task_token: Token de la tarea
    
    Returns:
        Respuesta de Step Functions
    """
    try:
        response = sfn_client.send_task_heartbeat(taskToken=task_token)
        
        logger.debug("Task heartbeat sent", task_token=task_token[:50])
        
        return response
    except Exception as e:
        logger.exception(
            f"Error sending task heartbeat: {str(e)}",
            task_token=task_token[:50]
        )
        raise
