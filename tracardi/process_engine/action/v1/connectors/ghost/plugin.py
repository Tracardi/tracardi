from tracardi.domain.resources.ghost import GhostResourceCredentials
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver.elastic import resource as resource_db
from .model.config import Configuration

import jwt
from datetime import datetime as date

import ssl
import aiohttp
import certifi
from tracardi.service.tracardi_http_client import HttpClient


def validate(config):
    return Configuration(**config)


class GhostAction(ActionRunner):
    credentials: GhostResourceCredentials
    config: Configuration

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)
        self.config = config
        self.credentials = resource.credentials.get_credentials(self, output=GhostResourceCredentials)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)

        _id, secret = self.credentials.api_key.split(':')
        iat = int(date.now().timestamp())
        header = {'alg': 'HS256', 'typ': 'JWT', 'kid': _id}
        payload = {
            'iat': iat,
            'exp': iat + 5 * 60,
            'aud': '/admin/'
        }
        token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)

        try:
            ssl_context = ssl.create_default_context(cafile=certifi.where())

            async with HttpClient(
                    1,
                    200,
                    headers={'Authorization': 'Ghost {}'.format(token)},
                    connector=aiohttp.TCPConnector(ssl=ssl_context)
            ) as client:
                async with client.get(
                    url=self.credentials.api_url + '/ghost/api/admin/members/?filter=uuid:' + dot[self.config.uuid]
                ) as response:
                    member = await response.json()

            ghost_id = member['members'][0]['id']
            labels = list(map(lambda x: x['name'], list(member['members'][0]['labels'])))
    
            if ( dot[self.config.label_add] not in labels and dot[self.config.label_add]!='' ) or \
                ( dot[self.config.label_remove] in labels and dot[self.config.label_remove]!='' ) :
                if dot[self.config.label_add] not in labels and dot[self.config.label_add]!='':
                    labels.append(dot[self.config.label_add])
                if dot[self.config.label_remove] in labels and dot[self.config.label_remove]!='':
                    labels.remove(dot[self.config.label_remove])

                async with HttpClient(
                        1,
                        200,
                        headers={'Authorization': 'Ghost {}'.format(token)},
                        connector=aiohttp.TCPConnector(ssl=ssl_context)
                ) as client:
                    async with client.put(
                        url=self.credentials.api_url + '/ghost/api/admin/members/' + ghost_id,
                        json={'members': [{'labels': labels}]}
                    ) as response:
                        response = await response.json()

            return Result(port='response', value=payload)
        except Exception as e:
            return Result(value={"message": str(e)}, port="error")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=GhostAction.__name__,
            inputs=["payload"],
            outputs=["result", "error"],
            version='0.8.2',
            init={
                "uuid": "",
                "label_add": "",
                "label_remove": ""
            },
            form=Form(groups=[
                FormGroup(
                    name="Ghost configuration",
                    fields=[
                        FormField(
                            id="source",
                            name="Ghost Resource",
                            description="Ghost Resource",
                            component=FormComponent(type="resource", props={
                                "label": "Resource",
                                "tag": "ghost"
                            })
                        ),
                        FormField(
                            id="uuid",
                            name="UUID",
                            description="Ghost member UUID.",
                            component=FormComponent(type="dotPath", props={
                                "label": "UUID",
                                "defaultSourceValue": "payload"
                            })
                        ),
                        FormField(
                            id="label_add",
                            name="Label_Add",
                            description="Label to be added to the Ghost member.",
                            component=FormComponent(type="dotPath", props={
                                "label": "Label_Add",
                                "defaultSourceValue": "payload"
                            })
                        ),
                        FormField(
                            id="label_remove",
                            name="Label_Remove",
                            description="Label to be removed from the Ghost member.",
                            component=FormComponent(type="dotPath", props={
                                "label": "Label_Remove",
                                "defaultSourceValue": "payload"
                            })
                        )
                    ])
            ]),
            license="MIT + CC",
            author="Matt Cameron",
            manual="ghost"
        ),
        metadata=MetaData(
            name='Ghost',
            desc='Adds labels to a Ghost member.',
            icon='ghost',
            group=["Connectors"],
            purpose=['collection'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="Returns response from Ghost service."),
                    "error": PortDoc(desc="Returns error message if plugin fails.")
                }
            )
        )
    )
