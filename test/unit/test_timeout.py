import pytest
import asyncio

from com_tracardi.decorator.timeout_decorator import timeout


@pytest.mark.asyncio
async def test_timeout_context_does_timeout():
    # This test verifies that the TimeoutError occurs when expected
    with pytest.raises(asyncio.TimeoutError):
        @timeout(0.1)
        async def xxx():
            await asyncio.sleep(0.5)
        await xxx()

# @pytest.mark.asyncio
# async def test_timeout_context_exactly_at_limit():
#     # This test checks if the code block completes exactly at the timeout limit
#     try:
#         async with timeout(1):
#             await asyncio.sleep(1)
#     except asyncio.TimeoutError:
#         pytest.fail("Timeout occurred unexpectedly.")
