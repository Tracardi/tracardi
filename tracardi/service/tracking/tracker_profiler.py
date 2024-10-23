from time import time
from tabulate import tabulate


class TrackerProfiler:

    def __init__(self):
        self._start = self._last = time()

        self._measures = []

    def measure(self, name):
        now = time()
        self._measures.append([name, now - self._start, now - self._last])
        self._last = now

    def report(self):
        headers = ["Point", "Time", "Step"]

        print(tabulate(self._measures, headers, tablefmt="grid"))

    def total(self):
        print(self._measures[-1])


    def get_measures(self):
        return self._measures


    def reset_measures(self):
        self._measures = []