from tracardi.service.plugin.plugin_endpoint import PluginEndpoint
from .model.config import Configuration
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage


def validate(config: dict):
    return Configuration(**config)


class Endpoint(PluginEndpoint):

    @staticmethod
    async def get_entity_types(config: dict):
        # Returns only 800 types
        result = await storage.driver.index.unique_entity_types(bucket_name="type", buckets_size=800)
        return {
            "total": result.total,
            "result": [{
                "id": key,
                "name": key
            } for key, _ in result.aggregations['type'][0].items() if key != "other"]
        }


class EntityDeleteAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload: dict, in_edge=None):

        try:
            dot = self._get_dot_accessor(payload)
            entity_id = dot[self.config.id]

            # todo load by self.config.type, and self.profile.id
            result = await storage.driver.entity.delete_by_id(entity_id)

            return Result(port="result", value={
                "entity": result
            })
        except Exception as e:
            return Result(port="error", value={
                "message": str(e)
            })


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='EntityDeleteAction',
            inputs=["payload"],
            outputs=["result", "error"],
            version='0.7.2',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "id": "",
                "type": {
                    "id": "",
                    "name": ""
                },
                "reference_profile": True
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Entity delete settings",
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
                                name="Delete entity only if belongs to current profile",
                                component=FormComponent(type="bool",
                                                        props={"label": "Must reference current profile"})
                            ),
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Delete entity',
            desc='Deletes entity by its id.',
            icon='entity',
            group=["Input/Output"],
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
