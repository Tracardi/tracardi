from tracardi.context import get_context
from tracardi.domain.user import User
from tracardi.service.storage.mysql.mapping.utils import split_list
from tracardi.service.storage.mysql.schema.table import UserTable


def map_to_user_table(user: User) -> UserTable:
    context = get_context()
    return UserTable(
        id=user.id,
        tenant=context.tenant,
        password=user.password,
        name=user.name,
        email=user.email,
        roles=','.join(user.roles),  # Convert list of roles to a comma-separated string
        enabled=user.enabled if user.enabled is not None else False,
        expiration_timestamp=user.expiration_timestamp,
        preference=user.preference
    )


def map_to_user(user_table: UserTable) -> User:
    return User(
        id=user_table.id,
        password=user_table.password,
        name=user_table.name,
        email=user_table.email,
        roles=split_list(user_table.roles),  # Convert comma-separated string back to list
        enabled=user_table.enabled if user_table.enabled is not None else False,
        expiration_timestamp=user_table.expiration_timestamp,
        preference=user_table.preference
    )
