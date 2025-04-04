import hashlib
from random import randbytes
import geoip2.database


def generate_short_code() -> str:
    """
    Generate a short code for a given URL.

    Args:

    Returns:
        str: A 6-character hexadecimal string representing the short code.
    """
    hash_object = hashlib.md5(randbytes(10))
    return hash_object.hexdigest()[:6]

def get_geo_info(ip: str):
    try:
        reader = geoip2.database.Reader('/app/GeoLite2-City.mmdb')
        response = reader.city(ip)
        country = response.country.iso_code
        city = response.city.name
        return country, city
    except Exception as e:
        print(f"get_geo_info: {e}")
        return None, None
