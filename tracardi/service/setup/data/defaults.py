from tracardi.domain.bridge import Bridge

open_rest_source_bridge = Bridge(
    id="778ded05-4ff3-4e08-9a86-72c0195fa95d",
    type="rest",
    name="API REST Bridge",
    description="API /track collector"
)

open_webhook_source_bridge = Bridge(
    id="3d8bb87e-28d1-4a38-b19c-d0c1fbb71e22",
    type="webhook",
    name="API Webhook Bridge",
    description="API Webhook collector"
)

default_db_data = {
    "bridge": [
        open_rest_source_bridge,
        open_webhook_source_bridge
    ]
}
