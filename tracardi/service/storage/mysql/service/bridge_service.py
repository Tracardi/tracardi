import logging

from typing import Optional, List

from tracardi.config import tracardi, mysql
from tracardi.domain.bridge import Bridge
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.engine import AsyncMySqlEngine
from sqlalchemy.future import select
from sqlalchemy import and_, delete, text

from tracardi.service.storage.mysql.schema.table import Base
from tracardi.service.storage.mysql.mapping.bridge_mapping import map_to_table
from tracardi.service.storage.mysql.schema.table import BridgeTable, local_context_filter, local_context_entity
from tracardi.service.storage.mysql.utils.select_result import SelectResult


logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)

class BridgeService:

    def __init__(self):
        self.client = AsyncMySqlEngine()
        self.engine = self.client.get_engine_for_database()

    async def _create_tables(self, async_engine):
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # Async function to create a database
    async def _create_database(self, async_engine):
        async with async_engine.connect() as conn:
            await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {mysql.mysql_database}"))
            await conn.commit()

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

    async def load_by_id(self, bridge_id: str) -> SelectResult:
        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                # Use SQLAlchemy core to perform an asynchronous query
                result = await session.execute(select(BridgeTable).where(local_context_entity(BridgeTable, bridge_id)))
                # Fetch all results
                return SelectResult(result.scalars().one_or_none())

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

    async def delete(self, bridge_id: str) -> str:

        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            async with session.begin():
                # Create an instance of the Bridge class with the given data

                await session.execute(
                    delete(BridgeTable).where(
                        and_(local_context_filter(BridgeTable), BridgeTable.id == bridge_id)
                ))

                return bridge_id

    async def bootstrap(self, default_bridges: List[Bridge]):

        # # Create an async engine instance
        async_engine = self.client.get_engine()

        # Connect to the database
        await self._create_database(async_engine)

        # Dispose the engine to avoid any connection issues
        await async_engine.dispose()

        # Create a new async engine instance with the database selected
        await self._create_tables(self.engine)

        bs = BridgeService()
        for bridge in default_bridges:
            await bs.insert(bridge)
            logger.info(f"Bridge {bridge.name} installed.")

