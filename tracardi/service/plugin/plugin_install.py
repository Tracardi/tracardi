import asyncio
import logging
import os
from collections import defaultdict
from typing import Dict

from tracardi.service.setup.setup_plugins import test_plugins, installed_plugins

from tracardi.config import tracardi
from tracardi.domain.settings import Settings
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.module_loader import pip_install, load_callable, import_package
from tracardi.service.plugin.domain.register import Plugin
from tracardi.service.setup.domain.plugin_metadata import PluginMetadata
from tracardi.service.storage.driver import storage
from tracardi.service.storage.index import resources

__local_dir = os.path.dirname(__file__)
logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def install_plugin(module):
    try:

        _module = import_package(module)

        try:
            # loads and installs dependencies
            plugin = load_callable(_module, 'register')
        except AttributeError as e:
            # No register function in module. Check if is is not somewhere else.
            if module in test_plugins:
                plugin_metadata = test_plugins[module]
            elif module in installed_plugins:
                plugin_metadata = installed_plugins[module]
            else:
                raise e

            return await install_plugin(plugin_metadata.plugin_registry)

        plugin_data = plugin()  # type: Plugin

        # If register returns tuple then is has to be Plugin and Settings.
        # Settings define if plugin is hidden from the list, etc.

        settings = None
        if isinstance(plugin_data, tuple):
            if len(plugin_data) != 2:
                raise ValueError("Invalid result of plugin registration. Expected a tuple of Plugin and Settings")
            plugin_data, settings = plugin_data
            if not isinstance(plugin_data, Plugin) and not isinstance(settings, Settings):
                raise ValueError("Invalid result of plugin registration. Expected a tuple of Plugin and Settings")

        if len(plugin_data.spec.inputs) > 1:
            raise ValueError(
                "Node can not have more then 1 input port. Found {} that is {}".format(
                    plugin_data.spec.inputs,
                    len(plugin_data.spec.inputs)
                ))

        # Action plugin id is a hash of its module and className

        await asyncio.sleep(0)
        logger.info(f"Module `{plugin_data.spec.module}` was REGISTERED.")
        return await storage.driver.action.save_plugin(plugin_data, settings)

    except ModuleNotFoundError as e:
        logger.error(f"Module `{module}` was NOT INSTALLED as it raised an error `{str(e)}`.")


async def install_plugins(plugins_list: Dict[str, PluginMetadata]):
    result = defaultdict(list)
    action_index = resources.get_index_constant('action')
    action_index = action_index.get_write_index()
    tries = 0
    while True:

        if tries > 3:
            raise ConnectionError(f"Plugins NOT INSTALLED. Could not find index {action_index}")

        if not await storage.driver.raw.exists_index(action_index):
            tries += 1
            logger.warning(f"No index {action_index}. Waiting to be created.")
            await asyncio.sleep(5)
            continue

        await storage.driver.action.refresh()

        for plugin in plugins_list.keys():
            status = await install_plugin(plugin)
            if status is not None:
                result["registered"].append(plugin)
            else:
                result["error"].append(plugin)

        return result


async def install_remote_plugin(plugin_data: Plugin):
    if len(plugin_data.spec.inputs) > 1:
        raise ValueError(
            "Node can not have more then 1 input port. Found {} that is {}".format(
                plugin_data.spec.inputs,
                len(plugin_data.spec.inputs)
            ))

    logger.info(f"Remote MICROSERVICE module `{plugin_data.spec.module}` was REGISTERED.")
    return await storage.driver.action.save_plugin(plugin_data)


async def install_default_plugins():
    return await install_plugins(installed_plugins)