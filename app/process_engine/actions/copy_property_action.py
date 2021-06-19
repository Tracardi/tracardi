import logging
from dotty_dict import dotty
# from app.domain.action import ActionEvaluator
from app.domain.payload.event_payload import EventPayload
from app.domain.payload.tracker_payload import TrackerPayload

_logger = logging.getLogger("CopyPropertyAction")


class CopyPropertyAction:

    async def run(self, payload: TrackerPayload, event: EventPayload, config: dict):
        """
        Copies properties from event to profile.
        Config example:

        config = {
            # event.property -> profile.properties
            'event.property1': ['profile.property1', 'profile.property2'],
            'event.property2': ['profile.property3'],
        }

        """
        payload.profile.properties = self.copy_properties(event.properties, payload.profile.properties, config)
        return payload.profile

    @staticmethod
    def copy_properties(event_properties, profile_properties, config):
        dotted_event = dotty(event_properties)
        dotted_profile_properties = dotty(profile_properties)
        for event_property, profile_properties in config.items():
            if not isinstance(profile_properties, list):
                raise ValueError(
                    "Incorrect config. Profile properties are not a list. " +
                    "Correct schema is event.property: [profile.property.a, profile.property.b]")
            for profile_property in profile_properties:
                if event_property in dotted_event:
                    if profile_property in dotted_profile_properties:
                        _logger.warning(
                            "Overriding profile property `{}` of value '{}' with value `{}` from `{}`".format(
                                profile_property,
                                dotted_profile_properties[profile_property],
                                dotted_event[event_property],
                                event_property))
                    dotted_profile_properties[profile_property] = dotted_event[event_property]
                else:
                    _logger.warning("Event property `{}` does not exist".format(event_property))
        return dict(dotted_profile_properties)
