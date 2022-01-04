from pydantic import BaseModel, validator, AnyHttpUrl

from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result


class Configuration(BaseModel):
    endpoint: AnyHttpUrl
    event_type: str = "user-consent-pref"
    agree_all_event_type: str = "agree-all-event-type"
    position: str = "bottom"
    expand_height: int = 400
    enable: bool = True

    @validator("agree_all_event_type")
    def all_event_type_should_no_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("This field should not be empty")
        return value

    @validator("endpoint")
    def endpoint_should_no_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("This field should not be empty")
        return value

    @validator("event_type")
    def event_type_should_no_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("This field should not be empty")
        return value

    @validator("position")
    def position_enum(cls, value):
        if len(value) == 0:
            raise ValueError("This field should be either [top] or [bottom]")
        return value

    @validator("expand_height")
    def height_enum(cls, value: str):
        if isinstance(value, str) and not value.isnumeric():
            raise ValueError("This field must be a number")
        return int(value)


def validate(config: dict):
    return Configuration(**config)


class ConsentUx(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload):
        tracardi_endpoint = "http://localhost:8686"
        uix_endpoint = "http://localhost:8686"
        self.ux.append({"tag": "div", "props": {
            "class": "tracardi-uix-consent",
            "data-endpoint": tracardi_endpoint,  # Tracardi endpoint
            "data-event-type": "user-consent-pref",
            "data-agree-all-event-type": "user-consent-agree-all",
            "data-position": "top",
            "data-expand-height": 400,
            "data-profile": self.profile.id,
            "data-session": self.session.id,
            "data-source": self.event.source.id
        }})
        self.ux.append({"tag": "script", "props": {"src": f"{uix_endpoint}/uix/consent/index.js"}})

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ConsentUx',
            inputs=["payload"],
            outputs=["payload"],
            init={
                "endpoint": "http://locahost:8686",
                "event_type": "user-consent-pref",
                "agree_all_event_type": "agree-all-event-type",
                "position": "bottom",
                "expand_height": 400,
                "enabled": True
            },
            version='0.6.1',
            license="MIT",
            author="Risto Kowaczewski",
            form=Form(groups=[
                FormGroup(
                    name="Consent Widget Configuration",
                    fields=[
                        FormField(
                            id="endpoint",
                            name="Tracardi API endpoint URL",
                            description="Provide URL where the events from this widget will be send.",
                            component=FormComponent(type="text", props={"label": "URL"})
                        ),
                        FormField(
                            id="event_type",
                            name="Event type",
                            description="Event type that will be send when user selects consent preferences.",
                            component=FormComponent(type="text", props={"label": "Event type"})
                        ),
                        FormField(
                            id="agree_all_event_type",
                            name="Event type for Agree To All",
                            description="Event type that will be send when user selects Agree to All consents.",
                            component=FormComponent(type="text", props={"label": "Event type"})
                        ),
                        FormField(
                            id="position",
                            name="Widget position",
                            description="Where would you like to place the widget.",
                            component=FormComponent(type="select", props={"label": "Position", "items": {
                                "top": "Top",
                                "bottom": "Bottom"
                            }})
                        ),
                        FormField(
                            id="expand_height",
                            name="Widget height",
                            description="Type height of the expanded widget",
                            component=FormComponent(type="text", props={"label": "Height"})
                        ),
                        FormField(
                            id="enabled",
                            name="Enable widget",
                            description="Only enabled widgets are show on the page",
                            component=FormComponent(type="bool", props={"label": "Enable"})
                        ),
                    ]
                ),
            ]),

        ),
        metadata=MetaData(
            name='Show consent bar',
            desc='Shows consent pop-up on the front end.',
            icon='react',
            group=["UI Widgets"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={"payload": PortDoc(desc="This port returns input payload object.")}
            )
        )
    )
