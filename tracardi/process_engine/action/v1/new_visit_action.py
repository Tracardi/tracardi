from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result


class NewVisitAction(ActionRunner):

    def __init__(self, *args, **kwargs):
        pass

    async def run(self, payload):

        if self.session is None:
            self.console.warning("Can not check if visit is new is session is not available.")

        elif self.session.operation.new:
            return Result(port="true", value=payload)

        return Result(port="false", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.new_visit_action',
            className='NewVisitAction',
            inputs=["payload"],
            outputs=['true', 'false'],
            init=None,
            manual="new_visit_action",
            version='0.6.0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Is it a new visit',
            desc='If new visit then it returns true on TRUE output, otherwise returns false on FALSE port.',
            keywords=['condition'],
            icon='question',
            group=["Conditions"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON like object.")
                },
                outputs={
                    "true": PortDoc(desc="This port returns payload if the defined condition is met."),
                    "false": PortDoc(desc="This port returns payload if the defined condition is NOT met.")
                }
            )
        )
    )
