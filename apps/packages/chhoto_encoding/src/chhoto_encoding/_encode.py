from ._map import value_to_char


def encode(value: int) -> str:
    """
    encode the value into random string
    """
    if not isinstance(value, int):
        raise ValueError(f"{value} type must be int")

    _result: list[str] = []
    while value > 0:
        remainder = value % 62
        value = value // 62

        _result.append(value_to_char[remainder])

    return "".join(_result)[::-1]
