import logging
import os
from hashlib import md5
from typing import Dict

from pydantic import BaseModel
from time import time

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.secrets import b64_decoder

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)

WEBHOOK_BRIDGE = "webhojGa"
API_BRIDGE = "kdIye85A"
REDIRECT_BRIGDE = "redi235s"

IMAP_BRIDGE = "imap7sd1"
RABBITMQ_BRIDGE = "rabYa25d"
KAFKA_BRIDGE = "kaff43sA"
MQTT_BRIDGE = "mqtt1kse"

SCHEDULER = "scheda75"
VALIDATOR = "vali34k0"
IDENTIFICATION = "ident19Ha"
COMPLIANCE = "compl1532"
RESHAPING = "resha-9ds"
REDIRECTS = "redir-atr"
INDEXER = "indxs4k1"
LICENSE = "lice12d4"
MULTI_TENANT = "multen9ck6"


class Service(BaseModel):
    id: str


class License(BaseModel):
    owner: str
    expires: int = 60 * 60 * 24
    services: Dict[str, Service]

    def is_expired(self):
        if self.expires == 0:
            return False
        return time() > self.expires

    def __iter__(self):
        return iter(self.services.items())

    def __contains__(self, item) -> bool:
        return item in self.services

    def get_service(self, service_id) -> Service:
        if service_id not in self.services:
            raise AssertionError("License not available")
        return self.services[service_id]

    def get_service_ids(self):
        return self.services.keys()

    @staticmethod
    def has_license() -> bool:
        return os.environ.get('LICENSE', None) is not None

    @staticmethod
    def has_service(service_id):
        if not License.has_license():
            return False

        try:
            license_string = os.environ.get('LICENSE', None)
            if not license_string:
                return False
            license = License.get_license(license_string)
            return license.get_service(service_id)
        except AssertionError:
            return False

    @staticmethod
    def check() -> 'License':
        license = os.environ.get('LICENSE', None)

        if license is None:
            raise AttributeError("Set LICENSE variable.")

        license = License.get_license(license)

        if license.is_expired():
            logger.error("License expired.")
            exit(1)

        return license

    @staticmethod
    def periodic_check(loop):

        def _check(loop):
            once_a_week = 60 * 60 * 24 * 7
            License.check()
            loop.call_later(once_a_week, _check, loop)

        _check(loop)

    @staticmethod
    def get_license(license: str) -> 'License':
        if license == "":
            raise AssertionError("Invalid license")

        try:
            license_key = license[: -7]
            license_id = int(license[-7:])

            not_coded = license_key[: -64]
            mesh = license_key[-64:]
            hash = []
            content = []
            for position, letter in enumerate(mesh):
                if position % 2 == 0:
                    hash.append(letter)
                else:
                    content.append(letter)

            hash = "".join(hash)
            content = "".join(content)
            content = f"{content}{not_coded}"

            check_hash = md5(f"{license_id}:{content}".encode('utf-8')).hexdigest()

            if check_hash != hash:
                raise AssertionError("Invalid license")

            license = b64_decoder(content)

            if 'u' not in license or 'e' not in license or 's' not in license:
                raise AssertionError("Invalid license")

            return License(owner=license['u'],
                           expires=license['e'],
                           services={
                               key: Service(id=service['i']) for key, service in license['s'].items()
                           })
        except ValueError as e:
            raise ValueError("License incorrect. Please check if you paste everything form the license key.")

