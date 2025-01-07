from typing import List, Optional, Dict, Set

from adapter.bigdata.elastic.client.model.field_sort import ElasticFieldSort


def get_query_by_values(fields_and_values: List[tuple],
                        sort_by: Optional[List[ElasticFieldSort]] = None,
                        limit=1000,
                        condition='must'
                        ) -> dict:
    if condition not in ['must', 'should']:
        raise AssertionError(f"Can not use {condition} for querying elasticsearch.")

    terms = []
    for field, value in fields_and_values:
        terms.append({
            "term": {
                f"{field}": value
            }
        })

    query = {
        "size": limit,
        "query": {
            "bool": {
                condition: terms
            }
        }
    }

    if sort_by:
        sort_by_query = []
        for field in sort_by:
            if isinstance(field, ElasticFieldSort):
                sort_by_query.append(field.to_query())
        if sort_by_query:
            query['sort'] = sort_by_query

    return query


def get_query_for_duplicated_profiles_by_ids(profile_ids: List[str]):
    return {
        "size": 1000,
        "query": {
            "bool": {
                "should": [
                    {
                        "terms": {
                            "ids": profile_ids
                        }
                    },
                    {
                        "terms": {
                            "id": profile_ids
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        },
        "sort": [
            {"metadata.time.insert": "asc"}
            # todo maybe should be based on updates (but update should always exist)
        ]
    }


def get_query_for_auto_merge():
    return {
        "query": {
            "exists": {
                "field": "metadata.system.aux.auto_merge"
            }
        }
    }


def get_agg_query_for_duplicated_profile_counts():
    return {
        "size": 0,
        "aggs": {
            "duplicate_ids": {
                "terms": {
                    "field": "ids",
                    "min_doc_count": 2,
                    "size": 1000
                }
            }
        }
    }


def get_update_query_to_update_profile_id(old_profile_id, new_profile_id):
    return {
        "script": {
            "source": "ctx._source.profile.id = params.merged_profile_id",
            "lang": "painless",
            "params": {
                "merged_profile_id": f"{new_profile_id}"
            }
        },
        "query": {
            "term": {
                "profile.id": old_profile_id
            }
        }
    }


def get_agg_query_for_duplicated_profiles_by_field(field: str):
    # Counts profiles by field

    return {
        "size": 0,
        "query": {
            "exists": {
                "field": field
            }
        },
        "aggs": {
            "duplicate_emails": {
                "terms": {
                    "field": field,
                    "min_doc_count": 2,
                    "size": 1000
                }
            },
        }
    }


def get_query_to_load_by_field_and_value(field, value, sort: List[Dict[str, Dict]] = None, limit=100) -> dict:
    query = {
        "size": limit,
        "query": {
            "term": {
                field: value
            }
        }
    }
    if sort:
        query['sort'] = sort

    return query


def get_query_for_unique_values_from_field(field: str, limit: int):
    return {
        "size": 0,
        "aggs": {
            "fields": {
                "terms": {"field": field, "size": limit}
            }
        }
    }


def get_agg_query_for_log_levels(date_from) -> dict:
    return {
        "size": 0,
        "query": {
            "range": {
                "date": {
                    "gte": date_from,
                    # "format": "yyyy-MM-dd'T'HH:mm:ss"
                }
            }
        },
        "aggs": {
            "error_levels": {
                "terms": {
                    "field": "level",
                    "size": 10
                }
            }
        }
    }

def get_query_to_load_profile_by_id(profile_id: str) -> dict:
    return {
        "size": 2,
        "query": {
            "bool": {
                "should": [
                    {
                        "term": {
                            "ids": profile_id
                        }
                    },
                    {
                        "term": {
                            "id": profile_id
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        },
        "sort": [
            {
                "metadata.time.update": {
                    "order": "desc"
                }
            }
        ]
    }


def get_agg_query_for_groups_of_profile_ids(profile_ids: Set[str]) -> dict:
    return {
        "size": 0,
        "query": {
            "terms": {
                "profile.id":list(profile_ids)
            }
        },
        "aggs": {
            "group_by_profile": {
                "terms": {
                    "field": "profile.id",
                    "size": 1000,
                    "order": {
                        "_count": "asc"
                    }
                }
            }
        }
    }