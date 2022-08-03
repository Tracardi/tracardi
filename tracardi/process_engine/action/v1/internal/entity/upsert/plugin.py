import json
from datetime import datetime

from tracardi.domain.entity import Entity, NullableEntity
from tracardi.domain.entity_record import EntityRecord
from tracardi.domain.profile import Profile
from tracardi.service.plugin.domain.result import Result
from .model.config import Configuration
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, FormGroup, Form, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage


def validate(config: dict):
    return Configuration(**config)


class EntityUpsertAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload: dict, in_edge=None):
        if self.profile is None and self.config.reference_profile is True:
            self.console.warning("This is profile-less event. Entity will be saved without the profile reference.")

        record = EntityRecord(
            timestamp=datetime.utcnow(),
            id=self.config.id,
            type=self.config.type,
            profile=Entity(id=self.profile.id) \
                if isinstance(self.profile, Profile) and self.config.reference_profile is True \
                else NullableEntity(id=None),
            properties=json.loads(self.config.properties),
            traits=json.loads(self.config.traits)
        )

        result = await storage.driver.entity.upsert(record)
        return Result(port="payload", value=result)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='EntityUpsertAction',
            inputs=["payload"],
            outputs=["payload"],
            version='0.7.2',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "id": None,
                "type": "",
                "reference_profile": True,
                "properties": "{}",
                "traits": "{}"
            },
            form=Form(groups=[
                FormGroup(
                    name="Entity settings",
                    fields=[
                        FormField(
                            id="id",
                            name="Entity ID",
                            description="Type the reference to the entity ID. It must be unique property of the "
                                        "entity that enables identification. For example: profile@pii.email for email "
                                        "or purchase order id for purchase",
                            component=FormComponent(type="dotPath", props={"label": "Entity ID",
                                                                           "defaultSourceValue": "event"})
                        ),
                        FormField(
                            id="reference_profile",
                            name="Connect entity with profile",
                            description="Entity will be assigned woth current profile if this feature is switched on.",
                            component=FormComponent(type="bool",
                                                    props={"label": "Assign entity to current profile"})
                        ),
                        FormField(
                            id="type",
                            name="Entity type",
                            description="Type the entity type, e.g. Purchase, E-mail, Car, Invoice, etc.",
                            component=FormComponent(type="text", props={"label": "Entity type"})
                        ),
                        FormField(
                            id="properties",
                            name="Entity properties",
                            component=FormComponent(type="json", props={"label": "Entity properties"})
                        ),
                        FormField(
                            id="traits",
                            name="Entity traits",
                            component=FormComponent(type="json", props={"label": "Entity traits"})
                        )
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name='Upsert entity',
            desc='Adds or updates entity.',
            icon='entity',
            group=["Input/Output"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns input payload.")
                }
            )
        )
    )
