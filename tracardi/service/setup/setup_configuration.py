from tracardi.domain.configuration import Configuration

GITHUB_CONFIGURATION = '9740f93e-66b2-4016-8bf1-9c9ed14cb226'
SAVE_LOGS_ENV_CONFIGURATION = 'SAVE_LOGS'

available_configuration_list = {
    GITHUB_CONFIGURATION: Configuration(
        id=GITHUB_CONFIGURATION,
        name="Github configuration",
        config={
            "token": "",
            "repo_owner": "",
            "repo_name": ""
        },
        description="Repository on GitHub to store system workflows.",
        enabled=True,
        tags=['github'],
        # cluster_wide_value = True
    ),
    SAVE_LOGS_ENV_CONFIGURATION: Configuration(
        id=SAVE_LOGS_ENV_CONFIGURATION,
        name=f"{SAVE_LOGS_ENV_CONFIGURATION} Env Variable",
        config="yes",  # default value
        description="When set to yes all logs will be saved in system log (Experimental).",
        enabled=True,
        tags=['env', 'setting'],
        # cluster_wide_value = True
    ),
}
