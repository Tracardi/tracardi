from lxml import etree
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.runner import ActionRunner
from pydantic import field_validator
from tracardi.domain.profile import Profile
from tracardi.service.tracardi_http_client import HttpClient

from bs4 import BeautifulSoup

class Configuration(PluginConfig):
    html: str
    method: str = "get_text"

    @field_validator('html')
    @classmethod
    def html_must_not_be_empty(cls, value):
        if value.strip() == "":
            raise ValueError("HTML must not be empty.")
        return value

def validate(config: dict):
    return Configuration(**config)

class BeautifulSoupAction(ActionRunner):
    
    config: Configuration
    
    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        dot = self._get_dot_accessor(payload)
        
        try:
            
            html=dot[self.config.html]
            soup = BeautifulSoup(html, 'html.parser')
            
            text = ''
            
            if self.config.method == "get_text":
                text = soup.get_text()
            else:
                raise ValueError(f"Unsupported method: {self.config.method}")
            
            return Result(port='result', value={'text':text})

        except Exception as e:
            return Result(value={"message": str(e)}, port="error")  

def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=BeautifulSoupAction.__name__,
            inputs=["payload"],
            outputs=["result", "error"],
            version="1.0.4",  
            init={
                "html": "",  
            },
            form=Form(groups=[
                FormGroup(
                    name="Beautiful Soup configuration",
                    fields=[
                        FormField(
                            id="html",
                            name="HTML",
                            description="The HTML to be converted.",
                            component=FormComponent(type="dotPath", props={
                                "label": "HTML"
                            }),
                        ),
                        FormField(
                            id="method",
                            name="Method",
                            description="The BeautifulSoup method to apply to the HTML",
                            component=FormComponent(type="select", props={
                                "label": "Method",
                                "items": {
                                    "get_text": "get_text",
                                }
                            })
                        ),
                    ]),
            ]),
            license="MIT",
            author="Matt Cameron",
            manual="beautifulsoup",  

        ),
        metadata=MetaData(
            name='BeautifulSoup',
            desc='Converts HTML to text.',
            icon='BeautifulSoup',
            group=['Data Processing'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="Returns response from Sitemap service."),
                    "error": PortDoc(desc="Returns error message if plugin fails.")
                }
            )
        )
    )

