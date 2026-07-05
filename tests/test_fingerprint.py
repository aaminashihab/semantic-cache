from semantic_cache.fingerprint import normalize, fingerprint

def test_normalize_whitespace():
    assert normalize("  hello   world  ") == "hello world"

def test_normalize_newline():
    assert normalize("hello\nworld") == "hello world"

def test_normalize_lowercase():
    assert normalize("HELLO World") == "hello world"

def test_normalize_unicode():
    # \u00e9 is é, \u0065\u0301 is e + ´
    str1 = "caf\u00e9"
    str2 = "caf\u0065\u0301"
    assert normalize(str1) == normalize(str2)

def test_fingerprint():
    prompt = "test prompt"
    norm_prompt = normalize(prompt)
    fp1 = fingerprint(norm_prompt)
    fp2 = fingerprint(normalize("TEST prompt   "))
    assert fp1 == fp2
