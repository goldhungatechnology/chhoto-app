_BASE62CHARACTERS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

char_to_value = {ch: i for i, ch in enumerate(_BASE62CHARACTERS)}
value_to_char = dict(enumerate(_BASE62CHARACTERS))


def __getattr__(name):
    if name.startswith("_"):
        raise AttributeError(f"{name} doesn't exist.")


__all__ = ["char_to_value", "value_to_char"]
