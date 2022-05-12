def get_import_types() -> dict:
    return {
        "mysql": {
            "module": "tracardi.process_engine.import.mysql_importer.MySQLTableImporter",
            "name": "MySQL Table Import"
        }
    }
