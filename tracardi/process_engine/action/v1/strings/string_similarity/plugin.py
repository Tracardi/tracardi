from tracardi.process_engine.action.v1.strings.string_similarity.model.configuration import Configuration, validate
from tracardi.process_engine.action.v1.strings.string_similarity.service.operations import search_similarity
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner

from tracardi.service.plugin.domain.result import Result


class SearchStringSimilarityAction(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        first_string = dot[self.config.first_string]
        second_string = dot[self.config.second_string]
        algorithm = self.config.algorithm

        return Result(port='payload', value={
            "similarity": search_similarity(algorithm, first_string, second_string)
        })


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className="SearchStringSimilarityAction",
            inputs=["payload"],
            outputs=["payload"],
            version="0.7.3",
            license="MIT + CC",
            author="Mateusz Zitaruk",
            init={
                "first_string": "",
                "second_string": "",
                "algorithm": "normalized_levenshtein"
            },
            manual="string_similarity_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="String similarity plugin configuration",
                        fields=[
                            FormField(
                                id="first_string",
                                name="First string",
                                description="Type first string that you want to compare.",
                                component=FormComponent(
                                    type="dotPath",
                                    props={
                                        "label": "Payload field",
                                        "defaultSourceValue": "event"
                                    }
                                )
                            ),
                            FormField(
                                id="second_string",
                                name="Second string",
                                description="Type second string that you want to compare.",
                                component=FormComponent(
                                    type="dotPath",
                                    props={
                                        "label": "Payload field",
                                        "defaultSourceValue": "event"
                                    }
                                )
                            ),
                            FormField(
                                id="algorithm",
                                name="Comparison algorithm",
                                description="Choose algorithm which you want use to compare strings.",
                                component=FormComponent(
                                    type="select",
                                    props={
                                        "label": "Comparison algorithms",
                                        "items": {
                                            "levenshtein": "Levenshtein",
                                            "normalized_levenshtein": "Normalized Levenshtein",
                                            "weighted_levenshtein": "Weighted Levenshtein",
                                            "damerau": "Damerau",
                                            "optimal_string_alignment": "Optimal string alignment",
                                            "jaro_winkler": "Jaro Winkler",
                                            "longest_common_subsequence": "Longest common subsequence"
                                        }
                                    }
                                )

                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name="String similarity",
            desc="Compare both strings according to chosen algorithm.",
            icon="question",
            group=["String"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={"true": PortDoc(desc="This port returns the result of the algorithm.")}
            )
        )
    )
