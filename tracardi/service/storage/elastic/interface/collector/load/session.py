from tracardi.service.storage.elastic.dal.session import flush, refresh, get_nth_last_session, load_by_id,\
    count_online, count_online_by_location, count


async def load_session_from_db(session_id: str):
    return await load_by_id(session_id)


async def load_nth_last_session_for_profile(profile_id: str, offset):
    return await get_nth_last_session(
        profile_id=profile_id,
        n=offset
    )


async def refresh_session_db():
    await refresh()


async def flush_session_db():
    await flush()


async def count_sessions_online_in_db():
    return await count_online()


async def count_online_sessions_by_location_in_db():
    return await count_online_by_location()


async def count_sessions_in_db():
    return await count()
