import logging
from celery import Celery
from tracardi.worker.config import redis_config
from tracardi.worker.service.worker.elastic_worker import ElasticImporter, ElasticCredentials
from tracardi.worker.service.worker.mysql_worker import MysqlConnectionConfig, MySQLImporter
from tracardi.worker.service.worker.mysql_query_worker import MysqlConnectionConfig as MysqlQueryConnConfig, MySQLQueryImporter
from tracardi.worker.service.import_dispatcher import ImportDispatcher
from tracardi.worker.domain.import_config import ImportConfig
from tracardi.worker.domain.migration_schema import MigrationSchema
import tracardi.worker.service.worker.migration_workers as migration_workers
from tracardi.worker.misc.update_progress import update_progress
from tracardi.worker.misc.add_task import add_task


celery = Celery(
    __name__,
    broker=redis_config.get_redis_with_password(),
    backend=redis_config.get_redis_with_password()
)

logger = logging.getLogger(__name__)


def import_mysql_table_data(celery_job, import_config, credentials):
    import_config = ImportConfig(**import_config)
    webhook_url = f"/collect/{import_config.event_type}/{import_config.event_source.id}"

    importer = ImportDispatcher(MysqlConnectionConfig(**credentials),
                                importer=MySQLImporter(**import_config.config),
                                webhook_url=webhook_url)

    for progress, batch in importer.run(import_config.api_url):
        update_progress(celery_job, progress)


def import_elastic_data(celery_job, import_config, credentials):
    import_config = ImportConfig(**import_config)
    webhook_url = f"/collect/{import_config.event_type}/{import_config.event_source.id}"

    importer = ImportDispatcher(ElasticCredentials(**credentials),
                                importer=ElasticImporter(**import_config.config),
                                webhook_url=webhook_url)

    for progress, batch in importer.run(import_config.api_url):
        update_progress(celery_job, progress)


def import_mysql_data_with_query(celery_job, import_config, credentials):
    import_config = ImportConfig(**import_config)
    webhook_url = f"/collect/{import_config.event_type}/{import_config.event_source.id}"

    importer = ImportDispatcher(
        MysqlQueryConnConfig(**credentials),
        importer=MySQLQueryImporter(**import_config.config),
        webhook_url=webhook_url
    )

    for progress, batch in importer.run(import_config.api_url):
        update_progress(celery_job, progress)


def migrate_data(celery_job, schemas, elastic_host, task_index):
    logger.info(f"Migration starts for elastic: {elastic_host}")

    schemas = [MigrationSchema(**schema) for schema in schemas]
    total = len(schemas)
    progress = 0

    for schema in schemas:
        logger.info(f"Scheduled migration of {schema.copy_index.from_index} to {schema.copy_index.to_index}")

    update_progress(celery_job, progress, total)

    # Adds task to database
    add_task(elastic_host, task_index, "Migration plan orchestrator", celery_job)

    sync_chain = None
    for schema in schemas:

        if schema.asynchronous is True:
            result = run_migration_worker.delay(schema.worker, schema.dict(), elastic_host, task_index)
            logger.info(f"Running worker {schema.worker} as job {result}")
        else:
            sync_chain = run_migration_worker.s(schema.worker, schema.dict(), elastic_host, task_index) if sync_chain \
                is None else sync_chain | run_migration_worker.s(schema.worker, schema.dict(), elastic_host, task_index)

        progress += 1
        if celery_job:
            celery_job.update_state(state="PROGRESS", meta={"current": progress, "total": total})

    if sync_chain is not None:
        sync_chain.delay()


@celery.task(bind=True)
def run_mysql_import_job(self, import_config, credentials):
    import_mysql_table_data(self, import_config, credentials)


@celery.task(bind=True)
def run_elastic_import_job(self, import_config, credentials):
    import_elastic_data(self, import_config, credentials)


@celery.task(bind=True)
def run_mysql_query_import_job(self, import_config, credentials):
    import_mysql_data_with_query(self, import_config, credentials)


@celery.task(bind=True)
def run_migration_job(self, schemas, elastic_host, task_index):
    return migrate_data(self, schemas, elastic_host, task_index)


@celery.task(bind=True)
def run_migration_worker(self, worker_func, schema, elastic_host, task_index):
    worker_function = getattr(migration_workers, worker_func, None)

    if worker_function is None:
        logger.log(level=logging.ERROR, msg=f"No migration worker defined for name {schema.worker}. "
                                            f"Skipping migration with name {schema.name}")
        return

    # Runs all workers defined in worker.service.worker.migration_workers.__init__
    # All have defined interface of:
    #   * celery_job,
    #   * schema: MigrationSchema,
    #   * elastic_url: str, task_index: str
    #   * elastic_task_index - this is for saving progress
    worker_function(self, MigrationSchema(**schema), elastic_host, task_index)
