import datetime
from patent_client.base.model import Model
from .session import session

class Result(Model):
    pos: str = None
    serial_num: str = None
    reg_num: str = None
    word_mark: str = None
    record_url: str = None
    status_url: str = None
    live: str = None
    classes: str = None



class TessRecord(Model):
    img_url: str = None
    word_mark: str = None
    goods_and_services: str = None
    standard_characters_claimed: str = None
    mark_drawing_code: str = None
    trademark_search_facility_classification_code: str = None
    serial_number: str = None
    filing_date: datetime.date = None
    current_basis: str = None
    original_filing_basis: str = None
    published_for_opposition: str = None
    registration_number: str = None
    registration_date: datetime.date = None
    owner: str = None
    attorney_of_record: str = None
    prior_registrations: str = None
    type_of_mark: str = None
    register: str = None
    renewal: str = None
    live_dead_indicator: str = None