from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.plugin_endpoint import PluginEndpoint
from ..configuration import Configuration
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage
from ..entity_plugin_service import convert_entity_id


def validate(config: dict):
    return Configuration(**config)


class Endpoint(PluginEndpoint):

    @staticmethod
    async def get_entity_types(config: dict):
        # Returns only 800 types
        result = await storage.driver.entity.unique_entity_types(bucket_name="type", buckets_size=800)
        return {
            "total": result.total,
            "result": [{
                "id": key,
                "name": key
            } for key, _ in result.aggregations['type'][0].items() if key != "other"]
        }


class EntityLoadAction(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None):

        try:

            if self.profile is None and self.config.reference_profile is True:
                self.console.warning("This is profile-less event. Entity will be loaded without the profile reference.")

            dot = self._get_dot_accessor(payload)

            entity_id = dot[self.config.id]
            entity_id = convert_entity_id(self.config, entity_id, self.profile)

            result = await storage.driver.entity.load_by_id(entity_id)

            if result is None:
                return Result(port="missing", value=payload)

            return Result(port="result", value=result.dict())
        except Exception as e:
            return Result(port="error", value={
                "message": str(e)
            })


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='EntityLoadAction',
            inputs=["payload"],
            outputs=["result", "missing", "error"],
            version='0.7.2',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "id": None,
                "type": {
                    "id": "",
                    "name": ""
                },
                "reference_profile": True
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Entity settings",
                        fields=[
                            FormField(
                                id="id",
                                name="Entity Id",
                                description="Please provide the entity Id.",
                                component=FormComponent(type="dotPath",
                                                        props={"label": "Entity Id", "defaultSourceValue": "event"})
                            ),
                            FormField(
                                id="type",
                                name="Entity type",
                                description="Please provide the entity type. E.g. purchase, e-mail, car, notification, "
                                            "product, etc",
                                component=FormComponent(type="autocomplete", props={
                                    "label": "Entity type",
                                    "onlyValueWithOptions": False,
                                    "endpoint": {
                                        "url": Endpoint.url(__name__, "get_entity_types"),
                                        "method": "post"
                                    }
                                })
                            ),
                            FormField(
                                id="reference_profile",
                                name="Load entity only if belongs to current profile",
                                component=FormComponent(type="bool",
                                                        props={"label": "Must reference current profile"})
                            ),
                        ]
                    ),

                ]
            )
        ),
        metadata=MetaData(
            name='Load entity',
            desc='Loads entity by its id.',
            icon='entity',
            group=["Input/Output"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="This port returns response if entity exists."),
                    "missing": PortDoc(desc="This port returns payload if entity does not exist."),
                    "error": PortDoc(desc="This port returns error message.")
                }
            )
        )
    )
