import hashlib


def add_canonical_suffix(base_name: str, source: str):
    return f"{base_name}_{hashlib.sha224(source.encode('utf-8')).hexdigest()}"
