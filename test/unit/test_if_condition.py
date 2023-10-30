import asyncio

from tracardi.domain.profile import Profile
from tracardi.process_engine.tql.condition import Condition
from tracardi.service.notation.dot_accessor import DotAccessor


def test_if_condition_for_equal():
    async def main():
        dot = DotAccessor(payload={"A": {"a": 1}}, profile=Profile(id="abc"))

        condition = Condition()
        result = await condition.evaluate("payload@A.a==1", dot)
        assert result is True
        condition.parse("profile@id == \"abc\"")
        result = await condition.evaluate("profile@id = \"abc\"", dot)
        assert result is True
    asyncio.run(main())


def test_if_condition_for_spaces():
    async def main():
        dot = DotAccessor(payload={"A": {"a b c": 1}})

        condition = Condition()
        result = await condition.evaluate('payload@A["a b c"] exists', dot)
        assert result is True
        result = await condition.evaluate('payload@A["a b c"] == 1', dot)
        assert result is True
        result = await condition.evaluate('payload@A["a @b c"] exists', dot)
        assert result is False
        result = await condition.evaluate('payload@A["a[\\" b@ c"] exists', dot)
        assert result is False

    asyncio.run(main())
