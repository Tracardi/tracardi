# from app.domain.action import ActionEvaluator
from app.domain.event import Event


class CopyAllAction:

    async def run(self, event: Event, config: dict):
        event.profile.properties.public.update(event.properties)
        return event.profile
