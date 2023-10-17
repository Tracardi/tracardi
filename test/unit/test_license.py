from time import time

from tracardi.service.license import License, Service


def test_create_license_with_owner_expiration_and_services():
    license = License(owner="John Doe", expires=3600,
                      services={"service1": Service(id="123"), "service2": Service(id="456")})
    assert license.owner == "John Doe"
    assert license.expires == 3600
    assert len(license.services) == 2
    assert "service1" in license.services
    assert "service2" in license.services


def test_check_license_expiration_and_validity():
    license = License(owner="John Doe",
                      expires=int(time() + 3600),
                      services={"service1": Service(id="123")})
    print(license.is_expired())
    assert not license.is_expired()
    license.expires = time() - 3600
    assert license.is_expired()


def test_retrieve_service_ids_from_license():
    license = License(owner="John Doe", expires=int(time() + 3600),
                      services={"service1": Service(id="123"), "service2": Service(id="456")})
    service_ids = license.get_service_ids()
    assert len(service_ids) == 2
    assert "service1" in service_ids
    assert "service2" in service_ids


def test_create_license_with_never_expires():
    license = License(owner="John Doe", expires=0, services={"service1": Service(id="123")})
    assert not license.is_expired()


def test_create_license_with_no_services():
    license = License(owner="John Doe", expires=int(time() + 3600), services={})
    assert len(license.services) == 0
