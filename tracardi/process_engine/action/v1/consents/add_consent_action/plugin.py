from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi_plugin_sdk.domain.result import Result
from .model.payload import Consents
from tracardi.service.storage.driver import storage


class ConsentAdder(ActionRunner):

    def __init__(self, **kwargs):
        pass

    async def run(self, payload):
        consents = Consents(__root__=payload["consents"] if "consents" in payload else {})
        for consent in consents:
            consent_type = await storage.driver.consent_type.get_by_id(consent[0])
            if consent_type is not None:
                if not consent_type["revokable"]:
                    consent[1].set_to_none()
                self.profile.consents[consent[0]] = consent[1]
            else:
                return Result(port="error", value=Exception(f"There is no consent type with id: {consent[0]}")), \
                       Result(port="payload", value=payload)
        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.consents.add_consent_action.plugin',
            className='ConsentAdder',
            inputs=["payload"],
            outputs=['payload', 'error'],
            version='0.1.2',
            license="MIT",
            author="Dawid Kruk",
            init={}
        ),
        metadata=MetaData(
            name='Add consent',
            desc='This plugin adds consents to profile.',
            type='flowNode',
            width=200,
            height=100,
            icon='icon',
            group=["Consents"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns given payload without any changes."),
                    "error": PortDoc(desc="This port returns error object if it occurs.")
                }
            )
        )
    )