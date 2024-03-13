from tracardi.domain.resources.github import GitHub
from tracardi.process_engine.action.v1.connectors.github.forms.GitHubFormFields import form_field_github_repo, \
    form_field_github_owner, form_field_github_resource, form_field_github_timeout
from tracardi.process_engine.action.v1.connectors.github.github_client import GitHubClient
from tracardi.process_engine.action.v1.connectors.github.model.config import GetIssueConfiguration, \
    init_github_base_configuration
from tracardi.service.plugin.domain.register import Plugin, Spec, Form, MetaData, FormComponent, FormField, FormGroup, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.domain import resource as resource_db


def validate(config: dict):
    return GetIssueConfiguration(**config)


class GitHubGetIssueAction(ActionRunner):
    config: GetIssueConfiguration
    credentials: GitHub

    async def set_up(self, init):
        self.config = validate(init)
        resource = await resource_db.load(self.config.resource.id)
        self.credentials = resource.credentials.get_credentials(self, output=GitHub)

    async def run(self, payload: dict, in_edge=None):
        dot = self._get_dot_accessor(payload)
        issue_id = dot[self.config.issue_id]

        client = GitHubClient(self.credentials, self.config, self.console)
        response = await client.get_issue(issue_id)

        if response['status'] in [200, 201, 202, 203, 204]:
            return Result(port="response", value=response)
        else:
            return Result(port="error", value=response)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=GitHubGetIssueAction.__name__,
            inputs=['payload'],
            outputs=['payload', 'error'],
            version='0.7.4',
            license='MIT',
            author='knittl',
            init={
                **init_github_base_configuration(),
                'issue_id': '',
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        form_field_github_resource(),
                        form_field_github_owner(),
                        form_field_github_repo(),
                        FormField(
                            id='issue_id',
                            name='Issue ID',
                            description='ID of the GitHub issue.',
                            component=FormComponent(type='dotPath', props={'defaultSourceValue': 'event'}),
                        ),
                        form_field_github_timeout(),
                    ],
                ),
            ]),
        ),
        metadata=MetaData(
            name='Get Issue',
            desc='Get single GitHub issue details',
            group=['GitHub'],
            tags=['github'],
            icon='github',
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes the payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns the issue data.")
                },
            ),
        ),
    )
