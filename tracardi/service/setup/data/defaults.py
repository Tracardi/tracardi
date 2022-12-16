from uuid import uuid4

from tracardi.domain.bridge import Bridge

default_db_data = {
    "bridge": [
        Bridge(
            id=str(uuid4()),
            type="rest",
            name="API Bridge Open-source",
            description="Opens and API and collects from it"
        )
    ]
}
