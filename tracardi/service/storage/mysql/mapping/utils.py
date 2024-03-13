from typing import Union


def split_list(data: Union[str, list]) -> list:
    if not data:
        return []

    if isinstance(data, list):
        return data

    if isinstance(data, str):
        return data.split(',')

    return []