from tracardi_dot_notation.dot_accessor import DotAccessor
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result

from tracardi.process_engine.rules_engine import RulesEngine


class NewEventAction(ActionRunner):

    def __init__(self, **kwargs):
        if 'event' not in kwargs or 'type' not in kwargs['event']:
            raise ValueError("Please define event.type as init parameter.")

        if 'event' not in kwargs or 'properties' not in kwargs['event']:
            raise ValueError("Please define event.properties as init parameter.")

        if kwargs['event']['type'] == 'undefined':
            raise ValueError("Please define event.type in config section. It has default value of undefined.")

        if kwargs['event']['properties'] == 'undefined':
            raise ValueError("Please define event.properties in config section. It has default value of undefined.")

        self.event_type = kwargs['event']['type']
        self.event_properties = kwargs['event']['properties']

    async def run(self, payload):

        dot = DotAccessor(self.profile, self.session, payload, self.event, self.flow)
        try:
            event_properties = dot[self.event_properties]
        except ValueError:
            # If there is error that means properties mus be as defined not a path.
            if isinstance(self.event_properties, dict):
                event_properties = self.event_properties
            else:
                raise ValueError("Properties must be either dict or dot notation path to event, profile or payload. Please correct action configuration.")

        session_copy = self.session.copy(deep=True)
        profile_copy = self.profile.copy(deep=True)

        event_result = await RulesEngine.raise_event(
            self.event_type,
            event_properties,
            session_copy,
            profile_copy,
            source_id=None)

        return Result(port="result", value=event_result)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.new_event_action',
            className='NewEventAction',
            inputs=["payload"],
            outputs=['result'],
            init={
                "event": {"type": "undefined", "properties": "undefined"}
            },
            manual="new_event_action"
        ),
        metadata=MetaData(
            name='New event',
            desc='Raises new event with defined properties. Please define event type and event properties in configuration tab.',
            type='flowNode',
            width=200,
            height=100,
            icon='event'
        )
    )
