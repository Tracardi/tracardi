def get_batches():
    return {
        "mysql": {
            "module": "tracardi.process_engine.import.mysql_importer.MySQLImporter",
            "name": "MySQL"
        }
    }
