from typing import Optional, List, Tuple

import logging

from tracardi.domain.user_payload import UserPayload
from tracardi.config import tracardi
from tracardi.domain.user import User
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.user_mapping import map_to_user_table, map_to_user
from tracardi.service.storage.mysql.schema.table import UserTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.table_filtering import sql_functions, \
    where_with_context
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)

# --------------------------------------------------------
# This Service Runs in Production and None-Production Mode
# It is PRODUCTION CONTEXT-LESS
# --------------------------------------------------------

def _where_with_context(*clause):
    return where_with_context(
        UserTable,
        False,
        *clause
    )

class UserService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        if search:
            where = _where_with_context(
                UserTable.name.like(f'%{search}%')
            )
        else:
            where = _where_with_context()

        return await self._select_query(UserTable,
                                        where=where,
                                        order_by=UserTable.name,
                                        limit=limit,
                                        offset=offset)


    async def load_by_id(self, user_id: str) -> SelectResult:
        return await self._load_by_id(UserTable, primary_id=user_id, server_context=False)

    async def delete_by_id(self, user_id: str) -> tuple:
        return await self._delete_by_id(UserTable,
                                        primary_id=user_id,
                                        server_context=False)

    async def upsert(self, user: User):
        return await self._replace(UserTable, map_to_user_table(user))


    # Custom

    async def load_by_credentials(self, email: str, password: str) -> Optional[User]:
        where = _where_with_context( # tenant only mode
            UserTable.email == email,
            UserTable.password == User.encode_password(password),
            UserTable.enabled == True
        )

        records = await self._select_query(UserTable, where=where)

        if not records.exists():
            return None

        return records.map_first_to_object(map_to_user)


    async def load_by_role(self, role: str) -> List[User]:
        where = _where_with_context( # tenant only mode
            sql_functions().find_in_set(role, UserTable.roles) > 0
        )

        records = await self._select_query(UserTable, where=where)

        if not records.exists():
            return []

        return list(records.map_to_objects(map_to_user))

    async def load_by_name(self, name: str, start:int, limit: int) -> List[User]:
        where = _where_with_context( # tenant only mode
            UserTable.name.like(name)
        )

        records = await self._select_query(UserTable, where=where, limit=start, offset=limit)

        users: List[User] = list(records.map_to_objects(map_to_user))

        return users

    async def check_if_exists(self, email: str) -> bool:
        where = _where_with_context( # tenant only mode
            UserTable.email == email
        )

        records = await self._select_query(UserTable, where=where)

        return records.exists()

    async def insert_if_none(self, user: User) -> Optional[str]:
        if not await self.check_if_exists(user.email):
            return await self._insert_if_none(
                UserTable,
                map_to_user_table(user),
                server_context=False
            )
        return None

    async def update_if_exist(self, user_id:str, user_payload: UserPayload) -> Tuple[bool, User]:

        user_record = await self.load_by_id(user_id)

        if not user_record.exists():
            raise LookupError(f"User does not exist {user_payload.email}")

        existing_user: User = user_record.map_to_object(map_to_user)

        user = User(
            id=user_id,
            password=User.encode_password(user_payload.password) if user_payload.password is not None else existing_user.password,
            name=user_payload.name if user_payload.name is not None else existing_user.name,
            email=user_payload.email if user_payload.email is not None else existing_user.email,
            roles=user_payload.roles if user_payload.roles is not None else existing_user.roles,
            enabled=user_payload.enabled if user_payload.enabled is not None else existing_user.enabled,
            preference=existing_user.preference,
            expiration_timestamp=existing_user.expiration_timestamp
        )

        result = await self._replace(UserTable, map_to_user_table(user))

        return result is not None, user