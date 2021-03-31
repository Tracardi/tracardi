import time

import elasticsearch
from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends

from .. import config
from ..domain.rule import Rule
from ..errors.errors import NullResponseError, RecordNotFound
from ..globals.authentication import get_current_user
from ..globals.context_server import context_server_via_uql
from ..globals.elastic_client import elastic_client
from ..routers.misc import query
from ..storage.actions.rule import upsert_rule

router = APIRouter(
    prefix="/rule",
    # dependencies=[Depends(get_current_user)]
)


@router.get("/{id}")
async def rule_get(id: str,
                   uql=Depends(context_server_via_uql),
                   elastic=Depends(elastic_client)):
    q = f"SELECT RULE WHERE id=\"{id}\""
    time.sleep(1)
    try:
        response_tuple = uql.select(q)
        result = uql.respond(response_tuple)

        if not result or 'list' not in result or not result['list']:
            raise HTTPException(status_code=404, detail="Item not found")

        try:
            elastic_result = elastic.get(config.index['rules'], id)
        except elasticsearch.exceptions.NotFoundError:
            elastic_result = RecordNotFound()
            elastic_result.message = "UQL statement not found."

        result = {
            'unomi': result['list'][0],
        }

        result['unomi']['synchronized'] = True if not isinstance(elastic_result, RecordNotFound) else False

        if not isinstance(elastic_result, RecordNotFound):
            result['doc'] = {
                "condition": elastic_result['_source']['doc']["condition"],
                "actions": elastic_result['_source']['doc']["actions"],
                "uql": elastic_result['_source']['doc']["uql"],
            }
        else:
            result['error'] = elastic_result.message

        return result

    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{id}")
async def rule_delete(id: str,
                      uql=Depends(context_server_via_uql),
                      elastic=Depends(elastic_client)):
    try:
        index = config.index['rules']
        elastic_result = elastic.delete(index, id)
        print(elastic_result)
    except elasticsearch.exceptions.NotFoundError:
        # todo logging
        print("Record {} not found in elastic.".format(id))

    q = f"DELETE RULE \"{id}\""
    response_tuple = uql.delete(q)
    print(response_tuple)
    return uql.respond(response_tuple)


@router.post("/")
async def create_query(rule: Rule, uql=Depends(context_server_via_uql), elastic=Depends(elastic_client)):
    q = f"CREATE RULE \"{rule.name}\" DESCRIBE \"{rule.desc}\" IN SCOPE \"{rule.scope}\" " + \
        f"WHEN {rule.condition} THEN {rule.action}"

    unomi_result = query(q, uql)

    upserted_records, errors = upsert_rule(elastic, q, rule)
    print(upserted_records, errors)

    return unomi_result


@router.post("/query/json")
async def get_unomi_query(request: Request, uql=Depends(context_server_via_uql)):
    q = await request.body()
    q = q.decode('utf-8')
    _, url, method, body, _ = uql.get_unomi_query(q)
    return url, method, body


@router.post("/select")
async def rule_select(request: Request, uql=Depends(context_server_via_uql)):
    try:
        q = await request.body()
        q = q.decode('utf-8')
        if q:
            q = f"SELECT RULE WHERE {q}"
        else:
            q = "SELECT RULE LIMIT 20"
        response_tuple = uql.select(q)
        print(response_tuple)
        result = uql.respond(response_tuple)
        # result = list(filter_rule(result))
        return result['list'] if 'list' in result else []
    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
