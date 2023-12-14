from pydantic import field_validator

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    endpoint: str # AnyHttpUrl
    uix_source: str # AnyHttpUrl
    position: str = "bottom"
    expand_height: int = 400
    enabled: bool = True
    always_display: bool = True

    @field_validator("uix_source")
    @classmethod
    def uix_source_should_no_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("This field should not be empty")
        return value

    @field_validator("endpoint")
    @classmethod
    def endpoint_should_no_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("This field should not be empty")
        return value

    @field_validator("position")
    @classmethod
    def position_enum(cls, value):
        if len(value) == 0:
            raise ValueError("This field should be either [top] or [bottom]")
        return value

    @field_validator("expand_height")
    @classmethod
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

        if self.config.always_display is False and self.profile.has_consents_set():
            # If consents were already granted (set) please do not show the widget.
            return Result(port="payload", value=payload)

        if self.config.enabled is True:
            self.ux.append({"tag": "div", "props": {
                "class": "tracardi-uix-consent",
                "data-endpoint": self.config.endpoint,  # Tracardi endpoint
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
                "enabled": True,
                "always_display": True
            },
            version='0.8.2',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual='show_consent_bar',
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
                        FormField(
                            id="always_display",
                            name="Display even if customer already granted consents",
                            description="When set widget will always be visible event if the consents were granted",
                            component=FormComponent(type="bool", props={"label": "Display always"})
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
                            description="Provide URL where the events from this widget will be send. Usually it is the "
                                        "location of Tracardi API. ",
                            component=FormComponent(type="text", props={"label": "URL"})
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
            frontend=True
        )
    )
