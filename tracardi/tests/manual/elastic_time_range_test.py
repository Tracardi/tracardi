import asyncio
from pprint import pprint

from tracardi.domain.index import Index
from tracardi.domain.time_range_query import DatetimeRangePayload


async def main():
    a = {
        "minDate": {
            "delta": {
                "entity": "month",
                "value": -3,
            }
        }
    }
    q = DatetimeRangePayload(**a)
    es = Index("session")
    r = await es.histogram(q)
    pprint(r)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()