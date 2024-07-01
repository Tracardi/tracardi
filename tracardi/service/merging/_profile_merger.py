from tracardi.domain.profile import Profile
from tracardi.domain.profile_data import ProfileData
# from tracardi.service.merging.merger import merge as dict_merge, list_merge, MergingStrategy
#
#
# def _merge_dict(base_dict, update_dict):
#     return dict_merge(
#         base_dict,
#         [update_dict],
#         MergingStrategy(
#             make_lists_uniq=True,
#             no_single_value_list=False
#         )
#     )
#

# def merge_profiles(base_profile: Profile, new_profile: Profile) -> Profile:
#
#     try:
#         new_profile.data = ProfileData(
#             **dict_merge(
#                 base_profile.data.model_dump(mode='json'),
#                 [new_profile.data.model_dump(mode='json')],
#                 MergingStrategy(
#                     make_lists_uniq=True,
#                     no_single_value_list=False,
#                     # cache number values have priority and override WF values
#                     default_number_strategy="override"
#                 )
#             )
#         )
#
#         new_profile.traits = dict_merge(
#             base_profile.traits,
#             [new_profile.traits],
#             MergingStrategy(
#                 make_lists_uniq=True,
#                 no_single_value_list=False,
#                 # cache number values have priority and override WF values
#                 default_number_strategy="override"
#             )
#         )
#
#         new_profile.metadata.aux = dict_merge(
#             base_profile.metadata.aux,
#             [new_profile.metadata.aux],
#             MergingStrategy(
#                 default_number_strategy="override"
#             )
#         )
#
#         # Copy time and visits from session. Updates to the last time
#         new_profile.metadata.time = base_profile.metadata.time
#         new_profile.metadata.time.visit = base_profile.metadata.time.visit
#         new_profile.metadata.status = base_profile.metadata.status
#
#         new_profile.aux = _merge_dict(
#             base_dict=base_profile.aux,
#             update_dict=new_profile.aux
#         )
#
#         new_profile.consents = _merge_dict(
#             base_dict=base_profile.consents,
#             update_dict=new_profile.consents
#         )
#
#         new_profile.interests = _merge_dict(
#             base_dict=base_profile.interests,
#             update_dict=new_profile.interests
#         )
#
#         # This sould be commented. New profile is as it is. No merging as it will keep the old segments.
#         # new_profile.segments = list_merge(
#         #     base=base_profile.segments,
#         #     new_list=new_profile.segments,
#         #     strategy=MergingStrategy(
#         #         make_lists_uniq=True,
#         #         no_single_value_list=False,
#         #         default_list_strateg='override'
#         #     )
#         # )
#
#         new_profile.set_meta_data(base_profile.get_meta_data())
#
#     except Exception as e:
#         print(e)
#
#     finally:
#         return new_profile

