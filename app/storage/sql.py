from app import config


def event_sql(min, max, query=""):
    event_index = config.unomi_index['event']
    sql = """SELECT * FROM "{}" WHERE timeStamp BETWEEN '{}' AND '{}'""".format(event_index, min.isoformat(),
                                                                                max.isoformat())

    if query:
        query = query.replace('"', "'")
        sql += " AND {}".format(query)

    query = {
        "query": sql
    }
    print(query)
    return query
