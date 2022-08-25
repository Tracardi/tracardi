from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from pydantic import validator
from tracardi.service.notation.dot_template import DotTemplate
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    api_url: str
    uix_source: str
    popup_title: str
    content: str
    left_button_text: str
    right_button_text: str
    horizontal_pos: str
    vertical_pos: str
    event_type: str
    save_event: bool
    popup_lifetime: str
    dark_theme: bool

    @validator("popup_lifetime")
    def validate_popup_lifetime(cls, value):
        if value is None or len(value) == 0 or not value.isnumeric():
            raise ValueError("This field must contain an integer.")
        return value

    @validator("uix_source")
    def validate_uix_source(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("api_url")
    def validate_api_url(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("left_button_text")
    def validate_left_button_text(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("right_button_text")
    def validate_right_button_text(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("event_type")
    def validate_event_type(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class QuestionPopupPlugin(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        template = DotTemplate()

        content = template.render(self.config.content, dot)

        self.ux.append({
            "tag": "div",
            "props": {
                "class": "tracardi-question-widget",
                "data-api-url": self.config.api_url,
                "data-source-id": self.event.source.id,
                "data-session-id": self.event.session.id,
                "data-left-button-text": self.config.left_button_text,
                "data-right-button-text": self.config.right_button_text,
                "data-popup-title": self.config.popup_title,
                "data-content": content,
                "data-horizontal-position": self.config.horizontal_pos,
                "data-vertical-position": self.config.vertical_pos,
                "data-popup-lifetime": self.config.popup_lifetime,
                "data-theme": "dark" if self.config.dark_theme else "",
                "data-event-type": self.config.event_type,
                "data-save-event": "yes" if self.config.save_event else "no",
                "data-profile-id": self.event.profile.id
            }
        })
        self.ux.append({
            "tag": "script",
            "props": {"src": f"{self.config.uix_source}/uix/question-popup/index.js"}
        })

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='QuestionPopupPlugin',
            inputs=["payload"],
            outputs=["payload"],
            version='0.6.1',
            license="MIT",
            author="Dawid Kruk",
            manual="question_popup_action",
            init={
                "api_url": "http://localhost:8686",
                "uix_source": "http://localhost:8686",
                "popup_title": None,
                "content": None,
                "left_button_text": None,
                "right_button_text": None,
                "horizontal_pos": "center",
                "vertical_pos": "bottom",
                "event_type": None,
                "save_event": True,
                "popup_lifetime": "6",
                "dark_theme": False,
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
                                description="Provide a URL of Tracardi instance to send event with answer.",
                                component=FormComponent(type="text", props={"label": "API URL"})
                            ),
                            FormField(
                                id="popup_title",
                                name="Popup title",
                                description="This text will become a title for your popup.",
                                component=FormComponent(type="text", props={"label": "Title"})
                            ),
                            FormField(
                                id="content",
                                name="Popup content",
                                description="That's the message to be displayed in the popup. You can use a template "
                                            "here.",
                                component=FormComponent(type="textarea", props={"label": "Message"})
                            ),
                            FormField(
                                id="left_button_text",
                                name="Left button text",
                                description="That's the text to be displayed on the left button. It will be sent back "
                                            "in event properties if left button gets clicked.",
                                component=FormComponent(type="text", props={"label": "Left button"})
                            ),
                            FormField(
                                id="right_button_text",
                                name="Right button text",
                                description="That's the text to be displayed on the right button. It will be sent back "
                                            "in event properties if right button gets clicked.",
                                component=FormComponent(type="text", props={"label": "Right button"})
                            ),
                            FormField(
                                id="horizontal_pos",
                                name="Horizontal position",
                                description="That's the horizontal position of your popup.",
                                component=FormComponent(type="select", props={"label": "Horizontal position", "items": {
                                    "left": "Left",
                                    "center": "Center",
                                    "right": "Right"
                                }})
                            ),
                            FormField(
                                id="vertical_pos",
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
                                description="Please provide a type of event to be sent back after clicking one of "
                                            "buttons.",
                                component=FormComponent(type="text", props={"label": "Event type"})
                            ),
                            FormField(
                                id="save_event",
                                name="Save event",
                                description="Please determine whether sent event should be saved or not.",
                                component=FormComponent(type="bool", props={"label": "Save event"})
                            ),
                            FormField(
                                id="popup_lifetime",
                                name="Popup lifetime",
                                description="Please provide a number of seconds for the popup to be displayed.",
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
            name='Show question popup',
            desc='Shows question popup to user, according to configuration.',
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
