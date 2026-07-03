import hashlib
import unicodedata
import re

def normalize(prompt: str, lowercase: bool = True) -> str:
    \"\"\"
    Normalize text by:
    1. NFKC unicode normalization
    2. Lowercasing (optional)
    3. Collapsing whitespace
    4. Stripping leading/trailing whitespace
    \"\"\"
    text = unicodedata.normalize('NFKC', prompt)
    if lowercase:
        text = text.lower()
    text = re.sub(r'\\s+', ' ', text)
    return text.strip()

def fingerprint(normalized_prompt: str) -> str:
    \"\"\"Generate a SHA-256 fingerprint for a normalized prompt.\"\"\"
    return hashlib.sha256(normalized_prompt.encode('utf-8')).hexdigest()
