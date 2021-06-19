from pydantic import BaseModel
from tracardi_plugin_sdk.action_runner import ActionRunner

from tracardi_plugin_sdk.domain.result import Result


class Say(BaseModel):
    id: int
    name: str


class task1(ActionRunner):
    def __init__(self, condition):
        self.condition = condition

    async def run(self, payload):
        print("Hello 1!")
        print("conditional=", self.condition)
        print("payload", payload)
        if self.condition == 'abc':
            return Result(port="TRUE", value=["1t"]), Result(port="FALSE", value=None)
        else:
            return Result(port="FALSE", value=["1f"]), Result(port="TRUE", value=None)


class task2(ActionRunner):

    async def run(self, NODE2_i):
        print("Hello, 2!")
        print(NODE2_i)
        NODE2_i += [2]
        return Result(port="NODE2_o", value=NODE2_i)


class task3(ActionRunner):

    async def run(self, NODE3_i):
        print("Hello, 3!")
        print(NODE3_i)
        NODE3_i += [3]
        return Result(port="NODE3_o", value=NODE3_i)


class task4(ActionRunner):

    async def run(self, NODE4_2_i=None, NODE4_3_i=None, NODE4_1_i=None):
        print("Hello, 4!")
        print("1={} 2={} 3={}".format(NODE4_1_i, NODE4_2_i, NODE4_3_i))
        if NODE4_2_i:
            NODE4_2_i += [4]
        if NODE4_3_i:
            NODE4_3_i += [4]
        if NODE4_1_i:
            NODE4_1_i += [4]
        return Result(port="NODE4_o", value=(NODE4_2_i, NODE4_3_i, NODE4_1_i))


class task7(ActionRunner):

    async def run(self, payload):
        print("Hello, 2!")
        return Result(port="NODE2_o", value=[2])

class task8(ActionRunner):

    async def run(self, INP1=None, INP2=None, INP3=None):
        print("Hello, 4!")
        print("1={} 2={} 3={}".format(INP1, INP2, INP3))
        if INP1:
            INP1 += [4]
        if INP2:
            INP2 += [4]
        if INP3:
            INP3 += [4]
        return Result(port="NODE4_o", value=(INP1, INP2, INP3))


class task5(ActionRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = 1

    async def run(self, **kwargs):
        print("Hello, 5!")
        print(kwargs)
        print()
        return Result(port="NODE5_o", value=5)


class task6(ActionRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = 1

    async def run(self, **kwargs):
        print("Hello, 6!")
        print(kwargs)
        return Result(port="say6_o", value=6)
