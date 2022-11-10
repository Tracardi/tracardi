from tracardi.service.plugin.domain.register import Plugin, Spec, Form, FormGroup, FormField, FormComponent, MetaData, \
    Documentation, PortDoc


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.connectors.google.analytics.plugin',
            className='GoogleAnalyticsEventTrackerAction',
            inputs=['payload'],
            outputs=['response', 'error'],
            verions="0.7.3",
            license='MIT',
            author='Mateusz Zitaruk',
            init={
                'source': {'id': '', 'name': ''},
                'category': '',
                'action': '',
                'label': '',
                'value': 0,
            },
            manual='google_event_tracker_action',
            form=Form(
                groups=[
                    FormGroup(
                        name="Google analytics event tracker configuration",
                        fields=[
                            FormField(
                                id='source',
                                name='Google Universal Analytics Tracking ID',
                                description='Select Google Universal Analytics resource. Credentials from selected resource '
                                            'will be used to authorize your account.',
                                component=FormComponent(type='resource', props={
                                    'label': 'resource',
                                    'tag': 'google'
                                })
                            ),
                            FormField(
                                id='category',
                                name='Event category',
                                description='Please type data you would like to use as your event category name.',
                                component=FormComponent(type='dotPath',
                                                        props={
                                                            'label': 'Payload field',
                                                            'defaultSourceValue': 'event'}
                                                        )
                            ),
                            FormField(
                                id='action',
                                name='Action name',
                                description='Please type data you would like to use as your event action name.',
                                component=FormComponent(type='dotPath',
                                                        props={
                                                            'label': 'Payload field',
                                                            'defaultSourceValue': 'event'})
                            ),
                            FormField(
                                id='label',
                                name='Event label',
                                description='Please type data you would like to use as your event label name.',
                                component=FormComponent(type='dotPath', props={
                                                            'label': 'Payload field',
                                                            'defaultSourceValue': 'event'})
                            ),
                            FormField(
                                id='value',
                                name='Event value',
                                description='Please type data you would like to use as your event value.',
                                component=FormComponent(type='dotPath', props={
                                                            'label': 'Payload field',
                                                            'defaultSourceValue': 'event'})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Google UA events',
            desc='Send your customized event to Google Universal Analytics event tracker',
            brand='Google',
            icon='google',
            group=['Google'],
            documentation=Documentation(
                inputs={
                    'payload': PortDoc(desc='This port takes payload object.')
                },
                outputs={
                    'response': PortDoc(desc='This port returns response status and content.'),
                    'error': PortDoc(desc='This port returns error if request will fail')
                }
            )
        )
    )
