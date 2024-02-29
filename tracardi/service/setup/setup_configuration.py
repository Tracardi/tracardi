from tracardi.domain.configuration import Configuration

GITHUB_CONFIGURATION = '9740f93e-66b2-4016-8bf1-9c9ed14cb226'

available_configuration_list = {
    GITHUB_CONFIGURATION: Configuration(
        id=GITHUB_CONFIGURATION,
        name="Github configuration",
        config={
            "token": "",
            "repo_owner": "",
            "repo_name": ""
        },
        description="Repository on GitHub to store Tracardi workflows.",
        enabled=True,
        tags=['github']
    )
}
