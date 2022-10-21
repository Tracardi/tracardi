from pydantic import validator, AnyHttpUrl

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    endpoint: AnyHttpUrl
    uix_source: AnyHttpUrl
    event_type: str = "user-consent-pref"
    agree_all_event_type: str = "agree-all-event-type"
    position: str = "bottom"
    expand_height: int = 400
    enabled: bool = True

    @validator("agree_all_event_type")
    def all_event_type_should_no_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("This field should not be empty")
        return value

    @validator("uix_source")
    def uix_source_should_no_be_empty(cls, value):
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

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        if self.config.enabled is True:
            self.ux.append({"tag": "div", "props": {
                "class": "tracardi-uix-consent",
                "data-endpoint": self.config.endpoint,  # Tracardi endpoint
                "data-event-type": self.config.event_type,
                "data-agree-all-event-type": self.config.agree_all_event_type,
                "data-position": self.config.position,
                "data-expand-height": self.config.expand_height,
                "data-profile": self.profile.id,
                "data-session": self.session.id if self.session else None,
                "data-source": self.event.source.id
            }})
            self.ux.append({"tag": "script", "props": {"src": f"{self.config.uix_source}/uix/consent/index.js"}})

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
                "endpoint": "http://localhost:8686",
                "uix_source": "http://localhost:8686",
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
                    name="Widget Configuration",
                    fields=[
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
                    ],

                ),
                FormGroup(
                    name="Widget Source Location",
                    fields=[
                        FormField(
                            id="uix_source",
                            name="Consent micro frontend location",
                            description="Provide URL where the micro frontend source is located. Usually it is the "
                                        "location of Tracardi API. Type different location if you use CDN.",
                            component=FormComponent(type="text", props={"label": "URL"})
                        ),
                        FormField(
                            id="endpoint",
                            name="Tracardi API endpoint URL",
                            description="Provide URL where the events from this widget will be send.",
                            component=FormComponent(type="text", props={"label": "URL"})
                        ),
                        FormField(
                            id="event_type",
                            name="Event type for consent preferences",
                            description="Event type that will be send when user selects Consent Preferences.",
                            component=FormComponent(type="text", props={"label": "Event type"})
                        ),
                        FormField(
                            id="agree_all_event_type",
                            name="Event type for Agree To All",
                            description="Event type that will be send when user selects Agree to All consents.",
                            component=FormComponent(type="text", props={"label": "Event type"})
                        )
                    ])
            ]),

        ),
        metadata=MetaData(
            name='Show consent bar',
            desc='Shows consent pop-up on the front end.',
            icon='react',
            group=["UIX Widgets"],
            type="flowNodeWithEvents",
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={"payload": PortDoc(desc="This port returns input payload object.")}
            ),
            frontend=True,
            emits_event={
                "Consent preferences": 'user-consent-pref',
                "Agree all": 'agree-all-event-type',
            }
        )
    )
