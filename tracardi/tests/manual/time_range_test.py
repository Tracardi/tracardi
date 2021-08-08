from tracardi.domain.time_range_query import DatetimeRangePayload

# g = DatetimeRangePayload()
# print(g.get_dates())
# print()

a = {"minDate": {"absolute": None, "delta": {"type": "minus", "value": -2, "entity": "day"}, "now": None},
     "maxDate": {"absolute": None, "delta": {"type": "plus", "value": 1, "entity": "week"}, "now": None},
     "where": "undefined", "limit": 10, "timeZone": "Europe/Warsaw", "rand": "0.9398943914399749"}
q = DatetimeRangePayload(**a)
print(q.minDate.absolute)
d1, d2 = q.get_dates()
print(d1, d2)
# exit()
# a = {
#     "minDate": {
#         "absolute": {
#             "year": 2010,
#             "month": 1,
#             "date": 1,
#             "hour": 2,
#             "minute": 3,
#             "second": 4,
#             "meridiem": "PM"
#         },
#         "delta": {
#             "entity": "hour",
#             "value": -1,
#         }
#     },
#     "maxDate": {
#         "absolute": {
#             "year": 2020,
#             "month": 1,
#             "date": 1,
#             "hour": 2,
#             "minute": 3,
#             "second": 4,
#             "meridiem": "PM"
#         },
#     }
# }
#
# q = DatetimeRangePayload(**a)
# dd = q.get_dates()
# pprint(dd)
