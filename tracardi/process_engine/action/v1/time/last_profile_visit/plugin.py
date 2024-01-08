from datetime import datetime
from dateutil import parser
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class LastVisitAction(ActionRunner):

    async def set_up(self, init):
        pass

    async def run(self, payload: dict, in_edge=None) -> Result:
        if self.profile is None:
            self.console.error("Can not get last profile visit for without a profile.")
        else:
            last_visit = None
            if self.profile.metadata.time.visit.current:
                last_visit = self.profile.metadata.time.visit.current
            elif self.profile.metadata.time.insert:
                last_visit = self.profile.metadata.time.insert

            if last_visit:

                if isinstance(last_visit, str):
                    last_visit = parser.parse(last_visit)

                if isinstance(last_visit, datetime):
                    diff_secs = (datetime.utcnow() - last_visit).total_seconds()

                    return Result(port="visit", value={
                        'last': last_visit,
                        'difference': {
                            "seconds": diff_secs,
                            "minutes": diff_secs / 60,
                            "hours": diff_secs / (60 * 60),
                            "days": diff_secs / (60 * 60 * 24),
                            "weeks": diff_secs / (60 * 60 * 24 * 7)
                        }
                    })
                else:
                    self.console.error(f"Last visit is not a date. Expected datetime object got {type(last_visit)}.")

        return Result(port="error", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=LastVisitAction.__name__,
            inputs=["payload"],
            outputs=["visit", "error"],
            version='0.7.3',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual='last_profile_visit_time'
        ),
        metadata=MetaData(
            name='Last profile visit time',
            desc='Returns last profile visit time difference till now.',
            icon='time',
            group=["Time"],
            tags=['previous', 'last'],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "visit": PortDoc(desc="Returns last visit."),
                    "payload": PortDoc(desc="This port returns exactly same payload as given one.")
                }
            )
        )
    )
