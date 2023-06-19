import asyncio

from tracardi.service.storage.driver.storage.driver import event as event_db


async def get_min_max(search_by=None, time_range=None):

    if search_by is None:
        search_by = []

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
    result = await event_db.query(
        query
    )
    print(result)
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
    search_by = [('type', "tlv-meas-SKWzug2"), ("traits.tlv_id", 8331), ("traits.plc", "a")]
    result = await get_min_max(search_by=search_by, time_range=1)
    print(result)


asyncio.run(main())
