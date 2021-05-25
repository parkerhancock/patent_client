from pathlib import Path
import datetime
from pprint import pprint, pformat
from .parser import FullTextParser
from .patent.schema import PatentSchema
from .published_application.schema import PublishedApplicationSchema

examples = Path(__file__).parent / "examples"

def generate_test(model):
    output = ""
    dictionary = model.to_dict()
    for k, v in dictionary.items():
        if isinstance(v, str) and len(v) > 200 or isinstance(v, list):
            output += f"assert len(result.{k}) == {len(v)}\n"
        elif isinstance(v, dict):
            output += f"assert result.{k} == {pformat(v)}\n"
        else:
            output += f"assert result.{k} == {repr(v)}\n"
    with open("generated_test.py", "w") as f:
        f.write(output)


def test_can_parse_pre_aia_patent():
    text = (examples / "patent.html").read_text()
    parser = FullTextParser()
    result = parser.parse(text)
    result = PatentSchema().deserialize(result)
    assert result.publication_number == '6095661'
    assert result.kind_code == 'B1'
    assert result.publication_date == datetime.date(2000, 8, 1)
    assert result.title == 'Method and apparatus for an L.E.D. flashlight'
    assert len(result.description) == 55314
    assert len(result.abstract) == 1543
    assert len(result.claims) == 17969
    assert result.appl_id == '09044559'
    assert result.filing_date == datetime.date(1998, 3, 19)
    assert result.family_id == '21933046'
    assert len(result.inventors) == 1
    assert len(result.applicants) == 0
    assert len(result.assignees) == 1
    assert len(result.related_us_applications) == 0
    assert len(result.prior_publications) == 0
    assert result.pct_filing_date == None
    assert result.pct_number == None
    assert result.national_stage_entry_date == None
    assert result.examiner == "O'Shea; Sandra"
    assert result.agent == 'Schwegman, Lundberg, Woessner & Kluth, P.A.'

def test_can_parse_published_app():
    text = (examples / "app.html").read_text()
    parser = FullTextParser()
    result = parser.parse(text)
    result = PublishedApplicationSchema().deserialize(result)
    assert result.publication_number == '20170370151'
    assert result.kind_code == 'A1'
    assert result.publication_date == datetime.date(2017, 12, 28)
    assert result.title == 'SYSTEMS AND METHODS TO CONTROL DIRECTIONAL DRILLING FOR HYDROCARBON WELLS'
    assert len(result.description) == 99084
    assert len(result.abstract) == 814
    assert len(result.claims) == 9208
    assert result.appl_id == '15540593'
    assert result.filing_date == datetime.date(2015, 12, 29)
    assert result.family_id == '56163586'
    assert len(result.inventors) == 4
    assert len(result.applicants) == 0
    assert len(result.assignees) == 1
    assert len(result.related_us_applications) == 3
    assert len(result.prior_publications) == 0
    assert result.pct_filing_date == datetime.date(2015, 12, 29)
    assert result.pct_number == 'PCT/US2015/067865'
    assert result.national_stage_entry_date == datetime.date(2017, 6, 29)
    assert result.examiner == None
    assert result.agent == None
