import dateparser

from .transformer_namespace import TransformerNamespace


class CommonTransformer(TransformerNamespace):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def ESCAPED_STRING(self, args):
        return 'ESCAPED_STRING', args.value.replace("\"", "")

    def INTEGER(self, args):
        return 'INTEGER', args.value

    def BOOL(self, args):
        return 'BOOL', True if args.value.lower() == 'true' else False

    def FLOAT(self, args):
        return 'FLOAT', args.value

    def value(self, args):
        type = args[0].type

        # remove namespace
        if '__' in type:
            type = type.split('__')[-1]

        if type == "ESCAPED_STRING":
            value = args[0].value.replace("\"", "")
        else:
            value = args[0].value
        return type, value

    def array(self, args):
        return 'ARRAY', args

    def compound_parser(self, args):
        return args[0].value

    def compound_value(self, args):
        value = args[1][1]
        value_type = args[0].lower()
        if value_type == 'date':
            date = dateparser.parse(value)
            if not date:
                raise ValueError("Could not parse date `{}`".format(value))
            value = date.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            raise ValueError("Unknown parse function `{}`".format(value_type))

        return value_type,value

    def DOTTED_FIELD(self, args):
        return 'DOTTED_FIELD', args.value