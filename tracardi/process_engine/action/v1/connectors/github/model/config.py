import re

from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig
from pydantic import field_validator


def _is_valid_github_owner_name(value: str):
    regex = re.compile('^[a-zA-Z0-9]+$')
    for part in value.split('-'):
        if not regex.match(part):
            return False
    return True


def _is_valid_github_repo_name(value: str):
    regex = re.compile('^[a-zA-Z0-9_-]+$')
    return regex.match(value)


def _is_non_empty(value: str):
    return bool(value)


def _validate(value: str, fn, error_message):
    if not fn(value):
        raise ValueError(error_message)
    return value


def init_github_base_configuration():
    return {
        'resource': {
            'id': '',
            'name': ''
        },
        'timeout': 10,
        'owner': '',
        'repo': '',
    }


class GitHubBaseConfiguration(PluginConfig):
    resource: NamedEntity
    owner: str
    repo: str
    timeout: int = 10

    @field_validator("owner")
    @classmethod
    def owner_must_be_valid(cls, value):
        return _validate(value, _is_valid_github_owner_name, 'Repository owner must be valid')

    @field_validator("repo")
    @classmethod
    def repo_must_be_valid(cls, value):
        return _validate(value, _is_valid_github_repo_name, 'Repository name must be valid')


class GetIssueConfiguration(GitHubBaseConfiguration):
    issue_id: str

    @field_validator("issue_id")
    @classmethod
    def owner_must_be_valid(cls, value):
        return _validate(value, _is_non_empty, 'Issue ID must be specified')
