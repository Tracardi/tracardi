from tracardi.context import Context
from tracardi.domain.profile import Profile
from tracardi.domain.profile_data import ProfileData
from tracardi.service.tracking.cache.profile_cache import load_profile_cache
from tracardi.service.merger import merge as dict_merge, list_merge


def _merge_dict(base_dict, update_dict):
    return dict_merge(base_dict,
                      [update_dict],
                      make_lists_uniq=True,
                      disallow_single_value_list=False
                      )


def merge_cache_and_profile(profile: Profile, context: Context):
    _cache_profile = load_profile_cache(profile.id, context)

    if not _cache_profile:
        return profile

    # Smart replace

    try:
        profile.data = ProfileData(**_merge_dict(
            base_dict=_cache_profile.data.model_dump(mode='json'),
            update_dict=profile.data.model_dump(mode='json')
        ))

        profile.traits = _merge_dict(
            base_dict=_cache_profile.traits,
            update_dict=profile.traits
        )

        profile.metadata.aux = _merge_dict(
            base_dict=_cache_profile.metadata.aux,
            update_dict=profile.metadata.aux
        )

        # Copy time and visits from session. Updates to the last time
        profile.metadata.time = _cache_profile.metadata.time
        profile.metadata.time.visit = _cache_profile.metadata.time.visit
        profile.metadata.status = _cache_profile.metadata.status

        profile.aux = _merge_dict(
            base_dict=_cache_profile.aux,
            update_dict=profile.aux
        )

        profile.consents = _merge_dict(
            base_dict=_cache_profile.consents,
            update_dict=profile.consents
        )

        profile.interests = _merge_dict(
            base_dict=_cache_profile.interests,
            update_dict=profile.interests
        )

        profile.segments = list_merge(
            base=_cache_profile.segments,
            new_list=profile.segments,
            make_lists_uniq=True,
            disallow_single_value_list=False
        )

    except Exception as e:
        print(e)

    finally:
        return profile
