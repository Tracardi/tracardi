import asyncio
from uuid import uuid4

import pytest

from tracardi.config import tracardi
from tracardi.context import ContextManager, ctx_id, ServerContext, Context, get_context
from tracardi.domain.user import User


def test_context():
    async def main():
        async def context1():
            ctx = ContextManager()

            await asyncio.sleep(.1)
            with pytest.raises(ValueError):
                ctx.get("b")

            ctx.set("a", Context(version="1"))
            await asyncio.sleep(.5)
            value = ctx.get("a")

            assert value.version == "1"

        async def context2():
            ctx = ContextManager()

            with pytest.raises(ValueError):
                ctx.get("b")

            ctx.set("a", Context(version="2"))
            await asyncio.sleep(.5)
            value = ctx.get("a")

            assert value.version == "2"

        with ServerContext(Context(production=True, tenant=tracardi.version.name)):
            context_handler = ctx_id.set(str(uuid4()))
            c1 = asyncio.create_task(context1())
            ctx_id.reset(context_handler)

            context_handler = ctx_id.set(str(uuid4()))
            c2 = asyncio.create_task(context2())
            ctx_id.reset(context_handler)

            await asyncio.gather(c1, c2)

    asyncio.run(main())


def test_server_context():
    ctx1 = Context(production=True, tenant=tracardi.version.name)
    ctx2 = Context(production=False, tenant=tracardi.version.name)
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
            ctx1 = Context(production=True, tenant=tracardi.version.name)
            with ServerContext(ctx1) as sc1:
                await asyncio.sleep(0.5)
                assert sc1.get_context() == ctx1

        async def context2():
            ctx2 = Context(production=False, tenant=tracardi.version.name)
            with ServerContext(ctx2) as sc2:
                await asyncio.sleep(0.5)
                assert sc2.get_context() == ctx2

        c1 = asyncio.create_task(context1())
        c2 = asyncio.create_task(context2())
        await asyncio.gather(c1, c2)

    asyncio.run(main())


def test_server_switch_context():
    fake_user = User(id="1", password="pass", name="name", roles=['market'], email="a")
    with ServerContext(Context(production=False, user=fake_user, tenant=tracardi.version.name)) as cm:
        assert cm.context.user == fake_user
        new_ctx = get_context()
        assert new_ctx.user == fake_user
        switched_ctx1 = get_context().switch_context(production=True)
        assert switched_ctx1.user == fake_user


def test_server_switch_context_async():
    fake_user1 = User(id="2", password="pass", name="name", roles=['market'], email="some")
    with ServerContext(Context(production=True, user=fake_user1, tenant=tracardi.version.name)) as ctx:
        fake_user2 = User(id="1", password="pass", name="name", roles=['market'], email="a")

        async def main():
            async def context1():
                await asyncio.sleep(0.1)
                with ServerContext(Context(production=False, user=fake_user2, tenant=tracardi.version.name)):
                    assert get_context().user == fake_user2
                    switched_ctx1 = get_context().switch_context(production=True)
                    assert switched_ctx1.user == fake_user2
                    with ServerContext(switched_ctx1) as sc1:
                        await asyncio.sleep(0.5)
                        assert sc1.get_context() == switched_ctx1

            async def context2():
                with ServerContext(Context(production=True, user=fake_user2, tenant=tracardi.version.name)):
                    assert get_context().user == fake_user2
                    switched_ctx2 = get_context().switch_context(production=False)
                    with ServerContext(switched_ctx2) as sc2:
                        await asyncio.sleep(0.5)
                        assert sc2.get_context() == switched_ctx2
                        assert sc2.get_context().user == fake_user2

            c1 = asyncio.create_task(context1())
            c2 = asyncio.create_task(context2())
            await asyncio.gather(c1, c2)

        assert ctx.context.user.id == '2'

        asyncio.run(main())


def test_context_hash():
    context = Context(production=True)
    assert hash(context) == hash((context.production, context.tenant))
