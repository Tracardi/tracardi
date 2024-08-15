from datetime import timedelta
from typing import Optional

from fastapi import HTTPException
from pytimeparse.timeparse import timeparse

from tracardi.service.storage.mysql.mapping.consent_type_mapping import map_to_consent_type
from tracardi.service.tracking.storage.session_storage import load_session
from tracardi.service.utils.date import now_in_utc
from tracardi.domain.payload.customer_consent import CustomerConsent
from tracardi.domain.profile import ConsentRevoke
from tracardi.service.storage.mysql.service.consent_type_service import ConsentTypeService

from tracardi.service.storage.mysql.interface import event_source_dao
from tracardi.service.storage.interface import profile_mutation_dao
from tracardi.service.storage.interface import profile_load_dao


async def add_consent(data: CustomerConsent, all: Optional[bool] = False):
    source = await event_source_dao.load_event_source_by_id(data.source.id)
    session = await load_session(data.session.id)

    profile = await profile_load_dao.load_profile(data.profile.id)

    if not source or not profile or not session:
        raise HTTPException(status_code=403, detail="Access denied")

    if all:
        cts = ConsentTypeService()
        consent_type_records = await cts.load_all()
        for consent_type in consent_type_records.map_to_objects(map_to_consent_type):
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

            profile.consents[consent_type.id] = revoke

    else:
        for consent, flag in data.consents.items():
            if flag:
                profile.consents[consent] = ConsentRevoke()
            else:
                if consent in profile.consents:
                    del profile.consents[consent]

    profile.aux['consents'] = {"granted": True}
    return await profile_mutation_dao.save_profile(profile, refresh=True)
