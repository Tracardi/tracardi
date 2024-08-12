import asyncio

from tracardi.context import ServerContext, Context
from tracardi.service.storage.mysql.service.system_entity_property_to_column_mapping_service import \
    SystemEntityPropertyToColumnMapping


async def main():
    with ServerContext(Context(production=False)):
        serv = SystemEntityPropertyToColumnMapping()
        await serv.load_by_type("profile")


asyncio.run(main())
