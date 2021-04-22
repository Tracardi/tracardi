from _datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel


class TimeRangeQuery(BaseModel):
    fromDate: dict
    toDate: dict
    query: Optional[str] = ""
    timeZone: Optional[str] = None
    offset: int = 0
    limit: int = 20
    rand: Optional[float] = 0

    @staticmethod
    def get_absolute_date(date_object):

        if 'now' in date_object and date_object['now'] == "now":
            return datetime.now()

        if 'relative' in date_object and date_object['relative'] is None:
            return None

        if 'relative' in date_object and isinstance(date_object['relative'], dict) \
                and date_object['relative']['type'] is not None \
                and date_object['relative']['value'] is not None \
                and date_object['relative']['entity'] is not None:
            return None

        if date_object['year'] is not None \
                and date_object['month'] is not None \
                and date_object['date'] is not None \
                and date_object['hour'] is not None \
                and date_object['minute'] is not None \
                and date_object['second'] is not None \
                and date_object['meridiem'] is not None:
            date = "{}/{}/{} {}:{}:{} {}".format(date_object['year'],
                                          date_object['month'],
                                          date_object['date'],
                                          date_object['hour'],
                                          date_object['minute'],
                                          date_object['second'],
                                          date_object['meridiem'])

            return datetime.strptime(date, '%Y/%m/%d %I:%M:%S %p')

        return None

    @staticmethod
    def get_relative_date(date_object):
        if 'relative' in date_object \
                and isinstance(date_object['relative'], dict) \
                and isinstance(date_object['relative']['type'], str) \
                and (isinstance(date_object['relative']['value'], int) or isinstance(date_object['relative']['value'], str)) \
                and isinstance(date_object['relative']['entity'], str):

            entity = date_object['relative']['entity']
            value = int(date_object['relative']['value'])
            type = date_object['relative']['type']
            if entity in ['second', 'seconds']:
                return timedelta(seconds=value), type
            elif entity in ['minute', 'minutes']:
                return timedelta(minutes=value), type
            elif entity in ['hour', 'hours']:
                return timedelta(hours=value), type
            elif entity in ['day', 'days']:
                return timedelta(days=value), type
            elif entity in ['week', 'weeks']:
                return timedelta(weeks=value), type
            elif entity in ['month', 'months']:
                return timedelta(days=value * 31), type
            elif entity in ['year', 'years']:
                return timedelta(days=value * 356), type

        return None, None

    def get_dates(self):
        from_absolute = TimeRangeQuery.get_absolute_date(self.fromDate)
        to_absolute = TimeRangeQuery.get_absolute_date(self.toDate)
        if from_absolute and to_absolute:
            return from_absolute, to_absolute

        if from_absolute and not to_absolute:
            to_delta, type = TimeRangeQuery.get_relative_date(self.toDate)
            if to_delta and type:
                if type == "minus":
                    raise ValueError("Incorrect time range. Start date can not be later then end date.")
                elif type == 'plus':
                    return from_absolute, from_absolute + to_delta

        if not from_absolute and to_absolute:
            from_delta, type = TimeRangeQuery.get_relative_date(self.fromDate)
            if from_delta and type:
                if type == "plus":
                    raise ValueError("Incorrect time range. End date can not be earlier then start date.")
                elif type == 'minus':
                    return to_absolute - from_delta, to_absolute

        raise ValueError("Incorrect time range. There is no anchor absolute date.")


if __name__ == "__main__":
    d1 = {
        "year": "2020",
        "month": "01",
        "date": "01",
        "hour": "12",
        "minute": 12,
        "second": 00,
    }

    d2 = {
        "year": "2020",
        "month": "01",
        "date": "01",
        "hour": "12",
        "minute": 12,
        "second": 00,
        "relative": {
            "type": "minus",
            "value": 1,
            "entity": "month"
        }
    }

    print(TimeRangeQuery.get_dates(d2, d1))
