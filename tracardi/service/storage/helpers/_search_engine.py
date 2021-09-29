# import logging
# from datetime import datetime
# from pprint import pprint
# from typing import Tuple, Optional
#
# from tracardi.domain.storage_result import StorageResult
#
# from tracardi.service.singleton import Singleton
#
# from tracardi.domain.query_result import QueryResult
# from tracardi.domain.time_range_query import DatetimeRangePayload
# from tracardi.exceptions.exception import StorageException
# from tracardi.process_engine.tql.parser import Parser
# from tracardi.process_engine.tql.transformer.filter_transformer import FilterTransformer
# from tracardi.service.storage.driver import storage
#
# _logger = logging.getLogger("SqlSearchQueryEngine")
#
#
# class SqlSearchQueryParser(metaclass=Singleton):
#     def __init__(self):
#         self.parser = Parser(Parser.read('grammar/filter_condition.lark'), start='expr')
#
#     def parse(self, query) -> Optional[dict]:
#         if not query:
#             return None
#
#         tree = self.parser.parse(query)
#         result = FilterTransformer().transform(tree)
#         return result
#
#
# class SqlSearchQueryEngine:
#
#     def __init__(self, index):
#         self.index = index
#         self.time_fields_map = {
#             'event': 'metadata.time.insert',
#             'session': 'metadata.time.insert',
#             'profile': 'metadata.time.insert',
#         }
#         self.parser = SqlSearchQueryParser()
#
#     @staticmethod
#     def _convert_time_zone(query, min_date_time, max_date_time) -> Tuple[datetime, datetime, Optional[str]]:
#         time_zone = "UTC" if query.timeZone is None or query.timeZone == "" else query.timeZone
#
#         if time_zone != "UTC":
#             min_date_time, time_zone = query.convert_to_local_datetime(min_date_time, time_zone)
#             max_date_time, time_zone = query.convert_to_local_datetime(max_date_time, time_zone)
#
#         return min_date_time, max_date_time, time_zone
#
#     async def search(self, query: str = None, start: int = 0, limit: int = 20):
#         query = self.parser.parse(query)
#
#         if query is None:
#             query = {
#                 "query": {
#                     "match_all": {}
#                 }
#             }
#
#         query['from'] = start
#         query['size'] = limit
#         result = await storage.driver.raw.index(self.index).query(query)
#         return StorageResult(result).dict()
#
#     def _query(self, query: DatetimeRangePayload, min_date_time, max_date_time, time_field: str, time_zone: str) -> dict:
#         query_range = {
#             'range': {
#                 time_field: {
#                     'from': min_date_time,
#                     'to': max_date_time,
#                     'include_lower': True,
#                     'include_upper': True,
#                     'boost': 1.0,
#                     'time_zone': time_zone if time_zone else "UTC"
#                 }
#             }
#         }
#
#         es_query = {
#             "from": query.start,
#             "size": query.limit,
#             'sort': [{time_field: 'desc'}]
#         }
#
#         query_where = self.parser.parse(query.where)
#
#         if query_where is not None:
#             es_query['query'] = {
#                 "bool": {
#                     "must": [
#                         query_where,
#                         query_range
#                     ]
#                 }
#             }
#         else:
#             es_query['query'] = query_range
#
#         return es_query
#
#     async def time_range(self, query: DatetimeRangePayload) -> QueryResult:
#
#         if self.index not in self.time_fields_map:
#             raise ValueError("No time_field available on `{}`".format(self.index))
#
#         min_date_time, max_date_time = query.get_dates()  # type: datetime, datetime
#         min_date_time, max_date_time, time_zone = self._convert_time_zone(query, min_date_time, max_date_time)
#
#         time_field = self.time_fields_map[self.index]
#
#         # query_range = {
#         #     'range': {
#         #         time_field: {
#         #             'from': min_date_time,
#         #             'to': max_date_time,
#         #             'include_lower': True,
#         #             'include_upper': True,
#         #             'boost': 1.0,
#         #             'time_zone': time_zone if time_zone else "UTC"
#         #         }
#         #     }
#         # }
#         #
#         # es_query = {
#         #     "from": query.start,
#         #     "size": query.limit,
#         #     'sort': [{time_field: 'desc'}]
#         # }
#         #
#         # query_where = self.parser.parse(query.where)
#         #
#         # if query_where is not None:
#         #     es_query['query'] = {
#         #         "bool": {
#         #             "must": [
#         #                 query_where,
#         #                 query_range
#         #             ]
#         #         }
#         #     }
#         # else:
#         #     es_query['query'] = query_range
#
#         es_query = self._query(query, min_date_time, max_date_time, time_field, time_zone)
#
#         from pprint import pprint
#         pprint(es_query)
#         try:
#             result = await storage.driver.raw.index(self.index).filter(es_query)
#         except StorageException as e:
#             _logger.error("Could not filter {}. Reason: {}".format(es_query, str(e)))
#             return QueryResult(total=0, result=[])
#
#         return QueryResult(**result.dict())
#
#     async def histogram(self, query: DatetimeRangePayload):
#
#         def __interval(min: datetime, max: datetime):
#
#             max_interval = 50
#             min_interval = 20
#
#             span = max - min
#
#             if span.days > max_interval:
#                 # up
#                 return int(span.days / max_interval), 'd', "%y-%m-%d"
#             elif min_interval > span.days:
#                 # down
#                 interval = int((span.days * 24) / max_interval)
#                 if interval > 0:
#                     return interval, 'h', "%d/%m %H:%M"
#
#                 # minutes
#                 interval = int((span.days * 24 * 60) / max_interval)
#                 if interval > 0:
#                     return interval, 'm', "%H:%M"
#
#                 return 1, 'm', "%H:%M"
#
#             return 1, 'd', "%y-%m-%d"
#
#         def __format(data, unit, interval, format):
#             for row in data:
#                 # todo timestamp no timezone
#                 timestamp = datetime.fromisoformat(row["key_as_string"].replace('Z', '+00:00'))
#                 yield {
#                     "time": "{}".format(timestamp.strftime(format)),
#                     'interval': "+{}{}".format(interval, unit),
#                     "events": row["doc_count"]
#                 }
#
#         min_date_time, max_date_time = query.get_dates()  # type: datetime, datetime
#         min_date_time, max_date_time, time_zone = self._convert_time_zone(query, min_date_time, max_date_time)
#
#         # sql = query.where
#         time_field = self.time_fields_map[self.index]
#
#         interval, unit, format = __interval(min_date_time, max_date_time)
#
#         es_query = self._query(query, min_date_time, max_date_time, time_field, time_zone)
#
#
#         # sql = to_time_range_sql_query(self.read_index, time_field, min_date_time, max_date_time, sql)
#
#         # try:
#         #     translated_query = await self.storage_service.translate(sql)
#         # except StorageException as e:
#         #     _logger.error("Could not translate SQL {}. Reason: {}".format(sql, str(e)))
#         #     return QueryResult(total=0, result=[])
#
#         # if time_zone:
#         #     if 'range' in translated_query['query']:
#         #         translated_query['query']['range'][time_field]['time_zone'] = time_zone
#         #     elif 'bool' in translated_query['query'] and 'must' in translated_query['query']['bool']:
#         #         translated_query['query']['bool']['must'][0]['range'][time_field]['time_zone'] = time_zone
#
#         es_query = {
#             "size": 0,
#             "query": es_query['query'],
#             "aggs": {
#                 "items_over_time": {
#                     "date_histogram": {
#                         "min_doc_count": 0,
#                         "field": time_field,
#                         "fixed_interval": f"{interval}{unit}",
#                         "extended_bounds": {
#                             "min": min_date_time,
#                             "max": max_date_time
#                         }
#                     }
#                 }
#             }
#         }
#
#         if time_zone:
#             es_query['aggs']['items_over_time']['date_histogram']['time_zone'] = time_zone
#
#         pprint(es_query)
#
#         try:
#             result = await storage.driver.raw.index(self.index).query(es_query)
#         except StorageException as e:
#             _logger.error("Could not query {}. Reason: {}".format(es_query, str(e)))
#             return QueryResult(total=0, result=[])
#
#         qs = {
#             'total': result['hits']['total']['value'],
#             'result': list(__format(result['aggregations']['items_over_time']['buckets'], unit, interval, format))
#         }
#
#         return QueryResult(**qs)
