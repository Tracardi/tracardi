from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result

from app.domain.profile_stats import ProfileStats


class IncreaseViewsAction(ActionRunner):

    def __init__(self, *args, **kwargs):
        pass

    async def run(self, **kwargs):

        if self.profile.stats is None:
            self.profile.stats = ProfileStats()

        self.profile.increase_views()

        return Result(port="profile", value=self.profile.dict())


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='app.process_engine.action.v1.increase_views_action',
            className='IncreaseViewsAction',
            inputs=["void"],
            outputs=['profile'],
            init={},
            manual="increase_views_action"
        ),
        metadata=MetaData(
            name='Increase views',
            desc='Increases view field in profile and returns profile.',
            type='flowNode',
            width=200,
            height=100,
            icon='plus'
        )
    )
