from typing import Optional

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from pydantic import field_validator
from tracardi.common.template.dot_template import DotTemplate
from tracardi.service.plugin.domain.config import PluginConfig
import html


class Config(PluginConfig):
    api_url: str
    uix_source: str
    popup_title: str
    popup_question: str
    left_button_text: str
    right_button_text: str
    horizontal_pos: str
    vertical_pos: str
    answer_event_type: str
    contact_event_type: Optional[str] = None
    save_event: bool
    popup_lifetime: str
    dark_theme: bool

    contact_text: Optional[str] = None
    display_contact_text_button: Optional[str] = 'none'

    @field_validator("popup_lifetime")
    @classmethod
    def validate_popup_lifetime(cls, value):
        if value is None or len(value) == 0 or not value.isnumeric():
            raise ValueError("This field must contain an integer.")
        return value

    @field_validator("uix_source")
    @classmethod
    def validate_uix_source(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("api_url")
    @classmethod
    def validate_api_url(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("left_button_text")
    @classmethod
    def validate_left_button_text(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("right_button_text")
    @classmethod
    def validate_right_button_text(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("answer_event_type")
    @classmethod
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

        popup_question = template.render(self.config.popup_question, dot)

        self.ux.append({
            "tag": "div",
            "props": {
                "class": "tracardi-question-widget",
                "data-api-url": self.config.api_url.strip(),
                "data-source-id": self.event.source.id.strip(),
                "data-session-id": self.event.session.id.strip(),
                "data-left-button-text": self.config.left_button_text.strip(),
                "data-right-button-text": self.config.right_button_text.strip(),
                "data-popup-title": html.escape(self.config.popup_title),
                "data-popup-question": html.escape(popup_question, quote=True),
                "data-horizontal-position": self.config.horizontal_pos.strip(),
                "data-vertical-position": self.config.vertical_pos.strip(),
                "data-popup-lifetime": self.config.popup_lifetime.strip(),
                "data-theme": "dark" if self.config.dark_theme else "",
                "data-answer-event-type": self.config.answer_event_type.strip(),
                "data-contact-event-type": self.config.contact_event_type.strip(),
                "data-save-event": "yes" if self.config.save_event else "no",
                "data-profile-id": self.event.profile.id.strip(),
                "data-contact-text": html.escape(self.config.contact_text.strip()),
                "data-display-contact-text-button": self.config.display_contact_text_button.strip()
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
            version='0.9.0',
            license="MIT + CC",
            author="Dawid Kruk, Risto Kowaczewski",
            manual="question_popup_action",
            init={
                "api_url": "http://localhost:8686",
                "uix_source": "http://localhost:8686",
                "popup_title": "",
                "popup_question": "",
                "left_button_text": None,
                "right_button_text": None,
                "horizontal_pos": "center",
                "vertical_pos": "bottom",
                "answer_event_type": "",
                "contact_event_type": "profile-update",
                "save_event": True,
                "popup_lifetime": "6",
                "dark_theme": False,
                "contact_text": "Would you like to connect?",
                "display_contact_text_button": "none"
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
                        ]
                    ),
                    FormGroup(
                        name="Question",
                        fields=[
                            FormField(
                                id="popup_title",
                                name="Popup title",
                                description="This text will become a title for your popup.",
                                component=FormComponent(type="text", props={"label": "Title"})
                            ),
                            FormField(
                                id="popup_question",
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
                        ]
                    ),
                    FormGroup(
                        name="Follow-up contact form",
                        fields=[
                            FormField(
                                id="contact_text",
                                name="Follow up contact form",
                                description="If you would like to ask for a contact write a message to be displayed, E.g. Would you like to connect?.",
                                component=FormComponent(type="textarea", props={"label": "Contact Invitation"})
                            ),
                            FormField(
                                id="display_contact_text_button",
                                name="When the contact form should be displayed?",
                                description="Define when the contact invitation form should appear. Enter the name of the button that activates the form, or type 'none' if the form should not appear, or type 'both' to make the form appear no matter which answer button is clicked.",
                                component=FormComponent(type="text", props={"label": "Contact Invitation"})
                            ),
                        ]
                    ),
                    FormGroup(
                        name="Registered events",
                        fields=[
                            FormField(
                                id="api_url",
                                name="API URL",
                                description="Provide a URL of Tracardi instance to send event with answer.",
                                component=FormComponent(type="text", props={"label": "API URL"})
                            ),
                            FormField(
                                id="answer_event_type",
                                name="Answer Event Type",
                                description="Please specify the type of event that should be sent back when one of the answer buttons is clicked.",
                                component=FormComponent(type="text", props={"label": "Answer Event Type"})
                            ),
                            FormField(
                                id="contact_event_type",
                                name="Contact Event Type",
                                description="Please provide a type of event to be sent back when customer provides contact information.",
                                component=FormComponent(type="text", props={"label": "Contact Event Type"})
                            ),
                            FormField(
                                id="save_event",
                                name="Save event",
                                description="Please determine whether sent events should be saved or not.",
                                component=FormComponent(type="bool", props={"label": "Save event"})
                            ),
                        ]
                    ),
                    FormGroup(
                        name="Positioning & Appearance",
                        fields=[
                            FormField(
                                id="popup_lifetime",
                                name="Popup lifetime",
                                description="Please provide a number of seconds for the popup to be displayed.",
                                component=FormComponent(type="text", props={"label": "Lifetime"})
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
