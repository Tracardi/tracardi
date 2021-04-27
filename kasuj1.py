from es.elastic.api import connect

conn = connect(host='localhost')
curs = conn.cursor()

sql = """
            SELECT * FROM "context-event-date-*" 
            WHERE timeStamp BETWEEN '2021-03-10T00:00:00.000Z' AND '2021-04-10T00:00:00.000Z' 
            AND (scope='kuptoo' or scope<='kuptoo1')
            """
rows = curs.execute(
    sql
)
print(list(rows.get_valid_view_names()))
print(dir(rows))
print(rows.fetchone())
# print([row for row in rows])
