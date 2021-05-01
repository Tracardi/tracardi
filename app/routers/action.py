from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends

from ..errors.errors import NullResponseError, convert_exception_to_json
from ..globals.authentication import get_current_user
from ..globals.elastic_client import elastic_client
from ..uql.query.mappers.action_mapper import action_mapper

router = APIRouter(
    prefix="/action",
    dependencies=[Depends(get_current_user)]
)


def __search_actions(query):
    for function_name, data in action_mapper.items():

        if not query:
            yield {
                "function": function_name,
                "metadata": data['metadata']
            }
        else:
            query = query.lower()
            if ('description' in data['metadata'] and query in data['metadata']['description'].lower()) or \
                    (query in function_name.lower()):
                if 'enabled' in data['metadata'] and data['metadata']['enabled']:
                    yield {
                        "function": function_name,
                        "metadata": data['metadata']
                    }


@router.get("/search")
async def event_data(query: str = None):
    try:
        return list(__search_actions(query))
    except Exception as e:
        raise HTTPException(status_code=500, detail=convert_exception_to_json(e))
