from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result

from tracardi.domain.profile_stats import ProfileStats


class IncreaseVisitsAction(ActionRunner):

    def __init__(self, *args, **kwargs):
        pass

    async def run(self, payload):

        if self.event.metadata.profile_less is True:
            self.console.warning("Can not increase profile visits in profile less events.")
        else:
            if self.profile.stats is None:
                self.profile.stats = ProfileStats()

            if self.session is not None and self.session.operation.new:
                self.profile.increase_visits()

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.increase_visits_action',
            className='IncreaseVisitsAction',
            inputs=["payload"],
            outputs=['payload'],
            init=None,
            manual="increase_visits_action",
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Increase visits',
            desc='Increases visit field in profile and returns payload.',
            icon='plus',
            group=["Stats"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns object received by plugin in input.")
                }
            )
        )
    )
