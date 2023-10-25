from pydantic import field_validator

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.notation.dot_template import DotTemplate
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    type: str = "success"
    message: str
    hide_after: str
    position_x: str
    position_y: str
    uix_mf_source: str = "http://localhost:8686"  # AnyHttpUrl

    @field_validator("message")
    @classmethod
    def should_no_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Message should not be empty")
        return value

    @field_validator("hide_after")
    @classmethod
    def hide_after_should_be_numeric(cls, value: str):
        if not value.isnumeric():
            raise ValueError("This value should be numeric")
        return value


def validate(config: dict):
    return Configuration(**config)


class SnackBarUx(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        template = DotTemplate()

        message = template.render(self.config.message, dot)

        self.ux.append({
            "tag": "div",
            "props": {
                "class": "tracardi-uix-snackbar",
                "data-type": self.config.type,
                "data-message": message,
                "data-vertical": self.config.position_y,
                "data-horizontal": self.config.position_x,
                "data-auto-hide": self.config.hide_after
            }
        })
        self.ux.append({"tag": "script", "props": {"src": f"{self.config.uix_mf_source}/uix/snackbar/index.js"}})

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SnackBarUx',
            inputs=["payload"],
            outputs=["payload"],
            init={
                "type": "success",
                "message": "",
                "hide_after": 6000,
                "position_x": "center",
                "position_y": "bottom",
                "uix_mf_source": "http://localhost:8686"
            },
            version='0.6.1',
            license="MIT + CC",
            author="Risto Kowaczewski",
            form=Form(groups=[
                FormGroup(
                    name="Widget Message Configuration",
                    fields=[
                        FormField(
                            id="message",
                            name="Pop-up message",
                            description="Provide message that will be shown on the web page.",
                            component=FormComponent(type="textarea", props={"label": "message"})
                        ),
                        FormField(
                            id="type",
                            name="Alert type",
                            description="Select alert type.",
                            component=FormComponent(type="select", props={"label": "Alert type", "items": {
                                "error": "Error",
                                "warning": "Warning",
                                "success": "Success",
                                "info": "Info"
                            }})
                        ),
                        FormField(
                            id="hide_after",
                            name="Hide message after",
                            description="Type number of milliseconds the message must be visible. Default: 6000. 6sec.",
                            component=FormComponent(type="text", props={"label": "hide after"})
                        ),
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
                    ]),
                FormGroup(
                    name="Widget Source Location",
                    fields=[
                        FormField(
                            id="uix_mf_source",
                            name="Micro frontend source location",
                            description="Provide URL where the micro frontend source is located. Usually it is the "
                                        "location of Tracardi API. Type different location if you use CDN.",
                            component=FormComponent(type="text", props={"label": "URL"})
                        ),
                    ],
                ),
            ]),

        ),
        metadata=MetaData(
            name='Show snack bar',
            desc='Shows snack bar pop-up on the front end.',
            icon='react',
            group=["UIX Widgets"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={"payload": PortDoc(desc="This port returns input payload object.")}
            ),
            frontend=True
        )
    )
