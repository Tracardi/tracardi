import asyncio
from concurrent.futures import ThreadPoolExecutor
from device_detector import DeviceDetector
from pydantic import field_validator
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.config import PluginConfig


class AgentConfiguration(PluginConfig):
    agent: str

    @field_validator("agent")
    @classmethod
    def is_valid_dot_path(cls, value):
        if len(value) < 1:
            raise ValueError("Event type can not be empty.")

        if value != value.strip():
            raise ValueError(f"This field must not have space. Space is at the end or start of '{value}'")

        return value.strip()


def validate(config: dict) -> AgentConfiguration:
    return AgentConfiguration(**config)


class DetectClientAgentAction(ActionRunner):

    config: AgentConfiguration

    async def set_up(self, init):
        self.config = validate(init)

    def detect_device(self, ua):
        try:
            detector = DeviceDetector(ua, skip_bot_detection=False)
            return detector.parse()
        except Exception as e:
            self.console.error(str(e))
            return {}

    async def run(self, payload: dict, in_edge=None) -> Result:

        try:
            if not isinstance(self.session.context, dict):
                raise KeyError("No session context defined.")

            dot = self._get_dot_accessor(payload)
            ua = dot[self.config.agent]

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
                            "name": device.device_brand(),
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

        return Result(port="payload", value=response)


def register() -> Plugin:
    return Plugin(
        start=False,
        debug=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.detect_client_agent_action',
            className='DetectClientAgentAction',
            inputs=["payload"],
            outputs=["payload"],
            init={
                "agent": "session@context.browser.browser.userAgent"
            },
            form=Form(groups=[
                FormGroup(
                    name="Detect client type",
                    fields=[
                        FormField(
                            id="agent",
                            name="Path to user agent data",
                            description="Type path to field that has user agent data. "
                                        "E.g. session@context.browser.browser.userAgent",
                            component=FormComponent(type="dotPath", props={"label": "Field path"})
                        )
                    ]
                )
            ]),
            manual="detect_client_agent_action",
            version='0.6.1',
            license="MIT + CC",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Detect device',
            desc='It will parse any user agent string and detect the browser, operating system, device used (desktop, '
                 'tablet, mobile, tv, cars, console, etc.), brand and model.',
            icon='browser',
            group=["Data processing"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns information about user's client, so browser, "
                                            "device info, etc.")
                }
            )
        )
    )
