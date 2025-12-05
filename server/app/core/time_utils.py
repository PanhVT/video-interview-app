from datetime import datetime
import re

def sanitize_name(name: str) -> str:
    name = re.sub(r'[^A-Za-z0-9_-]', '_', name)
    return name

def make_folder_name(user_name: str) -> str:
    now = datetime.now()
    safe = sanitize_name(user_name)
    return now.strftime(f"%d_%m_%Y_%H_%M_") + safe