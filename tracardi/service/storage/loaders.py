from tracardi.service.license import License, IDENTIFICATION
from tracardi.service.storage.drivers.elastic.profile import *
if License.has_service(IDENTIFICATION):
    from com_tracardi.service.identification_point_service import *


def get_profile_loader():
    if License.has_service(IDENTIFICATION):
        return identify_customer
    return load_merged_profile
