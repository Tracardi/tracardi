import re

from .dot_accessor import DotAccessor
from ..singleton import Singleton


class DotTemplate(metaclass=Singleton):

    def __init__(self):
        self._regex = re.compile(r"\{{2}\s*((?:payload|profile|event|session|flow|memory)"
                                r"@[\[\]0-9a-zA-a_\-\.]+(?<![\.\[]))\s*\}{2}")

    def render(self, template, dot: DotAccessor):
        return re.sub(self._regex, lambda x: str(dot[x.group(1)]), template)

