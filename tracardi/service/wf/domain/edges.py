from .edge import Edge  # noqa: F401


class Edges(dict):

    def validate(self, nodes):
        for id, edge in self.items():  # type: Edge
            edge.is_valid(nodes)
