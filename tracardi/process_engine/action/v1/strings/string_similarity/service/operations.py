from strsimpy import Levenshtein, NormalizedLevenshtein, WeightedLevenshtein, Damerau, OptimalStringAlignment, \
    LongestCommonSubsequence, MetricLCS
from strsimpy.jaro_winkler import JaroWinkler


def levenshtein(*args):
    levenshtein = Levenshtein()
    return levenshtein.distance(*args)


def normalized_levenshtein(*args):
    normalized_levenshtein = NormalizedLevenshtein()
    return normalized_levenshtein.distance(*args)


def weighted_levenshtein(*args):
    weighted_levenshtein = WeightedLevenshtein()
    return weighted_levenshtein.distance(*args)


def damerau(*args):
    damerau = Damerau()
    return damerau.distance(*args)


def optimal_string_alignment(*args):
    optimal_string_alignment = OptimalStringAlignment()
    return optimal_string_alignment.distance(*args)


def jaro_winkler(*args):
    jaro_winkler = JaroWinkler()
    return jaro_winkler.distance(*args)


def longest_common_subsequence(*args):
    longest_common_subsequence = LongestCommonSubsequence()
    return longest_common_subsequence.distance(*args)


def lcs(*args):
    lcs = MetricLCS()
    return lcs.distance(*args)


algo = {
    "levenshtein": levenshtein,
    "normalized_levenshtein": normalized_levenshtein,
    "weighted_levenshtein": weighted_levenshtein,
    "damerau": damerau,
    "optimal_string_alignment": optimal_string_alignment,
    "jaro_winkler": jaro_winkler,
    "longest_common_subsequence": longest_common_subsequence,
}


def search_similarity(name, first_string, second_string):
    if name in algo:
        result = algo[name](first_string, second_string)
        return result
    else:
        raise ValueError(f"Please provide correct searching algorithm from the list {algo.keys()} ")



