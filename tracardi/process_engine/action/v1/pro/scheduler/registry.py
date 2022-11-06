from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.pro.scheduler.plugin',
            className='SchedulerPlugin',
            inputs=["payload"],
            outputs=['response', 'error'],
            version='0.7.3',
            license="Tracardi Pro License",
            author="Risto Kowaczewski",
            init={
                "resource": {
                    "id": "",
                    "name": ""
                },
                "source": {
                    "id": "@current-source",
                    "name": "@current-source"
                },
                "event_type": "",
                "properties": "{}",
                "postpone": 60
            },
            form=Form(groups=[
                FormGroup(
                    name="Scheduled event settings",
                    description="This action will schedule event with defined event type and properties. "
                                "Event will have the same profile as current event.",
                    fields=[
                        FormField(
                            id="resource",
                            name="Scheduler service",
                            description="Please select your scheduler service.",
                            component=FormComponent(type="resource", props={"label": "Service", "tag": "schedule"})
                        ),
                        FormField(
                            id="postpone",
                            name="Event delay in seconds",
                            component=FormComponent(type="text", props={
                                "label": "delay in seconds"
                            })
                        ),
                    ]
                ),
                FormGroup(
                    name="Event settings",
                    fields=[
                        FormField(
                            id="source",
                            name="Inbound traffic",
                            description="Please select open inbound event source through which scheduler will send "
                                        "the event. If you do not know which one to choose than the save option is "
                                        "@current-source. It will use the current event inbound traffic source.",
                            component=FormComponent(type="autocomplete", props={
                                "label": "Event source",
                                "endpoint": {
                                    "url": "/event-sources/entity?add_current=true",
                                    "method": "get"
                                }
                            })
                        ),
                        FormField(
                            id="event_type",
                            name="Event type",
                            description="Type event type",
                            component=FormComponent(type="text", props={"label": "Event type"})
                        ),
                        FormField(
                            id="properties",
                            name="Properties",
                            description="Type event properties. Properties can be referenced by dot notation. e.g. "
                                        "profile@id.",
                            component=FormComponent(type="json", props={"label": "Event properties"})
                        )
                    ]
                )
            ]
            )
        ),
        metadata=MetaData(
            name='Schedule event',
            desc='This plugin schedules events',
            icon='calendar',
            group=["Time"],
            tags=["pro", "scheduler", "postpone", "delay", "event"],
            pro=True,
        )
    )
