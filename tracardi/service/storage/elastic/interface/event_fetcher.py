from typing import List

from tracardi.service.storage.driver.elastic import event as event_db


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

    def _query(self,
               query: str = None,
               start: int = 0,
               limit: int = 50,
               time_field: str = "metadata.time.insert",
               time_zone: str = "UTC",
               min_date_time='now-7d/d',
               max_date_time='now'
               ) -> dict:
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

        return es_query

    async def fetch_event_types(
            self,
            query: str = None,
            start: int = 0,
            limit: int = 50,
            time_field: str = "metadata.time.insert",
            time_zone: str = "UTC",
            min_date_time='now-7d/d',
            max_date_time='now'
    ) -> List[str]:
        query = self._query(
            query,
            start,
            limit,
            time_field,
            time_zone,
            min_date_time,
            max_date_time
        )
        events = await event_db.query(query)
        return [event['type'] for event in events]
