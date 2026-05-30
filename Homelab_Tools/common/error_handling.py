#!/usr/bin/env python3
"""
Common Error Handling Utilities
Standardized error handling patterns across all homelab modules
"""

import logging
import traceback
from typing import Dict, Any, Optional, Callable
from functools import wraps
import time

class HomelabError(Exception):
    """Base exception class for homelab applications"""
    def __init__(self, message: str, error_code: str = None, context: Dict[str, Any] = None):
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = time.time()

class ValidationError(HomelabError):
    """Raised when input validation fails"""
    def __init__(self, message: str, field: str = None, context: Dict[str, Any] = None):
        super().__init__(message, "VALIDATION_ERROR", context)
        self.field = field

class ResourceError(HomelabError):
    """Raised when resource allocation/access fails"""
    def __init__(self, message: str, resource_type: str = None, context: Dict[str, Any] = None):
        super().__init__(message, "RESOURCE_ERROR", context)
        self.resource_type = resource_type

class NetworkError(HomelabError):
    """Raised when network operations fail"""
    def __init__(self, message: str, host: str = None, port: int = None, context: Dict[str, Any] = None):
        super().__init__(message, "NETWORK_ERROR", context)
        self.host = host
        self.port = port

class SystemError(HomelabError):
    """Raised when system-level operations fail"""
    def __init__(self, message: str, system_component: str = None, context: Dict[str, Any] = None):
        super().__init__(message, "SYSTEM_ERROR", context)
        self.system_component = system_component

def setup_logger(name: str, log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """Setup standardized logger with consistent formatting"""
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(error_code)s] %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def log_errors(logger: logging.Logger, reraise: bool = True):
    """Decorator to automatically log exceptions with context"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HomelabError as e:
                # Log homelab errors with full context
                error_msg = f"{str(e)} | Context: {e.context}"
                if hasattr(e, 'field') and e.field:
                    error_msg += f" | Field: {e.field}"
                if hasattr(e, 'resource_type') and e.resource_type:
                    error_msg += f" | Resource: {e.resource_type}"
                if hasattr(e, 'host') and e.host:
                    error_msg += f" | Host: {e.host}:{e.port}"
                if hasattr(e, 'system_component') and e.system_component:
                    error_msg += f" | Component: {e.system_component}"
                
                logger.error(error_msg, extra={'error_code': e.error_code or 'UNKNOWN'})
                
                if reraise:
                    raise
                return None
            except Exception as e:
                # Log unexpected errors with full traceback
                logger.error(f"Unexpected error in {func.__name__}: {str(e)} | Traceback: {traceback.format_exc()}", 
                           extra={'error_code': 'UNEXPECTED'})
                
                if reraise:
                    raise
                return None
        return wrapper
    return decorator

def log_async_errors(logger: logging.Logger, reraise: bool = True):
    """Decorator to automatically log exceptions in async functions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HomelabError as e:
                # Log homelab errors with full context
                error_msg = f"{str(e)} | Context: {e.context}"
                if hasattr(e, 'field') and e.field:
                    error_msg += f" | Field: {e.field}"
                if hasattr(e, 'resource_type') and e.resource_type:
                    error_msg += f" | Resource: {e.resource_type}"
                if hasattr(e, 'host') and e.host:
                    error_msg += f" | Host: {e.host}:{e.port}"
                if hasattr(e, 'system_component') and e.system_component:
                    error_msg += f" | Component: {e.system_component}"
                
                logger.error(error_msg, extra={'error_code': e.error_code or 'UNKNOWN'})
                
                if reraise:
                    raise
                return None
            except Exception as e:
                # Log unexpected errors with full traceback
                logger.error(f"Unexpected error in {func.__name__}: {str(e)} | Traceback: {traceback.format_exc()}", 
                           extra={'error_code': 'UNEXPECTED'})
                
                if reraise:
                    raise
                return None
        return wrapper
    return decorator

def create_error_response(error: HomelabError, include_traceback: bool = False) -> Dict[str, Any]:
    """Create standardized error response for API endpoints"""
    response = {
        'status': 'error',
        'error_code': error.error_code,
        'message': str(error),
        'timestamp': error.timestamp,
        'context': error.context
    }
    
    # Add specific error type information
    if isinstance(error, ValidationError):
        response['error_type'] = 'validation'
        if error.field:
            response['field'] = error.field
    elif isinstance(error, ResourceError):
        response['error_type'] = 'resource'
        if error.resource_type:
            response['resource_type'] = error.resource_type
    elif isinstance(error, NetworkError):
        response['error_type'] = 'network'
        if error.host:
            response['host'] = error.host
            if error.port:
                response['port'] = error.port
    elif isinstance(error, SystemError):
        response['error_type'] = 'system'
        if error.system_component:
            response['system_component'] = error.system_component
    
    # Include traceback if requested (for debugging)
    if include_traceback:
        response['traceback'] = traceback.format_exc()
    
    return response

def create_success_response(data: Any = None, message: str = None) -> Dict[str, Any]:
    """Create standardized success response for API endpoints"""
    response = {
        'status': 'success',
        'timestamp': time.time()
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    return response

def validate_input(value: Any, field_name: str, required: bool = True, 
                   value_type: type = None, min_val: Any = None, max_val: Any = None,
                   allowed_values: list = None) -> Any:
    """Standardized input validation utility"""
    
    # Check required
    if required and (value is None or value == ''):
        raise ValidationError(f"{field_name} is required", field_name)
    
    # Skip further validation if not required and value is empty
    if not required and (value is None or value == ''):
        return value
    
    # Type validation
    if value_type and not isinstance(value, value_type):
        raise ValidationError(f"{field_name} must be of type {value_type.__name__}", field_name)
    
    # Numeric range validation
    if isinstance(value, (int, float)):
        if min_val is not None and value < min_val:
            raise ValidationError(f"{field_name} must be >= {min_val}", field_name)
        if max_val is not None and value > max_val:
            raise ValidationError(f"{field_name} must be <= {max_val}", field_name)
    
    # String length validation
    if isinstance(value, str):
        if min_val is not None and len(value) < min_val:
            raise ValidationError(f"{field_name} must be at least {min_val} characters", field_name)
        if max_val is not None and len(value) > max_val:
            raise ValidationError(f"{field_name} must be at most {max_val} characters", field_name)
    
    # Allowed values validation
    if allowed_values and value not in allowed_values:
        raise ValidationError(f"{field_name} must be one of: {allowed_values}", field_name)
    
    return value

def handle_safe_operation(operation: Callable, error_message: str = None, 
                         default_return: Any = None, logger: logging.Logger = None) -> Any:
    """Safely execute operation with error handling"""
    try:
        return operation()
    except Exception as e:
        if logger:
            logger.error(f"{error_message or 'Operation failed'}: {str(e)}")
        return default_return

# Common validation patterns
MEMORY_SIZE_RANGE = (1, 1024 * 1024)  # 1 byte to 1GB
PORT_RANGE = (1024, 65535)  # Non-privileged ports
COMMON_PERMISSIONS = ['r', 'w', 'rw']

def validate_memory_size(size_mb: float, field_name: str = "size_mb") -> float:
    """Validate memory size in MB"""
    return validate_input(size_mb, field_name, required=True, value_type=(int, float), 
                         min_val=0.1, max_val=1024*1024)  # 0.1MB to 1TB

def validate_port(port: int, field_name: str = "port") -> int:
    """Validate port number"""
    return validate_input(port, field_name, required=True, value_type=int, 
                         min_val=PORT_RANGE[0], max_val=PORT_RANGE[1])

def validate_permissions(permissions: str, field_name: str = "permissions") -> str:
    """Validate permission string"""
    return validate_input(permissions, field_name, required=True, value_type=str, 
                         allowed_values=COMMON_PERMISSIONS)

def validate_client_id(client_id: str, field_name: str = "client_id") -> str:
    """Validate client ID"""
    return validate_input(client_id, field_name, required=True, value_type=str, 
                         min_val=1, max_val=100)  # 1-100 characters
