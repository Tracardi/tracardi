from lark import Transformer


class Namespace:
    def __init__(self, namespace, transformer):
        self.namespace = namespace
        self.transformer = transformer
        self._namespace_size = len(self.namespace) if self.namespace else 0

    def __repr__(self):
        return "Namespace:`{}`, Transformer: `{}`".format(self.namespace, type(self.transformer).__name__)

    def get_method(self, item):
        if self.namespace and item[:self._namespace_size] == self.namespace:
            method = item[self._namespace_size:]
            try:
                method = getattr(self.transformer, method)
            except AttributeError as e:
                raise AttributeError("Method get_method returned {}".format(str(e)))
            if callable(method):
                return method
        return None


class TransformerNamespace(Transformer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._namespaces = []

    def namespace(self, namespace, transformer):
        if not isinstance(namespace, str):
            raise ValueError("Namespace parameter is not string")

        self._namespaces.append(Namespace(namespace, transformer))

    def __getattr__(self, item):
        if self._namespaces:
            for n in self._namespaces:
                method = n.get_method(item)
                if method:
                    return method

        raise AttributeError(
                "Method `{}` not available in any of defined namespaces. Available namespaces are {}".format(item,
                                                                                                         self._namespaces))


if __name__ == "__main__":
    class A(TransformerNamespace):
        def a(self):
            print("A.a")


    class B(TransformerNamespace):
        def a(self):
            print("B.a")

        def b(self):
            print("B.b")


    t = TransformerNamespace()

    t.namespace("__a_", A())
    t.namespace("__b_", B())

    t.__a_a()
