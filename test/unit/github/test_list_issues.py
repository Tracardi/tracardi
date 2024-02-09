from pprint import pprint

import pytest

from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.resources.github import GitHub
from tracardi.process_engine.action.v1.connectors.github.github_client import GitHubClient
from tracardi.process_engine.action.v1.connectors.github.model.config import GitHubBaseConfiguration
from tracardi.service.plugin.domain.console import Console

token = "xxx"

@pytest.mark.asyncio
async def test_list_issues_returns_expected_response():
    # Arrange
    resource = GitHub(api_url="https://api.github.com",
                      personal_access_token=token)
    config = GitHubBaseConfiguration(
        resource=NamedEntity(id="1", name="resource"),
        owner="atompie",
        repo="test")
    console = Console("1", "s")
    client = GitHubClient(resource, config, console)

    # Act
    response = await client.list_issues()
    print(response)
    print(console)

@pytest.mark.asyncio
async def test_listing_files():
    # Arrange
    resource = GitHub(api_url="https://api.github.com",
                      personal_access_token=token)
    config = GitHubBaseConfiguration(
        resource=NamedEntity(id="1", name="resource"),
        owner="atompie",
        repo="test")
    console = Console("1", "s")
    client = GitHubClient(resource, config, console)

    # Act
    response = await client.list_files(path="")
    pprint(response)
    print(console)


@pytest.mark.asyncio
async def test_list_file_commits():
    # Arrange
    resource = GitHub(api_url="https://api.github.com",
                      personal_access_token=token)
    config = GitHubBaseConfiguration(
        resource=NamedEntity(id="1", name="resource"),
        owner="atompie",
        repo="test")
    console = Console("1", "s")
    client = GitHubClient(resource, config, console)

    # Act
    response = await client.list_file_commits(filepath="test.txt")
    pprint(response)
    print(console)