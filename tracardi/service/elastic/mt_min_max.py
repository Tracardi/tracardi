import asyncio
from collections import defaultdict
from datetime import timedelta
from tracardi.service.storage.driver.elastic import event as event_db


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

    result = await event_db.query(
        query
    )

    aggregates = result.aggregations("cars").buckets()
    for m in aggregates:
        diff = m['max']['value'] - m['min']['value']
        if unit == "time":
            value = timedelta(seconds=diff)
        elif unit in ["km", "kWh"]:
            value = diff/1000
        else:
            value = diff
        yield {
            "car":  m['key'],
            "metric": metric,
            "values": m['doc_count'],
            "max": m['max']['value'],
            "min": m['min']['value'],
            "diff": m['max']['value'] - m['min']['value'],
            "value": value,
            "unit": unit
        }

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
    train = "SKWzug2"
    report = defaultdict(list)
    async for result in get_min_max(train=train, tlv_id=8331, metric="Motor work time", unit="time"):
        report[result['car']].append(result)
    async for result in get_min_max(train=train, tlv_id=8332, metric="Battery work time", unit="time"):
        report[result['car']].append(result)
    async for result in get_min_max(train=train, tlv_id=8333, metric="Distance", unit="km"):
        report[result['car']].append(result)
    async for result in get_min_max(train=train, tlv_id=8334, metric="Charge power", unit="kWh"):
        report[result['car']].append(result)
    async for result in get_min_max(train=train, tlv_id=8335, metric="Drain power", unit="kWh"):
        report[result['car']].append(result)

    from tabulate import tabulate
    data = []
    for car, stats in report.items():
        for stat in stats:
            data.append([train, f"Car {car}", stat['metric'], stat['values'], stat['value'], stat['unit']])

    print(tabulate(data, headers=['Train', 'Car', 'Metric', 'Readings', 'Value', "Unit"], tablefmt='presto'))

asyncio.run(main())
