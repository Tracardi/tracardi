from datetime import date
import datetime

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class WeekDaysChecker(ActionRunner):

    def __init__(self, **kwargs):
        pass

    async def run(self, payload: dict, in_edge=None):
        today = datetime.datetime.today()
        if date.weekday(today) <= 4:
            weekdays = {"today": today.strftime("%A"),
                        "weekend": date.weekday(today) > 4}
        else:
            weekdays = {"today": today.strftime("%A"),
                        "weekend": date.weekday(today) < 4}
        return Result(port="date", value=weekdays)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='WeekDaysChecker',
            inputs=["payload"],
            outputs=["date"],
            version='0.7.2',
            license="MIT",
            author="Mateusz Zitaruk",
            manual="weekdays_checker_action"

        ),
        metadata=MetaData(
            name='If its a weekend',
            desc='This plugin checks current date and flag it if its a weekend or not.',
            icon='global',
            group=["Input/Output"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={"date": PortDoc(desc="This port returns current date and flag if its a weekend or not.")}
            )
        )
    )
