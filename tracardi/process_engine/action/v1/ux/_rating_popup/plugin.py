from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from pydantic import field_validator
from tracardi.service.plugin.domain.result import Result
from tracardi.service.notation.dot_template import DotTemplate
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    api_url: str
    uix_source: str
    title: str
    message: str
    lifetime: str
    horizontal_position: str
    vertical_position: str
    event_type: str
    save_event: bool
    dark_theme: bool

    @field_validator("api_url")
    @classmethod
    def validate_api_url(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("uix_source")
    @classmethod
    def validate_uix_source(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("message")
    @classmethod
    def validate_message(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("lifetime")
    @classmethod
    def validate_lifetime(cls, value):
        if value is None or len(value) == 0 or not value.isnumeric():
            raise ValueError("This field must contain an integer.")
        return value

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class RatingPopupPlugin(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        template = DotTemplate()

        message = template.render(self.config.message, dot)

        self.ux.append({
            "tag": "div",
            "props": {
                "class": "tracardi-uix-rating-widget",
                "data-position-vertical": self.config.vertical_position,
                "data-position-horizontal": self.config.horizontal_position,
                "data-title": self.config.title,
                "data-message": message,
                "data-event-type": self.config.event_type,
                "data-api-url": self.config.api_url,
                "data-theme": "dark" if self.config.dark_theme else "",
                "data-auto-hide": self.config.lifetime,
                "data-source-id": self.event.source.id,
                "data-profile-id": self.event.profile.id,
                "data-session-id": self.event.session.id,
                "data-save-event": "yes" if self.config.save_event else "no"
            }
        })
        self.ux.append({"tag": "script", "props": {"src": f"{self.config.uix_source}/uix/rating_popup/index.js"}})

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='RatingPopupPlugin',
            inputs=["payload"],
            outputs=["payload"],
            version='0.6.1',
            license="MIT + CC",
            author="Dawid Kruk",
            manual="rating_popup_action",
            init={
                "api_url": "http://localhost:8686",
                "uix_source": "http://localhost:8686",
                "title": None,
                "message": None,
                "lifetime": "6",
                "horizontal_position": "center",
                "vertical_position": "bottom",
                "event_type": None,
                "save_event": True,
                "dark_theme": False
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="uix_source",
                                name="UIX source",
                                description="Provide URL where the micro frontend source is located. Usually it is the "
                                            "location of Tracardi API. Type different location if you use CDN.",
                                component=FormComponent(type="text", props={"label": "URL"})
                            ),
                            FormField(
                                id="api_url",
                                name="API URL",
                                description="Provide a URL of Tracardi instance to send event with rating.",
                                component=FormComponent(type="text", props={"label": "API URL"})
                            ),
                            FormField(
                                id="title",
                                name="Title",
                                description="This text will become a title for your rating popup.",
                                component=FormComponent(type="text", props={"label": "Title"})
                            ),
                            FormField(
                                id="message",
                                name="Popup message",
                                description="That's the message to be displayed in the rating popup. You can use a "
                                            "template here.",
                                component=FormComponent(type="textarea", props={"label": "Message"})
                            ),
                            FormField(
                                id="horizontal_position",
                                name="Horizontal position",
                                description="That's the horizontal position of your popup.",
                                component=FormComponent(type="select", props={"label": "Horizontal position", "items": {
                                    "left": "Left",
                                    "center": "Center",
                                    "right": "Right"
                                }})
                            ),
                            FormField(
                                id="vertical_position",
                                name="Vertical position",
                                description="That's the vertical position of your popup.",
                                component=FormComponent(type="select", props={"label": "Vertical position", "items": {
                                    "top": "Top",
                                    "bottom": "Bottom"
                                }})
                            ),
                            FormField(
                                id="event_type",
                                name="Event type",
                                description="Please provide a type of event to be sent back after selecting rating.",
                                component=FormComponent(type="text", props={"label": "Event type"})
                            ),
                            FormField(
                                id="save_event",
                                name="Save event",
                                description="Please determine whether sent event should be saved or not.",
                                component=FormComponent(type="bool", props={"label": "Save event"})
                            ),
                            FormField(
                                id="lifetime",
                                name="Popup lifetime",
                                description="Please provide a number of seconds for the rating popup to be displayed.",
                                component=FormComponent(type="text", props={"label": "Lifetime"})
                            ),
                            FormField(
                                id="dark_theme",
                                name="Dark theme",
                                description="You can switch to dark mode for your popup. Default theme is bright.",
                                component=FormComponent(type="bool", props={"label": "Dark mode"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Show rating widget',
            desc='Shows rating widget with defined title and content.',
            icon='react',
            group=["UIX Widgets"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns given payload without any changes.")
                }
            )
        )
    )
