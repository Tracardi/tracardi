from datetime import datetime


class PostponedCall:

    def __init__(self, callable, *args):
        self.callable = callable
        self.args = args
        self.wait = 60
        self.postpone = False
        self.scheduled = False

    def _postpone_call(self, loop):
        print(datetime.now())
        if self.postpone:
            loop.call_later(self.wait, self._postpone_call, loop)
            self.postpone = False
        else:
            self.callable(*self.args)
            self.scheduled = False

    def run(self, loop):
        if self.scheduled is False:
            print("first run")
            loop.call_later(self.wait, self._postpone_call, loop)
            self.scheduled = True
        else:
            print("postponed")
            self.postpone = True


def to_be_run():
    print('Exec')


postponed_call = PostponedCall(to_be_run)
postponed_call.wait = 5
