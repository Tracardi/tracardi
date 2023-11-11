from typing import Optional

from tracardi.domain.bridge import Bridge
from tracardi.service.storage.mysql.engine import AsyncMySqlEngine
from sqlalchemy.future import select
from sqlalchemy import and_

from tracardi.service.storage.mysql.mapping.bridge import map_to_table
from tracardi.service.storage.mysql.table import BridgeTable, local_context_filter
from tracardi.service.storage.mysql.utils.select_result import SelectResult




class BridgeService:

    def __init__(self, database):
        self.client = AsyncMySqlEngine()
        self.engine = self.client.get_engine_for_database(database)

    async def load_all(self) -> SelectResult:
        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                # Use SQLAlchemy core to perform an asynchronous query
                result = await session.execute(select(BridgeTable).where(local_context_filter(BridgeTable)))
                # Fetch all results
                bridges = result.scalars().all()
                return SelectResult(bridges)

    async def insert(self, bridge: Bridge) -> Optional[str]:

        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            async with session.begin():
                # Create an instance of the Bridge class with the given data

                existing_bridge = (await session.execute(
                    select(BridgeTable).where(
                        and_(local_context_filter(BridgeTable), BridgeTable.id == bridge.id)
                ))).scalar()

                if existing_bridge is None:
                    new_bridge = map_to_table(bridge)

                    # Add the new object to the session
                    session.add(new_bridge)

                    # The actual commit happens here
                    await session.commit()

                    # Return the id of the new record
                    return new_bridge.id

                return None
