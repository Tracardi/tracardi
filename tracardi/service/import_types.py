def get_import_types():
    return {
        "mysql": {
            "module": "tracardi.process_engine.import.mysql_importer.MySQLImporter",
            "name": "MySQL"
        }
    }
