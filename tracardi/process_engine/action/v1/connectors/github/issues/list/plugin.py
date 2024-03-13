from tracardi.domain.resources.github import GitHub
from tracardi.process_engine.action.v1.connectors.github.forms.GitHubFormFields import form_field_github_resource, \
    form_field_github_owner, form_field_github_repo, form_field_github_timeout
from tracardi.process_engine.action.v1.connectors.github.github_client import GitHubClient
from tracardi.process_engine.action.v1.connectors.github.model.config import GitHubBaseConfiguration, \
    init_github_base_configuration
from tracardi.service.plugin.domain.register import Plugin, Spec, Form, MetaData, FormGroup, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.domain import resource as resource_db


def validate(config: dict):
    return GitHubBaseConfiguration(**config)


class GitHubListIssuesAction(ActionRunner):
    config: GitHubBaseConfiguration
    credentials: GitHub

    async def set_up(self, init):
        self.config = validate(init)
        resource = await resource_db.load(self.config.resource.id)
        self.credentials = resource.credentials.get_credentials(self, output=GitHub)

    async def run(self, payload: dict, in_edge=None):
        client = GitHubClient(self.credentials, self.config, self.console)
        response = await client.list_issues()

        if response['status'] in [200, 201, 202, 203, 204]:
            return Result(port="response", value=response)
        else:
            return Result(port="error", value=response)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=GitHubListIssuesAction.__name__,
            inputs=['payload'],
            outputs=['payload', 'error'],
            version='0.7.4',
            license='MIT',
            author='knittl',
            init={
                **init_github_base_configuration()
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        form_field_github_resource(),
                        form_field_github_owner(),
                        form_field_github_repo(),
                        form_field_github_timeout(),
                    ],
                ),
            ]),
        ),
        metadata=MetaData(
            name='List Issues',
            desc='Lists GitHub issues',
            group=['GitHub'],
            tags=['github'],
            icon='github',
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes the payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns the issues data.")
                },
            ),
        ),
    )
