from device_detector import DeviceDetector
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner


class DetectClientAgentAction(ActionRunner):

    def __init__(self, *args, **kwargs):
        pass

    async def run(self, void):

        try:
            if not isinstance(self.session.context, dict):
                raise KeyError("No session context defined.")

            ua = self.session.context['browser']['browser']['userAgent']

            detector = DeviceDetector(ua, skip_bot_detection=False)
            device = detector.parse()

            response = {
                'status': {
                    "code": 200,
                    "message": "OK"
                },
                "device": {
                    "model": {
                        "name": device.device_model(),
                        "brand": {
                            "name": device.device_brand_name(),
                        },
                        "type": device.device_type()
                    },
                    "os": {
                        "name": device.os_name(),
                        "version": device.os_version(),
                    },
                    "client": {
                        "type": device.client_type(),
                        "name": device.client_name(),
                        "version": device.secondary_client_version(),
                        "engine": device.engine(),
                    },
                    "type": {
                        "mobile": device.is_mobile(),
                        "desktop": device.is_desktop(),
                        "bot": device.is_bot(),
                        "tv": device.is_television(),
                    }

                }
            }
        except KeyError as e:
            response = {
                'status': {
                    "code": 500,
                    "message": str(e)
                },
                "device": {
                    "model": {
                        "name": 'Unknown',
                        "brand": {
                            "name": 'Unknown',
                        },
                        "type": 'Unknown'
                    },
                    "os": {
                        "name": 'Unknown',
                        "version": 'Unknown',
                    },
                    "client": {
                        "type": 'Unknown',
                        "name": 'Unknown',
                        "version": 'Unknown',
                        "engine": 'Unknown',
                    },
                    "type": {
                        "mobile": 'Unknown',
                        "desktop": 'Unknown',
                        "bot": 'Unknown',
                        "tv": 'Unknown',
                    }
                }
            }

        return Result(port="client-info", value=response)


def register() -> Plugin:
    return Plugin(
        start=False,
        debug=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.detect_client_agent_action',
            className='DetectClientAgentAction',
            inputs=["void"],
            outputs=["client-info"],
            init=None,
            manual="detect_client_agent_action",
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Get client agent',
            desc='It will parse any user agent and detect the browser, operating system, device used (desktop, '
                 'tablet, mobile, tv, cars, console, etc.), brand and model. It detects thousands '
                 'of user agent strings, even from rare and obscure browsers and devices. It returns an object containing '
                 'all the information',
            type='flowNode',
            width=100,
            height=100,
            icon='browser',
            group=["Processing"]
        )
    )
