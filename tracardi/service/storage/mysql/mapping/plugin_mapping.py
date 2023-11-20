from tracardi.context import get_context
from tracardi.domain.flow_action_plugin import FlowActionPlugin
from tracardi.domain.metadata import Metadata as TimeMetadata
from tracardi.domain.settings import Settings
from tracardi.domain.time import Time
from tracardi.service.plugin.domain.register import (
    Plugin,
    MetaData,
    Spec,
    MicroserviceConfig,
    Form,
    RunOnce,
    NodeEvents)
from tracardi.service.storage.mysql.schema.table import PluginTable
from tracardi.service.storage.mysql.utils.serilizer import to_json, from_json


def map_to_table(flow_plugin: FlowActionPlugin) -> PluginTable:
    context = get_context()
    return PluginTable(
        id=flow_plugin.id,
        tenant=context.tenant,
        production=context.production,
        plugin_debug=flow_plugin.plugin.debug,
        plugin_start=flow_plugin.plugin.start,
        plugin_metadata_name=flow_plugin.plugin.metadata.name,
    )


def map_to_spec(table: PluginTable) -> Spec:
    return Spec(
        className=table.plugin_spec_class_name,
        module=table.plugin_spec_module,
        inputs=table.plugin_spec_inputs.split(','),  # List
        outputs=table.plugin_spec_outputs.split(','),  # List
        init=from_json(table.plugin_spec_init, dict),
        microservice=from_json(table.plugin_spec_microservice, MicroserviceConfig),
        skip=table.plugin_spec_skip,
        block_flow=table.plugin_spec_block_flow,
        run_in_background=table.plugin_spec_run_in_background,
        on_error_continue=table.plugin_spec_on_error_continue,
        on_connection_error_repeat=table.plugin_spec_on_connection_error_repeat,
        append_input_payload=table.plugin_spec_append_input_payload,
        join_input_payload=table.plugin_spec_join_input_payload,
        form=from_json(table.plugin_spec_form, Form),
        manual=table.plugin_spec_manual,
        author=table.plugin_spec_author,
        license=table.plugin_spec_license,
        version=table.plugin_spec_version,
        run_once=RunOnce(
            value=table.plugin_spec_run_once_value,
            ttl=table.plugin_spec_run_once_ttl,
            enabled=table.plugin_spec_run_once_enabled,
            type=table.plugin_spec_run_once_type
        ),
        node=NodeEvents(
            on_create=table.plugin_spec_node_on_create,
            on_remove=table.plugin_spec_node_on_remove
        )
    )


def map_to_flow_action_plugin(table: PluginTable) -> FlowActionPlugin:
    return FlowActionPlugin(
        id=table.id,
        metadata=TimeMetadata(
            time=Time(
                insert=table.metadata_time_insert,
                create=table.metadata_time_create,
                update=table.metadata_time_update
            )
        ),
        plugin=Plugin(
            start=table.plugin_start,
            debug=table.plugin_debug,
            spec=map_to_spec(table),
            metadata=MetaData(
                name=table.plugin_metadata_name,
                brand=table.plugin_metadata_brand
            )
        ),
        settings=Settings(
            enabled=table.settings_enabled,
            hidden=table.settings_hidden
        )
    )
