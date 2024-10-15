import uuid
from typing import Optional, List, Set
from .entity import PrimaryEntity, Entity, FlatEntity
from .profile import Profile
from .profile_data import FLAT_PROFILE_MAPPING, PREFIX_IDENTIFIER_ID, PREFIX_IDENTIFIER_PK
from .storage_record import RecordMetadata, StorageRecord
from ..config import tracardi
from ..service.tracking.profile_pii_hashing import get_allowed_piis_to_be_hashed_as_ids
from ..service.utils.date import now_in_utc
from tracardi.domain.profile_data import PREFIX_EMAIL_BUSINESS, PREFIX_EMAIL_MAIN, PREFIX_EMAIL_PRIVATE, \
    PREFIX_PHONE_MAIN, PREFIX_PHONE_BUSINESS, PREFIX_PHONE_MOBILE, PREFIX_PHONE_WHATSUP
from ..service.utils.hasher import hash_id, has_hash_id
from tracardi.service.storage.index import Resource


class FlatProfile(FlatEntity):

    def __init__(self, dictionary):
        super().__init__(dictionary)

        # Set default values and basic validation
        self.set_new(False)
        self.set_updated(False)
        ids = self.get('ids', None)
        if ids is None:
            self['ids'] = []
        elif not isinstance(ids, list):
            raise ValueError("IDS value must be a list.")

    @staticmethod
    def as_primary_entity(flat_profile: 'FlatProfile'):
        if not flat_profile:
            return None
        return PrimaryEntity(id=flat_profile['id'], primary_id=flat_profile.get('primary_id', None))

    @staticmethod
    def as_entity(flat_profile: 'FlatProfile'):
        if not flat_profile:
            return None
        return Entity(id=flat_profile['id'])

    @property
    def ids(self) -> List[str]:
        ids = self.get('ids', None)
        if ids is None:
            self['ids'] = []

        return self['ids']

    @property
    def traits(self) -> {}:
        return self.get('traits', {})

    @ids.setter
    def ids(self, value: List[str]):
        """Setter method"""
        if not isinstance(value, list):
            raise ValueError("IDS value must be a list.")

        self['ids'] = value

    def add_to_ids(self, id: str):
        ids = self.get('ids', [])
        ids.append(id)
        # This should register changes in change logger
        self['ids'] = list(set(ids))

    def get_all_ids(self) -> Set[str]:
        return {self.id, *self.ids} if isinstance(self.ids, list) else {self.id}

    @staticmethod
    def new(id: Optional[str] = None) -> 'FlatProfile':
        _now = now_in_utc()

        flat_profile = FlatProfile(
            {
                "id": str(uuid.uuid4()) if not id else id,
                "metadata": {"time": {"create": _now,
                                      "insert": _now}}
            }
        )
        flat_profile.fill_meta_data()
        flat_profile.set_new()
        flat_profile.set_updated()
        flat_profile['active'] = True

        return flat_profile

    def has_not_saved_changes(self) -> bool:
        return self.is_new() or self.needs_update()

    def needs_update(self) -> bool:
        return bool(self.get('operation.update', False))

    def fill_meta_data(self):
        """
        Used to fill metadata with default current index and id.
        """
        self._fill_meta_data('profile')

    def dump(self) -> dict:
        dump = self.to_dict()
        try:
            del dump['operation']
        except KeyError:
            pass
        return dump

    def instanceof(self, field: str, instance: type) -> bool:
        if field not in self:
            return False
        return isinstance(self.get(field, None), instance)

    def _fill_meta_data(self, index_type: str):
        """
        Used to fill metadata with default current index and id.
        """
        if not self.has_meta_data():
            resource = Resource()
            self.set_meta_data(RecordMetadata(id=self.id, index=resource[index_type].get_write_index()))

    def add_auto_merge_hashed_id(self, flat_field: str) -> Optional[str]:
        field_closure = FLAT_PROFILE_MAPPING.get(flat_field, None)
        if field_closure:

            value, prefix = field_closure(self)

            if value:

                value = value.strip().lower()

                if 'ids' not in self or self['ids'] is None:
                    self['ids'] = []

                # Add new
                # Can not simply append. Must reassign
                _hash_id = hash_id(value, prefix)

                # Do not add value if exists
                if has_hash_id(_hash_id, self['ids']):
                    return None

                ids = self['ids']
                ids.append(_hash_id)
                # Assign to replace value
                self['ids'] = list(set(ids))

                return flat_field

        return None

    # def get_profile_pii_as_hashed_ids(self) -> Set[str]:
    #     added_ids = set()
    #     if not tracardi.is_apm_on():
    #         return added_ids
    #
    #     allowed_piis = get_allowed_piis_to_be_hashed_as_ids()
    #
    #     # Iterate changed values
    #     for flat_field, timestamp_data in self.get_change_logger().changes():  # type: str, list
    #         # Adds hashed id for email, phone, etc.
    #         if flat_field in allowed_piis:
    #             added_hashed_id = self._add_auto_merge_hashed_id(flat_field)
    #             if added_hashed_id:
    #                 added_ids.add(added_hashed_id)
    #
    #     return added_ids

    def increase_interest(self, interest, value=1):

        interest_key = f'interests.{interest}'
        _existing_interest_value = self.get(interest_key, None)

        if _existing_interest_value:
            # Convert if string
            if isinstance(_existing_interest_value, str) and _existing_interest_value.isnumeric():
                _existing_interest_value = float(_existing_interest_value)

            if isinstance(_existing_interest_value, (int, float)):
                self[interest_key] += value

        else:
            self[interest_key] = value

    def decrease_interest(self, interest, value=1):

        interest_key = f'interests.{interest}'
        _existing_interest_value = self.get(interest_key, None)

        if _existing_interest_value:
            # Convert if string
            if isinstance(_existing_interest_value, str) and _existing_interest_value.isnumeric():
                _existing_interest_value = float(_existing_interest_value)

            if isinstance(_existing_interest_value, (int, float)):
                self[interest_key] -= value

        else:
            self[interest_key] = -value

    def reset_interest(self, interest, value=0):
        interest_key = f'interests.{interest}'
        self[interest_key] = value

    def mark_for_update(self):
        self['operation.update'] = True
        self['metadata.time.update'] = now_in_utc()

    def is_new(self) -> bool:
        return bool(self.get('operation.new', False))

    def set_new(self, flag=True):
        self['operation.new'] = flag

    def set_updated(self, flag=True):
        self['operation.update'] = flag

    def mark_as_merged(self):
        self['metadata.system.aux.auto_merge'] = []
        self['metadata.aux.merge_time'] = now_in_utc()

    def update_changed_fields(self, changed_fields):
        self['metadata.fields'] = changed_fields

    # ToDO refactor
    def set_auto_merge_fields(self, auto_merge_ids: set):
        if 'metadata.system.aux.auto_merge' not in self or not isinstance(self['metadata.system.aux.auto_merge'], list):
            self['metadata.system.aux.auto_merge'] = list(auto_merge_ids)
        else:
            self['metadata.system.aux.auto_merge'] = list(
                set(self['metadata.system.aux.auto_merge']).union(auto_merge_ids))

    def has(self, value, equal=None) -> bool:
        if equal is None:
            return value in self
        return value in self and self[value] == equal

    def has_not_empty(self, value) -> bool:
        return value in self and self[value] is not None

    def set_if_none(self, field, value):
        if field not in self:
            self[field] = value

    def set_if_not_instance(self, field: str, value, instance: type):
        if field not in self or not isinstance(self[field], instance):
            self[field] = value

    def set_visit_time(self):
        if self.has('metadata.time.visit.current'):
            self['metadata.time.visit.last'] = self['metadata.time.visit.current']
        self['metadata.time.visit.current'] = now_in_utc()

    def get_consent_ids(self) -> Set[str]:
        if not self.instanceof('consents', dict):
            return set()
        return set(self['consents'].keys())

    @staticmethod
    def from_es_storage_record(record: StorageRecord) -> 'FlatProfile':
        fp = FlatProfile(record)
        fp.set_new(False)
        fp.set_updated(False)
        fp.set_meta_data(record.get_meta_data())
        return fp

    @staticmethod
    def from_profile(profile: Profile) -> 'FlatProfile':
        fp = FlatProfile(profile.model_dump(mode="json"))
        fp.set_meta_data(profile.get_meta_data())
        return fp

    def as_profile(self) -> Profile:
        return Profile(**self.to_dict()).set_meta_data(self.get_meta_data())

    # --------------- ID Hashing -----------------------

    def hash_all_allowed_pii_as_ids(self) -> bool:

        """ Used for creating hashed IDS """

        # Check for missing hash IDS, and create missing, Mark for update
        changed_fields = self.create_auto_merge_hashed_ids()
        if changed_fields:
            # Add missing fields to auto_merge
            self.set_auto_merge_fields(changed_fields)
            return True

        return False

    def has_hashed_phone_id(self, type: str = None) -> bool:

        if type is None:
            type = PREFIX_PHONE_MAIN, PREFIX_PHONE_BUSINESS, PREFIX_PHONE_MOBILE, PREFIX_PHONE_WHATSUP

        for id in self.ids:
            if id.startswith(type):
                return True
        return False

    def has_hashed_email_id(self, type: str = None) -> bool:
        """
        This only checks if there are prefixed ids. It does not check if they are correct. APM does it.
        """
        if type is None:
            type = PREFIX_EMAIL_MAIN, PREFIX_EMAIL_PRIVATE, PREFIX_EMAIL_BUSINESS

        for id in self.ids:
            if id.startswith(type):
                return True
        return False

    def has_hashed_id(self) -> bool:
        for id in self.ids:
            if id.startswith(PREFIX_IDENTIFIER_ID):
                return True
        return False

    def has_hashed_pk(self) -> bool:
        for id in self.ids:
            if id.startswith(PREFIX_IDENTIFIER_PK):
                return True
        return False

    def create_auto_merge_hashed_ids(self) -> Optional[set]:

        if tracardi.is_apm_on():

            new_ids = set()
            update_fields = set()

            if self.has('data.identifier.pk') and not self.has_hashed_pk():
                new_ids.add(hash_id(self['data.identifier.pk'], PREFIX_IDENTIFIER_PK))
                update_fields.add('data.identifier.pk')

            if self.has('data.identifier.id') and not self.has_hashed_id():
                new_ids.add(hash_id(self['data.identifier.id'], PREFIX_IDENTIFIER_ID))
                update_fields.add('data.identifier.id')

            if self.has('data.contact.email.business') and not self.has_hashed_email_id(PREFIX_EMAIL_BUSINESS):
                new_ids.add(hash_id(self['data.contact.email.business'], PREFIX_EMAIL_BUSINESS))
                update_fields.add('data.contact.email.business')

            if self.has('data.contact.email.main') and not self.has_hashed_email_id(PREFIX_EMAIL_MAIN):
                new_ids.add(hash_id(self['data.contact.email.main'], PREFIX_EMAIL_MAIN))
                update_fields.add('data.contact.email.main')

            if self.has('data.contact.email.private') and not self.has_hashed_email_id(PREFIX_EMAIL_PRIVATE):
                new_ids.add(hash_id(self['data.contact.email.private'], PREFIX_EMAIL_PRIVATE))
                update_fields.add('data.contact.email.private')

            if self.has('data.contact.phone.business') and not self.has_hashed_phone_id(PREFIX_PHONE_BUSINESS):
                new_ids.add(hash_id(self['data.contact.phone.business'], PREFIX_PHONE_BUSINESS))
                update_fields.add('data.contact.phone.business')

            if self.has('data.contact.phone.main') and not self.has_hashed_phone_id(PREFIX_PHONE_MAIN):
                new_ids.add(hash_id(self['data.contact.phone.main'], PREFIX_PHONE_MAIN))
                update_fields.add('data.contact.phone.main')

            if self.has('data.contact.phone.mobile') and not self.has_hashed_phone_id(PREFIX_PHONE_MOBILE):
                new_ids.add(hash_id(self['data.contact.phone.mobile'], PREFIX_PHONE_MOBILE))
                update_fields.add('data.contact.phone.mobile')

            if self.has('data.contact.phone.whatsapp') and not self.has_hashed_phone_id(PREFIX_PHONE_WHATSUP):
                new_ids.add(hash_id(self['data.contact.phone.whatsapp'], PREFIX_PHONE_WHATSUP))
                update_fields.add('data.contact.phone.whatsapp')

            # Update if new data
            if new_ids:
                self.ids = list(set(self.ids) | new_ids)
                return update_fields

        return None

    def fill_changed_fields(self):
        if not self.has_changes():
            return

        # Make sure that the dict is in metadata.fields
        self.set_if_not_instance('metadata.fields', {}, instance=dict)

        # Iterate and set new values. Leave old intact.
        for flat_field, change_data in self.get_change_logger().changes():  # type: str, list
            self['metadata.fields'][flat_field] = change_data
