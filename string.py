from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result

class MyPlugin(ActionRunner):  # 


    async def run(self, payload: dict, in_edge=None):  # 


        if self.event.type == "my-event":
            return Result(port="MyEvent", value=payload)  # 


        else:
            return Result(port="NotMyEvent", value={})  # 

