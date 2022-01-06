from collections import defaultdict


class DagGraphSorter:

    def __init__(self, nodes):
        self.graph = defaultdict(list)
        self.V = nodes

    def add_edge(self, u, v):
        self.graph[u].append(v)

    def _topological_sort(self, v, visited, stack):
        visited[v] = True

        for i in self.graph[v]:
            if not visited[i]:
                self._topological_sort(i, visited, stack)

        stack.insert(0, v)

    def topological_sort(self):
        visited = {node: False for node in self.V}
        stack = []

        for i in self.V:
            if not visited[i]:
                self._topological_sort(i, visited, stack)

        return stack
