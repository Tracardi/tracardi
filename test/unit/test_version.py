from tracardi.domain.version import Version


def test_version_name():
    version = Version(version="x.0.0", db_version="090x")
    assert version.name == Version._generate_name("090x")
