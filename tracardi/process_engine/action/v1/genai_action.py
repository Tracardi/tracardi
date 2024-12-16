from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.domain import resource as resource_db
from pydantic import field_validator
from tracardi.service.tracardi_http_client import HttpClient
from tracardi.domain.resources.genai import genAIResourceCredentials
from tracardi.domain.named_entity import NamedEntity
from langchain.prompts import PromptTemplate
from base64 import b64encode
from typing import Literal

class Configuration(PluginConfig):
    resource: NamedEntity
    provider: Literal["cloudflare", "ollama"]
    model: str
    prompt_template: str
    max_tokens: str = 50
    temperature: str = 0.7

    @field_validator('prompt_template')
    @classmethod
    def prompt_template_must_not_be_empty(cls, value):
        if value.strip() == "":
            raise ValueError("Prompt template must not be empty.")
        return value

def validate(config: dict):
    return Configuration(**config)

class GenAIAction(ActionRunner):
    
    config: Configuration
    credentials: genAIResourceCredentials
    
    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.resource.id)
        self.config = config
        self.credentials = resource.credentials.get_credentials(self)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        prompt_input = dot[self.config.prompt_template]
        
        try:
            # Use langchain to format the prompt dynamically
            prompt_template = PromptTemplate(input_variables=["prompt"], template=prompt_input)
            formatted_prompt = prompt_template.format(prompt=prompt_input)

            if self.config.provider == "cloudflare":
                response_text = await self._call_cloudflare(formatted_prompt)
            elif self.config.provider == "ollama":
                response_text = await self._call_ollama(formatted_prompt)
            else:
                raise ValueError("Unsupported GenAI provider.")
            
            return Result(port='result', value={'text': response_text,'text_base64' :b64encode(response_text.encode("utf-8"))})

        except Exception as e:
            return Result(value={"message": str(e)}, port="error") 

    async def _call_cloudflare(self, prompt_input: str) -> str:
        api_key = self.credentials['api_key']
        api_url = self.credentials['api_url']
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        
        payload = {
            "prompt": prompt_input,
            "max_tokens": int(self.config.max_tokens),
            "temperature": float(self.config.temperature)
        }

        # Use HttpClient to send the request
        async with HttpClient(3, [200], headers=headers) as client:
            async with client.post((api_url+self.config.model), json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("result", {}).get("response", "").strip()
                else:
                    raise Exception(f"Cloudflare AI API error: {response.status}, {await response.text()}")

    async def _call_ollama(self, prompt_input: str) -> str:
        api_url = self.credentials['api_url']
        
        payload = {
            "model": self.config.model,
            "prompt": prompt_input,
            "stream": False,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }

        # Use HttpClient to send the request
        async with HttpClient(3, [200], headers={}) as client:
            async with client.post(api_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("response", "").strip()
                else:
                    raise Exception(f"Ollama API error: {response.status}")

def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=GenAIAction.__name__,
            inputs=["payload"],
            outputs=["result", "error"],
            version="1.0.4",
            init={
                "resource": "",
                "provider": "cloudflare",
                "model": "",
                "prompt_template": "",
                "max_tokens": "50",
                "temperature": "0.7"
            },
            form=Form(groups=[
                FormGroup(
                    name="genAI Configuration",
                    fields=[
                        FormField(
                            id="resource",
                            name="genAI Resource",
                            description="genAI Resource",
                            component=FormComponent(type="resource", props={
                                "label": "Resource",
                                "tag": "genAI"
                            })
                        ),
                        FormField(
                            id="provider",
                            name="Provider",
                            description="Select the GenAI provider.",
                            component=FormComponent(type="select", props={
                                "label": "Provider",
                                "items": {
                                    "cloudflare": "Cloudflare AI",
                                    "ollama": "Ollama AI",
                                }
                            }),
                        ),
                        FormField(
                            id="model",
                            name="Model",
                            description="Specify the model to use.",
                            component=FormComponent(type="text", props={
                                "label": "Model"
                            })
                        ), 
                        FormField(
                            id="prompt_template",
                            name="Prompt Template",
                            description="Template for generating text.",
                            component=FormComponent(type="dotPath", props={
                                "label": "Prompt Template"
                            }),
                        ),
                        FormField(
                            id="max_tokens",
                            name="Max Tokens",
                            description="Maximum number of tokens to generate.",
                            component=FormComponent(type="text", props={
                                "label": "Max Tokens",
                                "default": "50"
                            })
                        ),
                        FormField(
                            id="temperature",
                            name="Temperature",
                            description="Controls the randomness of the output.",
                            component=FormComponent(type="text", props={
                                "label": "Temperature",
                                "default": "0.7"
                            })
                        ),
                    ]),
            ]),
            license="MIT",
            author="Matt Cameron",
            manual="genai-action",
        ),
        metadata=MetaData(
            name='GenAI',
            desc='Generates text based on a prompt using GenAI providers.',
            icon='GenAI',
            group=['AI', 'Data Processing'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="Generated text from the AI model."),
                    "error": PortDoc(desc="Error message if plugin fails.")
                }
            )
        )
    )