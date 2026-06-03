from src.importer import normalize_name, normalize_source, validate_phone

def test_normalize_name():
    assert normalize_name("  john doe  ") == "John Doe"
    assert normalize_name("JANE  SMITH") == "Jane Smith"
    assert normalize_name("alice") == "Alice"
    assert normalize_name("  ") == ""

def test_normalize_source():
    assert normalize_source("fb") == "Facebook"
    assert normalize_source("  insta  ") == "Instagram"
    assert normalize_source("google") == "Google"
    assert normalize_source("unknown source") == "Unknown Source"
    assert normalize_source(" ") == "Unknown"

def test_validate_phone():
    assert validate_phone("555-1234") == True
    assert validate_phone("+1 (555) 123-4567") == True
    assert validate_phone("555 1234") == True
    assert validate_phone("1234567890") == True
    assert validate_phone("  ") == False
    assert validate_phone("555-ABCD") == False
    assert validate_phone("phone123") == False
