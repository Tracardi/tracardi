from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from pydantic import BaseModel, validator
from tracardi.service.notation.dot_template import DotTemplate


class Config(BaseModel):
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
    def validate_api_url(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("api_url")
    def validate_api_url(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("left_button_text")
    def validate_api_url(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("right_button_text")
    def validate_api_url(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @validator("event_type")
    def validate_api_url(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class QuestionPopupPlugin(ActionRunner):

    def __init__(self, **kwargs):
        self.config = Config(**kwargs)

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        template = DotTemplate()

        self.config.content = template.render(self.config.content, dot)

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
                "data-content": self.config.content,
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
            manual="question_popup_action", # TODO MANUAL
            init={
                "api_url": None,
                "uix_source": None,
                "popup_title": None,
                "content": None,
                "left_button_text": None,
                "right_button_text": None,
                "horizontal_pos": "center",
                "vertical_pos": "bottom",
                "event_type": None,
                "save_event": True,
                "popup_lifetime": None,
                "dark_theme": False,
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="api_url",

                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Show question popup',
            desc='Shows question popup to user, according to configuration.',
            icon='plugin',
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
