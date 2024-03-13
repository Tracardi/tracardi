from tracardi.context import ServerContext, Context
from tracardi.domain.event_redirect import EventRedirect
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.mysql.mapping.event_redirect_mapping import map_to_event_redirect_table, \
    map_to_event_redirect
from tracardi.service.storage.mysql.schema.table import EventRedirectTable


def test_correct_mapping():
    with ServerContext(Context(production=True)):

        event_redirect = EventRedirect(
            id="123",
            name="Test Event Redirect",
            url="https://example.com",
            source=NamedEntity(id="456", name="Test Source"),
            event_type="click",
            props={"param1": "value1", "param2": "value2"},
            tags=["tag1", "tag2"]
        )


        result = map_to_event_redirect_table(event_redirect)

        assert result.id == event_redirect.id
        assert result.name == event_redirect.name
        assert result.production
        assert result.description == ""
        assert result.url == event_redirect.url
        assert result.source_id == event_redirect.source.id
        assert result.source_name == event_redirect.source.name
        assert result.event_type == event_redirect.event_type
        assert result.props == {"param1": "value1", "param2": "value2"}
        assert result.tags == "tag1,tag2"


def test_handle_missing_fields():
    event_redirect_table = EventRedirectTable(
        id="123",
        name="Test Event Redirect",
        url="https://example.com",
        source_id="456",
        source_name="Test Source",
        event_type="test"
    )

    event_redirect = map_to_event_redirect(event_redirect_table)

    assert event_redirect.id == "123"
    assert event_redirect.name == "Test Event Redirect"
    assert event_redirect.description == ""
    assert event_redirect.url == "https://example.com"
    assert event_redirect.source.id == "456"
    assert event_redirect.source.name == "Test Source"
    assert event_redirect.event_type == 'test'
    assert event_redirect.props is None
    assert event_redirect.tags == []
