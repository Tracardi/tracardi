from tracardi.service.storage.elastic.dal.session import aggregate_session


async def aggregate_session_data(bucket_name, by, filter_query=None, buckets_size=100):
    result = await aggregate_session(bucket_name, by, filter_query, buckets_size)

    if bucket_name not in result.aggregations:
        return []

    return [{"name": id, "value": count} for id, count in result.aggregations[bucket_name][0].items()]
