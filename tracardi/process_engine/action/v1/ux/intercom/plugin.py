from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from pydantic import validator
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.config import PluginConfig


intercom_snippet = """window.intercomSettings = { app_id: '###APP_ID###' };
(function(){var w=window;var ic=w.Intercom;if(typeof ic==="function"){ic('reattach_activator');ic('update',w.intercomSettings);}else{var d=document;var i=function(){i.c(arguments);};i.q=[];i.c=function(args){i.q.push(args);};w.Intercom=i;var l=function(){var s=d.createElement('script');s.type='text/javascript';s.async=true;s.src='https://widget.intercom.io/widget/' + '###APP_ID###';var x=d.getElementsByTagName('script')[0];x.parentNode.insertBefore(s, x);};if(document.readyState==='complete'){l();}else if(w.attachEvent){w.attachEvent('onload',l);}else{w.addEventListener('load',l,false);}}})();
"""


class Config(PluginConfig):
    app_id: str

    @validator("app_id")
    def validate_file_path(cls, value):
        if value is None:
            raise ValueError("Application ID can not be empty.")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class IntercomWidgetPlugin(ActionRunner):
    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        content = intercom_snippet.replace("###APP_ID###", self.config.app_id),

        self.ux.append({
            "tag": "script",
            "type": "text/javascript",
            "content": content
        })

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=IntercomWidgetPlugin.__name__,
            brand="intercom",
            inputs=["payload"],
            outputs=["payload"],
            version='0.7.3',
            license="MIT",
            author="Mateusz Zitaruk, Risto Kowaczewski",
            manual="intercom_widget_action",
            init={
                "app_id": ""
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Intercom widget configuration",
                        fields=[
                            FormField(
                                id="app_id",
                                name="Your Intercom application ID",
                                component=FormComponent(type="password", props={"label": "Application ID"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Intercom widget',
            desc='Shows Intercom widget on the webpage.',
            icon='intercom',
            tags=['messaging', 'chat'],
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
