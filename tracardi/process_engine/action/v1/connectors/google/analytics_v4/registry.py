from tracardi.service.plugin.domain.register import Plugin, Spec, Form, FormGroup, FormField, FormComponent, MetaData, \
    Documentation, PortDoc


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.connectors.google.analytics_v4.plugin',
            className='GoogleAnalyticsV4EventTrackerAction',
            inputs=['payload'],
            outputs=['response', 'error'],
            version='0.7.3',
            license='MIT',
            author='Mateusz Zitaruk',
            init={
                'source': {'id': '', 'name': ''},
                'name': '',
                'params': ''
            },
            manual='google_v4_event_tracker_action',
            form=Form(
                groups=[
                    FormGroup(
                        name='Google analytics event tracker configuration',
                        fields=[
                            FormField(
                                id='source',
                                name='Google Analytics 4 Api Key and Measurement ID',
                                description='Select Google Analytics 4 resource. Credentials from selected resource '
                                            'will be used to authorize your account.',
                                component=FormComponent(type='resource', props={
                                    'label': 'resource',
                                    'tag': 'google'
                                })
                            ),
                            FormField(
                                id='name',
                                name='Event name',
                                description='Please type name you would like to use as your event name.',
                                component=FormComponent(type='dotPath',
                                                        props={
                                                            'label': 'Payload field',
                                                            'defaultSourceValue': 'event'
                                                        })
                            ),
                            FormField(
                                id='params',
                                name='Event parameters',
                                description='Please type data you would like to use as your event parameters.',
                                component=FormComponent(type='dotPath',
                                                        props={
                                                            'label': 'Payload field',
                                                            'defaultSourceValue': 'event'
                                                        })
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Google Analytics 4 events',
            desc='Send your customized event to Google Analytics 4 event tracker',
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