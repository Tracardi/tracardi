import elasticsearch
from fastapi import HTTPException


def update_record(elastic, index, id, record):
    try:
        return elastic.update(index, id, record)
    except elasticsearch.exceptions.TransportError as e:
        raise HTTPException(status_code=e.status_code, detail=e.info)
