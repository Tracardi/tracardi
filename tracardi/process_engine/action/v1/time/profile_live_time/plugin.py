from tracardi.service.utils.date import now_in_utc

from datetime import datetime
from dateutil import parser
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class ProfileLiveTimeAction(ActionRunner):

    async def set_up(self, init):
        pass

    async def run(self, payload: dict, in_edge=None) -> Result:
        if self.profile is None:
            self.console.error("Can not get profile live time without a profile.")
        else:
            created = self.profile.metadata.time.insert

            if created:

                if isinstance(created, str):
                    created = parser.parse(created)

                if isinstance(created, datetime):
                    diff_secs = (now_in_utc() - created).total_seconds()

                    return Result(port="live-time", value={
                        'last': created,
                        'time': {
                            "seconds": diff_secs,
                            "minutes": diff_secs / 60,
                            "hours": diff_secs / (60 * 60),
                            "days": diff_secs / (60 * 60 * 24),
                            "weeks": diff_secs / (60 * 60 * 24 * 7)
                        }
                    })
                else:
                    self.console.error(
                        f"Profile time.insert is not a date. Expected datetime object got {type(created)}.")

        return Result(port="error", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=ProfileLiveTimeAction.__name__,
            inputs=["payload"],
            outputs=["live-time", "error"],
            version='0.8.0',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual='profile_live_time'
        ),
        metadata=MetaData(
            name='Profile live time',
            desc='Returns how long ago a profile was registered in the system.',
            icon='time',
            group=["Time"],
            tags=['previous', 'last'],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "live-time": PortDoc(desc="This port returns profile live time.")
                }
            )
        )
    )
