from ..errors.errors import RecordNotFound


def filter_scope(result):
    for scope in result:
        if '_source' not in scope:
            raise RecordNotFound("No _source in response form elastic.")
        yield scope['_source']



