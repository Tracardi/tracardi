from tracardi.domain.profile import Profile
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.url_constructor import ApiCredentials


def test_should_create_correct_url():
    creds = ApiCredentials(
        url="localhost",
        password="pass"
    )

    url = creds.get_url()
    assert url == 'http://localhost'

    creds = ApiCredentials(
        url="localhost:80",
        username="user",
        password="pass"
    )

    url = creds.get_url()
    assert url == 'http://user:pass@localhost:80'

    creds = ApiCredentials(
        url="https://localhost:80",
        username="user",
        password="pass"
    )

    url = creds.get_url()
    assert url == 'https://user:pass@localhost:80'

    creds = ApiCredentials(
        url="https://localhost:80/",
        username="user",
        password="pass"
    )

    url = creds.get_url(endpoint="/test")
    assert url == 'https://user:pass@localhost:80/test'


def test_should_replace_url_placeholders():
    creds = ApiCredentials(
        url="https://localhost:80",
        username="user",
        password="pass"
    )

    dot = DotAccessor(profile=Profile(id="1"))

    url = creds.get_url(dot, endpoint="/test{{profile@id}}")
    assert url == 'https://user:pass@localhost:80/test1'
