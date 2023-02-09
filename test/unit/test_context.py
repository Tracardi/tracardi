import asyncio
from uuid import uuid4

from tracardi.context import ContextManager, ctx_id, ServerContext, Context, fake_admin


def test_context():

    async def main():
        async def context1():
            ctx = ContextManager()

            await asyncio.sleep(.1)
            value = ctx.get("b")
            assert value is None

            ctx.set("a", 1)
            await asyncio.sleep(.5)
            value = ctx.get("a")

            assert value == 1

        async def context2():
            ctx = ContextManager()

            value = ctx.get("b")
            assert value is None

            ctx.set("a", 2)
            await asyncio.sleep(.5)
            value = ctx.get("a")

            assert value == 2

        context_handler = ctx_id.set(str(uuid4()))
        c1 = asyncio.create_task(context1())
        ctx_id.reset(context_handler)

        context_handler = ctx_id.set(str(uuid4()))
        c2 = asyncio.create_task(context2())
        ctx_id.reset(context_handler)

        await asyncio.gather(c1, c2)

    asyncio.run(main())


def test_server_context():
    ctx1 = Context(production=True, user=fake_admin)
    ctx2 = Context(production=False)
    with ServerContext(ctx1) as sc1:
        assert sc1.get_context() == ctx1
        with ServerContext(ctx2) as sc2:
            assert sc2.get_context() == ctx2
            assert sc1.get_context() == ctx2
        assert sc1.get_context() == ctx1


def test_server_context_async():

    async def main():
        async def context1():
            await asyncio.sleep(0.1)
            ctx1 = Context(production=True, user=fake_admin)
            with ServerContext(ctx1) as sc1:
                await asyncio.sleep(0.5)
                assert sc1.get_context() == ctx1

        async def context2():
            ctx2 = Context(production=False)
            with ServerContext(ctx2) as sc2:
                await asyncio.sleep(0.5)
                assert sc2.get_context() == ctx2

        c1 = asyncio.create_task(context1())
        c2 = asyncio.create_task(context2())
        await asyncio.gather(c1, c2)

    asyncio.run(main())





