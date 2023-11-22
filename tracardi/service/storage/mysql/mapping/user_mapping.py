from tracardi.context import get_context
from tracardi.domain.user import User
from tracardi.service.storage.mysql.schema.table import UserTable
from tracardi.service.storage.mysql.utils.serilizer import from_json, to_json


def map_to_user_table(user: User) -> UserTable:
    context = get_context()
    return UserTable(
        id=user.id,
        tenant=context.tenant,
        production=context.production,
        password=user.password,
        full_name=user.full_name,
        email=user.email,
        roles=','.join(user.roles),  # Convert list of roles to a comma-separated string
        disabled=user.disabled if user.disabled is not None else False,
        expiration_timestamp=user.expiration_timestamp,
        preference=to_json(user.preference) if user.preference else "{}"
    )


def map_to_user(user_table: UserTable) -> User:
    return User(
        id=user_table.id,
        password=user_table.password,
        full_name=user_table.full_name,
        email=user_table.email,
        roles=user_table.roles.split(',') if user_table.roles else [],  # Convert comma-separated string back to list
        disabled=user_table.disabled if user_table.disabled is not None else False,
        expiration_timestamp=user_table.expiration_timestamp,
        preference=from_json(user_table.preference) if user_table.preference else {}
    )
