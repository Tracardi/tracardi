import asyncio
import datetime

def to_be_run():
    print("executed")


class PostponedCall:

    def __init__(self, callable, *args):
        self.callable = callable
        self.args = args
        self.wait = 2
        self.postpone = False
        self.scheduled = False

    def set_postpone(self, wait):
        self.wait = wait

    def _postpone_call(self, loop):
        print(datetime.datetime.now())
        if self.postpone:
            loop.call_later(self.wait, self._postpone_call, loop)
            self.postpone = False
        else:
            self.callable(*self.args)
            self.scheduled = False

    def run(self, loop):
        if self.scheduled is False:
            loop.call_later(self.wait, self._postpone_call, loop)
            self.scheduled = True
        else:
            self.postpone = True

def main():
    loop = asyncio.get_event_loop()

    # Schedule the first call
    p = PostponedCall(to_be_run)
    p.run(loop)

    loop.run_forever()


main()
