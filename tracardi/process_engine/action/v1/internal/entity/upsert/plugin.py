import json
from datetime import datetime

from pydantic.utils import deep_update

from tracardi.domain.entity import Entity, NullableEntity
from tracardi.domain.entity_record import EntityRecord
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.domain.result import Result
from .model.config import Configuration
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, FormGroup, Form, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage
from ..entity_plugin_service import convert_entity_id, get_referenced_profile


def validate(config: dict):
    return Configuration(**config)


class EntityUpsertAction(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None):
        try:
            dot = self._get_dot_accessor(payload)

            properties = json.loads(self.config.properties)
            traits = json.loads(self.config.traits)
            traverser = DictTraverser(dot, default=None)
            traits = traverser.reshape(traits)
            properties = traverser.reshape(properties)

            # Requires merging
            merge_entity_with = self.config.merge_entity_with.strip()
            if merge_entity_with != "" and merge_entity_with != "payload@":
                entity_data = dot[self.config.merge_entity_with]

                # merge traits

                if 'traits' in entity_data:
                    traits = deep_update(entity_data['traits'], traits)
                else:
                    self.console.warning(f"No traits found in {self.config.merge_entity_with}")

                # merge properties

                if 'properties' in entity_data:
                    properties = deep_update(entity_data['properties'], properties)
                else:
                    self.console.warning(f"No properties found in {self.config.merge_entity_with}")

            entity_id = dot[self.config.id]
            entity_id = convert_entity_id(self.config, entity_id)

            if self.profile is None and self.config.reference_profile is True:
                self.console.warning("This is profile-less event. Entity will be saved without the profile reference.")

            referenced_profile_id = get_referenced_profile(self.config, self.profile)
            record = EntityRecord(
                timestamp=datetime.utcnow(),
                id=entity_id,
                type=self.config.type,
                profile=Entity(id=referenced_profile_id) if referenced_profile_id else NullableEntity(id=None),
                properties=properties,
                traits=traits
            )

            result = await storage.driver.entity.upsert(record)

            return Result(port="result", value={"result": result, "entity": record.dict()})
        except Exception as e:
            return Result(port="error", value={
                "message": str(e)
            })


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='EntityUpsertAction',
            inputs=["payload"],
            outputs=["result", "error"],
            version='0.7.3',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "id": "",
                "type": "",
                "reference_profile": True,
                "merge_entity_with": "",
                "properties": "{}",
                "traits": "{}"
            },
            form=Form(groups=[
                FormGroup(
                    name="Entity type and identification settings",
                    description="Entities are identified by type and id. Please provide the following data.",
                    fields=[
                        FormField(
                            id="type",
                            name="Entity type",
                            description="Type the entity-type, e.g. purchase, e-mail, car, invoice, etc. Type will be "
                                        "lower cased and all spaces will be replaced by dashes.",
                            component=FormComponent(type="text", props={"label": "Entity type"})
                        ),
                        FormField(
                            id="id",
                            name="Entity ID",
                            description="Type the entity ID. It can be a reference to the data in event, profile, etc. "
                                        "It must be a unique value that enables identification. "
                                        "For example: profile@pii.email for email or purchase order id for purchase.",
                            component=FormComponent(type="dotPath", props={"label": "Entity ID",
                                                                           "defaultSourceValue": "event"})
                        ),
                        FormField(
                            id="reference_profile",
                            name="Connect entity with profile",
                            description="Entity may be assigned with current profile.",
                            component=FormComponent(type="bool",
                                                    props={"label": "Assign entity to current profile"})
                        ),
                    ]
                ),
                FormGroup(
                    name="Entity properties and traits",
                    fields=[

                        FormField(
                            id="properties",
                            name="Entity properties",
                            description="New properties can be merged with existing properties if you provide the "
                                        "current entity data. See below: Entity to merge with",
                            component=FormComponent(type="json", props={"label": "Entity properties"})
                        ),
                        FormField(
                            id="traits",
                            name="Entity traits",
                            description="New traits can be merged with existing traits if you provide the "
                                        "current entity data. See below: Entity to merge with",
                            component=FormComponent(type="json", props={"label": "Entity traits"})
                        ),
                        FormField(
                            id="merge_entity_with",
                            name="Entity to merge with",
                            description="If you want the new properties to be merged with existing entity, please "
                                        "provide reference to the existing entity data. This usually requires to load "
                                        "entity to payload first.",
                            component=FormComponent(type="dotPath", props={"label": "Entity data",
                                                                           "defaultSourceValue": "payload"})
                        ),
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name='Create entity',
            desc='Adds or updates entity.',
            icon='entity',
            group=["Input/Output"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="This port returns input payload."),
                    "error": PortDoc(desc="This port returns error message.")
                }
            )
        )
    )
