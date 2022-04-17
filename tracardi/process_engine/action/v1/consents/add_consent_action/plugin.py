from tracardi.domain.consent_type import ConsentType
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from .model.payload import Consents, Configuration
from tracardi.service.storage.driver import storage


def validate(config: dict):
    return Configuration(**config)


class ConsentAdder(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload):

        if self.event.metadata.profile_less is False:

            dot = self._get_dot_accessor(payload)

            consents_data = dot[self.config.consents]

            if not isinstance(consents_data, dict):
                raise ValueError(
                    "Consents must be defined as dict, with keys as consent-id and value as Consent object with revoke.")

            consents = Consents(__root__=consents_data)
            for consent_id, consent in consents:
                consent_type_data = await storage.driver.consent_type.get_by_id(consent_id)

                if consent_type_data is not None:
                    consent_type = ConsentType(**consent_type_data)
                    if consent_type.revokable is False:
                        consent.revoke = None
                    self.profile.consents[consent_id] = consent
                else:
                    self.console.warning(f"The consent id `{consent_id}` was not appended to profile as there is no consent "
                                         f"type `{consent_id}` defined in the system.")

            return Result(port="payload", value=self.profile.consents)
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
            version='0.6.0.1',
            license="MIT",
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
                    "payload": PortDoc(desc="This port takes any JSON like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns given payload without any changes.")
                }
            )
        )
    )
