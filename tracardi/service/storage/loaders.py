from tracardi.service.license import License, IDENTIFICATION
from tracardi.service.storage.driver.elastic import profile as profile_db

if License.has_service(IDENTIFICATION):
    from com_tracardi.service.identification_point_service import *


def get_profile_loader():
    if License.has_service(IDENTIFICATION):
        return identify_customer
    return profile_db.load_profile_without_identification
