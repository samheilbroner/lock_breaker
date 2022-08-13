import hashlib

def sha_hash(string: str) -> int:
    print('string to hash = ', string)
    return int(hashlib.sha256(string.encode()).hexdigest(), 16)