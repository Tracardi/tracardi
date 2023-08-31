from time import time

from tracardi.service.license import License, VALIDATOR

s = time()
print(License.has_service(VALIDATOR))
print(time() - s)