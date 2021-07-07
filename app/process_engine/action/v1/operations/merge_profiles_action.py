from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner

from app.process_engine.dot_accessor import DotAccessor


class MergeProfilesAction(ActionRunner):

    def __init__(self, *args, **kwargs):
        if 'mergeBy' not in kwargs:
            raise ValueError("Field mergeBy is not set. Define it in config section.")
        self.merge_key = kwargs['mergeBy']
        self.merge_key = [key.lower() for key in self.merge_key]

        if len(self.merge_key) == 0:
            raise ValueError("Field mergeBy is empty and has no effect on merging. "
                             "Add merging key or remove this action from flow.")

        for key in self.merge_key:
            if not key.startswith('profile@'):
                raise ValueError(
                    f"Field mergeBy must define profile fields. Dot notation `{key}` does not start with profile@...")

    async def run(self, payload):
        self.profile.operation.merge = self.merge_key
        return None


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='app.process_engine.action.v1.operations.merge_profiles_action',
            className='MergeProfilesAction',
            inputs=["payload"],
            outputs=[],
            init={"mergeBy": []},
            manual="merge_profiles_action"
        ),
        metadata=MetaData(
            name='Merge profiles',
            desc='Merges profile in storage when flow ends. This operation is expensive so use it with caution, '
                 'only where this is new PII inforamtion added.',
            type='flowNode',
            width=200,
            height=100,
            icon='merge',
            group=["Operations"]
        )
    )
