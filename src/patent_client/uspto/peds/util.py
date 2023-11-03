import datetime

from dateutil.parser import parse as dt_parse


def date_to_solr_date(date):
    if isinstance(date, datetime.datetime):
        pass
    elif isinstance(date, str):
        date = dt_parse(date)
    elif isinstance(date, datetime.date):
        date = datetime.datetime.combine(date, datetime.datetime.min.time())
    elif not isinstance(date, datetime.datetime):
        raise ValueError(f"Invalid date type: {type(date)}")
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")
