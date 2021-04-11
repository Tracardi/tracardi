import json
from datetime import datetime
from time import sleep

import requests
from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends

from .. import config
from ..errors.errors import NullResponseError
from ..filters.datagrid import filter_event
from ..globals.authentication import get_current_user
from ..globals.context_server import context_server_via_uql
from ..globals.elastic_client import elastic_client
from ..storage.sql import event_sql

router = APIRouter(
    prefix="/event",
    # dependencies=[Depends(get_current_user)]
)


@router.get("/chart/data")
async def event_data(min: datetime, max: datetime, offset: int = 0, limit: int = 20,
                     elastic=Depends(elastic_client), query: str = ""):
    query = event_sql(min, max, query)
    translated_query = elastic.sql.translate(query)

    query = {
        "from": offset,
        "size": limit,
        "query": translated_query['query'],
        "sort": [
            {
                "timeStamp": "asc"
            }
        ]
    }

    print(query)

    event_index = config.unomi_index['event']
    result = elastic.search(event_index, query)

    return {
        'total': result['hits']['total']['value'],
        'data': [row['_source'] for row in result['hits']['hits']]
    }


@router.get("/chart/histogram")
async def event_histogram(min: datetime, max: datetime, elastic=Depends(elastic_client), query: str = ""):
    def __interval(min: datetime, max: datetime):

        max_interval = 50
        min_interval = 20

        span = max - min

        if span.days > max_interval:
            # up
            return int(span.days / max_interval), 'd', "%y-%m-%d"
        elif min_interval > span.days:
            # down
            interval = int((span.days * 24) / max_interval)
            if interval > 0:
                return interval, 'h', "%H:%M"

            # minutes
            interval = int((span.days * 24 * 60) / max_interval)
            if interval > 0:
                return interval, 'm', "%H:%M"

            return 10, 'm', "%H:%M"

        return 1, 'd', "%y-%m-%d"

    def __format(data, unit, interval, format):
        for row in data:
            timestamp = datetime.fromisoformat(row["key_as_string"].replace('Z', '+00:00'))
            yield {
                "time": "{}".format(timestamp.strftime(format)),
                'interval': "+{}{}".format(interval, unit),
                "events": row["doc_count"]
            }

    try:
        interval, unit, format = __interval(min, max)

        query = event_sql(min, max, query)
        translated_query = elastic.sql.translate(query)

        event_index = config.unomi_index['event']
        query = {
            "size": 0,
            "query": translated_query['query'],
            "aggs": {
                "events_over_time": {
                    "date_histogram": {
                        "min_doc_count": 0,
                        "field": "timeStamp",
                        "fixed_interval": f"{interval}{unit}",
                        "extended_bounds": {
                            "min": min,
                            "max": max
                        }
                    }
                }
            }
        }

        print(query)

        result = elastic.search(event_index, query)

        return {
            'total': result['hits']['total']['value'],
            'data': list(__format(result['aggregations']['events_over_time']['buckets'], unit, interval, format))
        }
    except Exception:
        return {
            "total": 0,
            "data": [
                {"time": 0,
                 "interval": 0,
                 "events": 0},
                {"time": 0,
                 "interval": 0,
                 "events": 0},
                {"time": 0,
                 "interval": 0,
                 "events": 0}
            ]
        }


@router.get("/{id}")
async def event_get(id: str, uql=Depends(context_server_via_uql)):
    q = f"SELECT EVENT WHERE id=\"{id}\""

    try:
        response_tuple = uql.select(q)
        result = uql.respond(response_tuple)
        return result["list"][0]
    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/select")
async def event_select(request: Request, uql=Depends(context_server_via_uql)):
    try:
        q = await request.body()
        q = q.decode('utf-8')
        if q:
            q = f"SELECT EVENT WHERE {q} SORT BY timeStamp DESC"
        else:
            q = "SELECT EVENT SORT BY timestamp DESC LIMIT 20"

        response_tuple = uql.select(q)
        result = uql.respond(response_tuple)
        result = list(filter_event(result))
        return result
    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
