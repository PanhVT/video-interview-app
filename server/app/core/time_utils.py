from datetime import datetime
import re
import unicodedata
import hashlib


def sanitize_name(name: str, max_length: int = 48, sep: str = "_") -> str:
    """Produce a filesystem-safe, readable, deterministic name from user input.

    Behavior:
    - NFKD normalize and drop diacritics
    - Convert to ASCII (drop other scripts)
    - Replace runs of non-alphanumeric characters with a single separator (`sep`)
    - Lowercase the result
    - Trim leading/trailing separators
    - Truncate to `max_length`
    - If the result is empty (e.g. name was non-ASCII only), return a fallback
      of the form `user_<sha1_first8>` so the folder name is not empty.

    Examples:
    - "Hồng Anh" -> "hong_anh"
    - "Nguyễn-Văn" -> "nguyen_van"
    - "张伟" -> "user_a1b2c3d4" (fallback)
    """
    if name is None:
        return ""
    # Preserve empty input as empty (do not produce a hashed fallback for empty)
    if isinstance(name, str) and name.strip() == "":
        return ""

    # Decompose unicode characters and drop diacritics
    normalized = unicodedata.normalize("NFKD", name)
    ascii_str = normalized.encode("ascii", "ignore").decode("ascii")

    # Replace any run of non-alphanumeric chars with a single separator
    cleaned = re.sub(r"[^A-Za-z0-9]+", sep, ascii_str).strip(sep)

    # Normalize to lower-case for consistency
    cleaned = cleaned.lower()

    # Fallback when the cleaned name is empty (e.g., non-Latin input)
    if not cleaned:
        digest = hashlib.sha1(name.encode("utf-8")).hexdigest()[:8]
        cleaned = f"user_{digest}"

    # Truncate to max_length and trim trailing separator
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip(sep)

    return cleaned


def make_folder_name(user_name: str) -> str:
    now = datetime.now()
    safe = sanitize_name(user_name)
    return now.strftime(f"%d_%m_%Y_%H_%M_") + safe