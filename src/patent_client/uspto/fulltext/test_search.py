import datetime

from .patent.manager import PatentManager

today = "{dt.month}/{dt.day}/{dt.year}".format(dt=datetime.datetime.now().date())


def test_can_generate_query():
    """
    TODO: use _gt and _lt nomenclature for date ranges
    """
    search = PatentManager()
    query = search.generate_query(
        {
            "assignee_name": "National Oilwell Varco",
            "issue_date_range": ("1995-01-01", "20130101"),
        }
    )
    assert query == 'AN/"National Oilwell Varco" AND ISD/1/1/1995->1/1/2013'
    query = search.generate_query(
        {
            "assignee_name": "National Oilwell Varco",
            "issue_date_gt": "1995-01-01",
        }
    )
    assert query == f'AN/"National Oilwell Varco" AND ISD/1/1/1995->{today}'
    query = search.generate_query(
        {
            "assignee_name": "National Oilwell Varco",
            "issue_date_lt": "2020-10-26",
        }
    )
    assert query == 'AN/"National Oilwell Varco" AND ISD/1/1/1900->10/26/2020'
    query = search.generate_query(
        {
            "assignee_name": "National Oilwell Varco",
            "issue_date": "2020-10-26",
        }
    )
    assert query == 'AN/"National Oilwell Varco" AND ISD/10/26/2020'
