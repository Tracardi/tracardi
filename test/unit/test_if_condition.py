import asyncio

from tracardi.process_engine.tql.condition import Condition
from tracardi.service.notation.dot_accessor import DotAccessor


def test_if_condition_for_equal():
    async def main():
        dot = DotAccessor(payload={"A": {"a": 1}})

        condition = Condition()
        result = await condition.evaluate("payload@A.a==1", dot)
        assert result is True

    asyncio.run(main())


def test_if_condition_for_spaces():
    async def main():
        dot = DotAccessor(payload={"A": {"a b c": 1}})

        condition = Condition()
        result = await condition.evaluate("payload@A.\"a b c\" exists", dot)
        print(result)

    asyncio.run(main())