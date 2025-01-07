import asyncio
import elasticsearch
import json
import os
from elasticsearch import NotFoundError
from typing import Tuple

from tracardi.common.logging.log_handler import get_installation_logger
from tracardi.common.tools.diff import get_changed_values
from tracardi.config import tracardi, elastic
from tracardi.context import ServerContext, get_context
from tracardi.domain.credentials import Credentials
from tracardi.service.adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from tracardi.service.license import License, MULTI_TENANT
from tracardi.service.plugin.plugin_install import install_default_plugins
from tracardi.service.setup.setup_indices import create_schema, run_on_start
from tracardi.service.storage.index import Resource, Index

logger = get_installation_logger(__name__)

if License.has_license() and License.has_service(MULTI_TENANT):
    from com_tracardi.service.multi_tenant_manager import MultiTenantManager


def _is_elastic_on_localhost():
    local_hosts = {'127.0.0.1', 'localhost'}
    if isinstance(elastic.host, list):
        return set(elastic.host).intersection(local_hosts)
    return elastic.host in local_hosts


def get_missing(indices, type) -> list:
    return [idx[1] for idx in indices if idx[0] == type]


async def _install_big_data_schema(credentials: Credentials):
    schema_result = await create_schema(Resource().get_index_mappings(), credentials.update_mapping)

    await run_on_start()

    return {
        "created": schema_result,
        "admin": False
    }


class ElasticInstallAdapter(ElasticAdapter):

    async def get_indices_status(self):

        for key, index in Resource().resources.items():  # type: str, Index

            if index.multi_index:

                # Template
                _template = index.get_prefixed_template_name()

                if not await self.template.exists(_template):
                    yield "missing_template", _template
                else:
                    yield "existing_template", _template

                # Alias

                _alias = index.get_index_alias()
                _template_pattern = index.get_templated_index_pattern()

                if get_context().is_production():
                    has_alias = await self.client.exists_alias(_alias)
                else:
                    has_alias = await self.client.exists_alias(_alias, index=_template_pattern)

                if not has_alias:
                    yield "missing_alias", _alias
                else:
                    yield "existing_alias", _alias

            else:

                # Index
                _index = index.get_write_index()
                if not await self.client.index_exists(_index):
                    yield "missing_index", _index
                else:
                    yield "existing_index", _index

                # Alias
                _alias = index.get_index_alias()

                if get_context().is_production():
                    has_alias = await self.client.exists_alias(_alias)
                else:
                    has_alias = await self.client.exists_alias(_alias, index=_index)

                if not has_alias:
                    yield "missing_alias", _alias
                else:
                    yield "existing_alias", _alias

    async def check_indices_mappings_consistency(self):
        """

        This code is checking the mapping of an Elasticsearch
        index against a system mapping file. It loops through
        a dictionary of resources and for each resource, it
        retrieves the system mapping file and loads it into memory.
        It then compares this system mapping to the mapping of an
        Elasticsearch index that is being written to. If there are
        any differences between the two mappings, it saves these
        differences in a dictionary. And, it returns the result dictionary at the end.

        :return: dict
        """

        result = {}

        for key, index in Resource().resources.items():  # type: str, Index

            system_mapping_file = index.get_mapping()

            with open(system_mapping_file) as file:
                system_mapping = file.read()
                system_mapping = index.prepare_mappings(system_mapping, index)
                if index.multi_index:
                    system_mapping = system_mapping['template']
                del system_mapping['settings']

            try:
                es_mapping = await self.client.get_mapping(index.get_write_index())
                es_mapping = es_mapping[index.get_write_index()]

                diff = get_changed_values(old_dict=es_mapping, new_dict=system_mapping)
                if diff:
                    result[index.get_write_index()] = json.loads(json.dumps(diff, default=str))
            except NotFoundError as e:
                result[index.get_write_index()] = {"Message": str(e)}

        return result

    async def is_big_data_schema_ok(self) -> Tuple[bool, list]:
        # Missing indices in staging
        with ServerContext(get_context().switch_context(production=False)):
            _indices_staging = [item async for item in self.get_indices_status()]

        # Missing indices in production
        with ServerContext(get_context().switch_context(production=True)):
            _indices_production = [item async for item in self.get_indices_status()]

        _indices = _indices_staging + _indices_production

        missing_indices = get_missing(_indices, type='missing_index')
        missing_aliases = get_missing(_indices, type='missing_alias')
        missing_templates = get_missing(_indices, type='missing_template')

        is_schema_ok = not missing_indices and not missing_aliases and not missing_templates

        if not is_schema_ok:
            logger.warning(
                f"Missing schemas: Indices {missing_indices}, Aliases: {missing_aliases}, Templates: {missing_templates}")

        return is_schema_ok, _indices

    async def wait_for_connection(self, no_of_tries=10):
        success = False
        while True:
            try:

                if no_of_tries < 0:
                    break

                _health = await self.client.health()
                for key, value in _health.items():
                    key = key.replace("_", " ")
                    logger.info(f"Elasticsearch {key}: {value}")
                logger.info(f"Elasticsearch query timeout: {elastic.query_timeout}s")
                success = True
                break

            except elasticsearch.exceptions.ConnectionError as e:
                no_of_tries -= 1
                logger.warning(
                    f"Could not connect to elasticsearch at {elastic.host}. Number of tries left: {no_of_tries}. "
                    f"Waiting 5s before retry. Error details: {str(e)}")
                if _is_elastic_on_localhost():
                    logger.warning("You are trying to connect to 127.0.0.1. If this instance is running inside docker "
                                   "then you can not use localhost as elasticsearch is probably outside the container. Use "
                                   "external IP that docker can connect to.")
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
        exit(1)

    async def install_big_data_database(self, credentials: Credentials):
        if tracardi.multi_tenant:
            if not License.has_license():
                raise PermissionError("Installation forbidden. Multi-tenant installation is not "
                                      "allowed in open-source version.")
            if not License.has_service(MULTI_TENANT):
                raise PermissionError("Installation forbidden. Multi-tenant installation is not "
                                      "included in your license.")
            context = get_context()
            mtm = MultiTenantManager()
            logger.info(f"Authorizing `{context.tenant}` for installation at {mtm.auth_endpoint}.")

            if not tracardi.multi_tenant_manager_api_key:
                raise PermissionError(f"Installation stopped no Tenant Management API key set.")

            if not tracardi.multi_tenant_manager_url:
                raise PermissionError(f"Installation stopped not Tenant Management API URL set.")

            try:
                await mtm.authorize(tracardi.multi_tenant_manager_api_key)
                tenant = await mtm.is_tenant_allowed(context.tenant)
            except Exception as e:
                raise PermissionError(
                    f"Installation stopped Tenant Management System returned na error when authorizing "
                    f"tenant {context.tenant}: Details {str(e)}.")

            if not tenant:
                raise PermissionError(f"Installation forbidden. Tenant [{context.tenant}] not allowed.")

            if tenant.install_token and tenant.install_token != credentials.token:
                raise PermissionError("Installation forbidden. Invalid installation token.")

            logger.info(f"Tenant `{context.tenant}` authorized for installation.")

        else:
            if tracardi.installation_token and tracardi.installation_token != credentials.token:
                raise PermissionError("Installation forbidden. Invalid installation token.")

        info = await self.client.health()

        if 'number_of_data_nodes' in info and int(info['number_of_data_nodes']) == 1:
            os.environ['ELASTIC_INDEX_REPLICAS'] = "0"
            elastic.replicas = "0"
            logger.warning("Elasticsearch replicas decreased to 0 due to only one data node in the cluster.")

        if credentials.needs_admin:
            if credentials.empty() or not credentials.username_as_email():
                raise PermissionError("Installation forbidden. Invalid admin account "
                                      "login or password. Login must be a valid email and password "
                                      "can not be empty.")


        logger.info(f"Installing plugins on startup")
        installed_plugins = await install_default_plugins()

        # Install staging
        with ServerContext(get_context().switch_context(production=False)):
            staging_install_result = await _install_big_data_schema(credentials)

        # Install production
        with ServerContext(get_context().switch_context(production=True)):
            production_install_result = await _install_big_data_schema(credentials)

        staging_install_result['plugins'] = installed_plugins
        production_install_result['plugins'] = installed_plugins

        return staging_install_result, production_install_result
