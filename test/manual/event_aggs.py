import asyncio

from tracardi.service.storage.driver.elastic import event as event_db


async def main():
    result = await event_db.aggregate_events_by_type_and_source()

    for x in result.aggregations('by_type').buckets():
        print("x", x, type(x))
        row = {'type': x['key'], 'source': []}
        for bucket in x['by_source']['buckets']:
            row['source'].append({
                "id": bucket['key'],
                "count": bucket['doc_count']
            })
        print(row)


asyncio.run((main()))
