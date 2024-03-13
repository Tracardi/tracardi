from tracardi.service.utils.date import now_in_utc

from tracardi.domain.profile import Profile

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class SegmentProfileAction(ActionRunner):

    async def run(self, payload: dict, in_edge=None) -> Result:
        if isinstance(self.profile, Profile):
            self.profile.set_segmented(True)
            self.profile.metadata.time.segmentation = now_in_utc()
        else:
            if self.event.metadata.profile_less is True:
                self.console.warning("Can not segment profile when processing profile less events.")
            else:
                self.console.error("Can not segment profile. Profile is empty.")

        return Result(value=payload, port="payload")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SegmentProfileAction',
            inputs=["payload"],
            outputs=["payload"],
            version="0.6.0.1",
            init=None,
            manual="segmentation/force_segment_action"
        ),
        metadata=MetaData(
            name='Force segmentation',
            desc='Segment profile when flow ends.This action forces segmentation on profile after flow ends. See '
                 'documentation for more information.',
            icon='segment',
            group=["Segmentation"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any payload.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns input payload.")
                }
            )
        )
    )
