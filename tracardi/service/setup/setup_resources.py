def get_resource_types():
    return {
        "web-page": {
            "config": {
                "user": "<user>",
                "password": "<password>"
            },
            "tags": ['web-page', "input", "output"],
            "name": "Web page",
            "icon": "web"
        },
        "api": {
            "config": {
                "url": "<url>",
                "username": "<username>",
                "password": "<password>"
            },
            "tags": ['api', "destination"],
            "name": "API endpoint",
            "icon": "cloud",
            "destination": {
                "package": "tracardi.process_engine.destination.http_connector.HttpConnector",
                "init": {
                    "method": "post",
                    "timeout": 30,
                    "headers": {
                        "content-type": "application/json"
                    },
                    "cookies": {},
                    "ssl_check": True
                },
                "form": {}
            }
        },
        "smtp-server": {
            "config": {
                "smtp": "<smpt-server-host>",
                "port": "<port>",
                "username": "<username>",
                "password": "<password>"
            },
            "tags": ['mail', 'smtp'],
            "name": "SMTP"
        },
        "ip-geo-locator": {
            "config": {
                "host": "geolite.info",
                "license": "<license-key>",
                "accountId": "<accound-id>"
            },
            "tags": ['api', 'geo-locator'],
            "name": "MaxMind Geo-Location"
        },
        "postgresql": {
            "config": {
                "host": "<url>",
                "port": 5432,
                "user": "<username>",
                "password": "<password>",
                "database": "<database>"
            },
            "tags": ['database', 'postgresql'],
            "name": "PostgreSQL"
        },
        "elastic-search": {
            "config": {
                "url": "<url>",
                "port": 9200,
                "scheme": "http",
                "username": "<username>",
                "password": "<password>",
                "verify_certs": True
            },
            "tags": ['elastic'],
            "name": "Elasticsearch",
            "icon": "elasticsearch"
        },
        "pushover": {
            "config": {
                "token": "<token>",
                "user": "<user>"
            },
            "tags": ['pushover', 'message'],
            "name": "Pushover",
            "icon": "pushover"
        },
        "mysql": {
            "config": {
                "host": "localhost",
                "port": 3306,
                "user": "<username>",
                "password": "<password>",
                "database": "<database>"
            },
            "tags": ['mysql', 'database'],
            "name": "MySQL",
            "icon": "mysql"
        },
        "mqtt": {
            "config": {
                "url": "<url>",
                "port": "<port>"
            },
            "tags": ['mqtt', 'queue'],
            "name": "MQTT"
        },
        "twilio": {
            "config": {
                "token": "<token>"
            },
            "tags": ['token', 'twilio'],
            "name": "Twilio"
        },
        "redis": {
            "config": {
                "url": "<url>",
                "user": "<user>",
                "password": "<password>"
            },
            "tags": ['redis'],
            "name": "Redis",
            "icon": "redis"

        },
        "mongodb": {
            "config": {
                "uri": "mongodb://127.0.0.1:27017/",
                "timeout": 5000
            },
            "tags": ['mongo', 'database', 'nosql'],
            "name": "MongoDB",
            "icon": "mongo"
        },
        "trello": {
            "config": {
                "token": "<trello-api-token>",
                "api_key": "<trello-api-key>"
            },
            "tags": ["trello"],
            "name": "Trello"
        },
        "token": {
            "config": {
                "token": "<token>"
            },
            "tags": ['token'],
            "name": "Token"
        },
        "google-cloud-service-account": {
            "config": {
                "type": "service_account",
                "project_id": "<project-id>",
                "private_key_id": "<private-key-id>",
                "private_key": "<private-key>",
                "client_email": "<client-email>",
                "client_id": "<client-id>",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "<client-x509-cert-url>"
            },
            "tags": ['gcp-service-account'],
            "name": "Google Cloud Service Account"
        },
        "influxdb": {
            "config": {
                "url": "http://localhost:8086",
                "token": "<API-token>"
            },
            "tags": ["influx"],
            "name": "InfluxDB",
            "icon": "influxdb"
        },
        "mixpanel": {
            "config": {
                "token": "<your-project-token>",
                "server_prefix": "US | EU",
                "username": "<service-account-username>",
                "password": "<service-account-password>"
            },
            "tags": ["mixpanel"],
            "name": "MixPanel",
            "icon": "mixpanel"
        },
        "mautic": {
            "config": {
                "public_key": "<client-public-key>",
                "private_key": "<client-private-key>",
                "api_url": "<url-of-mautic-instance>"
            },
            "icon": "mautic",
            "tags": ["mautic", "destination"],
            "name": "Mautic",
            "destination": {
                "package": "tracardi.process_engine.destination.mautic_connector.MauticConnector",
                "init": {
                    "overwrite_with_blank": False
                },
                "form": {}
            },
        },
        "airtable": {
            "config": {
                "api_key": "<your-api-key>"
            },
            "tags": ["airtable"],
            "name": "Airtable",
            "icon": "airtable"
        },
        "matomo": {
            "config": {
                "token": "<your-token>",
                "api_url": "<your-matomo-url>"
            },
            "tags": ["matomo"],
            "name": "Matomo",
            "icon": "matomo"
        },
        "civi_crm": {
            "config": {
                "api_key": "<api-key>",
                "site_key": "<site-key>",
                "api_url": "<api-url>"
            },
            "tags": ["civi_crm"],
            "name": "CiviCRM",
            "icon": "civicrm"
        },
        "active_campaign": {
            "config": {
                "api_key": "<api-key>",
                "api_url": "<api-url>"
            },
            "tags": ["active_campaign"],
            "name": "ActiveCampaign",
            "icon": "plugin"
        },
        "marketing_cloud": {
            "config": {
                "client_id": "<your-client-id>",
                "client_secret": "<your-client-secret>",
                "subdomain": "<your-subdomain>"
            },
            "tags": ["marketing_cloud"],
            "name": "Salesforce Marketing Cloud",
            "icon": "plugin"
        }
    }


def get_destinations():
    resource_types = get_resource_types()
    for resource_type in resource_types.values():
        if 'destination' in resource_type:
            yield resource_type["destination"]['package'], resource_type


def get_type_of_resources():
    resource_types = get_resource_types()
    for key, resource_type in resource_types.items():
        if 'pro' not in resource_type:
            yield key, resource_type
