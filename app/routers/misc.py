from fastapi import HTTPException
from ..errors.errors import NullResponseError, convert_exception_to_json


def query(q, uql):
    try:
        response_tuple = uql.query(q)
        return uql.respond(response_tuple)
    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=convert_exception_to_json(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=convert_exception_to_json(e))
