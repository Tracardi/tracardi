from tracardi.service.storage.mysql.utils.select_result import SelectResult


def test_initialized_with_list_of_rows():
    rows = [1, 2, 3]
    select_result = SelectResult(rows)
    assert select_result.rows == rows


def test_initialized_with_empty_list():
    rows = []
    select_result = SelectResult(rows)
    assert select_result.rows == rows
    assert not select_result.exists()


def test_map_to_objects():
    rows = [1, 2, 3]
    select_result = SelectResult(rows)
    mapper = lambda x: x * 2
    result = list(select_result.map_to_objects(mapper))
    assert result == [2, 4,6]


def test_map_to_object():

    def mapper(x):
        return x['value'] * 2

    rows = {"value": 2}
    select_result = SelectResult(rows)
    result = select_result.map_to_object(mapper)
    assert result == 4

def test_map_to_objects_empty_list():
    rows = []
    select_result = SelectResult(rows)
    mapper = lambda x: x * 2
    result = list(select_result.map_to_objects(mapper))
    assert result == []
