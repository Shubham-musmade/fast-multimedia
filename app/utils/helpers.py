import re
from datetime import datetime
from typing import Tuple

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and special characters.
    """
    # Remove dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Limit length
    if len(filename) > 200:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:195] + ("." + ext if ext else "")
    return filename.strip()


def get_file_extension(filename: str) -> str:
    """Extract and return lowercase file extension"""
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()


def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename with timestamp"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    name, ext = original_filename.rsplit(".", 1) if "." in original_filename else (original_filename, "")
    safe_name = sanitize_filename(name)
    return f"{timestamp}_{safe_name}.{ext}" if ext else f"{timestamp}_{safe_name}"


def validate_uuid(uuid_str: str) -> bool:
    """Basic UUID validation"""
    uuid_pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    return re.match(uuid_pattern, uuid_str) is not None