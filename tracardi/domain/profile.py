import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, Set
from pydantic import BaseModel, ValidationError
from dateutil import parser

from .entity import Entity
from .metadata import ProfileMetadata
from .profile_data import ProfileData
from .storage_record import RecordMetadata
from .time import ProfileTime
from .value_object.operation import Operation
from .value_object.storage_info import StorageInfo
from ..service.dot_notation_converter import DotNotationConverter
from .profile_stats import ProfileStats


class ConsentRevoke(BaseModel):
    revoke: Optional[datetime] = None


class CustomMetric(BaseModel):
    next: datetime
    timestamp: datetime
    value: Any = None

    def expired(self) -> bool:
        return datetime.utcnow() > self.next

    def changed(self, value) -> bool:
        return value != self.value


class Profile(Entity):
    ids: Optional[List[str]] = []
    metadata: Optional[ProfileMetadata] = ProfileMetadata(time=ProfileTime(insert=datetime.utcnow()))
    operation: Optional[Operation] = Operation()
    stats: ProfileStats = ProfileStats()
    traits: Optional[dict] = {}
    segments: Optional[List[str]] = []
    interests: Optional[dict] = {}
    consents: Optional[Dict[str, ConsentRevoke]] = {}
    active: bool = True
    aux: Optional[dict] = {}
    data: Optional[ProfileData] = ProfileData()

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._add_id_to_ids()

    def serialize(self):
        return {
            "profile": self.model_dict(),
            "storage": self.get_meta_data().model_dict()
        }

    def has_metric(self, metric_name) -> bool:
        return metric_name in self.data.metrics.custom

    def need_metric_computation(self, metric_name) -> bool:
        if not self.has_metric(metric_name):
            return False

        if 'next' not in self.data.metrics.custom[metric_name]:
            return True

        if not isinstance(self.data.metrics.custom[metric_name], dict):
            print(f"ERROR: Metric {metric_name} is not dict.")
            return False

        try:
            metric = CustomMetric(**self.data.metrics.custom[metric_name])
        except ValidationError as e:
            print(str(e))
            return False

        return metric.expired()

    def get_next_metric_computation_date(self) -> Optional[datetime]:

        if not self.data.metrics.custom:
            return None

        all_next_dates = []
        for _, _metric_data in self.data.metrics.custom.items():
            if 'next' in _metric_data:
                _next = _metric_data['next']
                if isinstance(_next, str):
                    _next = parser.parse(_next)

                if not isinstance(_next, datetime):
                    print("err")

                all_next_dates.append(_next)
        return min(all_next_dates)

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
        return set([consent_id for consent_id, _ in self.consents.items()])

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

    @staticmethod
    def new(id: Optional[id] = None) -> 'Profile':
        """
        @return Profile
        """
        return Profile(
            id=str(uuid.uuid4()) if not id else id,
            metadata=ProfileMetadata(time=ProfileTime(insert=datetime.utcnow()))
        )
