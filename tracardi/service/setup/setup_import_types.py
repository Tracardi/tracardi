def get_import_types() -> dict:
    return {
        "mysql-table-importer": {
            "module": "tracardi.process_engine.import.mysql_importer.MySQLTableImporter",
            "name": "MySQL Table Import"
        },
        "elastic-index-importer": {
            "module": "tracardi.process_engine.import.elastic_importer.ElasticIndexImporter",
            "name": "Elastic Index Import"
        },
        "mysql-query-importer": {
            "module": "tracardi.process_engine.import.mysql_query_importer.MySQLQueryImporter",
            "name": "MySQL Query Import"
        }
    }
