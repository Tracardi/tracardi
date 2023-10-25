from pydantic import validator

from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormComponent, FormField
from tracardi.service.plugin.domain.config import PluginConfig

from password_generator import PasswordGenerator


class Config(PluginConfig):
    max_length: int
    min_length: int
    uppercase: int
    lowercase: int
    special_characters: int

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("min_length")
    def check_min_max_value(cls, value, values):
        if value > values["max_length"]:
            raise ValueError(
                f'Minimal length {value} cannot be bigger than given maximal length {values["max_length"]}')
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class PasswordGeneratorAction(ActionRunner):

    config: Config
    pgo: PasswordGenerator

    async def set_up(self, init):
        self.pgo = PasswordGenerator()
        self.config = validate(init)
        self.pgo.minlen = self.config.min_length
        self.pgo.maxlen = self.config.max_length
        self.pgo.minuchars = self.config.uppercase
        self.pgo.minlchars = self.config.lowercase
        self.pgo.minschars = self.config.special_characters

    async def run(self, payload: dict, in_edge=None) -> Result:
        password = self.pgo.generate()
        return Result(port="password", value={"password": password})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='PasswordGeneratorAction',
            inputs=["payload"],
            outputs=["password"],
            version='0.7.1',
            license="MIT + CC",
            author="Mateusz Zitaruk",
            init={
                "min_length": 8,
                "max_length": 13,
                "uppercase": 2,
                "lowercase": 4,
                "special_characters": 2
            },
            manual="password_generator_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Password generator configuration",
                        fields=[
                            FormField(
                                id="max_length",
                                name="Password maximum length",
                                description="Please provide maximum length of password.",
                                component=FormComponent(
                                    type="text",
                                    props={
                                        "label": "Maximum password length"
                                    }
                                )

                            ),
                            FormField(
                                id="min_length",
                                name="Password minimum length",
                                description="Please provide minimum length of password.",
                                component=FormComponent(
                                    type="text",
                                    props={
                                        "label": "Minimum password length"
                                    }
                                )

                            ),
                            FormField(
                                id="uppercase",
                                name="Uppercase characters",
                                description="Please provide number of uppercase characters.",
                                component=FormComponent(
                                    type="text",
                                    props={
                                        "label": "Number of uppercase letters"
                                    }
                                )
                            ),
                            FormField(
                                id="lowercase",
                                name="Lowercase characters",
                                description="Please provide number of lowercase characters.",
                                component=FormComponent(
                                    type="text",
                                    props={
                                        "label": "Number of lowercase letters"
                                    }
                                )
                            ),
                            FormField(
                                id="special_characters",
                                name="Special characters",
                                description="Please provide number of special characters.",
                                component=FormComponent(
                                    type="text",
                                    props={
                                        "label": "Number of special characters"
                                    }
                                )
                            ),
                        ]
                    )
                ]
            )

        ),
        metadata=MetaData(
            name='Generate password',
            desc='Generate new password according to user input',
            icon='password',
            group=["Operations"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={"password": PortDoc(desc="This port returns generated password.")}
            )
        )
    )
