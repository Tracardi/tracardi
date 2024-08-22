from tracardi.service.storage.driver.elastic import session as session_db


async def load_session_from_db(session_id: str):
    return await session_db.load_by_id(session_id)


async def load_nth_last_session_for_profile(profile_id: str, offset):
    return await session_db.get_nth_last_session(
        profile_id=profile_id,
        n=offset
    )


async def refresh_session_db():
    await session_db.refresh()


async def flush_session_db():
    await session_db.flush()


async def count_sessions_online_in_db():
    return await session_db.count_online()


async def count_online_sessions_by_location_in_db():
    return await session_db.count_online_by_location()


async def count_sessions_in_db():
    return await session_db.count()
