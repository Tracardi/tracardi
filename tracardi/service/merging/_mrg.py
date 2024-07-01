import asyncio
from deepdiff import DeepDiff
from dotty_dict import dotty

from tracardi.context import Context, ServerContext
from tracardi.service.merging.merger import universal_merger, get_changed_values, get_modifications
from tracardi.service.merging._merging_rules import rules
from tracardi.service.tracking.storage.profile_storage import load_profile


async def main():
    with ServerContext(Context(production=False, tenant="t01")):
        profile = await load_profile("@debug-profile-id")

        flat_original_profile = dotty({
            "segments": ['c', 'a', {"ala": 1}],
            "x": 1,
            "d": 1
        })

        flat_cache_profile = dotty(dict(profile))
        flat_profile = dotty({
            "segments": ['b', 'c'],
            "x": 2,
            "c": "a"
        })

        diff_result = get_modifications(flat_original_profile, flat_profile)
        print(diff_result)

        # rule = rules['merge-with-cached-profile']
        # for field_merging_strategy in rule:
        #
        #     base = flat_cache_profile[field_merging_strategy.field]
        #     delta = flat_profile[field_merging_strategy.field]
        #
        #     print(1, base, type(base))
        #     print(1, delta, type(delta))
        #     print(field_merging_strategy.strategy)
        #
        #     xxx = universal_merger(
        #             base,
        #             delta,
        #             field_merging_strategy.strategy
        #         )
        #     print(base, type(base))
        #     print(delta, type(delta))
        #     print(xxx, type(xxx))

asyncio.run(main())
