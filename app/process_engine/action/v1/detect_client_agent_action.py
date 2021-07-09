from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner


class DetectClientAgentAction(ActionRunner):

    def __init__(self, *args, **kwargs):
        pass

    async def run(self, void):
        if self.debug and self.profile.id == '@debug-profile-id':
            raise ValueError("Start action can not run in debug mode without connection to Debug action.")
        return Result(port="payload", value=self.event.dict())


def register() -> Plugin:
    return Plugin(
        start=True,
        debug=False,
        spec=Spec(
            module='app.process_engine.action.v1.detect_client_agent_action',
            className='DetectClientAgentAction',
            inputs=["void"],
            outputs=["client-info"],
            init=None,
            manual="detect_client_agent_action"
        ),
        metadata=MetaData(
            name='Get client agent',
            desc='It will parse any user agent and detect the browser, operating system, device used (desktop, '
                 'tablet, mobile, tv, cars, console, etc.), brand and model. It detects thousands '
                 'of user agent strings, even from rare and obscure browsers and devices. It returns an object containing '
                 'all te information',
            type='flowNode',
            width=100,
            height=100,
            icon='start',
            group=["Input/Output"]
        )
    )
