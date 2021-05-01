from .transformer_namespace import TransformerNamespace


class MetaTransformer(TransformerNamespace):

    def READ_ONLY(self, args):
        return 'READ_ONLY', True

    def DISABLED(self, args):
        return 'DISABLED', False

    def HIDDEN(self, args):
        return 'HIDDEN', True

    def describe(self, args):
        return 'DESCRIBE', str(args[0].value).strip("\"")

    def NAME(self, args):
        return 'NAME', args.value.strip("\"")

    def in_scope(self, args):
        return 'IN_SCOPE', str(args[0].value).strip("\"")

    def with_tags(self, args):
        return 'TAGS', [t.value.strip("\"") for t in args]


