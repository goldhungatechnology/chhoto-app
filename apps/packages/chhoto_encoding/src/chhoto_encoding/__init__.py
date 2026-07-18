from ._decode import decode
from ._encode import encode

__all__ = ["decode", "encode"]


def __getattr__(name):
    if name in __all__:
        return globals()[name]
    raise AttributeError(f"module {__name__} has no attribute {name}")
