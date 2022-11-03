from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from pydantic import validator
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.config import PluginConfig


livechat_snippet = """window.__lc = window.__lc || {};
window.__lc.license = ###LICENSE###;
;(function(n,t,c){function i(n){return e._h?e._h.apply(null,n):e._q.push(n)}var e={_q:[],_h:null,_v:"2.0",on:function(){i(["on",c.call(arguments)])},once:function(){i(["once",c.call(arguments)])},off:function(){i(["off",c.call(arguments)])},get:function(){if(!e._h)throw new Error("[LiveChatWidget] You can't use getters before load.");return i(["get",c.call(arguments)])},call:function(){i(["call",c.call(arguments)])},init:function(){var n=t.createElement("script");n.async=!0,n.type="text/javascript",n.src="https://cdn.livechatinc.com/tracking.js",t.head.appendChild(n)}};!n.__lc.asyncInit&&e.init(),n.LiveChatWidget=n.LiveChatWidget||e}(window,document,[].slice))
"""


class Config(PluginConfig):
    license: str

    @validator("license")
    def validate_file_path(cls, value):
        if value == "":
            raise ValueError("License can not be empty.")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class LivechatWidgetPlugin(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        content = livechat_snippet.replace("###LICENSE###", self.config.license),

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
            className=LivechatWidgetPlugin.__name__,
            brand="livechat",
            inputs=["payload"],
            outputs=["payload"],
            version='0.7.3',
            license="MIT",
            author="Risto Kowaczewski",
            manual="livechat_widget_action",
            init={
                "license": ""
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Livechat widget configuration",
                        fields=[
                            FormField(
                                id="license",
                                name="Your LiveChat license number",
                                component=FormComponent(type="password", props={"label": "Livechat License"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='LiveChat widget',
            desc='Shows LiveChat widget on the webpage.',
            icon='livechat',
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
