from tracardi.service.storage.elastic.interface.collector.load.profile import load_profile
from uuid import uuid4

from tracardi.domain.event_metadata import EventMetadata
from tracardi.domain.time import EventTime
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.configuration import Configuration
from typing import Optional
from tracardi.domain.event import Event
from tracardi.domain.session import Session, SessionMetadata, SessionTime
from tracardi.domain.entity import Entity


def validate(config: dict):
    return Configuration(**config)


class StartSegmentationAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, *args, **kwargs) -> Optional[Result]:

        if self.debug is True:
            event = Event(
                id=str(uuid4()),
                type="@segmentation",
                name="Segmentation",
                source=Entity(id=str(uuid4())),
                metadata=EventMetadata(time=EventTime(), debug=self.debug)
            )

            session = Session(
                id=str(uuid4()),
                metadata=SessionMetadata(time=SessionTime())
            )

            if not self.config.profile_id:
                msg = "Can not run segmentation without profile. "
                if self.debug:
                    msg += "Set profile id in the configuration form. "
                self.console.error(msg)
                return None

            profile = await load_profile(self.config.profile_id)

            if profile is None:
                msg = "Loaded profile is empty. Can not run segmentation without profile. "
                self.console.error(msg)
                return None

            self.session.replace(session)
            self.profile.replace(profile)
            self.event.replace(event)

        return Result(port="payload", value={})


def register() -> Plugin:
    return Plugin(
        start=True,
        debug=False,
        spec=Spec(
            module=__name__,
            className=StartSegmentationAction.__name__,
            inputs=[],
            outputs=["payload"],
            init={
                "profile_id": ""
            },
            form=Form(groups=[
                FormGroup(
                    name="Debugging configuration",
                    description="In debug mode the following event will be injected into workflow.",
                    fields=[
                        FormField(
                            id="profile_id",
                            name="Profile ID",
                            description="You can load profile by its id for debugging purpose. "
                                        "This field is required if you would like to debug the workflow. It will be "
                                        "ignored when run on production.",
                            component=FormComponent(type="text", props={"label": "Profile ID"})
                        )
                    ]
                ),
            ]),
            version='0.8.2',
            license="MIT + CC",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Start',
            desc='Starts workflow and returns event data on payload port.',
            keywords=['start node'],
            type="startNode",
            icon='profile',
            width=200,
            height=200,
            group=["Flow"],
            purpose=['segmentation'],
            documentation=Documentation(
                inputs={},
                outputs={
                    "payload": PortDoc(desc="This port returns empty payload object.")
                }
            )
        )
    )
