import os
import re
from werkzeug.utils import secure_filename
from config import Config

def is_allowed_file(filename: str, allowed_extensions: set = None) -> bool:
    """
    Check if a filename has an allowed extension.
    Prevents empty extensions and hidden files.
    """
    if not filename or "." not in filename:
        return False
    
    ext = filename.rsplit(".", 1)[1].lower()
    allowed = allowed_extensions or Config.ALLOWED_EXTENSIONS
    return ext in allowed

def get_safe_filename(original_filename: str) -> str:
    """
    Sanitize filename and prepend a safe unique prefix to prevent overwrite
    and path traversal attacks.
    """
    safe_name = secure_filename(original_filename)
    if not safe_name:
        safe_name = "uploaded_file"
    return safe_name

def validate_required_fields(data: dict, required_fields: list) -> tuple[bool, str]:
    """
    Validate that all required fields exist and are non-empty in the input dict.
    Returns (is_valid, error_message).
    """
    if not isinstance(data, dict):
        return False, "Invalid payload format. Expected JSON object."
    
    missing = [field for field in required_fields if field not in data or data[field] is None or str(data[field]).strip() == ""]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    return True, ""

def validate_numeric(val, min_val=None, max_val=None, field_name="Field") -> tuple[bool, float, str]:
    """
    Validate that a value can be converted to float and is within optional bounds.
    Returns (is_valid, numeric_val, error_message).
    """
    try:
        num = float(val)
        if min_val is not None and num < min_val:
            return False, num, f"{field_name} must be at least {min_val}"
        if max_val is not None and num > max_val:
            return False, num, f"{field_name} must be no greater than {max_val}"
        return True, num, ""
    except (ValueError, TypeError):
        return False, 0.0, f"{field_name} must be a valid number"
