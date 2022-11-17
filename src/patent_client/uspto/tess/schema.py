import re
import lxml.etree as ET
from yankee.xml import Schema, fields as f

classification_re = re.compile(r"IC (\d{3}).")

def fmt_classification(string):
    match = classification_re.search(string)
    return match.group(1) if match else None

class ResultSchema(Schema):
    pos = f.Int(".//td[1]")
    serial_num = f.Str(".//td[2]")
    reg_num = f.Str(".//td[3]")
    word_mark = f.Str(".//td[4]")
    record_url = f.Str(".//td[2]/a/@href", formatter=lambda s: "https://tmsearch.uspto.gov" + s)
    status_url = f.Str(".//td[5]/a/@href")
    live = f.Str(".//td[6]")#, true_value="LIVE")
    classes = f.Str(".//td[7]", formatter=fmt_classification)

num_results_re = re.compile(r"docs: (\d*)")

def fmt_num_results(string):
    match = num_results_re.search(string)
    return match.group(1) if match else None

occ_re = re.compile(r"occ: (\d*)")

def fmt_occ(string):
    match = occ_re.search(string)
    return match.group(1) if match else None

last_updated_re = re.compile(r"TESS was last updated on (.*$)")

def fmt_last_updated(string):
    match = last_updated_re.search(string)
    return match.group(1) if match else None

class ResultTableSchema(Schema):
    num_results = f.Int(".//table[5]//td[4]", formatter=fmt_num_results)
    num_occurences = f.Int(".//table[5]//td[4]", formatter=fmt_occ)
    last_updated = f.DateTime(".//table[2]//i", formatter=fmt_last_updated)
    results = f.List(ResultSchema, './/table[@id="searchResultTable"]/tr')
    
table_xpath = './/td/b[contains(text(), "{}")]/following::td'

class RecordSchema(Schema):
    img_url = f.Str('.//img[@alt="Mark Image"]/@src', formatter=lambda s: "https://tmsearch.uspto.gov" + s)
    word_mark = f.Str(table_xpath.format("Word Mark"))
    goods_and_services = f.Str(table_xpath.format("Goods and Services"))
    standard_characters_claimed = f.Str(table_xpath.format("Standard Characters Claimed"))
    mark_drawing_code = f.Str(table_xpath.format("Mark Drawing Code"))
    trademark_search_facility_classification_code = f.Str(table_xpath.format("Trademark Search Facility Classification Code"))
    serial_number = f.Str(table_xpath.format("Serial Number"))
    filing_date = f.Date(table_xpath.format("Filing Date"))
    current_basis = f.Str(table_xpath.format("Current Basis"))
    original_filing_basis = f.Str(table_xpath.format("Original Filing Basis"))
    published_for_opposition = f.Date(table_xpath.format("Published for Opposition"))
    registration_number = f.Str(table_xpath.format("Registration Number"))
    registration_date = f.Date(table_xpath.format("Registration Date"))
    owner = f.Str(table_xpath.format("Owner"))
    attorney_of_record = f.Str(table_xpath.format("Attorney of Record"))
    prior_registrations = f.Str(table_xpath.format("Prior Registrations"))
    type_of_mark = f.Str(table_xpath.format("Type of Mark"))
    register = f.Str(table_xpath.format("Register"))
    renewal = f.Str(table_xpath.format("Renewal"))
    live_dead_indicator = f.Str(table_xpath.format("Live/Dead Indicator"))
