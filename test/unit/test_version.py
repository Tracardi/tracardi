from tracardi.domain.version import Version


def test_version_name():
    version = Version(version="0.8.2-dev", db_version="08x")
    assert version.name == Version._generate_name("08x")
