from enum import Enum
from pydantic import validator

from tracardi.service.plugin.domain.config import PluginConfig


class SearchingAlgorithm(str, Enum):
    levenshtein = "levenshtein"
    normalized_levenshtein = "normalized_levenshtein"
    weighted_levenshtein = "weighted_levenshtein"
    damerau_levenshtein = "damerau_levenshtein"
    optimal_string_alignment = "optimal_string_alignment"
    jaro_winkler = "jaro_winkler"
    longest_common_subsequence = "longest_common_subsequence"
    metric_longest_common_subsequence = "metric_longest_common_subsequence"


class Configuration(PluginConfig):
    first_string: str
    second_string: str
    searching_algorithm: SearchingAlgorithm

    class SearchAlgorithmConfig:
        use_enum_values = True

    @validator("first_string", "second_string")
    def validate_field(cls, value):
        if not value:
            raise ValueError("Field cannot be empty")
        return value

    @validator("searching_algorithm")
    def validate_algo(cls, value):
        if not value:
            raise ValueError("You have to choose one of searching algorithms")
        return value


def validate(config: dict) -> Configuration:
    return Configuration(**config)
