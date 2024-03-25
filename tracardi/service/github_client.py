import json

from typing import Optional

from tracardi.exceptions.log_handler import get_logger
from tracardi.service.tracardi_http_client import HttpClient
import base64

from tracardi.service.utils.date import now_in_utc

logger = get_logger(__name__)

class GitHubClient:

    def __init__(self, token: str, repo_owner: str, repo_name: str):

        if not token or not token.strip():
            raise ValueError("Github token undefined. Please see GitHub connection configuration.")

        if not repo_owner or not repo_owner.strip():
            raise ValueError("Repository owner undefined. Please see GitHub connection configuration.")

        if not repo_name or not repo_name.strip():
            raise ValueError("Repository name undefined. Please see GitHub connection configuration.")

        self.repo_name = repo_name
        self.repo_owner = repo_owner
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
        }

    async def _get_file_sha(self, api_url) -> Optional[str]:
        """Get the SHA of the existing file, if it exists."""
        async with HttpClient(2) as client:
            async with client.get(url=api_url, headers=self.headers) as response:
                if response.status == 200:
                    return (await response.json())['sha']
                else:
                    return None

    async def send_file(self, file_path:str, content: str, message: str = None):

        if not file_path.strip():
            raise ValueError("File path can not be empty")

        # If updating an existing file, include the SHA in the request
        api_url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}'

        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

        data = {
            'message': message or f'Commit at {now_in_utc()}',
            'content': encoded_content,
        }
        sha  = await self._get_file_sha(api_url)
        if sha:
            data['sha'] = sha

        async with HttpClient(2, accept_status=[200,201]) as client:
            async with client.put(url=api_url, headers=self.headers, json=data) as response:
                if response.status in [200, 201]:
                    return await response.json()
                else:
                    raise ConnectionError(f"Failed to update or create the file. Status code: {response.status}, Response: {response.text}")

    async def list_files(self, path):

        """List all files and directories at the specified path in the repository."""

        api_url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{path}'

        async with HttpClient(2, accept_status=[200]) as client:
            async with client.get(url=api_url, headers=self.headers) as response:
                if response.status == 200:
                    contents = await response.json()
                    for content in contents:
                        yield content['type'].lower(), content['name'], content['path'], content['sha'], content['html_url']
                else:
                    raise ConnectionError(f"Failed to retrieve contents. Status code: {response.status}, Response: {response.text}")

    async def load_file(self, file_path):
        """Fetch the file content from the GitHub repository."""

        api_url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}'

        async with HttpClient(2, accept_status=[200]) as client:
            async with client.get(url=api_url, headers=self.headers) as response:
                if response.status == 200:
                    content = await response.json()
                    # The content is base64 encoded, so decode it
                    file_content = base64.b64decode(content['content']).decode('utf-8')
                    return json.loads(file_content)
                else:
                    raise ConnectionError(f"Failed to retrieve file. Status code: {response.status}, Response: {await response.text()}")
