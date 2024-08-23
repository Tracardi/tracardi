from tracardi.domain.query_result import QueryResult
from tracardi.service.storage.elastic.dal import console_log as console_log_db


async def load_by_event(event_id: str, sort: str = None) -> QueryResult:
    """
    Returns event logs for event with given ID
    """

    if sort in ['asc', 'desc']:
        sort = [{
            "date": sort
        }]

    records, total = await console_log_db.load_by_event(event_id, sort=sort)
    return QueryResult(
        result=records,
        total=total
    )


async def load_by_node(node_id: str, sort: str = None) -> QueryResult:
    """
    Returns node console log.
    """

    if sort in ['asc', 'desc']:
        sort = [{
            "date": sort
        }]

    records, total = await console_log_db.load_by_node(node_id, sort=sort)

    return QueryResult(
        result=records,
        total=total
    )


async def load_by_flow(workflow_id: str, sort: str = None) -> QueryResult:
    """
    Returns flow console log.
    """
    if sort in ['asc', 'desc']:
        sort = [{
            "date": sort
        }]

    records, total = await console_log_db.load_by_flow(workflow_id, sort=sort)

    return QueryResult(
        result=records,
        total=total
    )


async def load_by_profile(profile_id: str, sort: str = None) -> QueryResult:
    """
    Gets logs for profile with given ID (str)
    """

    if sort in ['asc', 'desc']:
        sort = [{
            "date": sort
        }]

    records, total = await console_log_db.load_by_profile(profile_id, sort=sort)
    return QueryResult(
        result=records,
        total=total
    )
