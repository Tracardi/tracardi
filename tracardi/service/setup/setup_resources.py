from tracardi.domain.resource_settings import ResourceSettings, DestinationData
from typing import List


def get_resource_types() -> List[ResourceSettings]:
    return [
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
            id="api",
            name="API endpoint",
            icon="cloud",
            config={
                "url": "<url>",
                "proxy": "<proxy>",
                "username": "<username>",
                "password": "<password>"
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
                "password": "<password>"
            }
        ),
        ResourceSettings(
            id="ip-geo-locator",
            name="MaxMing Geo-Location",
            tags=["api", "geo-locator"],
            config={
                "host": "geolite.info",
                "license": "<license-key>",
                "accountId": "<accound-id>"
            }
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
            tags=["elastic"],
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
                "port": "<port>",
                "username": "<username>",
                "password": "<password>"
            }
        ),
        ResourceSettings(
            id="twilio",
            name="Twilio",
            tags=["token", "twilio"],
            config={
                "token": "<token>"
            }
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
                "url": "<url>",
                "user": "<user>",
                "password": "<password>"
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
            id="novu",
            name="Novu",
            tags=["token", "novu"],
            config={
                "token": "<token>"
            },
            manual="novu_resource"
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
            tags=["influx"],
            icon="influx",
            config={
                "url": "http://localhost:8086",
                "token": "<API-token>"
            }
        ),
        ResourceSettings(
            id="mixpanel",
            name="MixPanel",
            tags=["mixpanel"],
            icon="mixpanel",
            config={
                "token": "<your-project-token>",
                "server_prefix": "US | EU",
                "username": "<service-account-username>",
                "password": "<service-account-password>"
            }
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
            )
        ),
        ResourceSettings(
            id="elastic-email",
            name="ElasticEmail",
            config={
                "api_key": "<api-key>",
                "public_account_id": "<public-account-id>"
            },
            icon="email",
            tags=["elastic-email"],
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
            )
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
            id="marketing_cloud",
            name="Salesforce Marketing Cloud",
            tags=["marketing_cloud"],
            config={
                "client_id": "<your-client-id>",
                "client_secret": "<your-client-secret>",
                "subdomain": "<your-subdomain>"
            }
        ),
        ResourceSettings(
            id="hubspot",
            config={
                "client_id": "<your-client-id>",
                "client_secret": "<your-client-secret>",
                "refresh_token": "<your-refresh-token-optionally>",
                "access_token": "<your-access-token-optionally>",
                "redirect_url": "<your-redirect-url-optionally>",
                "code": "<your-code-optionally-optionally>"
            },
            icon="hubspot",
            tags=["hubspot"],
            name="HubSpot"
        )
    ]


def get_destinations():
    resource_types = get_resource_types()
    for resource_type in resource_types:
        if resource_type.destination is not None:
            yield resource_type.destination.package, resource_type.dict()


def get_type_of_resources():
    resource_types = get_resource_types()
    for resource_type in resource_types:
        if resource_type.pro is None:
            yield resource_type.id, resource_type.dict()
