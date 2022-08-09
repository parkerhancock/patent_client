import datetime

from .patent.manager import PatentManager

today = datetime.datetime.now().date().strftime("%Y%m%d")


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
    assert query == 'AN/"National Oilwell Varco" AND ISD/19950101->20130101'
    query = search.generate_query(
        {
            "assignee_name": "National Oilwell Varco",
            "issue_date_gt": "1995-01-01",
        }
    )
    assert query == f'AN/"National Oilwell Varco" AND ISD/19950101->{today}'
    query = search.generate_query(
        {
            "assignee_name": "National Oilwell Varco",
            "issue_date_lt": "2020-10-26",
        }
    )
    assert query == 'AN/"National Oilwell Varco" AND ISD/19000101->20201026'
    query = search.generate_query(
        {
            "assignee_name": "National Oilwell Varco",
            "issue_date": "2020-10-26",
        }
    )
    assert query == 'AN/"National Oilwell Varco" AND ISD/20201026'
