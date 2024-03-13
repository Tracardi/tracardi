from tracardi.context import get_context, ServerContext, Context
from tracardi.domain.user import User
from tracardi.service.storage.mysql.mapping.user_mapping import map_to_user_table, map_to_user
from tracardi.service.storage.mysql.schema.table import UserTable


def test_valid_user_object():

    with ServerContext(Context(production=True)):
        user = User(
            id="123",
            password="password123",
            name="John Doe",
            email="john.doe@example.com",
            roles=["admin", "user"],
            enabled=True,
            expiration_timestamp=1640995200,
            preference={"key": "value"}
        )

        result = map_to_user_table(user)

        assert isinstance(result, UserTable)
        assert result.id == user.id
        assert result.tenant == get_context().tenant
        assert result.password == user.password
        assert result.name == user.name
        assert result.email == user.email
        assert result.roles == ','.join(user.roles)
        assert result.enabled == user.enabled
        assert result.expiration_timestamp == user.expiration_timestamp
        assert result.preference == user.preference


def test_all_fields_mapped():

    user_table = UserTable(
        id="123",
        password="password",
        name="John Doe",
        email="john.doe@example.com",
        roles="admin,user",
        preference={"key": "value"}
    )

    expected_user = User(
        id="123",
        password="password",
        name="John Doe",
        email="john.doe@example.com",
        roles=["admin", "user"],
        enabled=False,
        expiration_timestamp=None,
        preference={"key": "value"}
    )

    result = map_to_user(user_table)

    assert result.id == expected_user.id
    assert result.password == expected_user.password
    assert result.name == expected_user.name
    assert result.email == expected_user.email
    assert result.roles == expected_user.roles
    assert result.enabled == expected_user.enabled
    assert result.expiration_timestamp == expected_user.expiration_timestamp

