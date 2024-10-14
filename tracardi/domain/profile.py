import uuid
from typing import Optional, List, Dict, Any, Set

from pydantic import PrivateAttr

from .entity import PrimaryEntity
from .metadata import ProfileMetadata
from .profile_data import ProfileData, FIELD_TO_PROPERTY_MAPPING, PREFIX_IDENTIFIER_ID, PREFIX_IDENTIFIER_PK
from .storage_record import RecordMetadata
from .time import ProfileTime
from .value_object.operation import Operation
from .value_object.storage_info import StorageInfo
from ..config import tracardi
from ..service.dot_notation_converter import DotNotationConverter
from .profile_stats import ProfileStats
from ..service.tracking.profile_pii_hashing import get_allowed_piis_to_be_hashed_as_ids
from ..service.utils.date import now_in_utc
from tracardi.domain.profile_data import PREFIX_EMAIL_BUSINESS, PREFIX_EMAIL_MAIN, PREFIX_EMAIL_PRIVATE, \
    PREFIX_PHONE_MAIN, PREFIX_PHONE_BUSINESS, PREFIX_PHONE_MOBILE, PREFIX_PHONE_WHATSUP
from ..service.utils.hasher import hash_id, has_hash_id
from tracardi.domain.consent_revoke import ConsentRevoke


class Profile(PrimaryEntity):
    ids: Optional[List[str]] = []
    metadata: Optional[ProfileMetadata] = ProfileMetadata(
        time=ProfileTime()
    )
    operation: Optional[Operation] = Operation()
    stats: ProfileStats = ProfileStats()
    traits: Optional[dict] = {}
    segments: Optional[List[str]] = []
    interests: Optional[dict] = {}
    consents: Optional[Dict[str, ConsentRevoke]] = {}
    active: bool = True
    aux: Optional[dict] = {}
    data: Optional[ProfileData] = ProfileData()
    trash: Optional[dict] = None

    _updated_in_workflow: bool = PrivateAttr(False)
    _list_of_pii_to_be_hashed_ids: Optional[str] = PrivateAttr(None)

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._add_id_to_ids()

    def is_new(self) -> bool:
        return self.operation.new

    def set_new(self, flag=True):
        self.operation.new = flag

    def set_updated(self, flag=True):
        self.operation.update = flag

    def is_segmented(self, flag):
        self.operation.segment = flag

    def mark_as_merged(self):
        self.metadata.system.reset_auto_merge_fields()

    def set_merge_key(self, merge_key):
        self.operation.merge = merge_key

    def get_merge_keys(self) -> list:
        return self.operation.merge

    def has_consents_set(self) -> bool:
        return 'consents' in self.aux and 'granted' in self.aux['consents'] and self.aux['consents']['granted'] is True

    def has_hashed_email_id(self, type: str = None) -> bool:
        """
        This only checks if there are prefixed ids. It does not check if they are correct. APM does it.
        """
        if type is None:
            type = self.data.contact.email.email_types()

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

    def _add_auto_merge_hashed_id(self, flat_field) -> Optional[str]:
        field_closure = FIELD_TO_PROPERTY_MAPPING.get(flat_field, None)
        if field_closure:
            value, prefix = field_closure(self)

            value = value.strip().lower()

            if self.ids is None:
                self.ids = []

            # Add new hashed Id

            if value:
                _hash_id = hash_id(value, prefix)

                # Do not add value if exists
                if has_hash_id(_hash_id, self.ids):
                    return None

                self.ids.append(_hash_id)

                return flat_field

        return None

    def set_metadata_fields_timestamps(self, field_timestamp_manager: Dict[str, List]) -> Set[str]:
        added_hashed_ids = set()
        for flat_field, timestamp_data in field_timestamp_manager.items():
            self.metadata.fields[flat_field] = timestamp_data
            # If enabled hash emails and phone on field change
            if tracardi.is_apm_on():
                added_hashed_id = self._add_auto_merge_hashed_id(flat_field)
                if added_hashed_id:
                    added_hashed_ids.add(added_hashed_id)

        return added_hashed_ids

    def has_hashed_phone_id(self, type: str = None) -> bool:

        if type is None:
            type = self.data.contact.phone.phone_types()

        for id in self.ids:
            if id.startswith(type):
                return True
        return False

    def fill_meta_data(self):
        """
        Used to fill metadata with default current index and id.
        """
        self._fill_meta_data('profile')

    def set_updated_in_workflow(self, state=True):
        self._updated_in_workflow = state

    def is_updated_in_workflow(self) -> bool:
        return self._updated_in_workflow

    def set_list_of_allowed_pii_to_be_hashed_ids(self, allow: str):
        self._list_of_pii_to_be_hashed_ids = allow

    def has_list_of_allowed_pii_to_be_hashed_ids(self) -> List[str]:
        if not self._list_of_pii_to_be_hashed_ids:
            return []
        return self._list_of_pii_to_be_hashed_ids.split(',')

    def serialize(self):
        return {
            "profile": self.model_dump(),
            "storage": self.get_meta_data().model_dump()
        }

    def mark_for_update(self):
        self.operation.update = True
        self.metadata.time.update = now_in_utc()
        self.data.compute_anonymous_field()
        self.set_updated_in_workflow()

    def is_merged(self, profile_id) -> bool:
        return profile_id != self.id and profile_id in self.ids

    @staticmethod
    def deserialize(serialized_profile: dict) -> 'Profile':
        profile = Profile(**serialized_profile['profile'])
        profile.set_meta_data(RecordMetadata(**serialized_profile['storage']))
        return profile

    def replace(self, profile: 'Profile'):
        if isinstance(profile, Profile):
            # Make segments unique
            profile.segments = list(set(profile.segments))

            self.id = profile.id
            self.primary_id = profile.primary_id
            self.ids = profile.ids
            self.metadata = profile.metadata
            self.operation = profile.operation
            self.stats = profile.stats
            self.traits = profile.traits
            self.segments = profile.segments
            self.consents = profile.consents
            self.active = profile.active
            self.interests = profile.interests
            self.aux = profile.aux
            self.data = profile.data

    def get_merge_key_values(self) -> List[tuple]:
        converter = DotNotationConverter(self)
        return [converter.get_profile_file_value_pair(key) for key in self.operation.merge]

    def _get_merging_keys_and_values(self):
        merge_key_values = self.get_merge_key_values()

        # Add keyword
        merge_key_values = [(field, value) for field, value in merge_key_values if value is not None]

        return merge_key_values

    def _add_id_to_ids(self):
        if self.id not in self.ids:
            self.ids.append(self.id)
            self.operation.update = True

    def get_consent_ids(self) -> Set[str]:
        return set(self.consents.keys())

    def increase_visits(self, value=1):
        self.stats.visits += value
        self.operation.update = True

    def increase_views(self, value=1):
        self.stats.views += value
        self.operation.update = True

    def increase_interest(self, interest, value=1):
        if interest in self.interests:
            self.interests[interest] += value
        else:
            self.interests[interest] = value
        self.operation.update = True

    def decrease_interest(self, interest, value=1):
        if interest in self.interests:
            self.interests[interest] -= value
            self.operation.update = True

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'profile',
            Profile,
            exclude={"operation": ...},
            multi=True
        )

    def has_not_saved_changes(self) -> bool:
        return self.operation.new or self.needs_update()

    def needs_update(self) -> bool:
        return self.operation.needs_update()

    def needs_segmentation(self) -> bool:
        return self.operation.needs_segmentation()

    def needs_merging(self):
        return self.operation.needs_merging()

    @staticmethod
    def new(id: Optional[id] = None) -> 'Profile':
        """
        @return Profile
        """

        _now = now_in_utc()

        profile = Profile(
            id=str(uuid.uuid4()) if not id else id,
            metadata=ProfileMetadata(time=ProfileTime(
                create=_now,
                insert=_now
            ))
        )
        profile.fill_meta_data()
        profile.set_new()
        return profile

    # --------------- ID Hashing -----------------------

    def hash_all_allowed_pii_as_ids(self) -> bool:

        """ Used for creating hashed IDS """

        # Check for missing hash IDS, and create missing, Mark for update
        changed_fields = self._create_auto_merge_hashed_ids()
        if changed_fields:
            # Add missing fields to auto_merge
            self.metadata.system.set_auto_merge_fields(changed_fields)
            return True

        return False

    def _create_auto_merge_hashed_ids(self) -> Optional[set]:

        """
        It will update missing hashes if the APM is ON and there is no defined identification event type.
        If the identification event type is defined only that event type can create ID hashes from emails, etc.
        """

        if tracardi.is_apm_on():

            new_ids = set()
            update_fields = set()
            allowed_piis = get_allowed_piis_to_be_hashed_as_ids()

            if 'data.identifier.pk' in allowed_piis and self.data.identifier.pk and not self.has_hashed_pk():
                new_ids.add(hash_id(self.data.identifier.pk, PREFIX_IDENTIFIER_PK))
                update_fields.add('data.identifier.pk')

            if 'data.identifier.id' in allowed_piis and self.data.identifier.id and not self.has_hashed_id():
                new_ids.add(hash_id(self.data.identifier.id, PREFIX_IDENTIFIER_ID))
                update_fields.add('data.identifier.id')

            if 'data.contact.email.business' in allowed_piis and self.data.contact.email.has_business() and not self.has_hashed_email_id(
                    PREFIX_EMAIL_BUSINESS):
                new_ids.add(hash_id(self.data.contact.email.business, PREFIX_EMAIL_BUSINESS))
                update_fields.add('data.contact.email.business')

            if 'data.contact.email.main' in allowed_piis and self.data.contact.email.has_main() and not self.has_hashed_email_id(
                    PREFIX_EMAIL_MAIN):
                new_ids.add(hash_id(self.data.contact.email.main, PREFIX_EMAIL_MAIN))
                update_fields.add('data.contact.email.main')

            if 'data.contact.email.private' in allowed_piis and self.data.contact.email.has_private() and not self.has_hashed_email_id(
                    PREFIX_EMAIL_PRIVATE):
                new_ids.add(hash_id(self.data.contact.email.private, PREFIX_EMAIL_PRIVATE))
                update_fields.add('data.contact.email.private')

            if 'data.contact.phone.business' in allowed_piis and self.data.contact.phone.has_business() and not self.has_hashed_phone_id(
                    PREFIX_PHONE_BUSINESS):
                new_ids.add(hash_id(self.data.contact.phone.business, PREFIX_PHONE_BUSINESS))
                update_fields.add('data.contact.phone.business')

            if 'data.contact.phone.main' in allowed_piis and self.data.contact.phone.has_main() and not self.has_hashed_phone_id(
                    PREFIX_PHONE_MAIN):
                new_ids.add(hash_id(self.data.contact.phone.main, PREFIX_PHONE_MAIN))
                update_fields.add('data.contact.phone.main')

            if 'data.contact.phone.mobile' in allowed_piis and self.data.contact.phone.has_mobile() and not self.has_hashed_phone_id(
                    PREFIX_PHONE_MOBILE):
                new_ids.add(hash_id(self.data.contact.phone.mobile, PREFIX_PHONE_MOBILE))
                update_fields.add('data.contact.phone.mobile')

            if 'data.contact.phone.whatsapp' in allowed_piis and self.data.contact.phone.has_whatsapp() and not self.has_hashed_phone_id(
                    PREFIX_PHONE_WHATSUP):
                new_ids.add(hash_id(self.data.contact.phone.whatsapp, PREFIX_PHONE_WHATSUP))
                update_fields.add('data.contact.phone.whatsapp')

            # Update if new data
            if new_ids:
                self.ids = list(set(self.ids) | new_ids)
                return update_fields

        return None
