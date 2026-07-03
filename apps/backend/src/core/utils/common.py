from datetime import datetime


def serialize(obj):
    """
    serialize
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj
