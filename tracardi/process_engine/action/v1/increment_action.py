from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result
from tracardi.domain.profile import Profile
from tracardi_dot_notation.dot_accessor import DotAccessor


class IncrementAction(ActionRunner):

    def __init__(self, **kwargs):

        if 'field' not in kwargs or kwargs['field'] is None:
            raise ValueError("Field is not set. Define it in config section.")

        if 'increment' not in kwargs or kwargs['increment'] is None:
            raise ValueError("Increment is not set. Define it in config section.")

        self.field = kwargs['field']
        self.increment = kwargs['increment']

        if type(self.increment) != int and type(self.increment) != float:
            raise ValueError("Increment must be a number. {} given.".format(type(self.increment)))

        if not self.field.startswith('profile@stats.counters'):
            raise ValueError("Only fields inside `profile@stats.counters` can be incremented. Field `{}` given.".format(self.field))

    async def run(self, payload):

        dot = DotAccessor(self.profile, self.session, payload, self.event, self.flow)

        try:

            value = dot[self.field]

            if value is None:
                value = 0

        except KeyError:
            value = 0

        if type(value) != int:
            raise ValueError("Filed `{}` value is not numeric.".format(self.field))

        value += self.increment

        dot[self.field] = value

        self.profile.replace(Profile(**dot.profile))

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.increment_action',
            className='IncrementAction',
            inputs=["payload"],
            outputs=['payload'],
            init={"field": None, "increment": 1},
            manual="increment_action",
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Increment counter',
            desc='Increment profile stats.counters value. Returns payload',
            type='flowNode',
            width=200,
            height=100,
            icon='plus',
            group=["Stats"]
        )
    )

