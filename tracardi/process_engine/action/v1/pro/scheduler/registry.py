from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.pro.scheduler.plugin',
            className='SchedulerPlugin',
            inputs=["payload"],
            outputs=['response', 'error'],
            version='0.7.1',
            license="Tracardi Pro License",
            author="Risto Kowaczewski"
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
