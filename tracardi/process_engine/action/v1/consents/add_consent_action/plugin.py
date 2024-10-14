from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.storage.mysql.mapping.consent_type_mapping import map_to_consent_type
from tracardi.service.storage.mysql.service.consent_type_service import ConsentTypeService
from .model.payload import Configuration
from pytimeparse import parse
from datetime import datetime
from tracardi.domain.consent_revoke import ConsentRevoke


def validate(config: dict):
    return Configuration(**config)


class ConsentAdder(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        if self.event.metadata.profile_less is False:

            dot = self._get_dot_accessor(payload)

            consents_data = dot[self.config.consents]

            if not isinstance(consents_data, dict):
                raise ValueError(
                    "Consents must be defined as object, with keys as consent-id and value as bool.")

            # consents = Consents(__root__=)
            for consent_id, granted in consents_data.items():
                if granted is True:
                    cts = ConsentTypeService()
                    consent_type_record = await cts.load_by_id(consent_id)

                    if consent_type_record.exists():
                        consent_type = consent_type_record.map_to_object(map_to_consent_type)
                        if consent_type.revokable is False:
                            self.profile.consents[consent_id] = ConsentRevoke(revoke=None)
                        else:
                            revoke_offset = parse(consent_type.auto_revoke)

                            if revoke_offset is None:
                                raise ValueError(f"Error while adding consent type {consent_id}: consent is marked "
                                                     f"as revokable, but has no auto revoke property, or auto revoke "
                                                     f"property is incorrect.")

                            self.profile.consents[consent_id] = ConsentRevoke(revoke=datetime.fromtimestamp(
                                self.event.metadata.time.insert.timestamp() +
                                parse(consent_type.auto_revoke
                                      )))
                    else:
                        self.console.warning(
                            f"The consent id `{consent_id}` was not appended to profile as there is no consent "
                            f"type `{consent_id}` defined in the system.")

            return Result(port="payload", value=payload)
        else:
            self.console.error("Can not add profile consents on profile less event.")
            return Result(port="payload", value=None)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.consents.add_consent_action.plugin',
            className='ConsentAdder',
            inputs=["payload"],
            outputs=['payload'],
            version='0.6.3',
            license="MIT + CC",
            author="Dawid Kruk",
            init={
                "consents": None
            },
            manual="add_consents_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Consent data reference",
                        description="Please configure the reference to the event property that hold an information on "
                                    "granted consents.",
                        fields=[
                            FormField(
                                id="consents",
                                name="Reference to consents",
                                description="Select the reference path to consents. The most possible use-case is when "
                                            "customer grants consents by filling a form. This data is sent to Tracardi as "
                                            "an event with properties set to granted consents. We need a reference path to "
                                            "this data.",
                                component=FormComponent(
                                    type="forceDotPath",
                                    props={
                                        "defaultSourceValue": "event"
                                    })
                            )
                        ]

                    ),
                ]),
        ),
        metadata=MetaData(
            name='Add consent',
            desc='This plugin adds consents to profile.',
            icon='consent',
            group=["Consents"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns given payload without any changes.")
                }
            )
        )
    )
