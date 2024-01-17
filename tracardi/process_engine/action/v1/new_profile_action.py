from tracardi.domain.profile import Profile

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class NewProfileAction(ActionRunner):

    async def run(self, payload: dict, in_edge=None) -> Result:
        if self.event.metadata.profile_less is True:
            self.console.warning("Can not check if profile is new in profile less events.")
        elif isinstance(self.profile, Profile) and self.profile.is_new():
            return Result(port="true", value=payload)

        return Result(port="false", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.new_profile_action',
            className='NewProfileAction',
            inputs=["payload"],
            outputs=['true', 'false'],
            init=None,
            manual="new_profile_action",
            version='0.6.0.1',
            license="MIT + CC",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Is it a new profile',
            desc='If new profile then it returns true on TRUE output, otherwise returns false on FALSE port.',
            tags=['condition'],
            type="condNode",
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON like object.")
                },
                outputs={
                    "true": PortDoc(desc="This port returns payload if the defined condition is met."),
                    "false": PortDoc(desc="This port returns payload if the defined condition is NOT met.")
                }
            ),
            icon='exists',
            group=["Flow control"]
        )
    )
