from datetime import datetime
import re
import unicodedata


def sanitize_name(name: str) -> str:
    """Normalize a Unicode name to ASCII, remove diacritics, and keep only alphanumerics.

    Examples:
    - "Hồng Anh" -> "HongAnh"
    - "Nguyễn-Văn" -> "NguyenVan"
    """
    if not name:
        return ""
    # Decompose unicode characters and drop diacritics
    normalized = unicodedata.normalize('NFKD', name)
    ascii_bytes = normalized.encode('ascii', 'ignore')
    ascii_str = ascii_bytes.decode('ascii')
    # Remove spaces and any non-alphanumeric characters
    cleaned = re.sub(r'[^A-Za-z0-9]', '', ascii_str)
    return cleaned


def make_folder_name(user_name: str) -> str:
    now = datetime.now()
    safe = sanitize_name(user_name)
    return now.strftime(f"%d_%m_%Y_%H_%M_") + safe