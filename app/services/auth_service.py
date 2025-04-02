import hashlib


def hash_password(password: str) -> str:
   """
   Hash a password using the MD5 algorithm.

   Args:
       password (str): The password to hash.

   Returns:
       str: The hashed password.
   """
   hash_object = hashlib.md5(password.encode())
   return hash_object.hexdigest()
    