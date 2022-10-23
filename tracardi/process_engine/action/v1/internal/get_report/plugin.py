from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.report_manager import ReportManager, ReportManagerException
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.plugin_endpoint import PluginEndpoint
import json
from tracardi.domain.entity import NullableEntity


def validate(config: dict) -> Config:
    return Config(**config)


class Endpoint(PluginEndpoint):

    @staticmethod
    async def get_params(config: dict) -> dict:
        config = NullableEntity(**config)
        if not config.id:
            return {}

        try:
            manager = await ReportManager.build(config.id)
            return {key: f"<{key.replace('_', '-')}>" for key in manager.get_expected_fields()}

        except ReportManagerException:
            return {}


class GetReportAction(ActionRunner):

    manager: ReportManager
    config: Config

    async def set_up(self, init):
        config = validate(init)
        manager = await ReportManager.build(config.report_config.report.id)

        self.config = config
        self.manager = manager

    async def run(self, payload: dict, in_edge=None):
        dot = self._get_dot_accessor(payload)
        traverser = DictTraverser(dot)
        try:
            result = await self.manager.get_report(traverser.reshape(self.config.report_config.params))
            return Result(port="result", value=result)

        except ReportManagerException as e:
            return Result(port="error", value={"detail": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='GetReportAction',
            inputs=["payload"],
            outputs=["result", "error"],
            version='0.7.2',
            license="MIT",
            author="Dawid Kruk",
            manual="get_report_action",
            init={
                "report_config": {
                    "report": {
                        "id": "",
                        "name": ""
                    },
                    "params": "{}"
                }
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Report plugin configuration",
                        fields=[
                            FormField(
                                id="report_config",
                                name="Report configuration",
                                description="Please select report and provide configuration. You can use dot paths as "
                                            "values.",
                                component=FormComponent(type="reportConfig", props={
                                    "endpoint": {
                                        "url": Endpoint.url(__name__, "get_params"),
                                        "method": "post"
                                    }
                                })
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Load report data',
            desc='Loads given report\'s results into payload.',
            icon='report',
            group=["Input/Output"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="This port returns results of selected report on success."),
                    "error": PortDoc(desc="This port returns error info")
                }
            )
        )
    )
