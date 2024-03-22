import jwt
import ssl
import aiohttp
import certifi

from datetime import datetime as date

from tracardi.domain.resources.ghost import GhostResourceCredentials
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.domain import resource as resource_db
from tracardi.service.tracardi_http_client import HttpClient
from tracardi.domain.profile import Profile
from .model.config import Configuration


def validate(config):
    print(config)
    return Configuration(**config)


class GhostAction(ActionRunner):
    credentials: GhostResourceCredentials
    config: Configuration

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.resource.id)
        self.config = config
        self.credentials = resource.credentials.get_credentials(self, output=GhostResourceCredentials)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        profile = Profile(**dot.profile)

        try:
            _id, secret = self.credentials.api_key.split(':')
        except Exception:
            message = f"Could not split API key into id and secret. Is the API_KEY ok. It should have : char in its body. Please check the resource configuration."
            self.console.error(message)
            return Result(port='error', value={"message": message})

        iat = int(date.now().timestamp())
        header = {'alg': 'HS256', 'typ': 'JWT', 'kid': _id}
        payload = {
            'iat': iat,
            'exp': iat + 5 * 60,
            'aud': '/admin/'
        }

        try:
            token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)
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
            labels.sort()

            profile_segments = profile.segments
            profile_segments.sort()

            if labels == profile_segments:
                return Result(port='result', value={'labels': labels})
            labels = profile.segments

            async with HttpClient(
                    self.node.on_connection_error_repeat,
                    200,
                    headers={'Authorization': 'Ghost {}'.format(token)},
                    connector=aiohttp.TCPConnector(ssl=ssl_context)
            ) as client:
                async with client.put(
                        url=self.credentials.api_url + '/ghost/api/admin/members/' + ghost_id,
                        json={'members': [{'labels': labels}]}
                ) as response:
                    result = await response.json()
                    if response.status == 200:
                        return Result(port='result', value={'labels': labels, "response": result})
                    return Result(port='error', value={"message": result})

        except Exception as e:
            message = str(e)
            self.console.error(message)
            return Result(value={"message": message}, port="error")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=GhostAction.__name__,
            inputs=["payload"],
            outputs=["result", "error"],
            version='0.9.0',
            init={
                'resource': {'id': '', 'name': ''},
                "uuid": ""
            },
            form=Form(groups=[
                FormGroup(
                    name="Ghost configuration",
                    fields=[
                        FormField(
                            id="resource",
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
                        )
                    ])
            ]),
            license="MIT",
            author="Matt Cameron",
            manual="ghost_labeler"
        ),
        metadata=MetaData(
            name='Ghost Labeler',
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
