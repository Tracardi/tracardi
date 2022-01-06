from .edge import Edge


class Edges(dict):

    def validate(self, nodes):
        for id, edge in self.items():  # type: Edge
            edge.is_valid(nodes)
