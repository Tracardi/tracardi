import asyncio
from concurrent.futures import ThreadPoolExecutor

from device_detector import DeviceDetector

from tracardi_dot_notation.dot_accessor import DotAccessor
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner


class DetectClientAgentAction(ActionRunner):

    def __init__(self, **kwargs):
        if 'userAgent' not in kwargs:
            raise ValueError("Please define userAgent path with dot notation.")

        self.user_agent = kwargs['userAgent']

    @staticmethod
    def detect_device(ua):
        detector = DeviceDetector(ua, skip_bot_detection=False)
        return detector.parse()

    async def run(self, payload):

        try:
            if not isinstance(self.session.context, dict):
                raise KeyError("No session context defined.")

            dot = DotAccessor(self.profile, self.session, payload, self.event, self.flow)
            ua = dot[self.user_agent]

            with ThreadPoolExecutor(max_workers=10) as pool:
                loop = asyncio.get_event_loop()
                device = await loop.run_in_executor(pool, self.detect_device, ua)  # type: DeviceDetector

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
            inputs=["payload"],
            outputs=["client-info"],
            init={
                "userAgent": "session@context.browser.browser.userAgent"
            },
            manual="detect_client_agent_action",
            version='0.1.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Parse client agent',
            desc='It will parse any user agent and detect the browser, operating system, device used (desktop, '
                 'tablet, mobile, tv, cars, console, etc.), brand and model. It detects thousands '
                 'of user agent strings, even from rare and obscure browsers and devices. It returns an object containing '
                 'all the information',
            type='flowNode',
            width=200,
            height=100,
            icon='browser',
            group=["Traits"]
        )
    )
