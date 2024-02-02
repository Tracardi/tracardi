from tracardi.domain.version import Version


def test_version_name():
    version = Version(version="0.8.2", db_version="082x")
    assert version.name == Version._generate_name("082x")
