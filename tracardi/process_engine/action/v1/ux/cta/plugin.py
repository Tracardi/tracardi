from .configuration import Configuration
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


async def validate(config: dict) -> Configuration:
    return Configuration(**config)


class CtaMessageUx(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = Configuration(**init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        self.ux.append({
            "tag": "div",
            "props": {
                "class": "tracardi-uix-cta-message",
                "data-title": self.config.title,
                "data-message": self.config.message,
                "data-vertical": self.config.position_y,
                "data-horizontal": self.config.position_x,
                "data-auto-hide": self.config.hide_after,
                "data-cta-button": self.config.cta_button,
                "data-cta-link": self.config.cta_link,
                "data-cancel-button": self.config.cancel_button,
                "data-border-radius": self.config.border_radius,
                "data-border-shadow": self.config.border_shadow,
                "data-min-width": self.config.min_width,
                "data-max-width": self.config.max_width
            }
        })
        self.ux.append({
            "tag": "script",
            "props": {"src": f"{self.config.uix_source}/uix/cta-message/index.js"}
        })

        return Result(port="response", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=CtaMessageUx.__name__,
            inputs=["payload"],
            outputs=["response", "error"],
            init={
                "title": "",
                "message": "",
                "uix_source": "http://localhost:8686",
                "cta_button": "",
                "cta_link": "",
                "cancel_button": "",
                "border_radius": 2,
                "border_shadow": 1,
                "min_width": 300,
                "max_width": 500,
                "hide_after": 6000,
                "position_x": "right",
                "position_y": "bottom",
            },
            version='1.0.2',
            license="MIT",
            author="Risto Kowaczewski",
            form=Form(
                groups=[
                    FormGroup(
                        name="Widget Message Configuration",
                        fields=[
                            FormField(
                                id="title",
                                name="Title",
                                description="Provide title. Title can be empty the it will no be displayed.",
                                component=FormComponent(type="text", props={"label": "title"})
                            ),
                            FormField(
                                id="message",
                                name="Message before CTA button",
                                description="Provide message that will be displayed before CTA button.",
                                component=FormComponent(type="textarea", props={"label": "message"})
                            ),
                            FormField(
                                id="cta_button",
                                name="CTA button text",
                                description="Provide text to be displayed o CTA button.",
                                component=FormComponent(type="text", props={"label": "CTA button text"})
                            ),
                            FormField(
                                id="cta_link",
                                name="CTA link",
                                description="Provide CTA button link.",
                                component=FormComponent(type="text", props={"label": "CTA link"})
                            ),
                            FormField(
                                id="cancel_button",
                                name="Cancel button text",
                                description="Provide CANCEL button text. If empty the button will not be displayed.",
                                component=FormComponent(type="text", props={"label": "Cancel text"})
                            ),
                            FormField(
                                id="hide_after",
                                name="Hide message after",
                                description="Type number of milliseconds the message must be visible. "
                                            "Default: 6000. 6sec.",
                                component=FormComponent(type="text", props={"label": "hide after"})
                            )
                        ]),
                    FormGroup(
                        name="Widget Position and Width",
                        fields=[
                            FormField(
                                id="position_y",
                                name="Vertical position",
                                description="Select where would you like to place the message.",
                                component=FormComponent(type="select", props={"label": "Vertical position", "items": {
                                    "bottom": "Bottom",
                                    "top": "Top"
                                }})
                            ),
                            FormField(
                                id="position_x",
                                name="Horizontal position",
                                description="Select where would you like to place the message.",
                                component=FormComponent(type="select", props={"label": "Horizontal position", "items": {
                                    "left": "Left",
                                    "center": "Center",
                                    "right": "Right"
                                }})
                            ),
                            FormField(
                                id="min_width",
                                name="Minimal width",
                                description="Minimal width of the pop-up window.",
                                component=FormComponent(type="text", props={"label": "minimal width"})
                            ),
                            FormField(
                                id="max_width",
                                name="Maximal width",
                                description="Maximal width of the pop-up window.",
                                component=FormComponent(type="text", props={"label": "maximal width"})
                            )
                        ]),
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
                ]),

        ),
        metadata=MetaData(
            name='CTA message',
            desc='Shows massage CTA button pop-up on the front end.',
            icon='react',
            group=["UIX Widgets"],
            frontend=True
        )
    )
