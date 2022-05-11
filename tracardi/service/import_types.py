def get_import_types() -> dict:
    return {
        "mysql": {
            "module": "tracardi.process_engine.import.mysql_importer.MySQLImporter",
            "name": "MySQL"
        }
    }
