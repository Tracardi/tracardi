import json

from tracardi.service.storage.driver import storage
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from .model.model import AwsSqsConfiguration, AwsIamAuth, MessageAttributes
from aiobotocore.session import get_session


def validate(config: dict):
    return AwsSqsConfiguration(**config)


class AwsSqsAction(ActionRunner):

    credentials: AwsIamAuth
    aws_config: AwsSqsConfiguration

    async def set_up(self, init):
        config = validate(init)
        resource = await storage.driver.resource.load(config.source.id)

        self.aws_config = config
        self.credentials = resource.credentials.get_credentials(self, output=AwsIamAuth)

    async def run(self, payload: dict, in_edge=None) -> Result:
        try:

            session = get_session()
            async with session.create_client('sqs', region_name=self.aws_config.region_name,
                                             aws_secret_access_key=self.credentials.aws_secret_access_key,
                                             aws_access_key_id=self.credentials.aws_access_key_id
                                             ) as client:

                if isinstance(self.aws_config.message_attributes, str) and len(self.aws_config.message_attributes):
                    attributes = MessageAttributes(json.loads(self.aws_config.message_attributes))
                    attributes = attributes.dict()
                    result = await client.send_message(QueueUrl=self.aws_config.queue_url,
                                                       MessageBody=self.aws_config.message.content,
                                                       DelaySeconds=self.aws_config.delay_seconds,
                                                       MessageAttributes=attributes)
                else:
                    result = await client.send_message(QueueUrl=self.aws_config.queue_url,
                                                       MessageBody=self.aws_config.message.content,
                                                       DelaySeconds=self.aws_config.delay_seconds)

                status = result.get("ResponseMetadata", {}).get("HTTPStatusCode")  # response from server

                return Result(port="result", value={
                        "status": status,
                        "result": result
                    })

        except Exception as e:
            self.console.error(str(e))
            return Result(port="error", value={"payload": payload, "error": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='AwsSqsAction',
            inputs=["payload"],
            outputs=["result", "error"],
            version='0.7.0',
            license="MIT",
            author="Bart Dobrosielski, Risto Kowaczewski",
        ),
        metadata=MetaData(
            name='Simple queue SQS',
            desc='Sends a message to the Amazon AWS SQS queue',
            icon='aws',
            tags=['aws', 'queue'],
            group=["Amazon Web Services (AWS)"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="Returns result."),
                    "error": PortDoc(desc="Gets triggered if an error occurs.")
                }
            ),
            pro=True
        )
    )
