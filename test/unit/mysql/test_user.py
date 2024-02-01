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
        assert result.production == get_context().production
        assert result.password == user.password
        assert result.name == user.name
        assert result.email == user.email
        assert result.roles == ','.join(user.roles)
        assert result.disabled == user.disabled
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
        enabled=True,
        expiration_timestamp=None,
        preference={"key": "value"}
    )

    result = map_to_user(user_table)

    assert result == expected_user
