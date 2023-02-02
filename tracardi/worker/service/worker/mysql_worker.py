import json
from datetime import datetime

import mysql.connector
from pydantic import BaseModel

from tracardi.worker.domain.named_entity import NamedEntity


class MysqlConnectionConfig(BaseModel):
    user: str
    password: str = None
    host: str
    port: int = 3306


class MySQLImporter(BaseModel):
    database_name: NamedEntity
    table_name: NamedEntity
    batch: int

    def _default_none_serializable_data(self, value):
        if isinstance(value, datetime):
            return str(value)
        elif isinstance(value, set):
            return list(value)
        else:
            return f"<<non-serializable: {type(value).__qualname__}>>"

    def count(self, cursor):
        sql = f"SELECT COUNT(1) as `count` FROM {self.database_name.id}.{self.table_name.id}"
        cursor.execute(sql)
        return int(cursor.fetchone()['count'])

    def data(self, credentials: MysqlConnectionConfig):
        connection = mysql.connector.connect(
            host=credentials.host,
            user=credentials.user,
            password=credentials.password,
            port=credentials.port
        )
        cursor = connection.cursor(dictionary=True)
        number_of_records = self.count(cursor)
        if number_of_records > 0:
            for batch_number, start in enumerate(range(0, number_of_records, self.batch)):
                sql = f"SELECT * FROM {self.database_name.id}.{self.table_name.id} LIMIT {start}, {self.batch}"
                cursor.execute(sql)
                for record, data in enumerate(cursor):
                    json_payload = json.dumps(data, default=self._default_none_serializable_data)
                    data = json.loads(json_payload)
                    progress = ((start + record + 1) / number_of_records) * 100
                    yield data, progress, batch_number + 1
        cursor.close()
        connection.close()
