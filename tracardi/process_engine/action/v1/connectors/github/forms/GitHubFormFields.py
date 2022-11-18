from tracardi.service.plugin.domain.register import FormField, FormComponent


def form_field_github_timeout():
    return FormField(
        id='timeout',
        name='Timeout',
        description='Timeout for requests in seconds.',
        component=FormComponent(type='text'),
    )


def form_field_github_resource():
    return FormField(
        id='resource',
        name='Resource',
        description='Select your GitHub resource.',
        component=FormComponent(
            type='resource',
            props={'label': 'GitHub Resource', 'tag': 'github'})
    )


def form_field_github_owner():
    return FormField(
        id='owner',
        name='Owner',
        description='Owner of the repository. Can be a user or an organization.',
        component=FormComponent(type='text'),
    )


def form_field_github_repo():
    return FormField(
        id='repo',
        name='Repo',
        description='Name of the repository.',
        component=FormComponent(type='text'),
    )
