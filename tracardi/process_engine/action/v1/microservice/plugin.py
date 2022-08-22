from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner


def validate(config: dict):
    # todo remotly validate
    print(config)


class MicroserviceAction(ActionRunner):

    def __init__(self, **kwargs):
        pass

    async def run(self, payload: dict, in_edge=None):
        return None


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='MicroserviceAction',
            inputs=["payload"],
            outputs=["payload", "error"],
            version='0.7.2',
            license="MIT",
            author="Risto Kowaczewski",
            microservice={
                "resource": {
                    "name": "",
                    "id": "",
                    "current": {
                        "url": "",
                        "token": "",
                        "service": {
                            "name": "",
                            "id": ""
                        }
                    },
                },

                "plugin": {
                    "name": "",
                    "id": ""
                }
            },
            init={

            }
        ),
        metadata=MetaData(
            name='Microservice',
            desc='Runs remote microservice plugin.',
            icon='plugin',
            group=["Operations"],
            remote=True,
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns microservice response.")
                }
            )
        )
    )
