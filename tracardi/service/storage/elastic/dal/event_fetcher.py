from typing import List

from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.elastic.driver.factory import storage_manager


class EventContextFetcher:

    def __init__(self, profile_id, session_id=None):
        self.session_id = session_id
        self.profile_id = profile_id

    def _get_query(self, query: str) -> str:
        if self.session_id:
            kql = f"profile.id:\"{self.profile_id}\" AND session.id: \"{self.session_id}\""
        else:
            kql = f"profile.id: \"{self.profile_id}\""

        if query:
            return f"{kql} AND ({query})"
        return kql

    async def fetch_event_types(self,
                                query: str = None,
                                start: int = 0,
                                limit: int = 50,
                                time_field: str = "metadata.time.insert",
                                time_zone: str = "UTC",
                                min_date_time='now-7d/d',
                                max_date_time='now'
                                ) -> StorageRecords:
        es_query = {
            "from": start,
            "size": limit,
            'sort': [{time_field: 'asc'}],
            "query": {
                "bool": {
                    "filter": {
                        "range": {
                            time_field: {
                                'from': min_date_time,
                                'to': max_date_time,
                                'include_lower': True,
                                'include_upper': True,
                                'boost': 1.0,
                                'time_zone': time_zone if time_zone else "UTC"
                            }
                        }
                    }
                }
            }
        }
        es_query['query']["bool"]["must"] = {'query_string': {"query": self._get_query(query)}}
        return await storage_manager("event").query(es_query)
