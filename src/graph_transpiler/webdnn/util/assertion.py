def assert_equal(a, b, message: str = ""):
    if a != b:
        raise AssertionError(f"{message}{'' if message == '' else ': '}{a} != {b}")
