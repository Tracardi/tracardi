from typing import Optional

from tracardi.config import tracardi
from tracardi.domain.profile import Profile
from tracardi.service.console_log import ConsoleLog
from tracardi.service.destination_orchestrator import DestinationOrchestrator


class ProfileDestinationDispatcher:

    def __init__(self, profile: Optional[Profile], console_log: ConsoleLog):
        if tracardi.enable_profile_destinations:
            self.has_profile = isinstance(profile, Profile)
            self.console_log = console_log
            self.copy = profile.model_dump(exclude={"operation": ...}) if self.has_profile else None

    async def dispatch(self, profile, session, events):
        if tracardi.enable_profile_destinations:
            do = DestinationOrchestrator(
                profile,
                session,
                events,
                self.console_log
            )
            await do.sync_destination(
                self.has_profile,
                self.copy,
            )
