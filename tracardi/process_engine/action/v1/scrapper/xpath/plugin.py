from lxml import html

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.configuration import Configuration


def validate(config: dict):
    return Configuration(**config)


class HtmlXpathScrapperAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        content = dot[self.config.content]
        tree = html.fromstring(content)
        result = tree.xpath(self.config.xpath)
        if result:
            return Result(port="result", value={"result": result})
        self.console.warning("Could not find any data at path '{}'".format(self.config.xpath))
        return Result(port="error", value=self.config.model_dump())


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=HtmlXpathScrapperAction.__name__,
            inputs=["payload"],
            outputs=["result", "error"],
            version='0.6.1',
            license="MIT + CC",
            author="Risto Kowaczewski",
            init={
                "xpath": None,
                "content": None
            },
            form=Form(groups=[
                FormGroup(
                    name="Scrapper configuration",
                    fields=[
                        FormField(
                            id="xpath",
                            name="XPATH to data",
                            description="Type XPATH that points to data you would like to scrap.",
                            component=FormComponent(type="text", props={"label": "XPATH"})
                        ),
                        FormField(
                            id="content",
                            name="Content",
                            description="Type path to content",
                            component=FormComponent(type="dotPath", props={"label": "Content"})
                        )
                    ]
                )
            ]),
            manual='xpath_html_scrapper'

        ),
        metadata=MetaData(
            name='XPATH HTML Scrapper',
            desc='Scraps data from HTML content.',
            icon='html5',
            group=["Data processing"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="Returns scrapped data."),
                    "error": PortDoc(
                        desc="Returns plugin configuration when could not scrap data.")
                }
            )
        )
    )
