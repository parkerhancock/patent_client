import pytest

from .manager import USApplicationManager

def test_all_apps():
    manager = USApplicationManager().filter(query=dict())
    assert len(manager) > 1000

def test_get_one_app():
    app = USApplicationManager().get(q="applicationNumberText:16123456")
    assert app is not None
    assert app.appl_id == "16123456"

def test_get_app_from_search_result():
    manager = USApplicationManager()
    result = manager.get(q="applicationNumberText:16123456")
    assert result.application.appl_id == "16123456"

def test_get_app_biblio_from_search_result():
    manager = USApplicationManager()
    result = manager.get(q="applicationNumberText:16123456")
    assert result.biblio.appl_id == "16123456"

def test_get_continuity_from_search_result():
    manager = USApplicationManager()
    result = manager.get(q="applicationNumberText:16123456")
    assert len(result.continuity.child_continuity) > 0

def test_get_documents_from_search_result():
    manager = USApplicationManager()
    result = manager.get(q="applicationNumberText:16123456")
    assert len(result.docs) > 0

def test_simple_keyword_searches():
    manager = USApplicationManager()
    result = manager.get("16123456")
    assert result.appl_id == "16123456"

def test_combination_search():
    manager = USApplicationManager()
    result = manager.filter(invention_title="Hair Dryer", filing_date_gte="2020-01-01")
    assert len(result) > 5
