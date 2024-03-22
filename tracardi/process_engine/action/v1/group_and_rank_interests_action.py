import json
from pydantic import field_validator
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.domain.profile import Profile


class Configuration(PluginConfig):
    interests: str
    segment_mapping: str
    segments_to_apply: str

    @field_validator('interests')
    @classmethod
    def must_not_be_empty(cls, value):
        if value.strip() == "":
            raise ValueError("interests must not be empty.")
        return value
    
    @field_validator('segment_mapping')
    @classmethod
    def must_not_be_empty(cls, value):
        if value.strip() == "":
            raise ValueError("segment_mapping must not be empty.")
        return value
    
    @field_validator('segments_to_apply')
    @classmethod
    def must_not_be_empty(cls, value):
        if value.strip() == "" or value.isnumeric() != True:
            raise ValueError("segments_to_apply must not be empty and must be a number.")
        return value
    
def validate(config: dict):
    return Configuration(**config)

class GroupAndRankInterestsAction(ActionRunner):
    
    config: Configuration
    
    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        profile = Profile(**dot.profile)

        
        try:
            segment_mapping = json.loads(dot[self.config.segment_mapping])
            interests = dot[self.config.interests]

            segment_count = {segment: 0 for segment in segment_mapping.keys()}

            for interest, count in interests.items():
                for segment, keywords in segment_mapping.items():
                    if interest.lower() in keywords:
                        segment_count[segment] += count

            ranked_segments = sorted(segment_count.keys(), key=lambda x: segment_count[x], reverse=True)
            
            # segments_to_apply=int(dot[self.config.segments_to_apply])
            # if segments_to_apply > len(ranked_segments):
            #     segments_to_apply=len(ranked_segments)
            #
            # for index in range(0, segments_to_apply):
            #     profile = trigger_segment_add(profile, self.session, ranked_segments[index])
                
            self.profile.replace(profile)

            return Result(port='result', value={'ranked_segments':ranked_segments})
        except Exception as e:
            return Result(value={"message": str(e)}, port="error")            

def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=GroupAndRankInterestsAction.__name__,
            inputs=["payload"],
            outputs=["result", "error"],
            version='0.9.0',
            init={
                "interests": "",
                "segment_mapping": "",
                "segments_to_apply": ""
            },
            form=Form(groups=[
                FormGroup(
                    name="Group And Rank Interests configuration",
                    fields=[
                        FormField(
                            id="interests",
                            name="Interests",
                            description="Interests, usually profile@interests",
                            component=FormComponent(type="dotPath", props={
                                "label": "Interests",
                                "defaultSourceValue": "profile"
                            })
                        ),
                        FormField(
                            id="segment_mapping",
                            name="Segment Mapping",
                            description="Used to pass the object containing segment to interest mapping.",
                            component=FormComponent(type="json", props={
                                "label": "segment_mapping"
                            })
                        ),
                        FormField(
                            id="segments_to_apply",
                            name="Segments To Apply",
                            description="Used to set the number of segments from segment_mapping that will be applied to the profile.",
                            component=FormComponent(type="dotPath", props={
                                "label": "segments_to_apply"
                            })
                        )
                        
                    ])
            ]),
            license="MIT",
            author="Matt Cameron",
            manual="group_and_rank_interests"
        ),
        metadata=MetaData(
            name='Group and Rank Interests',
            desc='Maps interests to profiles and returns matched profiles in order of importance.',
            icon='GroupAndRankInterests',
            group=['Segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="Returns response from GroupAndRankInterests service."),
                    "error": PortDoc(desc="Returns error message if plugin fails.")
                }
            )
        )
    )
