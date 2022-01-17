from geopy import distance
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.action_runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.configuration import Configuration


def validate(config: dict):
    return Configuration(**config)


class CircularGeoFenceAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload):

        dot = self._get_dot_accessor(payload)

        center_coordinates_tuple = (float(self.config.center_coordinate.lat), float(self.config.center_coordinate.lng))
        test_coordinates_tuple = (float(dot[self.config.test_coordinate.lat]), float(dot[self.config.test_coordinate.lng]))

        distance_from_center = distance.distance(center_coordinates_tuple, test_coordinates_tuple).km

        if distance_from_center <= self.config.radius:
            return Result(port="inside", value={"distance": distance_from_center})
        else:
            return Result(port="outside", value={"distance": distance_from_center})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='CircularGeoFenceAction',
            inputs=["payload"],
            outputs=["inside", "outside"],
            version='0.6.2',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "center_coordinate": {"lat": None, "lng": None},
                "test_coordinate": {"lat": None, "lng": None},
                "radius": 10
            },
            form=Form(groups=[
                FormGroup(
                    name="Center point coordinates",
                    fields=[
                        FormField(
                            id="center_coordinate.lat",
                            name="Center latitude",
                            description="Type center point latitude.",
                            component=FormComponent(type="text", props={"label": "Center latitude"})
                        ),
                        FormField(
                            id="center_coordinate.lng",
                            name="Center longitude",
                            description="Type center point longitude.",
                            component=FormComponent(type="text", props={"label": "Center longitude"})
                        )
                    ]
                ),
                FormGroup(
                    name="Test point coordinates",
                    fields=[
                        FormField(
                            id="test_coordinate.lat",
                            name="Test latitude",
                            description="Type test point latitude, or a path to data tha has it.",
                            component=FormComponent(type="dotPath", props={"label": "Test latitude"})
                        ),
                        FormField(
                            id="test_coordinate.lng",
                            name="Test longitude",
                            description="Type test point longitude, or a path to data tha has it",
                            component=FormComponent(type="dotPath", props={"label": "Test longitude"})
                        )
                    ]
                ),
                FormGroup(
                    name="Radius",
                    fields=[
                        FormField(
                            id="radius",
                            name="Radius from center point in kilometers",
                            component=FormComponent(type="text", props={"label": "Radius"})
                        )
                    ]
                ),
            ]),

        ),
        metadata=MetaData(
            name='Circular GeoFence',
            desc='Finds out if the test geo location coordinates are within the radius threshold from '
                 'center point coordinates.',
            icon='geo-fence',
            group=["Location"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "inside": PortDoc(desc="Returns distance from test point to center point if test point is "
                                           "inside the radius."),
                    "outside": PortDoc(
                        desc="Returns distance from test point to center point if test point is outside the radius.")
                }
            )
        )
    )
