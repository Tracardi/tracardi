from typing import Optional


class SessionContext(dict):

    def get_time_zone(self) -> Optional[str]:
        try:
            return self['time']['tz']
        except KeyError:
            return None

    def get_platform(self):
        try:
            return self['browser']['local']['device']['platform']
        except KeyError:
            return None

    def get_browser_name(self):
        try:
            return self['browser']['local']['browser']['name']
        except KeyError:
            return None