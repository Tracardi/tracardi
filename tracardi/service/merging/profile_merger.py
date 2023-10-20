from tracardi.domain.profile import Profile
from tracardi.domain.profile_data import ProfileData
from tracardi.service.merging.merger import merge as dict_merge, list_merge, MergingStrategy


def _merge_dict(base_dict, update_dict):
    return dict_merge(
        base_dict,
        [update_dict],
        MergingStrategy(
            make_lists_uniq=True,
            no_single_value_list=False
        )
    )


def merge_profiles(base_profile: Profile, profile: Profile) -> Profile:

    try:
        profile.data = ProfileData(
            **dict_merge(
                base_profile.data.model_dump(mode='json'),
                [profile.data.model_dump(mode='json')],
                MergingStrategy(
                    make_lists_uniq=True,
                    no_single_value_list=False,
                    # cache number values have priority and override WF values
                    default_number_strategy="override"
                )
            )
        )

        profile.traits = dict_merge(
            base_profile.traits,
            [profile.traits],
            MergingStrategy(
                make_lists_uniq=True,
                no_single_value_list=False,
                # cache number values have priority and override WF values
                default_number_strategy="override"
            )
        )

        profile.metadata.aux = dict_merge(
            base_profile.metadata.aux,
            [profile.metadata.aux],
            MergingStrategy(
                default_number_strategy="override"
            )
        )

        # Copy time and visits from session. Updates to the last time
        profile.metadata.time = base_profile.metadata.time
        profile.metadata.time.visit = base_profile.metadata.time.visit
        profile.metadata.status = base_profile.metadata.status

        profile.aux = _merge_dict(
            base_dict=base_profile.aux,
            update_dict=profile.aux
        )

        profile.consents = _merge_dict(
            base_dict=base_profile.consents,
            update_dict=profile.consents
        )

        profile.interests = _merge_dict(
            base_dict=base_profile.interests,
            update_dict=profile.interests
        )

        profile.segments = list_merge(
            base=base_profile.segments,
            new_list=profile.segments,
            strategy=MergingStrategy(
                make_lists_uniq=True,
                no_single_value_list=False
            )
        )

    except Exception as e:
        print(e)

    finally:
        return profile

