import re
from typing import Optional
from typing.re import Match
from ..model.configuration import Configuration


class Validator:
    def __init__(self, config: Configuration):
        self.config = config

    def check(self, string) -> Optional[Match[str]]:
        """Check the validation"""
        return re.match(self.config.validation_regex, string)
