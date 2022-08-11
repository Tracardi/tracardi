import logging
from typing import List
from uuid import uuid4

from pydantic import ValidationError

from tracardi.config import tracardi
from tracardi.domain.session import Session
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.driver import storage

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def correct_session(session_id) -> List[str]:

    """
    This is a recovery procedure in case there are duplicated sessions in the index.
    It copies the duplicated session data and creates new one with the different id. Old session is
    removed. If the duplicated session is corrupted it will be removed.

    Returns list of profile ids that were connected to the sessions.
    """

    referenced_profiles_ids = []
    for _session_record in await storage.driver.session.load_duplicates(session_id):
        try:
            _session_profile_id = _session_record['profile']['id']
        except KeyError:
            # This is corrupted session. Session must have profile id
            await storage.driver.session.delete(_session_record['id']),
            await storage.driver.session.refresh()
            continue

        if _session_profile_id not in referenced_profiles_ids:

            # If there are multiple session with the same profile id. Create new session with new id.
            # And delete all old session. This merges all duplicated session into 1 session.

            referenced_profiles_ids.append(_session_profile_id)
            try:
                _session = Session(**_session_record)
                _session.id = str(uuid4())

                result = await storage.driver.session.save(_session)
                if result.saved != 1:
                    raise RuntimeError(f"Could not recreate session {_session_record['id']}")
                else:
                    logger.warning(f"Session {_session_record['id']} recreated with new id {_session.id}")
                await storage.driver.session.refresh()

                # Find all events with old session and current profile id and
                # change session id to new session

                await storage.driver.event.reassign_session(
                    old_session_id=_session_record['id'],
                    new_session_id=_session.id,
                    profile_id=_session_profile_id
                )

                # Delete conflicting session from all indices

                await storage.driver.session.delete(_session_record['id']),
                await storage.driver.session.refresh()
                logger.warning(f"Session {_session_record['id']} deleted. It was recreated as {_session.id}")

            except ValidationError as e:
                logger.error(f"Could not recreate session from the data read from index. The following error "
                             f"occurred: {str(e)}")
            except Exception as e:
                logger.error(str(e))

    return referenced_profiles_ids
