from tracardi.service.notation.dot_accessor import DotAccessor


class PerformanceValueGetter:

    def __init__(self, dot: DotAccessor):
        self.dot = dot
        self.events = [
            "navigationStart",
            "redirectStart",
            "redirectEnd",
            "fetchStart",
            "domainLookupStart",
            "domainLookupEnd",
            "connectStart",
            "secureConnectionStart",
            "connectEnd",
            "requestStart",
            "responseStart",
            "responseEnd",
            "domContentLoadedEventStart",
            "domContentLoadedEventEnd",
            "domInteractive",
            "domContentLoaded",
            "domComplete",
            "loadEventStart",
            "loadEventEnd"
        ]

    def get_performance_value(self, key: str):

        index = self.events.index(key)

        value = 0
        while value == 0 and index >= 0:
            try:
                value = self.dot[f"event@context.performance.{self.events[index]}"]
            except KeyError:
                value = 0
            index -= 1

        return value



