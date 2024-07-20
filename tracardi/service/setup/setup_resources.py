from tracardi.service.license import License
from tracardi.domain.resource_settings import ResourceSettings, DestinationData
from typing import List

if License.has_license():
    from com_tracardi.resource.resource_types import commercial_resource_types


def get_resource_types() -> List[ResourceSettings]:
    os_resource_types = [
        ResourceSettings(
            id="api-key",
            name="Api Key",
            icon="hash",
            tags=["api", "key", "token", "api_key"],
            config={
                "api_key": ""
            }
        ),
        ResourceSettings(
            id="web-page",
            name="Web page",
            icon="web",
            tags=["web-page", "input", "output"],
            config={
                "user": "<user>",
                "password": "<password>"
            }
        ),
        ResourceSettings(
            id="aws-s3",
            name="AWS S3",
            icon="aws",
            tags=["aws", "s3"],
            config={
                "aws_secret_access_key": "<aws-secret-access-key>",
                "aws_access_key_id": "<aws-access-key-id>",
                "bucket": "<bucket>"
            },
            manual='s3_aws'
        ),
        ResourceSettings(
            id="aws-iam",
            name="AWS IAM",
            icon="aws",
            tags=["aws", "iam"],
            config={
                "aws_secret_access_key": "<aws-secret-access-key>",
                "aws_access_key_id": "<aws-access-key-id>",
            }
        ),
        ResourceSettings(
            id="api",
            name="API endpoint",
            icon="cloud",
            config={
                "url": "<url>",
                "proxy": "<proxy>",
                "username": "<username>",
                "password": "<password>",
                "headers": {}
            },
            tags=['api', "destination"],
            destination=DestinationData(
                package="tracardi.process_engine.destination.http_connector.HttpConnector",
                init={
                    "method": "post",
                    "timeout": 30,
                    "headers": {
                        "content-type": "application/json"
                    },
                    "cookies": {},
                    "ssl_check": True
                }
            )
        ),
        ResourceSettings(
            id="smtp-server",
            name="SMTP",
            tags=["mail", "smtp"],
            config={
                "smtp": "<smpt-server-host>",
                "port": "<port>",
                "username": "<username>",
                "password": "<password>",
                "ssl": False,
                "start_tls": True
            }
        ),
        ResourceSettings(
            id="imap-server",
            name="IMAP",
            tags=["mail", "imap"],
            config={
                "host": "<imap-server-host>",
                "port": "<port>",
                "username": "<username>",
                "password": "<password>",
                "ssl": False,
                "start_tls": True
            }
        ),
        ResourceSettings(
            id="telegram",
            name="Telegram",
            tags=["telegram"],
            config={
                "bot_token": "<bot-token>",
                "chat_id": "<chat-id>"
            },
            manual='telegram_resource'
        ),
        ResourceSettings(
            id="ip-geo-locator",
            name="MaxMind Geo-Location",
            tags=["api", "geo-locator"],
            config={
                "host": "geolite.info",
                "license": "<license-key>",
                "accountId": "<accound-id>"
            },
            manual="max_mind_resource"
        ),
        ResourceSettings(
            id="postgresql",
            name="PostgreSQL",
            tags=["database", "postgresql"],
            config={
                "host": "<url>",
                "port": 5432,
                "user": "<username>",
                "password": "<password>",
                "database": "<database>"
            }
        ),
        ResourceSettings(
            id="elastic-search",
            name="Elasticsearch",
            tags=["elasticsearch", "database"],
            icon="elasticsearch",
            config={
                "url": "<url>",
                "port": 9200,
                "scheme": "http",
                "username": "<username>",
                "password": "<password>",
                "verify_certs": True
            }
        ),
        ResourceSettings(
            id="mysql",
            name="MySQL",
            icon="mysql",
            tags=["mysql", "database"],
            config={
                "host": "localhost",
                "port": 3306,
                "user": "<username>",
                "password": "<password>",
                "database": "<database>"
            }
        ),
        ResourceSettings(
            id="mqtt",
            name="MQTT",
            tags=["mqtt", "queue"],
            config={
                "url": "<url>",
                "port": 1883,
                "username": "<username>",
                "password": "<password>"
            }
        ),
        ResourceSettings(
            id="sms77",
            name="Sms77",
            tags=["api_key", "sms77"],
            config={
                "api_key": "<api_key>"
            }
        ),
        ResourceSettings(
            id="clicksend",
            name="ClickSend",
            tags=["clicksend", "api_key"],
            config={
                "username": "<username>",
                "api_key": "<api_key>"
            },
            manual='clicksend_resource'
        ),
        ResourceSettings(
            id="full-contact",
            name="FullContact",
            tags=["token", "full-contact"],
            config={
                "token": "<token>"
            }
        ),
        ResourceSettings(
            id="sendgrid",
            name="SendGrid",
            tags=["token", "sendgrid"],
            config={
                "token": "<token>"
            },
            manual='sendgrid_resource'
        ),
        ResourceSettings(
            id="redis",
            name="Redis",
            tags=["redis"],
            icon="redis",
            config={
                "url": "<url>:<port>",
                "user": "<user>",
                "password": "<password>",
                "protocol": "redis",
                "database": "0"

            },
            manual="redis_resource"
        ),
        ResourceSettings(
            id="mongodb",
            name="MongoDB",
            tags=["mongo", "database", "nosql"],
            icon="mongo",
            config={
                "uri": "mongodb://127.0.0.1:27017/",
                "timeout": 5000
            }
        ),
        ResourceSettings(
            id="token",
            name="Token",
            tags=["token"],
            config={
                "token": "<token>"
            }
        ),
        ResourceSettings(
            id="twitter",
            name="Twitter",
            tags=["twitter"],
            icon='twitter',
            config={
                "api_key": "<api_key>",
                "api_secret": "<api_secret_key>",
                "access_token": "<access_token>",
                "access_token_secret": "<access_token_secret>"
            },
            manual="twitter_resource"
        ),
        ResourceSettings(
            id="novu",
            name="Novu",
            tags=["token", "novu"],
            config={
                "host": "https://api.novu.co",
                "token": "<token>"
            },
            manual="novu_resource"
        ),
        ResourceSettings(
            id="google_id",
            name="Google Universal Analytics Tracking ID",
            tags=["google"],
            config={
                "google_analytics_id": "<google_analytics_id>"
            },
            manual="ua3_tracker_resource"
        ),

        ResourceSettings(
            id="google_v4_id",
            name="Google Analytics 4",
            tags=["google"],
            config={
                "api_key": "<api_key>",
                "measurement_id": "<measurement_id>"
            },
            icon='google',
            manual="ga4_tracker_resource",
            destination=DestinationData(
                package="com_tracardi.destination.ga4_connector.Ga4Connector",
                init={}
            )
        ),
        ResourceSettings(
            id="google-cloud-service-account",
            name="Google Cloud service account",
            tags=["gcp-service-account"],
            config={
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
            }
        ),
        ResourceSettings(
            id="influxdb",
            name="InfluxDB",
            tags=["influxdb"],
            icon="influxdb",
            config={
                "url": "http://localhost:8086",
                "token": "<token>"
            }
        ),
        ResourceSettings(
            id="mixpanel",
            name="MixPanel",
            tags=["mixpanel"],
            icon="mixpanel",
            config={
                "token": "<your-project-token>",
                "server_prefix": "US | EU"
            },
            manual="mixpanel_resource"
        ),
        ResourceSettings(
            id="mautic",
            name="Mautic",
            icon="mautic",
            tags=["mautic", "destination"],
            config={
                "public_key": "<client-public-key>",
                "private_key": "<client-private-key>",
                "api_url": "<url-of-mautic-instance>"
            },
            destination=DestinationData(
                package="tracardi.process_engine.destination.mautic_connector.MauticConnector",
                init={
                    "overwrite_with_blank": False
                }
            ),
            manual="mautic_resource"
        ),
        ResourceSettings(
            id="elasticemail",
            name="ElasticEmail",
            config={
                "api_key": "<api-key>",
                "public_account_id": "<public-account-id>"
            },
            icon="email",
            tags=["elasticemail"],
            manual="elastic_email_resource"
        ),
        ResourceSettings(
            id="airtable",
            name="AirTable",
            icon="airtable",
            tags=["airtable"],
            config={
                "api_key": "<your-api-key>"
            }
        ),
        ResourceSettings(
            id="amplitude",
            name="Amplitude",
            icon="amplitude",
            tags=["amplitude"],
            config={
                "api_key": "<your-api-key>"
            }
        ),
        ResourceSettings(
            id="matomo",
            name="Matomo",
            tags=["matomo"],
            icon="matomo",
            config={
                "token": "<your-token>",
                "api_url": "<your-matomo-url>"
            },
            manual="matomo_resource"
        ),
        ResourceSettings(
            id="civi_crm",
            name="CiviCRM",
            icon="civicrm",
            tags=["civi_crm"],
            config={
                "api_key": "<api-key>",
                "site_key": "<site-key>",
                "api_url": "<api-url>"
            },
            destination=DestinationData(
                package="tracardi.process_engine.destination.civicrm_connector.CiviCRMConnector"
            ),
            manual="civi_resource"
        ),
        ResourceSettings(
            id="active_campaign",
            name="ActiveCampaign",
            tags=["active_campaign"],
            config={
                "api_key": "<api-key>",
                "api_url": "<api-url>"
            }
        ),
        ResourceSettings(
            id="salesforce",
            name="Salesforce Marketing Cloud",
            tags=["salesforce"],
            config={
                "client_id": "<your-client-id>",
                "client_secret": "<your-client-secret>",
                "subdomain": "<your-subdomain>"
            },
            manual="salesforce_resource"
        ),
        ResourceSettings(
            id="hubspot",
            config={
                "token": "<your-access-token>"
            },
            icon="hubspot",
            tags=["hubspot"],
            name="HubSpot",
            manual="hubspot_resource",
            destination=DestinationData(
                package="tracardi.process_engine.destination.hubspot_connector.HubSpotConnector",
                init={},
                pro=False
            )
        ),
        ResourceSettings(
            id='github',
            config={
                'api_url': 'https://api.github.com/',
                'personal_access_token': '<your-access-token>',
            },
            icon='github',
            tags=['github'],
            name='GitHub',
            manual='github_resource',
        ),
        ResourceSettings(
            id='discord',
            config={
                'url': '<webhook_url>',
            },
            icon='discord',
            tags=['discord'],
            name='Discord',
            manual='discord_resource',
        ),
        ResourceSettings(
            id='apache-pulsar',
            config={
                'host': '<pulsar://localhost:6650>',
                'token': '<token>'
            },
            icon='pulsar',
            tags=['pulsar', 'apache', 'queue'],
            name='Apache Pulsar',
            manual='apache_pulsar_resource',
            destination=DestinationData(
                package="com_tracardi.destination.pulsar_connector.PulsarConnector",
                init={
                    "topic": "<topic>",
                    "serializer": "json"
                },
                pro=True
            )
        ),
        ResourceSettings(
            id="apache-kafka",
            name="Apache Kafka",
            icon='kafka',
            tags=['kafka', 'pro', 'queue', 'destination'],
            config={
                "bootstrap_servers": 'localhost:port',
                "security_protocol": "PLAINTEXT",
                "sasl_mechanism": "PLAIN",
                "sasl_plain_username": None,
                "sasl_plain_password": None,
                "metadata_max_age_ms": 300000,
                "request_timeout_ms": 40000,
                "max_batch_size": 16384,
                "max_request_size": 1048576,
                "ssl_context": False
            },
            destination=DestinationData(
                package="com_tracardi.destination.kafka_connector.KafkaConnector",
                init={
                    "topic": "<topic>",
                    "serializer": "json"
                },
                pro=True
            )
        ),
        ResourceSettings(
            id= "rabbitmq",
            name= "RabbitMq",
            tags=['rabbitmq', 'pro', 'queue', 'destination'],
            config={
                "uri": "amqp://localhost:5672/",
                "port": "5672",
                "timeout": "5",
                "virtual_host": ""
            },
            destination = DestinationData(
                package = "com_tracardi.destination.rabbitmq_connector.RabbitMqConnector",
                init= {
                    "queue": {
                        "name": None,
                        "routing_key": "routing",
                        "queue_type": "direct",
                        "compression": None,
                        "auto_declare": True,
                        "serializer": "json"
                    }
                },
                pro=True
            )
        ),
        ResourceSettings(
            id='ghost',
            config={
                "api_url": "<api-url>",
                "api_key": "<api-key>"
            },
            icon='ghost',
            tags=['ghost'],
            name='Ghost',
            manual='ghost_resource',
            # destination=DestinationData(
            #     package="tracardi.process_engine.destination.ghost_connector.GhostConnector",
            #     init={
            #         "uuid": "<uuid>",
            #         "label_add": "<label-to-add>",
            #         "label_remove": "<label-to-remove>"
            #     }
            # )
        )
    ]

    if License.has_license():
        return commercial_resource_types + os_resource_types

    return os_resource_types


# def get_destinations():
#     resource_types = get_resource_types()
#     for resource_type in resource_types:
#         if resource_type.destination is not None:
#             yield resource_type.destination.package, resource_type.dict()


def get_type_of_resources():
    resource_types = get_resource_types()
    for resource_type in resource_types:
        if resource_type.pro is None:
            yield resource_type.id, resource_type.dict()
