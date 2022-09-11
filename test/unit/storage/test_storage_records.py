from tracardi.domain.storage_record import StorageRecords, StorageRecord, RecordMetadata, StorageAggregate, \
    StorageAggregates


def test_should_assign_and_read_values():
    records = StorageRecords.build_from_elastic({
        "took": 5,
        "timed_out": False,
        "_shards": {
            "total": 100,
            "successful": 1,
            "skipped": 0,
            "failed": 0
        },
        "hits": {
            "total": {
                "value": 20,
                "relation": "eq"
            },
            "max_score": 1.3862942,
            "hits": [
                {
                    "_index": "my-index-000001",
                    "_id": "0",
                    "_score": 1.3862942,
                    "_source": {
                        "@timestamp": "2099-11-15T14:12:12",
                        "http": {
                            "request": {
                                "method": "get"
                            },
                            "response": {
                                "status_code": 200,
                                "bytes": 1070000
                            },
                            "version": "1.1"
                        },
                        "source": {
                            "ip": "127.0.0.1"
                        },
                        "message": "GET /search HTTP/1.1 200 1070000",
                        "user": {
                            "id": "kimchy"
                        }
                    }
                }
            ]
        }
    })

    assert isinstance(records, dict)
    first_record = records.first()

    assert isinstance(first_record, StorageRecord)
    assert first_record.get_meta_data().index == "my-index-000001"
    assert first_record.get_meta_data().id == "0"
    assert first_record["id"] == "0"
    assert first_record["@timestamp"] == "2099-11-15T14:12:12"
    assert first_record["source"]["ip"] == "127.0.0.1"
    assert first_record["message"] == "GET /search HTTP/1.1 200 1070000"

    assert records.dict()["total"] == 20
    assert len(records) == 1
    assert len(records.dict()["result"]) == 1

    records.transform_hits(lambda record: {"replaced": 1})

    list_of_records = list(records)
    assert list_of_records[0] == {"replaced": 1, "id": "0"}
    assert list_of_records[0].get_meta_data().index == "my-index-000001"


def test_should_handle_empty_data():
    records = StorageRecords.build_from_elastic()
    assert isinstance(records, dict)
    list_of_records = list(records)
    assert list_of_records == []
    assert records.dict()["total"] == 0
    assert records.dict()["result"] == []


def test_should_slice_records():
    records = StorageRecords.build_from_elastic({
        "took": 5,
        "timed_out": False,
        "_shards": {
            "total": 1,
            "successful": 1,
            "skipped": 0,
            "failed": 0
        },
        "hits": {
            "total": {
                "value": 20,
                "relation": "eq"
            },
            "max_score": 1.3862942,
            "hits": [
                {
                    "_index": "my-index-000001",
                    "_id": "0",
                    "_score": 1.3862942,
                    "_source": {
                        "@timestamp": "2099-11-15T14:12:12",
                        "http": {
                            "request": {
                                "method": "get"
                            },
                            "response": {
                                "status_code": 200,
                                "bytes": 1070000
                            },
                            "version": "1.1"
                        },
                        "source": {
                            "ip": "127.0.0.1"
                        },
                        "message": "GET /search HTTP/1.1 200 1070000",
                        "user": {
                            "id": "kimchy"
                        }
                    }
                },
                {
                    "_index": "my-index-000002",
                    "_id": "1",
                    "_score": 1.3862942,
                    "_source": {
                        "@timestamp": "2099-11-15T14:12:12",
                        "http": {
                            "request": {
                                "method": "get"
                            },
                            "response": {
                                "status_code": 200,
                                "bytes": 1070000
                            },
                            "version": "1.1"
                        },
                        "source": {
                            "ip": "127.0.0.1"
                        },
                        "message": "GET /search HTTP/1.1 200 1070000",
                        "user": {
                            "id": "kimchy"
                        }
                    }
                },
                {
                    "_index": "my-index-000003",
                    "_id": "2",
                    "_score": 1.3862942,
                    "_source": {
                        "@timestamp": "2099-11-15T14:12:12",
                        "http": {
                            "request": {
                                "method": "get"
                            },
                            "response": {
                                "status_code": 200,
                                "bytes": 1070000
                            },
                            "version": "1.1"
                        },
                        "source": {
                            "ip": "127.0.0.1"
                        },
                        "message": "GET /search HTTP/1.1 200 1070000",
                        "user": {
                            "id": "kimchy"
                        }
                    }
                }
            ]
        }
    })

    assert records[0]["id"] == "0"
    assert records[1]["id"] == "1"
    assert records[2]["id"] == "2"

    record = records[0]  # type: StorageRecord

    assert isinstance(record, StorageRecord)
    assert isinstance(record.get_meta_data(), RecordMetadata)
    assert record.get_meta_data().index == "my-index-000001"

    assert [row["id"] for row in records[1:]] == ["1", "2"]
    assert [row["id"] for row in records[:1]] == ["0"]
    assert [row["id"] for row in records[0:2]] == ["0", "1"]

    for i, row in enumerate(records[0:2]):
        assert isinstance(row, StorageRecord)
        assert isinstance(row.get_meta_data(), RecordMetadata)
        assert row.get_meta_data().index == f"my-index-00000{i + 1}"


def test_should_handle_aggregates():
    response = {
        "hits": {"total": {"value": 0, "relation": "eq"}, "max_score": None, "hits": []},
        "aggregations": {
            "aggr_name": {
                "doc_count_error_upper_bound": 0,
                "sum_other_doc_count": 0,
                "buckets": [
                    {
                        "key": "collected",
                        "doc_count": 2,
                        "items_over_time": {
                            "buckets": [
                                {"key_as_string": "2021-08-19T00:00:00.000+02:00", "key": 1629324000000,
                                 "doc_count": 0},
                                {"key_as_string": "2021-09-02T00:00:00.000+02:00", "key": 1630533600000,
                                 "doc_count": 0},
                                {"key_as_string": "2021-09-16T00:00:00.000+02:00", "key": 1631743200000,
                                 "doc_count": 0},
                                {"key_as_string": "2021-09-30T00:00:00.000+02:00", "key": 1632952800000,
                                 "doc_count": 0},
                                {"key_as_string": "2021-10-14T00:00:00.000+02:00", "key": 1634162400000,
                                 "doc_count": 0},
                                {"key_as_string": "2021-10-28T00:00:00.000+02:00", "key": 1635372000000, "doc_count": 0}
                            ]
                        }
                    }
                ]
            }
        }
    }

    records = StorageRecords.build_from_elastic(response)
    assert isinstance(records.aggregations("aggr_name"), StorageAggregate)
    assert isinstance(records.aggregations(), StorageAggregates)
    assert records.aggregations("aggr_name").buckets() == [
                    {
                        "key": "collected",
                        "doc_count": 2,
                        "items_over_time": {
                            "buckets": [
                                {"key_as_string": "2021-08-19T00:00:00.000+02:00", "key": 1629324000000,
                                 "doc_count": 0},
                                {"key_as_string": "2021-09-02T00:00:00.000+02:00", "key": 1630533600000,
                                 "doc_count": 0},
                                {"key_as_string": "2021-09-16T00:00:00.000+02:00", "key": 1631743200000,
                                 "doc_count": 0},
                                {"key_as_string": "2021-09-30T00:00:00.000+02:00", "key": 1632952800000,
                                 "doc_count": 0},
                                {"key_as_string": "2021-10-14T00:00:00.000+02:00", "key": 1634162400000,
                                 "doc_count": 0},
                                {"key_as_string": "2021-10-28T00:00:00.000+02:00", "key": 1635372000000, "doc_count": 0}
                            ]
                        }
                    }
                ]
