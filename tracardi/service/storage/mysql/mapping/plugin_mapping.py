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
    NodeEvents, Documentation)
from tracardi.service.storage.mysql.mapping.utils import split_list
from tracardi.service.storage.mysql.schema.table import PluginTable
from tracardi.service.storage.mysql.utils.serilizer import to_model, from_model


def map_to_plugin_table(plugin: FlowActionPlugin) -> PluginTable:
    context = get_context()
    return PluginTable(
        id=plugin.id,

        tenant=context.tenant,

        metadata_time_insert=plugin.metadata.time.insert,
        metadata_time_update=plugin.metadata.time.update,
        metadata_time_create=plugin.metadata.time.create,

        plugin_debug=plugin.plugin.debug or False,
        plugin_start=plugin.plugin.start or False,

        plugin_metadata_desc=plugin.plugin.metadata.desc,
        plugin_metadata_brand=plugin.plugin.metadata.brand or 'Tracardi',
        plugin_metadata_group=",".join(plugin.plugin.metadata.group) or "General",
        plugin_metadata_height=plugin.plugin.metadata.height or 100,
        plugin_metadata_width=plugin.plugin.metadata.width or 300,
        plugin_metadata_icon=plugin.plugin.metadata.icon or 'plugin',
        plugin_metadata_keywords=",".join(plugin.plugin.metadata.keywords or ""),
        plugin_metadata_name=plugin.plugin.metadata.name,
        plugin_metadata_type=plugin.plugin.metadata.type or 'flowNode',
        plugin_metadata_tags=",".join(plugin.plugin.metadata.tags or ""),
        plugin_metadata_pro=plugin.plugin.metadata.pro or False,
        plugin_metadata_commercial=plugin.plugin.metadata.commercial or False,
        plugin_metadata_remote=plugin.plugin.metadata.remote or False,
        plugin_metadata_documentation=from_model(plugin.plugin.metadata.documentation),
        plugin_metadata_frontend=plugin.plugin.metadata.frontend or False,
        plugin_metadata_emits_event=plugin.plugin.metadata.emits_event,
        plugin_metadata_purpose=",".join(plugin.plugin.metadata.purpose or ""),

        plugin_spec_id=plugin.plugin.spec.id,
        plugin_spec_class_name=plugin.plugin.spec.className,
        plugin_spec_module=plugin.plugin.spec.module,
        plugin_spec_inputs=','.join(plugin.plugin.spec.inputs or []),
        plugin_spec_outputs=','.join(plugin.plugin.spec.outputs or []),
        plugin_spec_microservice=from_model(plugin.plugin.spec.microservice),
        plugin_spec_init=plugin.plugin.spec.init,
        plugin_spec_skip=plugin.plugin.spec.skip or False,
        plugin_spec_block_flow=plugin.plugin.spec.block_flow or False,
        plugin_spec_run_in_background=plugin.plugin.spec.run_in_background or False,
        plugin_spec_on_error_continue=plugin.plugin.spec.on_error_continue or False,
        plugin_spec_on_connection_error_repeat=plugin.plugin.spec.on_connection_error_repeat or 1,
        plugin_spec_append_input_payload=plugin.plugin.spec.append_input_payload or False,
        plugin_spec_join_input_payload=plugin.plugin.spec.join_input_payload or False,
        plugin_spec_form=from_model(plugin.plugin.spec.form),
        plugin_spec_manual=plugin.plugin.spec.manual,
        plugin_spec_author=plugin.plugin.spec.author,
        plugin_spec_license=plugin.plugin.spec.license or 'MIT',
        plugin_spec_version=plugin.plugin.spec.version or '1.0.0',
        plugin_spec_run_once_value=plugin.plugin.spec.run_once.value or "",
        plugin_spec_run_once_ttl=plugin.plugin.spec.run_once.ttl or 0,
        plugin_spec_run_once_type=plugin.plugin.spec.run_once.type or "value",
        plugin_spec_run_once_enabled=plugin.plugin.spec.run_once.enabled,
        plugin_spec_node_on_remove=plugin.plugin.spec.node.on_remove if plugin.plugin.spec.node else None,
        plugin_spec_node_on_create=plugin.plugin.spec.node.on_create if plugin.plugin.spec.node else None,

        settings_enabled=plugin.settings.enabled if plugin.settings else True,
        settings_hidden=plugin.settings.hidden if plugin.settings else False
    )


def map_to_spec(table: PluginTable) -> Spec:
    return Spec(
        className=table.plugin_spec_class_name,
        module=table.plugin_spec_module,
        inputs=split_list(table.plugin_spec_inputs),  # List
        outputs=split_list(table.plugin_spec_outputs),  # List
        init=table.plugin_spec_init,
        microservice=to_model(table.plugin_spec_microservice, MicroserviceConfig),
        skip=table.plugin_spec_skip,
        block_flow=table.plugin_spec_block_flow,
        run_in_background=table.plugin_spec_run_in_background,
        on_error_continue=table.plugin_spec_on_error_continue,
        on_connection_error_repeat=table.plugin_spec_on_connection_error_repeat,
        append_input_payload=table.plugin_spec_append_input_payload,
        join_input_payload=table.plugin_spec_join_input_payload,
        form=to_model(table.plugin_spec_form, Form),
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


def map_to_plugin_metadata(table: PluginTable) -> MetaData:
    docs = to_model(table.plugin_metadata_documentation, Documentation)

    return MetaData(
        name=table.plugin_metadata_name,
        desc=table.plugin_metadata_desc,
        brand=table.plugin_metadata_brand,
        keywords=split_list(table.plugin_metadata_keywords),
        type=table.plugin_metadata_type,
        width=table.plugin_metadata_width,
        height=table.plugin_metadata_height,
        icon=table.plugin_metadata_icon,
        documentation=docs,
        group=split_list(table.plugin_metadata_group),
        tags=split_list(table.plugin_metadata_tags),
        pro=table.plugin_metadata_pro,
        commercial=table.plugin_metadata_commercial or False,
        remote=table.plugin_metadata_remote or False,
        frontend=table.plugin_metadata_frontend or False,
        emits_event=table.plugin_metadata_emits_event,
        purpose=split_list(table.plugin_metadata_purpose)
    )


def map_to_plugin(table: PluginTable) -> Plugin:
    return Plugin(
        start=table.plugin_start,
        debug=table.plugin_debug,
        spec=map_to_spec(table),
        metadata=map_to_plugin_metadata(table),
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
        plugin=map_to_plugin(table),
        settings=Settings(
            enabled=table.settings_enabled,
            hidden=table.settings_hidden
        )
    )
