from uuid import uuid4

from typing import Optional, Tuple, Union

from tracardi.common.security.hashing.hasher import get_shadow_session_id
from tracardi.common.tools.getters import get_entity_id
from tracardi.domain import ExtraInfo
from tracardi.domain.entity import PrimaryEntity, DefaultEntity, Entity
from tracardi.domain.flat_session import FlatSession
from tracardi.common.logging.log_handler import get_logger
from tracardi.domain.flat_profile import FlatProfile
from tracardi.service.collector.load.flat_profile import load_flat_profile

logger = get_logger(__name__)


def _copy_tracker_payload_session_metadata(tracker_session: DefaultEntity, flat_session: FlatSession) -> FlatSession:
    if tracker_session and isinstance(tracker_session, DefaultEntity) and tracker_session.metadata:
        if tracker_session.metadata.insert:
            flat_session['metadata.time.insert'] = tracker_session.metadata.insert
        if tracker_session.metadata.update:
            flat_session['metadata.time.update'] = tracker_session.metadata.update
        if tracker_session.metadata.create:
            flat_session['metadata.time.create'] = tracker_session.metadata.create
    return flat_session


def _fill_flat_profile_metadata(tracker_profile, flat_profile: FlatProfile):
    # Copy metadata to new profile
    if tracker_profile and tracker_profile.metadata:
        if tracker_profile.metadata.insert:
            flat_profile['metadata.time.insert'] = tracker_profile.metadata.insert
        if tracker_profile.metadata.update:
            flat_profile['metadata.time.update'] = tracker_profile.metadata.update
        if tracker_profile.metadata.create:
            flat_profile['metadata.time.create'] = tracker_profile.metadata.create


def _create_default_profile(tracker_profile, static: bool) -> FlatProfile:
    if static:
        profile_id = tracker_profile.id
    else:
        profile_id = str(uuid4())

    flat_profile = FlatProfile.new(id=profile_id)
    flat_profile.monitor_changes(True)

    # Copy metadata to new profile
    _fill_flat_profile_metadata(tracker_profile, flat_profile)

    return flat_profile


def _has_tracker_payload_profile_id(tracker_profile) -> bool:
    return tracker_profile is not None and isinstance(tracker_profile.id, str) and tracker_profile.id.strip() != ""


def _has_profile_id_in_session(flat_session: FlatSession) -> bool:
    return (flat_session and flat_session.get('profile',None) and isinstance(flat_session.get('profile.id', None), str)
            and flat_session['profile.id'].strip() != "")


def _profile_consistency_check(requested_profile_id: str, profile: FlatProfile):
    if profile.id != requested_profile_id and requested_profile_id not in profile.ids:
        raise ValueError(f"Loading of profile failed. Some inconsistent profile loaded. "
                         f"Requested profile (ID: {requested_profile_id}), loaded profile (ID: {profile.id} "
                         f"with profile.ids={profile.ids}). "
                         f"Requested id could not be found in any ID collection.")


def _resolve_conflicts(tracker_session: Entity, requested_profile_id, loaded_session_profile_id, profile: FlatProfile,
                       flat_session: FlatSession) -> Tuple[FlatSession, Entity]:
    no_profiles_conflict = loaded_session_profile_id in profile.ids or loaded_session_profile_id == profile.id

    if not no_profiles_conflict:
        # The first attempt to resolve this issue was on the session loading level.
        # But we did not have profile loaded, so we are resolving it again.

        # Force new session ID. Create shadow session
        shadow_session_id = get_shadow_session_id(flat_session.id)

        # Create new session, to protect old session
        flat_session = FlatSession.new(id=shadow_session_id, profile_id=profile.id)
        _copy_tracker_payload_session_metadata(tracker_session, flat_session)

        # Update tracker payload
        tracker_session.id = flat_session.id

        logger.warning(f"Conflicting data in tracker payload. Session exists but belongs to profile "
                       f"profile (ID: {flat_session['profile.id']}) that has not the same ID as requested in payload profile "
                       f"(ID: {loaded_session_profile_id}). "
                       f"New session ID ({flat_session.id}) created with attached existing in DB profile "
                       f"(ID {flat_session['profile.id']}).",
                       extra=ExtraInfo.build(origin='profile-loading', profile_id=profile.id)
                       )
    return flat_session, tracker_session


def _load_default_profile(tracker_profile, flat_session: FlatSession, static: bool) -> Tuple[FlatProfile, FlatSession, PrimaryEntity]:
    # Create new profile
    flat_profile = _create_default_profile(tracker_profile, static)

    assert flat_profile.has('operation.new') and flat_profile['operation.new'] is True
    assert flat_profile.has('operation.update') and flat_profile['operation.update'] is True

    if flat_profile:
        if not isinstance(tracker_profile, PrimaryEntity):
            tracker_profile = PrimaryEntity(id=flat_profile.id)
        else:
            tracker_profile.id = flat_profile.id

    if flat_session.get('profile.id', None) != flat_profile.id:
        flat_session['profile.id'] = flat_profile.id

    return flat_profile, flat_session, tracker_profile


async def _load_profile_by_session_profile_id(tracker_profile, flat_session: FlatSession, static: bool) -> Tuple[
    FlatProfile, FlatSession, PrimaryEntity]:
    # Check if the profile.id from session is not empty

    if not flat_session.get('profile.id',None):
        return _load_default_profile(tracker_profile, flat_session, static)

    requested_profile_id = flat_session['profile.id']

    # ID exists in session, load profile with session.profile.id
    flat_profile: Optional[FlatProfile] = await load_flat_profile(requested_profile_id)

    if flat_profile is not None:

        _profile_consistency_check(requested_profile_id, flat_profile)

        # Update client profile ids
        if tracker_profile:
            tracker_profile.id = flat_profile.id
        else:
            tracker_profile = PrimaryEntity(id=flat_profile.id)

        flat_session['profile.id'] = flat_profile.id  # Assign profile id it could be different then requested_profile_id (it could load form profile.ids)

        return flat_profile, flat_session, tracker_profile

    # Profile id delivered but profile does not exist in storage.
    # ID was forged. Create new.

    return _load_default_profile(tracker_profile, flat_session, static)


async def _load_profile_by_payload_profile_id(tracker_profile, tracker_session, flat_session: FlatSession, static: bool) -> \
Tuple[Tuple[FlatProfile, FlatSession, PrimaryEntity], Entity]:
    # We have valid profile definition
    requested_profile_id = get_entity_id(tracker_profile)
    loaded_session_profile_id = flat_session.get('profile.id',None)  # Session id delivered in payload

    # ID exists, load profile from storage
    flat_profile: Optional[FlatProfile] = await load_flat_profile(requested_profile_id)

    if flat_profile is not None:
        _profile_consistency_check(requested_profile_id, flat_profile)

        # Check if the loaded profile has not different ID.
        # It may happen if profile is loaded by IDS and the Profile ID is different

        # Update Tracker Profile ID
        tracker_profile.id = flat_profile.id

        # Update Tracker Session Profile ID
        flat_session['profile.id'] = flat_profile.id

        # Check if there is a conflict in IDS.
        # Session ID exists but do not point to profile ID from tracker payload

        flat_session, tracker_session = _resolve_conflicts(tracker_session, requested_profile_id, loaded_session_profile_id,
                                                      flat_profile, flat_session)

        return (flat_profile, flat_session, tracker_profile), tracker_session

    # Profile missing in db
    conflicting_profiles = flat_session['profile.id'] != get_entity_id(tracker_profile)
    if conflicting_profiles:  # if there is different profile in session lets try to load this profile
        return await _load_profile_by_session_profile_id(tracker_profile, flat_session, static), tracker_session
    else:
        return _load_default_profile(tracker_profile, flat_session, static), tracker_session


async def _get_profile(tracker_profile: Optional[PrimaryEntity], tracker_session: Optional[DefaultEntity],
                       flat_session: FlatSession, static: bool) -> Tuple[FlatProfile, FlatSession, PrimaryEntity, DefaultEntity]:
    # Check consistency

    if static and not get_entity_id(tracker_profile):
        raise ValueError("Can not use static profile id without profile.id.")

    # Let's check what was sent

    if _has_tracker_payload_profile_id(tracker_profile):

        # Tracked Profile ID exists, start loading profile with tracker_payload.profile.id
        # And do the regular fallback

        (flat_profile, flat_session, tracker_profile), tracker_session = await _load_profile_by_payload_profile_id(
            tracker_profile,
            tracker_session,
            flat_session,
            static)

    elif _has_profile_id_in_session(flat_session):

        # Fallback to loading from session with regular fallback

        flat_profile, flat_session, tracker_profile = await _load_profile_by_session_profile_id(
            tracker_profile,
            flat_session,
            static)

    else:

        flat_profile, flat_session, tracker_profile = _load_default_profile(
            tracker_profile,
            flat_session,
            static)

    return flat_profile, flat_session, tracker_profile, tracker_session


async def get_profile_and_session(
        flat_session: FlatSession,
        static: bool,
        profile_less: bool,
        tracker_profile: Optional[PrimaryEntity],
        tracker_session: Optional[Union[DefaultEntity, Entity]],

) -> Tuple[Optional[FlatProfile], FlatSession, PrimaryEntity, DefaultEntity]:
    """
    Returns session. Creates profile if it does not exist.If it exists connects session with profile.
    """

    if flat_session is None:  # loaded session is empty
        raise ValueError("Session must exist at this point")

    if profile_less is True:
        return None, flat_session, tracker_profile, tracker_session

    # There is profile

    # Load profile
    # Calling self._get_profile(session) revolves inconsistencies such as - missing ids.
    flat_profile, flat_session, tracker_profile, tracker_session = await _get_profile(tracker_profile,
                                                                                      tracker_session,
                                                                                      flat_session,
                                                                                      static=static)

    # Check consistency

    if flat_session and tracker_session:
        # Correct session ID are when they are the same or a shadowed session was created when there was a conflict.
        correct_session = tracker_session.id == flat_session.id or flat_session.id == get_shadow_session_id(flat_session.id)
        if not correct_session:
            logger.warning(
                f"Session ID ({tracker_session.id}) in Tracker Payload does not equal to "
                f"loaded session ({flat_session.id}) ")

    if flat_profile and tracker_profile:
        if tracker_profile.id != flat_profile.id:
            raise AssertionError(f"Profile ID ({tracker_profile.id}) in Tracker Payload does not equal "
                                 f"to loaded profile ({flat_profile.id}) ")
        flat_session_profile_id = flat_session.get('profile.id', None)
        if flat_session_profile_id != flat_profile.id:
            raise AssertionError(
                f"Profile ID in session ({flat_session_profile_id}) does not equal to loaded profile ({flat_profile.id}) ")

    return flat_profile, flat_session, tracker_profile, tracker_session


async def load_profile_and_session1(
        flat_session: FlatSession,
        is_static_profile_id: bool,
        profile_less: bool,  # tracker_payload.profile_less
        tracker_profile: Optional[PrimaryEntity],  # tracker_payload.profile
        tracker_session: Optional[Union[DefaultEntity, Entity]],  # tracker_payload.session

) -> Tuple[Optional[FlatProfile], Optional[FlatSession], Optional[PrimaryEntity], Optional[Union[DefaultEntity, Entity]]]:
    # Check if profile should have static ID

    if profile_less is True:
        flat_profile = None
    else:
        flat_profile, flat_session, tracker_profile, tracker_session = await get_profile_and_session(
            flat_session,
            is_static_profile_id,
            profile_less,
            tracker_profile,
            tracker_session,
        )

    # AT THIS POINT Profile is None only if is profile-less

    # Check if necessary hashed ID are present and add missing
    if flat_profile is not None:

        if flat_profile.hash_all_allowed_pii_as_ids():
            flat_profile.mark_for_update()

        # Add Ids from payload
        if isinstance(tracker_profile, PrimaryEntity) and tracker_profile.ids:
            payload_ids = set(tracker_profile.ids)
            profile_ids = set(flat_profile.ids) if flat_profile.ids else set()
            payload_ids.update(profile_ids)
            # Check if update needed
            if profile_ids != payload_ids:
                # Something was added
                flat_profile.ids = list(payload_ids)
                flat_profile.mark_for_update()
                # TODO This may need to add changed fields and mark for merge but we do not know fields as ids are just numbers.

    return flat_profile, flat_session, tracker_profile, tracker_session
