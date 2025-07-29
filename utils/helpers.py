import logging
import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_session_id() -> str:
    """Generate a unique session ID"""
    return str(uuid.uuid4())

def generate_tool_call_id() -> str:
    """Generate a unique tool call ID"""
    return f"tool_call_{uuid.uuid4().hex[:8]}"

def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format datetime to ISO string"""
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat()

def safe_json_dumps(obj: Any) -> str:
    """Safely serialize object to JSON"""
    try:
        return json.dumps(obj, default=str)
    except Exception as e:
        logger.error(f"Error serializing object to JSON: {e}")
        return json.dumps({"error": "Serialization failed"})

def parse_json_safely(data: str) -> Optional[Dict[str, Any]]:
    """Safely parse JSON string"""
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing JSON: {e}")
        return None

def validate_required_fields(data: Dict[str, Any], required_fields: list) -> list:
    """Validate that required fields are present in data"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    return missing_fields

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    import re
    # Remove or replace unsafe characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    return sanitized

def get_memory_usage() -> Dict[str, Any]:
    """Get current memory usage information"""
    import psutil
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size in MB
            "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size in MB
            "percent": process.memory_percent(),
            "available_mb": psutil.virtual_memory().available / 1024 / 1024
        }
    except Exception as e:
        logger.error(f"Error getting memory usage: {e}")
        return {"error": str(e)}

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def create_error_response(error: str, status_code: int = 500) -> Dict[str, Any]:
    """Create a standardized error response"""
    return {
        "error": error,
        "status_code": status_code,
        "timestamp": format_timestamp(),
        "request_id": str(uuid.uuid4())
    }

def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Create a standardized success response"""
    return {
        "data": data,
        "message": message,
        "timestamp": format_timestamp(),
        "request_id": str(uuid.uuid4())
    } 