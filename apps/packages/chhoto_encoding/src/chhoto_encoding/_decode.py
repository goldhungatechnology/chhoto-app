from ._map import char_to_value


def decode(value: str) -> int:
    """
    decode the value into it's original form
    """

    _result: int = 0
    for position, ch in enumerate(value[::-1]):
        val = char_to_value[ch] * 62**position
        _result = _result + val

    return _result
