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
            "tags": ['api'],
            "name": "API endpoint"
        },
        "rabbitMQ": {
            "config": {
                "uri": "amqp://127.0.0.1:5672//",
                "timeout": 5,
                "virtual_host": None,
                "port": 5672
            },
            "tags": ['rabbitmq', 'queue'],
            "name": "RabbitMQ",
            "icon": "rabbitmq",
            "package": "tracardi.process_engine.destination.rabbitmq_connector.RabbitMqConnector"
        },
        "aws": {
            "config": {
                "aws_access_key_id": "<key-id>",
                "aws_secret_access_key": "<access-key>",
            },
            "tags": ['aws', 'cloud', 'token'],
            "name": "AWS IAM Credentials",
            "icon": "aws"
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
            "name": "Elasticsearch"
        },
        "pushover": {
            "config": {
                "token": "<token>",
                "user": "<user>"
            },
            "tags": ['pushover', 'message'],
            "name": "Pushover"
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
            "name": "MySQL"

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
            "name": "Redis"

        },
        "mongodb": {
            "config": {
                "uri": "mongodb://127.0.0.1:27017/",
                "timeout": 5000
            },
            "tags": ['mongo', 'database', 'nosql'],
            "name": "MongoDB"
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
            "name": "InfluxDB"
        },
        "mixpanel": {
            "config": {
                "token": "<your-project-token>",
                "server_prefix": "US | EU",
                "username": "<service-account-username>",
                "password": "<service-account-password>"
            },
            "tags": ["mixpanel"],
            "name": "MixPanel"
        },
        "scheduler": {
            "config": {
                "host": "<tracardi-pro-host>",
                "callback_host": "<callback-host>",
                "token": "<token>"
            },
            "tags": ["pro", "scheduler"],
            "name": "Scheduler"
        },
        "mautic": {
            "config": {
                "public_key": "<client-public-key>",
                "private_key": "<client-private-key>",
                "api_url": "<url-of-mautic-instance>"
            },
            "tags": ["mautic"],
            "name": "Mautic"
        }
    }


def get_destinations():
    resource_types = get_resource_types()
    for _, resource_type in resource_types.items():
        if 'package' in resource_type:
            yield resource_type['package'], resource_type
