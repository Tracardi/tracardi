from geopy import distance
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.configuration import Configuration


def validate(config: dict):
    return Configuration(**config)


class GeoDistanceAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        dot = self._get_dot_accessor(payload)

        center_coordinates_tuple = (float(self.config.start_coordinate.lat), float(self.config.start_coordinate.lng))
        test_coordinates_tuple = (float(dot[self.config.end_coordinate.lat]), float(dot[self.config.end_coordinate.lng]))

        distance_from_center = distance.distance(center_coordinates_tuple, test_coordinates_tuple).km

        return Result(port="payload", value={"distance": distance_from_center})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='GeoDistanceAction',
            inputs=["payload"],
            outputs=["payload"],
            version='0.6.1',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual='geo_distance'
        ),
        metadata=MetaData(
            name='Geo distance',
            desc='Finds out if the test geo location coordinates are within the radius threshold from '
                 'center point coordinates.',
            icon='path',
            group=["Location"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns true if inside the radius, otherwise false.")
                }
            ),
            pro=True
        )
    )
