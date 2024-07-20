import logging

import asyncio

from huey import RedisHuey

from tracardi.exceptions.log_handler import get_installation_logger
from tracardi.service.storage.redis.driver.redis_connection_pool import get_redis_connection_pool

import tracardi.worker.service.worker.migration_workers as migration_workers

from tracardi.context import Context, ServerContext
from tracardi.config import redis_config
from tracardi.worker.service.async_job import run_async_task
from tracardi.worker.service.worker.elastic_worker import ElasticImporter, ElasticCredentials
from tracardi.worker.service.worker.mysql_worker import MysqlConnectionConfig, MySQLImporter
from tracardi.worker.service.worker.mysql_query_worker import MysqlConnectionConfig as MysqlQueryConnConfig, MySQLQueryImporter
from tracardi.worker.service.import_dispatcher import ImportDispatcher
from tracardi.worker.domain.import_config import ImportConfig
from tracardi.worker.domain.migration_schema import MigrationSchema
from tracardi.worker.misc.task_progress import task_create, task_progress, task_finish

queue = RedisHuey('upgrade',
                  connection_pool=get_redis_connection_pool(redis_config),
                  results=False
                  )

logger = get_installation_logger(__name__, level=logging.INFO)

@run_async_task
async def import_mysql_table_data(task_name:str, import_config: dict, credentials, context: Context):
    with ServerContext(context):
        import_config = ImportConfig(**import_config)

        task_id = await task_create(
            "import",
            task_name if task_name else import_config.name,
            import_config.model_dump(mode='json')
        )

        webhook_url = f"/collect/{import_config.event_type}/{import_config.event_source.id}"

        importer = ImportDispatcher(MysqlConnectionConfig(**credentials),
                                    importer=MySQLImporter(**import_config.config),
                                    webhook_url=webhook_url)

        for progress, batch in importer.run(import_config.api_url):
            await task_progress(task_id, progress)

        await task_finish(task_id)


@run_async_task
async def import_elastic_data(task_name:str, import_config, credentials, context: Context):
    with ServerContext(context):
        import_config = ImportConfig(**import_config)

        task_id = await task_create(
            "import",
            task_name if task_name else import_config.name,
            import_config.model_dump(mode='json')
        )

        webhook_url = f"/collect/{import_config.event_type}/{import_config.event_source.id}"

        importer = ImportDispatcher(ElasticCredentials(**credentials),
                                    importer=ElasticImporter(**import_config.config),
                                    webhook_url=webhook_url)

        for progress, batch in importer.run(import_config.api_url):
            await task_progress(task_id, progress)

        await task_finish(task_id)

@run_async_task
async def import_mysql_data_with_query(task_name:str, import_config, credentials, context: Context):
    import_config = ImportConfig(**import_config)

    task_id = await task_create(
        "import",
        task_name if task_name else import_config.name,
        import_config.model_dump(mode='json')
    )

    webhook_url = f"/collect/{import_config.event_type}/{import_config.event_source.id}"

    importer = ImportDispatcher(
        MysqlQueryConnConfig(**credentials),
        importer=MySQLQueryImporter(**import_config.config),
        webhook_url=webhook_url
    )

    for progress, batch in importer.run(import_config.api_url):
        await task_progress(task_id, progress)

    await task_finish(task_id)

async def _run_migration_worker(worker_func, schema, elastic_host, context: Context):
    worker_function = getattr(migration_workers, worker_func, None)

    if worker_function is None:
        logger.log(level=logging.ERROR, msg=f"No migration worker defined for name {schema.worker}. "
                                            f"Skipping migration with name {schema.name}")
        return

    # Runs all workers defined in worker.service.worker.migration_workers.__init__
    # All have defined interface of:
    #   * schema: MigrationSchema,
    #   * elastic_url: str, task_index: str
    #   * context

    await worker_function(MigrationSchema(**schema), elastic_host, context)

async def migrate_data(schemas, elastic_host, context: Context):
    logger.info(f"Migration starts for elastic: {elastic_host}")

    schemas = [MigrationSchema(**schema) for schema in schemas]
    total = len(schemas)
    progress = 0

    for schema in schemas:
        logger.info(f"Scheduled migration of {schema.copy_index.from_index} to {schema.copy_index.to_index}")

    # Adds task to database

    task_id = await task_create("upgrade", "Migration plan orchestrator")

    tasks = []
    for schema in schemas:

        coro = _run_migration_worker(schema.worker, schema.model_dump(), elastic_host, context)

        try:
            if schema.asynchronous is True:
                tasks.append(asyncio.create_task(coro))
            else:
                await coro
        except Exception as e:
            logger.error(f"Task failed {str(e)}")

        progress += 1
        await task_progress(task_id, int(progress / total))

    await asyncio.gather(*tasks)

    await task_finish(task_id)

@run_async_task
async def _run_migration_job(schemas, elastic_host, context: Context):
    with ServerContext(context):
        return await migrate_data(schemas, elastic_host, context)


@queue.task(retries=1)
def run_mysql_import_job(task_name: str, import_config, credentials, context: Context):
    import_mysql_table_data(task_name, import_config, credentials, context)


@queue.task(retries=1)
def run_elastic_import_job(task_name: str, import_config, credentials, context: Context):
    import_elastic_data(task_name, import_config, credentials, context)


@queue.task(retries=1)
def run_mysql_query_import_job(import_config, credentials):
    import_mysql_data_with_query(import_config, credentials)

"""
This is start job
"""
@queue.task(retries=1)
def run_migration_job(schemas, elastic_host, context: dict):
    context = Context.from_dict(context)
    _run_migration_job(schemas, elastic_host, context)
    logger.info("Migration finished")

