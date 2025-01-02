from typing import Protocol, Optional, List, Union, Set

from tracardi.domain.flat_event import FlatEvent
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.session import Session


class CollectorProtocol(Protocol):

    async def load_session(self, session_id: str, **kwargs) -> Optional[Session]:
        pass

    async def load_profile(self, profile_id: str, **kwargs) -> Optional[FlatProfile]:
        pass

    async def save_profiles(self, profiles: Union[FlatProfile, List[FlatProfile], Set[FlatProfile]], **kwargs):
        pass

    async def save_sessions(self, sessions: Union[Session, List[Session], Set[Session]], **kwargs):
        pass

    async def save_events(self, events: Union[FlatEvent, List[FlatEvent], Set[FlatEvent]], **kwargs):
        pass
