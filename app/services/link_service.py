import hashlib


def generate_short_code(original_url: str) -> str:
    """
    Generate a short code for a given URL.

    Args:
        original_url (str): The original URL to generate a short code for.

    Returns:
        str: A 6-character hexadecimal string representing the short code.
    """
    hash_object = hashlib.md5(original_url.encode())
    return hash_object.hexdigest()[:6]
