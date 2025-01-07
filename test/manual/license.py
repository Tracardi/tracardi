from time import time

from tracardi.service.license import License
from tracardi.service.license_type import VALIDATOR

s = time()
print(License.has_service(VALIDATOR))
print(time() - s)