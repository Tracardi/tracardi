from fastapi import HTTPException
from ..errors.errors import NullResponseError


def query(q, uql):
    try:
        response_tuple = uql.query(q)
        return uql.respond(response_tuple)
    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
