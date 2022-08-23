from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, MicroserviceConfig
from tracardi.service.plugin.runner import ActionRunner


class MicroserviceAction(ActionRunner):

    def __init__(self, **kwargs):
        # todo do not remotely validate. Validate during exec.
        pass

    async def run(self, payload: dict, in_edge=None):
        # todo remotely run
        return None


# todo do not need register as this is not registered.
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
            icon='cloud',
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
