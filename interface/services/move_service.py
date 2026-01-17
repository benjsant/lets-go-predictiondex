from .api_client import _get


def get_types():
    return _get("/types/")
