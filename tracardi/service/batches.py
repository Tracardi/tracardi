def get_batches():
    return {
        "mysql": {
            "module": "tracardi.process_engine.batch.mysql.MySQLBatch",
            "name": "MySQL"
        }
    }
