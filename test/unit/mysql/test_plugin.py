from datetime import datetime

from tracardi.context import ServerContext, Context
from tracardi.domain.flow_action_plugin import FlowActionPlugin
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.resource import ResourceCredentials
from tracardi.service.plugin.domain.register import Spec, Form, FormGroup, FormField, FormComponent, MetaData, \
    Documentation, PortDoc, Plugin, MicroserviceConfig, MicroserviceServer, MicroservicePlugin
from tracardi.service.storage.mysql.mapping.plugin_mapping import map_to_plugin_table, map_to_flow_action_plugin
from tracardi.service.storage.mysql.schema.table import PluginTable
from tracardi.service.storage.mysql.utils.serilizer import from_model


def test_to_plugin_mapping():
    config = MicroserviceConfig(
        server=MicroserviceServer(
            resource=NamedEntity(id="plugin1", name="Plugin 1"),
            credentials=ResourceCredentials(
                production={"a": 1},
                test={"a": 2}
            )
        ),
        service=NamedEntity(id="service1", name="Service 1"),
        plugin=MicroservicePlugin(
            id="plugin1", name="Plugin 1"
        )
    )

    form = Form(groups=[
        FormGroup(
            fields=[
                FormField(
                    id="field",
                    name="Path to field",
                    description="Provide path to field that should be decremented. "
                                "E.g. profile@aux.counters.boughtProducts",
                    component=FormComponent(type="dotPath", props={"label": "Field path",
                                                                   "defaultSourceValue": "profile"})
                )
            ]
        ),
        FormGroup(
            fields=[
                FormField(
                    id="decrement",
                    name="Decrementation",
                    description="Provide by what number the value at provided path should be "
                                "decremented. Default value equals 1.",
                    component=FormComponent(
                        type="text",
                        props={
                            "label": "Decrementation"
                        })
                )
            ]
        ),
    ])

    plugin_table = PluginTable(
        id="123",

        metadata_time_insert=datetime.utcnow(),
        metadata_time_create=datetime.utcnow(),
        metadata_time_update=datetime.utcnow(),

        plugin_start=True,
        plugin_debug=False,

        plugin_spec_class_name="MyPlugin",
        plugin_spec_module="my_module",
        plugin_spec_inputs='input1,input2',
        plugin_spec_outputs='output1,output2',
        plugin_spec_microservice=from_model(config),
        plugin_spec_init={"param1": "value1", "param2": "value2"},
        plugin_spec_skip=False,
        plugin_spec_block_flow=False,
        plugin_spec_run_in_background=True,
        plugin_spec_on_error_continue=True,
        plugin_spec_on_connection_error_repeat=3,
        plugin_spec_append_input_payload=True,
        plugin_spec_join_input_payload=False,
        plugin_spec_form=from_model(form),
        plugin_spec_manual="This is the manual",
        plugin_spec_author="John Doe",
        plugin_spec_license="MIT",
        plugin_spec_version="x.0.0",
        plugin_spec_run_once_value="my_value",
        plugin_spec_run_once_ttl=3600,
        plugin_spec_run_once_type="time",
        plugin_spec_run_once_enabled=True,
        plugin_spec_node_on_remove="remove_node",
        plugin_spec_node_on_create="create_node",

        plugin_metadata_desc="desc",
        plugin_metadata_brand="brand",
        plugin_metadata_group="groip1, group2",
        plugin_metadata_height=100,
        plugin_metadata_width=200,
        plugin_metadata_icon="icon",
        plugin_metadata_keywords="key1,key2",
        plugin_metadata_name="MyPluginName",
        plugin_metadata_type="node",
        plugin_metadata_tags='tag1,tag2',
        plugin_metadata_pro=True,
        # plugin_metadata_commercial = True,
        plugin_metadata_documentation="",
        plugin_metadata_purpose='collection',
        settings_enabled=True,
        settings_hidden=False
    )

    flow_action_plugin = map_to_flow_action_plugin(plugin_table)

    assert flow_action_plugin.id == "123"
    assert flow_action_plugin.metadata.time.insert is not None
    assert flow_action_plugin.metadata.time.create is None
    assert flow_action_plugin.metadata.time.update is None
    assert flow_action_plugin.plugin.start is True
    assert flow_action_plugin.plugin.debug is False
    assert flow_action_plugin.plugin.spec.className == "MyPlugin"
    assert flow_action_plugin.plugin.spec.module == "my_module"
    assert flow_action_plugin.plugin.spec.inputs == ["input1", "input2"]
    assert flow_action_plugin.plugin.spec.outputs == ["output1", "output2"]
    assert flow_action_plugin.plugin.spec.microservice == config
    assert flow_action_plugin.plugin.spec.init == {"param1": "value1", "param2": "value2"}
    assert flow_action_plugin.plugin.spec.skip is False
    assert flow_action_plugin.plugin.spec.block_flow is False
    assert flow_action_plugin.plugin.spec.run_in_background is True
    assert flow_action_plugin.plugin.spec.on_error_continue is True
    assert flow_action_plugin.plugin.spec.on_connection_error_repeat == 3
    assert flow_action_plugin.plugin.spec.append_input_payload is True
    assert flow_action_plugin.plugin.spec.join_input_payload is False
    assert flow_action_plugin.plugin.spec.form == form
    assert flow_action_plugin.plugin.spec.manual == "This is the manual"
    assert flow_action_plugin.plugin.spec.author == "John Doe"
    assert flow_action_plugin.plugin.spec.license == "MIT"
    assert flow_action_plugin.plugin.spec.version == "x.0.0"
    assert flow_action_plugin.plugin.start is True
    assert flow_action_plugin.plugin.spec.run_once.value == "my_value"
    assert flow_action_plugin.plugin.spec.run_once.ttl == 3600
    assert flow_action_plugin.plugin.spec.run_once.type == "time"
    assert flow_action_plugin.plugin.spec.run_once.enabled is True
    assert flow_action_plugin.plugin.spec.node.on_remove == "remove_node"
    assert flow_action_plugin.plugin.spec.node.on_create == "create_node"
    assert flow_action_plugin.settings.enabled is True
    assert flow_action_plugin.settings.hidden is False

def test_correctly_map_all_fields():
    flow_plugin = FlowActionPlugin(
        id="123",
        metadata=None,
        plugin=Plugin(
            start=False,
            spec=Spec(
                module=__name__,
                className='DecrementAction',
                inputs=["payload"],
                outputs=['payload', 'error'],
                init={"field": "profile@aux.counters", "decrement": 1},
                form=Form(groups=[
                    FormGroup(
                        fields=[
                            FormField(
                                id="field",
                                name="Path to field",
                                description="Provide path to field that should be decremented. "
                                            "E.g. profile@aux.counters.boughtProducts",
                                component=FormComponent(type="dotPath", props={"label": "Field path",
                                                                               "defaultSourceValue": "profile"})
                            )
                        ]
                    ),
                    FormGroup(
                        fields=[
                            FormField(
                                id="decrement",
                                name="Decrementation",
                                description="Provide by what number the value at provided path should be "
                                            "decremented. Default value equals 1.",
                                component=FormComponent(
                                    type="text",
                                    props={
                                        "label": "Decrementation"
                                    })
                            )
                        ]
                    ),
                ]),
                manual="decrement_action",
                version='0.8.2',
                license="MIT + CC",
                author="Risto Kowaczewski"
            ),
            metadata=MetaData(
                name='Decrement counter',
                desc='Decrement profile value. Returns payload or error if value is not numeric.',
                icon='minus',
                group=["Stats"],
                purpose=['collection', 'segmentation'],
                documentation=Documentation(
                    inputs={
                        "payload": PortDoc(desc="This port takes any JSON-like object.")
                    },
                    outputs={
                        "payload": PortDoc(
                            desc="This port returns taken object with field from configuration decremented "
                                 "by value from configuration.")
                    }
                )
            )
        )
    )

    with ServerContext(Context(production=True, tenant="123")):
        table = map_to_plugin_table(flow_plugin)

        assert table.id == "123"
        assert table.plugin_debug == False
        assert table.plugin_start is False
