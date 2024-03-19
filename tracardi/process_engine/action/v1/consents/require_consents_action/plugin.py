from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.mysql.mapping.consent_type_mapping import map_to_consent_type
from tracardi.service.storage.mysql.service.consent_type_service import ConsentTypeService
from .model.config import Config
from tracardi.service.plugin.domain.result import Result


def validate(config: dict) -> Config:
    return Config(**config)


class RequireConsentsAction(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        if self.event.metadata.profile_less is True:
            self.console.warning("Cannot perform consent check on profile less event.")
            return Result(port="false", value=payload)

        consent_ids = [consent["id"] for consent in self.config.consent_ids]

        profile_consents_copy = self.profile.consents
        for consent_id in profile_consents_copy:
            revoke = self.profile.consents[consent_id].revoke
            if revoke is not None and revoke < self.event.metadata.time.insert:
                self.profile.consents.pop(consent_id)

        for consent_id in consent_ids:
            cts = ConsentTypeService()
            consent_type_record = await cts.load_by_id(consent_id)

            if not consent_type_record.exists():
                raise ValueError(f"There is no consent type with ID {consent_id}")
            consent_type = consent_type_record.map_to_object(map_to_consent_type)

            if self.config.require_all is True:
                if consent_id not in self.profile.consents:
                    return Result(port="false", value=payload)

                if consent_type.revokable is True:

                    if self.profile.consents[consent_id].revoke is None:
                        self.console.warning(f"Consent type {consent_type.name} is set as revokable by "
                                             f"the revoke date is not set for this profile. "
                                             f"I an assuming that this consent is "
                                             f"timeless.")
                        continue

                    try:
                        revoke_timestamp = self.profile.consents[consent_id].revoke.timestamp()
                    except AttributeError:
                        raise ValueError(f"Corrupted data - no revoke date provided for revokable consent "
                                         f"type {consent_id}")

                    if revoke_timestamp <= self.event.metadata.time.insert.timestamp():
                        return Result(port="false", value=payload)

            else:
                if consent_id in self.profile.consents:
                    if consent_type.revokable is False:
                        return Result(port="true", value=payload)

                    if self.profile.consents[consent_id].revoke is None:
                        return Result(port="true", value=payload)

                    try:
                        revoke_timestamp = self.profile.consents[consent_id].revoke.timestamp()
                    except AttributeError as e:
                        raise ValueError(f"Corrupted data - no revoke date provided for revokable consent "
                                         f"type {consent_id}. Reason: {str(e)}")

                    if revoke_timestamp > self.event.metadata.time.insert.timestamp():
                        return Result(port="true", value=payload)

        return Result(port="true" if self.config.require_all is True else "false", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='RequireConsentsAction',
            inputs=["payload"],
            outputs=["true", "false"],
            version='0.6.2',
            license="MIT + CC",
            author="Dawid Kruk",
            manual="require_consents_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Consent requirements",
                        fields=[
                            FormField(
                                id="consent_ids",
                                name="IDs of required consents",
                                description="Provide a list of IDs of consents that the profile must grant. "
                                            "Press enter to add more the one consent.",
                                component=FormComponent(type="consentTypes")
                            ),
                            FormField(
                                id="require_all",
                                name="Require all",
                                description="If set to ON, plugin will require all of selected consents to be granted "
                                            "and not revoked. If set to OFF, plugin will require only one of defined "
                                            "consents to be granted.",
                                component=FormComponent(type="bool", props={"label": "Require all"})
                            )
                        ]
                    )
                ]
            ),
            init={
                "consent_ids": [],
                "require_all": False
            }
        ),
        metadata=MetaData(
            name='Has consents',
            desc='Checks if defined consents are granted by current profile.',
            icon='consent',
            group=["Consents"],
            type="condNode",
            tags=['condition'],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "true": PortDoc(desc="This port returns given payload if defined consents are granted."),
                    "false": PortDoc(desc="This port returns given payload if defined consents are not granted.")
                }
            )
        )
    )
