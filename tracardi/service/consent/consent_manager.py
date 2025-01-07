from datetime import timedelta
from typing import Optional

from pytimeparse.timeparse import timeparse

from tracardi.domain.flat_profile import FlatProfile
from tracardi.service.collector.load.flat_profile import load_flat_profile
from tracardi.service.collector.mutation import profile as mutation_profile_db
from tracardi.service.tracking.storage.session_storage import load_session
from tracardi.common.time.date import now_in_utc
from tracardi.domain.payload.customer_consent import CustomerConsent
from tracardi.domain.consent_revoke import ConsentRevoke
from tracardi.service.storage.mysql.interface import event_source_dao
import tracardi.service.storage.mysql.interface.consent_type as consent_type_dao


async def add_consent(data: CustomerConsent, all: Optional[bool] = False):
    source = await event_source_dao.load_event_source_by_id(data.source.id)
    session = await load_session(data.session.id)

    flat_profile: FlatProfile = await load_flat_profile(data.profile.id)

    if not source or not flat_profile or not session:
        raise PermissionError("Access denied")

    if all:
        for consent_type in await consent_type_dao.load_all():
            if consent_type.auto_revoke:
                try:
                    seconds = timeparse(consent_type.auto_revoke)
                    now = now_in_utc()
                    revoke = now + timedelta(seconds=seconds)
                    revoke = ConsentRevoke(revoke=revoke)
                except Exception:
                    revoke = ConsentRevoke()

            else:
                revoke = ConsentRevoke()

            flat_profile.set_if_not_instance('consents', {}, dict)

            flat_profile['consents'][consent_type.id] = revoke.model_dump(mode="json")


    else:
        for consent, flag in data.consents.items():
            if flag:
                flat_profile['consents'][consent] = ConsentRevoke().model_dump(mode="json")
            else:
                if consent in flat_profile['consents']:
                    del flat_profile['consents'][consent]

    flat_profile['aux.consents'] = {"granted": True}
    return await mutation_profile_db.save_flat_profile(flat_profile, refresh=True)
