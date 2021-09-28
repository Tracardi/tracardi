from datetime import datetime
from tracardi.config import elastic


def to_time_range_sql_query(index, time, min: datetime, max: datetime, query=""):
    sql = """SELECT * FROM "{}" WHERE {} BETWEEN '{}' AND '{}'""".format(
        index, time, min.isoformat(),
        max.isoformat())

    if query:
        query = query.replace('"', "'")
        sql += " AND {}".format(query)

    query = {
        "query": sql
    }

    return query


def to_sql_query(index: str, fields: str = "*", query: str = None, limit: int = 20):

    if elastic.elastic_opensearch:
        # Open search
        sql = "SELECT {} FROM {}".format(fields, index)
    else:
        # elastic
        sql = "SELECT {} FROM \"{}\"".format(fields, index)

    if query:
        query = query.replace('"', "'")
        sql += " WHERE {}".format(query)

    sql += " LIMIT {}".format(limit)

    query = {
        "query": sql
    }

    return query
