from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc

from password_generator import PasswordGenerator


class PasswordGeneratorAction(ActionRunner):
    def __int__(self, **kwargs):
        pass

    async def run(self, payload: dict, in_edge=None) -> Result:
        pgo = PasswordGenerator()

        self.pgo.minlen = 10
        self.pgo.minuchars = 5
        self.pgo.minlchars = 8
        self.pgo.minschars = 5
        password = pgo.generate()
        return Result(port="payload", value={"password": password})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.password.generator.action',
            className='PasswordGeneratorAction',
            inputs=[],
            outputs=["result"],
            version='0.7.2',
            license="MIT",
            author="Mateusz Zitaruk",
            manual="password_generator"
        )
    )
