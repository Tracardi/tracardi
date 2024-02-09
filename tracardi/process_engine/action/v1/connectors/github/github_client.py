import aiohttp

from tracardi.domain.resources.github import GitHub
from tracardi.process_engine.action.v1.connectors.github.model.config import GitHubBaseConfiguration
from tracardi.service.tracardi_http_client import HttpClient


def _normalize_issue_id(issue_id):
    return issue_id.lstrip('#')


async def _transform_response(response):
    return {
        'status': response.status,
        'body': await response.json()
    }


class GitHubClient:
    resource: GitHub
    config: GitHubBaseConfiguration

    def __init__(self, resource, config, console):
        self.resource = resource
        self.config = config
        self.console = console

    async def list_issues(self):
        url = f'{self._get_repo_url()}/issues'
        self.console.log(f'Getting issues from {url}')

        async with await self._new_client() as client:
            async with await self._http_get(client, url) as response:
                return await _transform_response(response)

    async def list_files(self, path):
        url = f'{self._get_repo_url()}/contents/{path}'
        async with await self._new_client() as client:
            async with await self._http_get(client, url) as response:
                return await _transform_response(response)

    async def list_file_commits(self, filepath):
        url = f"{self._get_repo_url()}/commits?path={filepath}"
        async with await self._new_client() as client:
            async with await self._http_get(client, url) as response:
                return await _transform_response(response)

    async def get_issue(self, issue_id):
        issue_id = _normalize_issue_id(issue_id)
        url = f'{self._get_repo_url()}/issues/{issue_id}'
        self.console.log(f'Getting issue details from {url}')

        async with await self._new_client() as client:
            async with await self._http_get(client, url) as response:
                return await _transform_response(response)

    async def _new_client(self):
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        return HttpClient(2, 200, timeout=timeout)

    def _get_repo_url(self):
        return f'{self.resource.api_url}/repos/{self.config.owner}/{self.config.repo}'

    async def _http_get(self, client, url):
        return client.request(
            method='GET',
            url=url,
            headers=self._make_headers(),
        )

    def _auth_header(self):
        pat = self.resource.personal_access_token
        if not pat:
            return {}
        return {'authorization': 'Bearer ' + pat}

    def _accept_header(self):
        return {'accept': 'application/vnd.github+json'}

    def _make_headers(self):
        return self._accept_header() | self._auth_header()
