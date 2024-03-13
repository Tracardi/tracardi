from asyncio import sleep

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from tracardi.config import mysql
from tracardi.exceptions.log_handler import get_logger

from sqlalchemy.sql import text

logger = get_logger(__name__)


async def wait_for_mysql_connection():
    engine = create_async_engine(mysql.mysql_database_uri, echo=False)
    async_session = sessionmaker(engine,
                                 class_=AsyncSession,
                                 expire_on_commit=False)

    try:
        retries = 0
        while True:
            retries += 1

            if retries == 5:
                logger.error(f"Mysql not available. Exiting...")
                exit(1)

            try:
                async with async_session() as session:
                    # Perform the query asynchronously
                    result = await session.execute(text("SELECT VERSION();"))
                    # Fetch the result
                    result = result.fetchone()
                    logger.info(f"Connected to Mysql {result}")
                    return result
            except SQLAlchemyError as e:
                logger.warning(f"Waiting for Mysql connection. Try: {retries} {str(e)}")
                await sleep(5)
    finally:
        await engine.dispose()