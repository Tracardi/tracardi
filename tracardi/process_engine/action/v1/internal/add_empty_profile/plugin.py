from tracardi.service.utils.date import now_in_utc
from uuid import uuid4
from tracardi.domain.entity import Entity, PrimaryEntity
from tracardi.domain.event_session import EventSession
from tracardi.domain.metadata import ProfileMetadata
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session, SessionMetadata, SessionTime
from tracardi.domain.time import ProfileTime, ProfileVisit
from tracardi.domain.value_object.operation import Operation
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .config import Config


def validate(config: dict) -> Config:
    return Config(**config)


class AddEmptyProfileAction(ActionRunner):
    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        now = now_in_utc()
        profile = Profile(
            id=str(uuid4()),
            metadata=ProfileMetadata(
                time=ProfileTime(
                    visit=ProfileVisit(
                        count=1,
                        current=now
                    )
                )
            ),
            operation=Operation(new=True, update=True)
        )

        self.event.profile = profile
        self.event.metadata.profile_less = False

        self.tracker_payload.profile_less = False

        self.execution_graph.set_profiles(profile)

        if self.config.session == 'never':
            return Result(port='payload', value=payload)

        if self.config.session == 'if-not-exists' and self.session is not None \
                and self.tracker_payload.is_on('saveSession', default=True):
            return Result(port='payload', value=payload)

        # Create session

        session = Session(
            id=str(uuid4()),
            profile=PrimaryEntity(id=profile.id),
            metadata=SessionMetadata(time=SessionTime()),
            operation=Operation(new=True, update=True)
        )

        # todo set session in tracker payload

        if self.session is not None:
            self.console.warning(
                f"Old session {self.session.id} was replaced by new session {session.id}. "
                f"Replacing session is not a good practice if you already have a session.")

        self.session = session

        self.event.session = EventSession(
            id=session.id,
            start=session.metadata.time.insert,
            duration=session.metadata.time.duration
        )

        self.execution_graph.set_sessions(session)

        if self.tracker_payload.session:
            self.tracker_payload.session.id = session.id

        self.tracker_payload.options.update({"saveSession": True})

        return Result(port='payload', value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='AddEmptyProfileAction',
            inputs=["payload"],
            outputs=['payload'],
            version='0.8.0',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual="internal/add_empty_profile",
            init={
                "session": 'always'
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="New profile configuration",
                        fields=[
                            FormField(
                                name="New session",
                                id="session",
                                description="Create new session for new profile.",
                                component=FormComponent(type="select", props={
                                    "label": "New session",
                                    "items": {
                                        "if-not-exists": "If not exists",
                                        "always": "Always",
                                        "never": "Never"
                                    }
                                })
                            )
                        ]
                    )
                ]
            )

        ),
        metadata=MetaData(
            name='Create empty profile',
            desc='Ads new profile to the event. Empty profile gets created with random id.',
            icon='profile',
            keywords=['new', 'create', 'add'],
            group=["Operations"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns input payload.")
                }
            )
        )
    )
