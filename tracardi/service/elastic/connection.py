import asyncio
import logging

import elasticsearch

from tracardi.config import tracardi, elastic
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.driver.elastic import system as system_db
from tracardi.service.storage.driver.elastic import raw as raw_db
from tracardi.service.storage.driver.elastic import bridge as bridge_db

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


def _is_elastic_on_localhost():
    local_hosts = {'127.0.0.1', 'localhost'}
    if isinstance(elastic.host, list):
        return set(elastic.host).intersection(local_hosts)
    return elastic.host in local_hosts


async def is_system_installed(no_of_tries: int = 10, pause: int = 15) -> bool:
    success = False
    while True:
        is_installed, indices = await system_db.is_schema_ok()

        if is_installed:
            success = True
            break

        if no_of_tries < 0:
            break

        logger.warning(f"System version {tracardi.version.version} not installed at {elastic.host}. "
                       f"{no_of_tries} more checks left. Waiting...")
        logger.warning(f"Missing indices {[idx[1] for idx in indices if idx[0] in ['missing_alias', 'missing_index']]}")

        no_of_tries -= 1
        await asyncio.sleep(pause)

    return success


async def wait_for_connection(no_of_tries=10):
    success = False
    while True:
        try:

            if no_of_tries < 0:
                break

            _health = await raw_db.health()
            for key, value in _health.items():
                key = key.replace("_", " ")
                logger.info(f"Elasticsearch {key}: {value}")
            logger.info(f"Elasticsearch query timeout: {elastic.query_timeout}s")
            success = True
            break

        except elasticsearch.exceptions.ConnectionError as e:
            no_of_tries -= 1
            logger.error(
                f"Could not connect to elasticsearch at {elastic.host}. Number of tries left: {no_of_tries}. "
                f"Waiting 5s before retry.")
            if _is_elastic_on_localhost():
                logger.warning("You are trying to connect to 127.0.0.1. If this instance is running inside docker "
                               "then you can not use localhost as elasticsearch is probably outside the container. Use "
                               "external IP that docker can connect to.")
            logger.error(f"Error details: {str(e)}")
            await asyncio.sleep(5)

        # todo check if this is needed when we make a single thread startup.
        except Exception as e:
            await asyncio.sleep(1)
            no_of_tries -= 1
            logger.error(f"Could not save data. Number of tries left: {no_of_tries}. Waiting 1s to retry.")
            logger.error(f"Error details: {repr(e)}")

    if success:
        logger.info(f"Connected to elastic at {elastic.host}")
        return

    logger.error(f"Could not connect to elasticsearch at {elastic.host}")
    exit()


async def wait_for_bridge_install(bridge) -> bool:
    success = False
    no_of_tries = 30
    while True:
        logger.info("Registering bridge")
        if no_of_tries < 0:
            break

        try:
            await bridge_db.install_bridge(bridge)
            success = True
            break
        except Exception as e:
            no_of_tries -= 1
            logger.error(
                f"Could install bridge die to an error {str(e)}. Bridge install postponed. "
                f"Number of tries left: {no_of_tries}. "
                f"Waiting 15s to retry.")
            await asyncio.sleep(15)

    return success
