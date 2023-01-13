import asyncio
from typing import Tuple, List

from tracardi.service.storage.driver import storage


async def get_min_max(search_by: List[Tuple[str, str]] = [], time_range=None):
    query = {
        "size": 0,
        "query": {
            "bool": {
                "must": []
            }
        },
        "aggs": {
            "max": {"max": {"field": "traits.measurement"}},
            "min": {"min": {"field": "traits.measurement"}}
        }
    }

    if time_range:
        query['query']['bool']['must'].append({"range": {
            "metadata.time.insert": {
                "gte": "now-1d",
                "lte": "now"
            }
        }
        })

    for key, value in search_by:
        query['query']['bool']['must'].append(
            {
                "term": {
                    key: {"value": value}
                }
            }
        )
    print(query)
    result = await storage.driver.event.query(
        query
    )

    aggregates = result.aggregations()
    try:
        min = aggregates['min']['value']
    except (ValueError, TypeError):
        min = None
    try:
        max = aggregates['max']['value']
    except (ValueError, TypeError):
        max = None

    return min, max


async def main():
    # event_type = "tlv-meas-SKWzug2"
    # search_by = [('type', event_type)]
    result = await get_min_max(search_by=[], time_range=1)
    print(result)


asyncio.run(main())
