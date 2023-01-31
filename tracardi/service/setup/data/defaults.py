from tracardi.domain.bridge import Bridge

open_source_bridge = Bridge(
    id="778ded05-4ff3-4e08-9a86-72c0195fa95d",
    type="rest",
    name="API Bridge Open-source",
    description="Opens and API and collects from it"
)

default_db_data = {
    "bridge": [
        open_source_bridge
    ]
}
