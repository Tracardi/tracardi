from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from pydantic import field_validator
from tracardi.service.notation.dot_template import DotTemplate
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    uix_source: str
    api_url: str
    content: str
    contact_type: str
    horizontal_pos: str
    vertical_pos: str
    event_type: str
    save_event: bool
    dark_theme: bool

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

    @field_validator("content")
    @classmethod
    def validate_content(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, value):
        if value is None or len(value) == 0:
            raise ValueError("This field cannot be empty.")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class ContactPopupPlugin(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        template = DotTemplate()

        content = template.render(self.config.content, dot)

        self.ux.append({
            "tag": "link",
            "props": {
                "rel": "stylesheet",
                "href": f"{self.config.uix_source}/uix/contact-popup/index.css"
            }
        })
        self.ux.append({
            "tag": "div",
            "props": {
                "class": "tracardi-uix-contact-widget",
                "data-message": content,
                "data-contact-type": self.config.contact_type,
                "data-api-url": self.config.api_url,
                "data-source-id": self.event.source.id,
                "data-profile-id": self.event.profile.id,
                "data-session-id": self.event.session.id,
                "data-event-type": self.config.event_type,
                "data-theme": "dark" if self.config.dark_theme else "",
                "data-position-horizontal": self.config.horizontal_pos,
                "data-position-vertical": self.config.vertical_pos,
                "data-save-event": "yes" if self.config.save_event else "no"
            }
        })
        self.ux.append({
            "tag": "script",
            "props": {"src": f"{self.config.uix_source}/uix/contact-popup/index.js"}
        })

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ContactPopupPlugin',
            inputs=["payload"],
            outputs=["payload"],
            version='0.6.1',
            license="MIT + CC",
            author="Dawid Kruk",
            manual="contact_popup_action",
            init={
                "uix_source": "http://localhost:8686",
                "api_url": "http://localhost:8686",
                "content": None,
                "contact_type": "email",
                "horizontal_pos": "center",
                "vertical_pos": "bottom",
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
                                description="Provide a URL of Tracardi instance to send event with contact data.",
                                component=FormComponent(type="text", props={"label": "API URL"})
                            ),
                            FormField(
                                id="content",
                                name="Popup message",
                                description="That's the message to be displayed in the popup. You can use a template "
                                            "here.",
                                component=FormComponent(type="textarea", props={"label": "Message"})
                            ),
                            FormField(
                                id="contact_type",
                                name="Contact data type",
                                description="Please select type of the contact data to be provided by user.",
                                component=FormComponent(type="select", props={"label": "Contact", "items": {
                                    "email": "Email",
                                    "phone": "Phone number"
                                }})
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
                                description="Please provide a type of event to be sent back after submitting contact "
                                            "data by the user.",
                                component=FormComponent(type="text", props={"label": "Event type"})
                            ),
                            FormField(
                                id="save_event",
                                name="Save event",
                                description="Please determine whether sent event should be saved or not.",
                                component=FormComponent(type="bool", props={"label": "Save event"})
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
            name='Show contact popup',
            desc='Shows a popup with field for contact data to user, according to configuration.',
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
