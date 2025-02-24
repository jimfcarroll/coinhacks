import re

def is_valid_hex_str(val: str) -> bool:
    """Check if a string is a valid hexadecimal string."""
    return bool(re.fullmatch(r"[0-9a-fA-F]+", val))
