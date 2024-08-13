def validate_input_name(s: str) -> bool:
    if s[0] != '"' and not s[0].islower() and not s[0].isdigit():
        return False
    return True