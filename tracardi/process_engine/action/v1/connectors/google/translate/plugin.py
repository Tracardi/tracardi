import googletrans
from pydantic import validator

from tracardi.service.plugin.domain.config import PluginConfig

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result

from googletrans import Translator


class Config(PluginConfig):
    text_to_translate: str
    source_language: str

    @validator("source_language")
    def check_given_source_language_type(cls, value):
        if not isinstance(value, str) or not value:
            raise ValueError("The language source must be a string!")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class GoogleTranslateAction(ActionRunner):
    config: Config
    translator: Translator

    async def set_up(self, init):
        self.config = validate(init)
        self.translator = Translator()

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        text_to_translate = dot[self.config.text_to_translate]

        translation = self.translator.translate(
            text_to_translate,
            src=self.config.source_language,
            dest='en')

        return Result(port="translation", value={"translation": translation.text})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className="GoogleTranslateAction",
            inputs=["payload"],
            version="0.7.2",
            license="MIT",
            author="Mateusz Zitaruk",
            init={
                "text_to_translate": None,
                "source_language": None
            },
            manual="google_translate_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Google translator configurator",
                        fields=[
                            FormField(
                                id="text_to_translate",
                                name="Text to translate",
                                description="Please provide path to text that you want to translate.",
                                component=FormComponent(
                                    type="dotPath",
                                    props={
                                        "label": "Path",
                                        "defaultSourceValue": "event"
                                    }
                                )
                            ),
                            FormField(
                                id="source_language",
                                name="Language source",
                                description="Please select source language of text that you want to translate.",
                                component=FormComponent(
                                    type="select",
                                    props={
                                        "label": "Source language",
                                        "items": googletrans.LANGUAGES
                                    }
                                )
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name="Google Translate",
            desc="Translates text",
            icon="google",
            group=["Google"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={"translation": PortDoc(desc="This port returns translated text.")}
            )
        )
    )
