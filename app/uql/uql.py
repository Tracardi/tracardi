from unomi_query_language.query.dispatcher import Dispatcher
from unomi_query_language.query.parser import Parser
from unomi_query_language.query.grammar.grammars import read
from unomi_query_language.query.transformers.delete_transformer import DeleteTransformer
from unomi_query_language.query.transformers.select_transformer import SelectTransformer

from ..errors.errors import NullResponseError
from .router import UqlRouter


class UQL:

    def __init__(self, host):
        self.dispatcher = Dispatcher(host)
        self.router = UqlRouter()
        self.parsers = {}

    def get_unomi_query(self, q):
        route = self.router(q)

        if route.grammar not in self.parsers:
            parser = Parser(read(route.grammar), start=route.start)
            self.parsers[route.grammar] = parser

        tree = self.parsers[route.grammar].parse(q)

        return route.transformer.transform(tree)

    def select(self, q):

        grammar = 'uql_select.lark'

        if grammar not in self.parsers:
            parser = Parser(read(grammar), start='select')
            self.parsers[grammar] = parser

        tree = self.parsers[grammar].parse(q)

        unomi_tuple = SelectTransformer().transform(tree)
        data_type, uri, method, query, status = unomi_tuple
        result = self.dispatcher.fetch(unomi_tuple)
        response, expected_status = result

        return data_type, response, expected_status

    def delete(self, q):

        grammar = 'uql_delete.lark'

        if grammar not in self.parsers:
            parser = Parser(read(grammar), start='delete')
            self.parsers[grammar] = parser

        tree = self.parsers[grammar].parse(q)

        unomi_tuple = DeleteTransformer().transform(tree)
        data_type, uri, method, query, status = unomi_tuple
        result = self.dispatcher.fetch(unomi_tuple)
        response, expected_status = result

        return data_type, response, expected_status

    def query(self, q):

        unomi_tuple = self.get_unomi_query(q)
        data_type, _, _, _, _ = unomi_tuple
        response, expected_status = self.dispatcher.fetch(unomi_tuple)

        return data_type, response, expected_status

    def respond(self, response_tuple):
        data_type, response, expected_status = response_tuple
        if response.status_code == expected_status:
            if expected_status != 204:
                result = response.json()
            else:
                result = {}
            result['data_type'] = data_type
            return result
        error = NullResponseError("Unexpected response with code {}".format(response.status_code))
        error.response_status = response.status_code
        raise error
