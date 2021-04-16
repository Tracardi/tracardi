import json
import time

# import requests
from fastapi import APIRouter, Request, HTTPException
from fastapi import Depends
# from ..uql.query.dispatcher import Dispatcher, Host

from ..errors.errors import NullResponseError
from ..globals.authentication import get_current_user
from ..globals.context_server import context_server_via_uql
from ..routers.misc import query

router = APIRouter(
    prefix="/console",
    dependencies=[Depends(get_current_user)]
)


@router.post("/uql2unomi/request")
async def uql_query_request(request: Request, uql=Depends(context_server_via_uql)):
    q = await request.body()
    q = q.decode('utf-8')
    if not q:
        return {}
    try:
        data_type, url, method, body, expected_status = uql.get_unomi_query(q)
        return {
            "type": data_type,
            'url': url,
            'method': method,
            'expectedStatus': expected_status,
            'body': body
        }
    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/uql2unomi/response")
async def uql_query_response(request: Request, uql=Depends(context_server_via_uql)):

    data = await request.json()
    response, expected_status = uql.dispatcher.fetch((
        data['type'], data['url'], data['method'], data['body'], data['expectedStatus']
    ))

    try:
        return {
            "status": response.status_code,
            "expectedStatus": expected_status,
            "body": response.json()
        }
    except json.decoder.JSONDecodeError:
        if data['expectedStatus'] == response.status_code:
            return {
                "status": response.status_code,
                "expectedStatus": response,
                "body": response.content
            }

        return {
            "status": response.status_code,
            "expectedStatus": expected_status,
            "body": {
                "error": response.content
            }
        }



@router.post("/uql")
async def uql_query(request: Request, uql=Depends(context_server_via_uql)):
    q = await request.body()
    q = q.decode('utf-8')
    return query(q, uql)


@router.post("/select")
async def select_query(request: Request, uql=Depends(context_server_via_uql)):
    q = await request.body()
    q = q.decode('utf-8')
    return query(q, uql)
