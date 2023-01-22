import asyncio
from typing import Tuple, List

from tracardi.service.storage.driver import storage


async def get_min_max(train, tlv_id, plc="a", metric="Metric", unit=None):
    query = {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "traits.train.keyword": {
                                "value": train
                            }
                        }
                    },
                    {
                        "term": {
                            "type": {
                                "value": "tlv-meas-SKWzug2"
                            }
                        }
                    },
                    {
                        "term": {
                            "traits.tlv_id": {
                                "value": tlv_id
                            }
                        }
                    },
                    {
                        "term": {
                            "traits.plc": {
                                "value": "a"
                            }
                        }
                    },
                    {
                        "range": {
                            "traits.measurement": {
                                "gt": 1,
                            }
                        }
                    }

                ]
            }
        },
        "aggs": {
            "cars": {
                "terms": {
                    "field": "traits.car",
                },
                "aggs": {
                    "max": {"max": {"field": "traits.measurement"}},
                    "min": {"min": {"field": "traits.measurement"}}
                }
            }
        }
    }

    query['query']['bool']['must'].append({"range": {
            "metadata.time.insert": {
                "gte": "now-1d",
                "lte": "now"
            }
        }
    })


    result = await storage.driver.event.query(
        query
    )

    aggregates = result.aggregations("cars").buckets()
    for m in aggregates:
        print()
        print("Car:", m['key'])
        print("No of measurments:", m['doc_count'])
        print(metric, m['max']['value'] - m['min']['value'], unit)

    # try:
    #     min = aggregates['min']['value']
    # except (ValueError, TypeError):
    #     min = None
    # try:
    #     max = aggregates['max']['value']
    # except (ValueError, TypeError):
    #     max = None
    #
    # return min, max


async def main():
    result = await get_min_max(train="SKWzug2", tlv_id=8333, metric="Distance", unit="m")


asyncio.run(main())
