import hashlib
from random import randbytes

def generate_short_code() -> str:
    """
    Generate a short code for a given URL.

    Args:

    Returns:
        str: A 6-character hexadecimal string representing the short code.
    """
    hash_object = hashlib.md5(randbytes(10))
    return hash_object.hexdigest()[:6]
