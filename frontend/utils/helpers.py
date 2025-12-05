# frontend/utils/helpers.py
import hashlib

def generate_key(content):
    """Generate a unique key based on content"""
    return hashlib.md5(content.encode()).hexdigest()[:8]

def truncate_text(text, max_length=60):
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."